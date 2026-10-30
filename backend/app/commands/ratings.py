import click
from sqlalchemy import func, select

from ..extensions import db
from ..models import MatchRecord, Member
from ..services import rating_service


@click.command("recalculate-all-ratings")
@click.option("--dry-run", is_flag=True, help="只顯示變動，不寫入資料庫")
@click.option("--yes", is_flag=True, help="不詢問確認")
def recalculate_all_ratings(dry_run: bool, yes: bool):
    """依時間順序重新計算所有球員的分數。"""
    before = {m.id: m.rating for m in db.session.scalars(select(Member))}
    match_count = db.session.scalar(select(func.count(MatchRecord.id)))
    click.echo(f"球員 {len(before)} 位，比賽 {match_count} 場。")
    if not dry_run and not yes:
        click.confirm("確定要重新計算所有分數嗎？", abort=True)

    rating_service.recalculate_all()
    changed = [m for m in db.session.scalars(select(Member)) if _differs(before[m.id], m.rating)]
    for member in changed:
        click.echo(f"  {member.name}: {_format(before[member.id])} → {_format(member.rating)}")

    if dry_run:
        db.session.rollback()
        click.secho(f"試算完成：{len(changed)} 位球員的分數會改變（未寫入）。", fg="yellow")
    else:
        db.session.commit()
        click.secho(f"重新計算完成：{len(changed)} 位球員的分數有變動。", fg="green")


@click.command("rating-stats")
def rating_stats():
    """顯示分數統計與前五名。"""
    rated = [m for m in db.session.scalars(select(Member)) if m.rating is not None]
    if not rated:
        click.echo("還沒有球員打過比賽。")
        return
    scores = [m.rating for m in rated]
    click.echo(f"有分數的球員 {len(rated)} 位，平均 {sum(scores) / len(scores):.1f}，")
    click.echo(f"範圍 {min(scores):.1f} – {max(scores):.1f}")
    click.echo("前五名：")
    for rank, member in enumerate(sorted(rated, key=lambda m: m.rating, reverse=True)[:5], start=1):
        click.echo(f"  {rank}. {member.display_name}  {member.rating:.1f}")


def _format(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def _differs(a: float | None, b: float | None) -> bool:
    if a is None or b is None:
        return a is not b
    return abs(a - b) > 1e-9
