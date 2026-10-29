.PHONY: setup backend frontend test lint format format-backend format-frontend

BACKEND_PY = backend/.venv/bin/python

# 第一次使用：建立 Python 虛擬環境並安裝前後端套件
setup:
	cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
	cd frontend && npm install

# 啟動後端（http://localhost:8000，前端的 Vite proxy 會轉發 /api）
backend:
	cd backend && .venv/bin/flask --app run.py run --port 8000 --debug

# 啟動前端（http://localhost:5173）
frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/python -m pytest -q

# 格式化所有程式碼
format: format-backend format-frontend

format-backend:
	cd backend && .venv/bin/ruff check --config ../pyproject.toml . --fix && .venv/bin/ruff format --config ../pyproject.toml .

format-frontend:
	cd frontend && npm run format && npm run lint

# 檢查但不修改
lint:
	cd backend && .venv/bin/ruff check --config ../pyproject.toml .
	cd frontend && npm run format:check && npm run lint:check
