# Suggested Commands for Development

## CRITICAL: Virtual Environment
**ALWAYS activate the virtual environment before running ANY Python command!**

```bash
source venv/bin/activate  # macOS/Linux (Darwin)
# OR
venv\Scripts\activate  # Windows
```

## Running the Application

### Start Callback Server
```bash
# With auto-publish (default)
python main.py server

# Without auto-publish
python main.py server --no-auto-publish
```

### Run Agent Workflow
```bash
# Single workflow run
python main.py run --once

# Dry run (no actual posting)
python main.py run --once --dry-run
```

### Manual Publishing
```bash
# Publish approved drafts (if auto-publish disabled)
python main.py publish --limit 3
```

### Check Engagement
```bash
# Fetch 24h metrics for published drafts
python main.py check-engagement --limit 50
```

### Health Check
```bash
python main.py health
```

## Testing

### Run All Tests
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_reddit_client.py -v
```

### Run Specific Test Function
```bash
pytest tests/test_reddit_client.py::test_function_name -v
```

## Database Migrations

### Apply Migrations
```bash
alembic upgrade head
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### View Migration History
```bash
alembic history
```

### Rollback Migration
```bash
alembic downgrade -1
```

## Code Quality

### Format Code (Black)
```bash
black . --line-length=100
```

### Sort Imports (isort)
```bash
isort . --profile=black --line-length=100
```

### Lint Code (Flake8)
```bash
flake8 . --max-line-length=100 --ignore=E501,W503,E203
```

### Type Check (mypy)
```bash
mypy . --ignore-missing-imports
```

### Run All Pre-commit Hooks
```bash
pre-commit run --all-files
```

### Install Pre-commit Hooks
```bash
pre-commit install
```

## Package Management

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Add New Dependency
```bash
pip install <package>
pip freeze > requirements.txt
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## Git Commands (Darwin-specific notes)

### Standard Git (same as Linux)
```bash
git status
git add .
git commit -m "message"
git push
```

### View Changes
```bash
git diff
git log --oneline
```

## System Utilities (Darwin)

### File Operations
```bash
ls -la          # List files with details
find . -name "*.py" -not -path "./venv/*"  # Find Python files
grep -r "pattern" --include="*.py" .       # Search in files
```

### Process Management
```bash
ps aux | grep python    # Find Python processes
kill -9 <PID>          # Force kill process
lsof -i :8000          # Check port usage
```

## Local Development with ngrok

### Start ngrok
```bash
ngrok http 8000
```

### Start Server with ngrok URL
```bash
PUBLIC_URL=https://xxxx.ngrok.io python main.py server
```

## Documentation

### Web App Docs (Local)
```bash
cd web-app/docs
npm install
npm run dev
# Access at http://localhost:3001
```

### Build Production Docs
```bash
cd web-app/docs
npm run build
```

## Environment Variables

### Copy Example .env
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Check Environment
```bash
cat .env | grep -v "^#" | grep .
```
