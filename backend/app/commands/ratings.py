import click
from sqlalchemy import func, select

from ..domain import rating as rating_domain
from ..extensions import db
from ..models import MatchRecord, Member
from ..services import rating_service


@click.command("recalculate-all-ratings")
@click.option("--dry-run", is_flag=True, help="只顯示變動，不寫入資料庫")
@click.option("--yes", is_flag=True, help="不詢問確認")
def recalculate_all_ratings(dry_run: bool, yes: bool):
    """依時間順序重新計算所有球員的評分。"""
    before = {m.id: (m.mu, m.sigma) for m in db.session.scalars(select(Member))}
    match_count = db.session.scalar(select(func.count(MatchRecord.id)))
    click.echo(f"球員 {len(before)} 位，比賽 {match_count} 場。")
    if not dry_run and not yes:
        click.confirm("確定要重新計算所有評分嗎？", abort=True)

    rating_service.recalculate_all()
    changed = [m for m in db.session.scalars(select(Member)) if _differs(before[m.id], (m.mu, m.sigma))]
    for member in changed:
        old_mu, old_sigma = before[member.id]
        click.echo(f"  {member.name}: μ {old_mu:.3f} → {member.mu:.3f}, σ {old_sigma:.3f} → {member.sigma:.3f}")

    if dry_run:
        db.session.rollback()
        click.secho(f"試算完成：{len(changed)} 位球員的評分會改變（未寫入）。", fg="yellow")
    else:
        db.session.commit()
        click.secho(f"重新計算完成：{len(changed)} 位球員的評分有變動。", fg="green")


@click.command("reset-all-ratings")
@click.option("--yes", is_flag=True, help="不詢問確認")
def reset_all_ratings(yes: bool):
    """把所有球員的評分重設為初始值（不重算比賽）。"""
    if not yes:
        click.confirm("確定要把所有球員的評分重設為初始值嗎？", abort=True)
    count = db.session.query(Member).update(
        {Member.mu: rating_domain.DEFAULT_MU, Member.sigma: rating_domain.DEFAULT_SIGMA}
    )
    db.session.commit()
    click.secho(f"已重設 {count} 位球員的評分。", fg="green")


@click.command("rating-stats")
def rating_stats():
    """顯示評分統計與前五名。"""
    members = db.session.scalars(select(Member)).all()
    if not members:
        click.echo("沒有球員資料。")
        return
    ranked = sorted(members, key=lambda m: rating_domain.conservative_score(m.rating), reverse=True)
    mus = [m.mu for m in members]
    sigmas = [m.sigma for m in members]
    click.echo(f"球員 {len(members)} 位")
    click.echo(f"μ：平均 {sum(mus) / len(mus):.2f}，範圍 {min(mus):.2f} – {max(mus):.2f}")
    click.echo(f"σ：平均 {sum(sigmas) / len(sigmas):.2f}，範圍 {min(sigmas):.2f} – {max(sigmas):.2f}")

    levels: dict[str, int] = {}
    for member in members:
        level = rating_domain.experience_level(member.rating)
        levels[level] = levels.get(level, 0) + 1
    click.echo("經驗等級：" + "、".join(f"{level} {count}" for level, count in levels.items()))

    click.echo("前五名：")
    for rank, member in enumerate(ranked[:5], start=1):
        score = rating_domain.conservative_score(member.rating)
        click.echo(f"  {rank}. {member.display_name}  {score:.2f}（μ={member.mu:.2f}, σ={member.sigma:.2f}）")


def _differs(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return abs(a[0] - b[0]) > 1e-9 or abs(a[1] - b[1]) > 1e-9
