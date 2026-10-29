# TKU Soft Tennis Stats

淡江軟網隊的比賽紀錄與 TrueSkill 排行榜。前端 Vue 3 + Naive UI，後端 Flask + SQLAlchemy，資料存在本地 SQLite。

## 本地執行

第一次使用：

```bash
make setup
```

`backend/.env` 至少需要：

```
SECRET_KEY=...
JWT_SECRET_KEY=...
DATABASE_URL=sqlite:///tkust.db   # 檔案位於 backend/instance/tkust.db
```

開兩個終端機分別啟動：

```bash
make backend    # http://localhost:8000
make frontend   # http://localhost:5173（/api 會轉發到後端）
```

## 資料庫

- 資料檔：`backend/instance/tkust.db`（已在 .gitignore，請自行備份這個檔案）
- 修改 models 後產生 migration：`cd backend && .venv/bin/flask --app run.py db migrate -m "..."`，再 `db upgrade`
- 從 PostgreSQL 備份（`pg_dump -Fc`）重新匯入：見 `backend/scripts/pg_to_sqlite.py` 開頭的說明

## 常用指令

```bash
make test                                                     # 後端測試
make lint                                                     # 檢查程式碼風格
cd backend && .venv/bin/flask --app run.py init-admin         # 建立管理員
cd backend && .venv/bin/flask --app run.py rating-stats       # 評分統計
cd backend && .venv/bin/flask --app run.py recalculate-all-ratings --dry-run
```

## API 格式

- 成功：`{"data": ..., "meta": {...}, "message": "..."}`
- 失敗：`{"error": {"code": "...", "message": "...", "details": {...}}}`
