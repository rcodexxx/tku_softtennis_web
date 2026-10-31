"""產生示範資料：一個獨立的 demo 資料庫，裡面有一季半的練習日、友誼賽與賽事。

只在檔名以 demo 開頭的 SQLite 資料庫上執行，避免蓋掉真實資料：
    DATABASE_URL=sqlite:///demo.db flask --app run.py demo-seed --yes
登入帳號密碼寫在 README 的「示範資料」一節。
"""

import math
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import stamp

from ..domain import pairing
from ..domain.identity import academic_year
from ..enums import (
    GenderEnum,
    MatchCategoryEnum,
    MatchFormatEnum,
    MatchOutcomeEnum,
    MatchTypeEnum,
    MemberIdentityEnum,
    StudyProgramEnum,
    UserRoleEnum,
)
from ..extensions import db
from ..models import Event, Match, MatchRecord, Member, Organization, PracticeSession, Season, User
from ..services import rating_service

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo-password"

SURNAMES = "陳林黃張李王吳劉蔡楊許鄭謝郭洪曾邱廖賴周徐蘇葉莊呂江何蕭羅高潘簡朱鍾彭游詹胡施沈余趙盧梁顏柯翁魏孫戴范方"
MALE_GIVEN = (
    "宇翔 冠廷 承恩 柏翰 宥廷 彥廷 家豪 俊傑 建宏 志明 浩宇 子軒 品睿 宇恩 晉宇 "
    "博宇 宗翰 昱廷 睿哲 立揚 承翰 哲維 育誠 志豪 致遠 偉倫 家銘 子豪 冠宇 柏宇"
).split()
FEMALE_GIVEN = (
    "怡君 雅婷 欣妤 詩涵 宜蓁 佳穎 子晴 品妍 芷涵 語彤 思妤 郁婷 筱涵 心怡 安琪 予恩 婕妤 舒涵 采潔 可欣".split()
)
JAPANESE = ["佐藤健太", "鈴木結衣", "高橋蓮"]
SCHOOLS = ["台灣大學", "政治大學", "陽明交通大學", "臺灣科技大學", "輔仁大學"]
EVENTS = [("北區大專軟網錦標賽", 2025, 11), ("校長盃軟網賽", 2026, 4), ("全國大專盃", 2026, 10)]

# 實力差 1 分 → 強隊每局約有 6 成機率（和分數系統「差 1 分拿 7 成局數」同一個量級）
GAME_SCALE = 1 / math.log(0.62 / 0.38)


@click.command("demo-seed")
@click.option("--yes", is_flag=True, help="不詢問直接重建 demo 資料庫")
@click.option("--seed", default=7, show_default=True, help="亂數種子，同一個種子產生同樣的資料")
@with_appcontext
def demo_seed(yes: bool, seed: int) -> None:
    """重建示範資料庫，產生大量假資料來展示數據功能。"""
    database = db.engine.url.database or ""
    if not Path(database).name.startswith("demo"):
        raise click.ClickException("只能在檔名以 demo 開頭的資料庫執行，例如 DATABASE_URL=sqlite:///demo.db")
    if not yes:
        click.confirm(f"會清空並重建 {database}，確定嗎？", abort=True)

    db.drop_all()
    db.create_all()
    stamp()
    DemoBuilder(random.Random(seed)).build()
    rating_service.recalculate_all()
    db.session.commit()
    click.echo(
        f"示範資料完成：{Member.query.count()} 位球員、{MatchRecord.query.count()} 場比賽、"
        f"{PracticeSession.query.count()} 個練習日。"
    )


class DemoBuilder:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.used_names: set[str] = set()
        # 看不到的真實實力、偏好位置、組合的隱藏默契
        self.skill: dict[int, float] = {}
        self.prefers_front: dict[int, bool] = {}
        self.bonus: dict[pairing.Pair, float] = {}

    def build(self) -> None:
        team = Organization(name="淡江大學")
        alumni = Organization(name="淡江大學軟式網球校友會", short_name="校友會")
        schools = [Organization(name=name) for name in SCHOOLS]
        db.session.add_all([team, alumni, *schools])
        db.session.flush()
        current_app.config.update(TEAM_ORGANIZATION_ID=team.id, ALUMNI_ORGANIZATION_ID=alumni.id)

        self.team = self._team(team)
        self.alumni = [self._player(alumni, MemberIdentityEnum.ALUMNI, base=5.0) for _ in range(10)]
        self.opponents = [self._player(self.rng.choice(schools), None, base=5.2, guest=True) for _ in range(16)]
        db.session.flush()
        self._chemistry()

        db.session.add_all(
            [
                Season(name="114 學年度", start_date=date(2025, 8, 1)),
                Season(name="115 學年度", start_date=date(2026, 8, 1)),
            ]
        )
        self._practice_days()
        self._friendlies()
        self._events()

    # ---------- 球員 ----------

    def _team(self, team: Organization) -> list[Member]:
        year = academic_year(date(2026, 10, 31))
        members = []
        for index in range(22):
            enrolled = self.rng.choice([year - 3, year - 2, year - 1, year])
            program = StudyProgramEnum.MASTER if index % 9 == 8 else StudyProgramEnum.BACHELOR
            member = self._player(team, MemberIdentityEnum.STUDENT, base=5.0, a_division=index < 3)
            member.study_program, member.enrolled_year = program, enrolled
            members.append(member)
        exchange = self._player(team, MemberIdentityEnum.EXCHANGE, base=5.3, name=JAPANESE[0])
        coach = self._player(team, MemberIdentityEnum.COACH, base=5.8, gender=GenderEnum.MALE)
        members += [exchange, coach]

        # 示範用管理員：自己也是一位校隊球員
        admin = members[3]
        admin.user = User(username=DEMO_USERNAME, display_name=admin.name, role=UserRoleEnum.ADMIN)
        admin.user.set_password(DEMO_PASSWORD)
        return members

    def _player(self, org, identity, base, a_division=False, guest=False, gender=None, name=None) -> Member:
        gender = gender or (GenderEnum.MALE if self.rng.random() < 0.62 else GenderEnum.FEMALE)
        member = Member(
            name=name or self._name(gender),
            gender=gender,
            organization_id=org.id,
            identity=identity,
            is_a_division=a_division or (guest and self.rng.random() < 0.2),
            is_guest=guest,
            guest_identifier=f"DEMO_{len(self.used_names)}" if guest else None,
        )
        db.session.add(member)
        db.session.flush()
        skill = self.rng.gauss(base, 0.6) - (1.0 if gender == GenderEnum.FEMALE else 0.0)
        self.skill[member.id] = skill + (1.0 if member.is_a_division else 0.0)
        self.prefers_front[member.id] = self.rng.random() < 0.45
        return member

    def _name(self, gender: GenderEnum) -> str:
        given = MALE_GIVEN if gender == GenderEnum.MALE else FEMALE_GIVEN
        while True:
            name = self.rng.choice(SURNAMES) + self.rng.choice(given)
            if name not in self.used_names:
                self.used_names.add(name)
                return name

    def _chemistry(self) -> None:
        """少數組合天生特別合（黃金組合），大部分只有一點點差異。"""
        ids = [m.id for m in self.team]
        for _ in range(4):
            a, b = self.rng.sample(ids, 2)
            self.bonus[pairing.pair_key(a, b)] = self.rng.uniform(0.5, 0.8)
        for _ in range(4):
            a, b = self.rng.sample(ids, 2)
            self.bonus.setdefault(pairing.pair_key(a, b), -self.rng.uniform(0.4, 0.6))

    # ---------- 比賽 ----------

    def _practice_days(self) -> None:
        day = date(2025, 9, 3)
        while day <= date(2026, 10, 28):
            if not (date(2026, 1, 15) <= day <= date(2026, 2, 20) or date(2026, 7, 1) <= day <= date(2026, 8, 31)):
                self._practice(day)
            day += timedelta(days=7)

    def _practice(self, day: date) -> None:
        pool = self.team + self.rng.sample(self.alumni, 2)
        attendees = self.rng.sample(pool, self.rng.randint(10, 14))
        session = PracticeSession(session_date=day, location="淡江網球場", attendees=attendees)
        db.session.add(session)
        played: Counter[int] = Counter()
        partnered: Counter[pairing.Pair] = Counter()
        mode = "balanced" if self.rng.random() < 0.3 else "rotate"
        ratings = {m.id: self.skill[m.id] for m in attendees}
        for round_number in range(self.rng.randint(4, 6)):
            round_ = pairing.next_round(
                [m.id for m in attendees],
                ratings,
                played,
                partnered,
                courts=3,
                mode=mode,
                seed=day.toordinal() + round_number,
            )
            for court in round_.courts:
                self._match(day, court.side_a, court.side_b, session=session)
                for side in (court.side_a, court.side_b):
                    played.update(side)
                    partnered[pairing.pair_key(*side)] += 1

    def _friendlies(self) -> None:
        for month_offset in range(0, 14, 2):
            day = date(2025, 9, 20) + timedelta(days=30 * month_offset)
            for _ in range(3):
                ours = self.rng.sample(self.team, 2)
                theirs = self.rng.sample(self.opponents, 2)
                self._match(
                    day, (ours[0].id, ours[1].id), (theirs[0].id, theirs[1].id), category=MatchCategoryEnum.FRIENDLY
                )

    def _events(self) -> None:
        for name, year, month in EVENTS:
            start = date(year, month, 12)
            event = Event(name=name, start_date=start, end_date=start + timedelta(days=1), location="台北")
            db.session.add(event)
            for _ in range(6):
                ours = self.rng.sample(self.team[:12], 2)
                theirs = self.rng.sample(self.opponents, 2)
                self._match(start, (ours[0].id, ours[1].id), (theirs[0].id, theirs[1].id), event=event)

    def _match(self, day, side_a, side_b, session=None, category=MatchCategoryEnum.INTERNAL, event=None) -> None:
        to_win = 4
        p_game = 1 / (1 + math.exp(-(self._strength(side_a) - self._strength(side_b)) / GAME_SCALE))
        a_games = b_games = 0
        while a_games < to_win and b_games < to_win:
            if self.rng.random() < p_game:
                a_games += 1
            else:
                b_games += 1
        match = Match(
            match_date=day,
            match_type=MatchTypeEnum.DOUBLES,
            match_format=MatchFormatEnum.GAMES_7,
            category=MatchCategoryEnum.EVENT if event else category,
            event=event,
            session=session,
        )
        record = MatchRecord(
            match=match,
            player1_id=side_a[0],
            player2_id=side_a[1],
            player3_id=side_b[0],
            player4_id=side_b[1],
            a_games=a_games,
            b_games=b_games,
            side_a_outcome=MatchOutcomeEnum.WIN if a_games > b_games else MatchOutcomeEnum.LOSS,
            a_front_id=self._front(side_a),
            b_front_id=self._front(side_b),
        )
        db.session.add_all([match, record])

    def _strength(self, side) -> float:
        a, b = side
        base = (self.skill[a] + self.skill[b]) / 2 + self.bonus.get(pairing.pair_key(a, b), 0.0)
        # 一個喜歡打前衛、一個喜歡打後衛的組合比較順
        if self.prefers_front[a] != self.prefers_front[b]:
            base += 0.25
        return base + self.rng.gauss(0, 0.35)

    def _front(self, side) -> int | None:
        """大約八成的比賽有記錄前衛：偏好打前衛的那位，兩個都一樣時隨機。"""
        if self.rng.random() > 0.8:
            return None
        a, b = side
        if self.prefers_front[a] != self.prefers_front[b]:
            return a if self.prefers_front[a] else b
        return self.rng.choice(side)
