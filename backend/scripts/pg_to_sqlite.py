"""把 PostgreSQL 資料庫完整複製到 SQLite 檔。

用法（以 Render 的 pg_dump 備份為例）：

    # 1. 暫時起一個 PostgreSQL 17 並還原備份
    docker run -d --rm --name tkust_restore -e POSTGRES_PASSWORD=restore -e POSTGRES_DB=tkust \\
        -p 127.0.0.1:55432:5432 postgres:17
    docker cp backup tkust_restore:/tmp/backup
    docker exec tkust_restore pg_restore -U postgres -d tkust --no-owner --no-privileges /tmp/backup

    # 2. 複製到 SQLite（需要 psycopg2-binary，見 requirements-dev.txt）
    .venv/bin/python scripts/pg_to_sqlite.py \\
        postgresql+psycopg2://postgres:restore@127.0.0.1:55432/tkust instance/tkust.db

    # 3. 移除暫時的 container
    docker stop tkust_restore
"""

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, select, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.extensions import db  # noqa: E402
from app.models import *  # noqa: E402,F403  註冊所有資料表到 metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source_url", help="PostgreSQL 連線字串")
    parser.add_argument("target_path", help="要建立的 SQLite 檔案路徑")
    parser.add_argument("--force", action="store_true", help="目標檔已存在時覆寫")
    args = parser.parse_args()

    target = Path(args.target_path).resolve()
    if target.exists():
        if not args.force:
            sys.exit(f"{target} 已存在，要覆寫請加 --force")
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)

    source = create_engine(args.source_url)
    sink = create_engine(f"sqlite:///{target}")
    metadata = db.metadata
    metadata.create_all(sink)

    with source.connect() as src, sink.begin() as dst:
        for table in metadata.sorted_tables:
            rows = [dict(row._mapping) for row in src.execute(select(table))]
            if rows:
                dst.execute(table.insert(), rows)
            copied = dst.scalar(select(func.count()).select_from(table))
            print(f"{table.name:<16} {copied:>5}")

        version = src.scalar(text("SELECT version_num FROM alembic_version"))
        dst.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
        dst.execute(text("INSERT INTO alembic_version (version_num) VALUES (:v)"), {"v": version})
        print(f"alembic_version  {version}")

    print(f"完成：{os.path.relpath(target)}")


if __name__ == "__main__":
    main()
