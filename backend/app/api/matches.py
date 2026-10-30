from flask import Blueprint

from ..core.auth import admin_required, staff_required
from ..core.requests import load_args, load_json
from ..core.responses import created, ok
from ..schemas.match import (
    MatchQuerySchema,
    MatchRecordBatchInputSchema,
    MatchRecordInputSchema,
    MatchRecordSchema,
)
from ..services import match_service

bp = Blueprint("matches", __name__, url_prefix="/match-records")

record_schema = MatchRecordSchema()


@bp.get("")
def list_records():
    page = match_service.list_records(load_args(MatchQuerySchema()))
    return ok(record_schema.dump(page.items, many=True), meta=page.meta)


@bp.get("/<int:record_id>")
def get_record(record_id: int):
    return ok(record_schema.dump(match_service.get_record(record_id)))


@bp.post("")
@staff_required
def create_record():
    record = match_service.create_record(load_json(MatchRecordInputSchema()))
    return created(record_schema.dump(record), message="比賽紀錄已建立。")


@bp.post("/batch")
@staff_required
def create_records():
    records = match_service.create_records(load_json(MatchRecordBatchInputSchema())["records"])
    return created(record_schema.dump(records, many=True), message=f"已建立 {len(records)} 場比賽紀錄。")


@bp.put("/<int:record_id>")
@staff_required
def update_record(record_id: int):
    record = match_service.update_record(record_id, load_json(MatchRecordInputSchema(), partial=True))
    return ok(record_schema.dump(record), message="比賽紀錄已更新。")


@bp.delete("/<int:record_id>")
@admin_required
def delete_record(record_id: int):
    match_service.delete_record(record_id)
    return ok(message="比賽紀錄已刪除。")
