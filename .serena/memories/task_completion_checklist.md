# Task Completion Checklist

## When a Task is Completed

### 1. Run Tests
```bash
source venv/bin/activate
pytest -v
```

**What to check:**
- All tests pass
- No new test failures
- Coverage remains >80% (if applicable)

### 2. Run Code Quality Tools

#### Format Code
```bash
source venv/bin/activate
black . --line-length=100
isort . --profile=black --line-length=100
```

#### Lint Code
```bash
source venv/bin/activate
flake8 . --max-line-length=100 --ignore=E501,W503,E203
```

#### Run Pre-commit Hooks
```bash
source venv/bin/activate
pre-commit run --all-files
```

**What to check:**
- No formatting issues
- No linting errors
- All pre-commit hooks pass

### 3. Type Checking (Optional but Recommended)
```bash
source venv/bin/activate
mypy . --ignore-missing-imports
```

**What to check:**
- No type errors
- All type hints valid

### 4. Database Migrations (If Schema Changed)
```bash
source venv/bin/activate

# Create migration
alembic revision --autogenerate -m "description of schema change"

# Review migration file in migrations/versions/

# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

**What to check:**
- Migration file created correctly
- Migration applies without errors
- Rollback works correctly

### 5. Manual Testing (If Applicable)

#### For Workflow Changes
```bash
source venv/bin/activate

# Terminal 1: Start server
python main.py server

# Terminal 2: Run workflow in dry-run mode
python main.py run --once --dry-run
```

**What to check:**
- No crashes or exceptions
- Expected behavior observed
- Logs show correct flow

#### For Reddit Client Changes
```bash
source venv/bin/activate

# Test with actual Reddit API (use test subreddit)
python main.py run --once --dry-run
```

**What to check:**
- API calls succeed
- No rate limit issues
- Shadowban detection working

### 6. Update Documentation

#### Update CLAUDE.md (If Major Change)
- Update status table
- Add to "Complete" section
- Update version if applicable

#### Update README.md (If User-Facing)
- Update features list
- Update commands if new CLI added
- Update configuration if new settings

#### Update progress.md
```markdown
## [Date] - [Feature/Fix Name]
- Brief description of what was done
- Key changes or decisions
```

#### Update decisions.md (If Architectural Decision)
```markdown
## [Date] - [Decision Title]
**Context:** Why this decision was needed
**Decision:** What was decided
**Rationale:** Why this approach was chosen
**Consequences:** Impact of this decision
```

#### Update bug.md (If Bug Fixed)
```markdown
## [Date] - [Bug Title]
**Issue:** Description of the bug
**Root Cause:** What caused the bug
**Fix:** How it was fixed
**Status:** FIXED
```

### 7. Check Safety Constraints (Critical for Reddit Agent)

**Verify:**
- [ ] max_comments_per_day ≤ 8 (hardcoded)
- [ ] max_comments_per_run ≤ 3 (hardcoded)
- [ ] HITL approval required for all drafts
- [ ] Shadowban detection active
- [ ] Token hashing in place
- [ ] PII scrubbing functional
- [ ] Anti-fingerprint timing preserved

### 8. Git Commit

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: description of feature"
# or
git commit -m "fix: description of bug fix"

# Push to remote
git push
```

**Commit message format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for test changes
- `refactor:` for code refactoring
- `chore:` for maintenance

### 9. Update Context Remaining (As per CLAUDE.md User Instructions)

**Check:**
- Review token usage
- Warn if context running low
- Ask user to compact if needed before next task

### 10. Final Checklist

- [ ] All tests pass
- [ ] Code formatted (black, isort)
- [ ] Code linted (flake8)
- [ ] Pre-commit hooks pass
- [ ] Database migrations applied (if applicable)
- [ ] Manual testing completed (if applicable)
- [ ] Documentation updated
- [ ] Safety constraints verified
- [ ] Git commit pushed
- [ ] progress.md updated
- [ ] decisions.md updated (if architectural change)
- [ ] bug.md updated (if bug fix)
- [ ] Context remaining checked

## Special Cases

### If Adding New Dependency
```bash
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt
```

### If Adding New Environment Variable
1. Add to `config.py` Settings class
2. Add to `.env.example` with description
3. Update README.md configuration section
4. Update CLAUDE.md configuration section

### If Changing API
1. Update all calling code
2. Update tests
3. Update documentation
4. Consider backward compatibility

### If Security-Related Change
1. Extra careful review
2. Test token handling
3. Verify no secrets logged
4. Check PII scrubbing
5. Document security implications
