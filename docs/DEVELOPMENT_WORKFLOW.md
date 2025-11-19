# Development Workflow

**Project:** Ocean-ML
**Last Updated:** 2025-11-19

---

## Daily Development Cycle

### Starting Your Day

```bash
# 1. Pull latest changes
cd Ocean-ML
git pull origin main

# 2. Check for updates to dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 3. Review your tasks
cat docs/IMPLEMENTATION_PLAN.md | grep "⏳ Pending\|🔄 In Progress"

# 4. Start local services
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# 5. Check everything is running
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## Working on a Checkpoint

### Step-by-Step Process

#### 1. Create Feature Branch

```bash
git checkout -b checkpoint-X.Y-feature-name
```

**Branch Naming Convention:**
- `checkpoint-X.Y-name` for checkpoint work
- `fix/description` for bug fixes
- `docs/description` for documentation updates

#### 2. Review Checkpoint Requirements

Open `docs/IMPLEMENTATION_PLAN.md` and find your checkpoint.

Read:
- Objectives
- Implementation details
- Testing requirements
- Success criteria

#### 3. Create Checkpoint Documentation File

```bash
# Create checkpoint doc
touch docs/checkpoints/X.Y-feature-name.md
```

Use this template:

```markdown
# Checkpoint X.Y: Feature Name

**Date Started:** YYYY-MM-DD
**Status:** 🔄 In Progress
**Estimated Time:** X hours

## Objective
[Copy from implementation plan]

## Progress Log

### YYYY-MM-DD HH:MM
- Started implementation
- [What you did]

### YYYY-MM-DD HH:MM
- [Progress update]
- [Challenges encountered]

## Implementation Notes
[Key decisions, trade-offs, alternatives considered]

## Code Changes
- `path/to/file.py` - Added feature X
- `path/to/test.py` - Added tests for X

## Testing
- [ ] Unit tests written
- [ ] Unit tests pass
- [ ] Integration tests written (if applicable)
- [ ] Integration tests pass
- [ ] Manual testing completed

## Issues Encountered
### Issue 1: [Description]
**Solution:** [How resolved]

### Issue 2: [Description]
**Status:** Still investigating
**Next steps:** [What to try next]

## Learnings
- [Key insight #1]
- [Key insight #2]

## Next Steps
- [ ] Complete remaining tests
- [ ] Update documentation
- [ ] Commit changes

## Time Spent
- Coding: X hours
- Testing: Y hours
- Debugging: Z hours
- **Total:** W hours
```

#### 4. Write Tests First (TDD Approach)

```bash
# Backend example
touch backend/tests/test_new_feature.py
```

Write failing tests:

```python
# backend/tests/test_new_feature.py
def test_new_feature():
    result = my_new_function()
    assert result == expected_value
```

Run tests (should fail):
```bash
cd backend
pytest tests/test_new_feature.py
```

#### 5. Implement Feature

Write minimal code to make tests pass:

```python
# backend/services/new_feature.py
def my_new_function():
    return expected_value
```

Run tests again (should pass):
```bash
pytest tests/test_new_feature.py
```

#### 6. Refactor & Add More Tests

- Improve code quality
- Add edge case tests
- Add integration tests
- Add documentation strings

#### 7. Manual Testing

Follow the testing procedure in `docs/IMPLEMENTATION_PLAN.md` for your checkpoint.

Document results in checkpoint file:

```markdown
## Manual Testing Results

### Test 1: Basic functionality
- **Result:** ✅ Pass
- **Notes:** Works as expected

### Test 2: Error handling
- **Result:** ⚠️  Pass with issues
- **Notes:** Error message could be clearer
- **Action:** Added TODO to improve
```

#### 8. Update Progress

Update checkpoint status table in `docs/IMPLEMENTATION_PLAN.md`:

```markdown
| 1.2 | Video Endpoints | ✅ Passed | 2025-11-19 | 3h | See checkpoint doc |
```

#### 9. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Complete checkpoint 1.2 - Video endpoints

- Implemented GET /api/videos (list all)
- Implemented GET /api/videos/{id} (get one)
- Added validation and error handling
- Tests: 12 unit tests, all passing
- Manual testing: Completed successfully

Closes #checkpoint-1.2"
```

**Commit Message Format:**
```
<type>: <short summary>

<detailed description>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `test:` Adding tests
- `docs:` Documentation only
- `refactor:` Code refactoring
- `style:` Formatting changes
- `chore:` Maintenance tasks

#### 10. Push to GitHub

```bash
git push origin checkpoint-X.Y-feature-name
```

#### 11. Create Pull Request (Optional)

If working in a team:

```bash
gh pr create --title "Checkpoint X.Y: Feature Name" --body "$(cat docs/checkpoints/X.Y-feature-name.md)"
```

#### 12. Merge to Main

```bash
git checkout main
git merge checkpoint-X.Y-feature-name
git push origin main

# Delete feature branch
git branch -d checkpoint-X.Y-feature-name
```

---

## Code Review Checklist

Before committing, review your code:

### Functionality
- [ ] Code does what it's supposed to do
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] No hard-coded values (use environment variables)

### Tests
- [ ] All tests pass
- [ ] New code has tests
- [ ] Tests cover edge cases
- [ ] Tests are readable and maintainable

### Code Quality
- [ ] Code follows project conventions
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Functions have docstrings
- [ ] Variables have meaningful names

### Documentation
- [ ] README updated if needed
- [ ] Checkpoint documentation complete
- [ ] API documentation updated (if backend changes)
- [ ] Comments added for complex logic

### Security
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] SQL injection prevention (use parameterized queries)
- [ ] XSS prevention (escape user input)

---

## Running Tests Before Commit

### Backend

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf
```

Must pass: **All tests ✅**, Coverage > **80%**

### Frontend

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode (during development)
npm test -- --watch
```

Must pass: **All tests ✅**, Coverage > **70%**

### Desktop

```bash
cd desktop

# Run all tests
pytest

# Run specific test file
pytest tests/test_protocol_handler.py
```

Must pass: **All tests ✅**, Coverage > **60%**

---

## Git Workflow

### Branching Strategy

```
main (production-ready)
  ├─ checkpoint-0.1-supabase-setup
  ├─ checkpoint-0.2-modal-setup
  ├─ checkpoint-1.1-fastapi-basic
  ├─ checkpoint-1.2-video-endpoints
  └─ ...
```

### Commit Frequently

Commit after each logical unit of work:

```bash
# Good: Small, focused commits
git commit -m "feat: Add GET /api/videos endpoint"
git commit -m "test: Add tests for video listing"
git commit -m "docs: Update API documentation"

# Bad: Large, unfocused commit
git commit -m "WIP: Lots of changes"
```

### Git Commands Reference

```bash
# Check status
git status

# View changes
git diff

# Stage specific files
git add file1.py file2.py

# Stage all changes
git add .

# Unstage file
git restore --staged file.py

# Discard changes (careful!)
git restore file.py

# View commit history
git log --oneline

# Create tag for checkpoint
git tag v0.1-checkpoint-1.2
git push origin v0.1-checkpoint-1.2

# View branches
git branch

# Switch branch
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name

# Delete branch
git branch -d branch-name

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes - careful!)
git reset --hard HEAD~1
```

---

## Debugging Workflow

### Backend Debugging

```python
# Use pdb for debugging
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()

# Run with debugger
python -m pdb main.py
```

**VS Code Debug Configuration:**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env"
    }
  ]
}
```

### Frontend Debugging

```typescript
// Use browser DevTools
console.log('Debug:', variable)
console.table(arrayOfObjects)
console.error('Error:', error)

// React DevTools (browser extension)
// View component hierarchy and props

// Network tab
// Monitor API requests and responses
```

### Desktop Debugging

```python
# PyQt5 debugging
from PyQt5.QtCore import QLoggingCategory

# Enable Qt logging
QLoggingCategory.setFilterRules("*.debug=true")

# Or use print statements
print(f"DEBUG: {variable}")

# Use PyCharm/VS Code debugger for GUI apps
```

---

## Troubleshooting Common Issues

### Backend Won't Start

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

**Issue:** `Supabase connection error`

**Solution:**
```bash
# Check .env file
cat backend/.env

# Verify credentials
curl https://YOUR_PROJECT.supabase.co/rest/v1/ \
  -H "apikey: YOUR_KEY"
```

---

### Frontend Won't Start

**Issue:** `Module not found: Can't resolve '@supabase/supabase-js'`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

**Issue:** `CORS error when calling backend`

**Solution:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Desktop App Issues

**Issue:** `Protocol handler not working`

**Solution:**
```bash
# Re-register protocol handler
cd desktop
python register_protocol.py
```

---

**Issue:** `Video download fails`

**Solution:**
```python
# Check Supabase Storage permissions
# Verify file exists in Storage
# Check network connection
# Try downloading manually via Supabase URL
```

---

### Modal Issues

**Issue:** `Modal deployment fails`

**Solution:**
```bash
# Re-authenticate
modal token set

# Check Modal app logs
modal app logs ocean-ml-training
```

---

**Issue:** `Training costs more than expected`

**Solution:**
```python
# Use cheaper GPU
@app.function(gpu="T4")  # Instead of A100

# Reduce epochs
epochs = 10  # For testing

# Use smaller dataset
# Only include subset of videos
```

---

## Performance Optimization

### Backend Optimization

```python
# Use async/await for I/O operations
async def get_videos():
    async with httpx.AsyncClient() as client:
        response = await client.get(SUPABASE_URL)
    return response.json()

# Cache expensive queries
from functools import lru_cache

@lru_cache(maxsize=100)
def get_video_metadata(video_id):
    # ... expensive operation
    pass

# Use database indexes
# Add to Supabase SQL editor:
CREATE INDEX idx_videos_annotated ON videos(annotated);
```

### Frontend Optimization

```typescript
// Use React.memo for expensive components
const VideoCard = React.memo(({ video }) => {
  return <div>...</div>
})

// Use useCallback for functions passed as props
const handleClick = useCallback(() => {
  doSomething()
}, [dependencies])

// Lazy load components
const TrainingDashboard = lazy(() => import('./TrainingDashboard'))

// Optimize images
// Use WebP format, lazy loading
<img src="thumbnail.webp" loading="lazy" />
```

---

## Documentation Standards

### Code Comments

```python
# Good: Explain WHY, not WHAT
# Use binary search because dataset is sorted
result = binary_search(data, target)

# Bad: Explain WHAT (obvious from code)
# Call binary_search function
result = binary_search(data, target)
```

### Docstrings

```python
def train_yolo(dataset_id: str, epochs: int) -> dict:
    """
    Train YOLO model on specified dataset.

    Args:
        dataset_id: Unique identifier for the dataset
        epochs: Number of training epochs (10-300)

    Returns:
        Dictionary containing training metrics:
            - map50: Mean Average Precision at IoU=0.5
            - loss: Final training loss
            - duration: Training time in seconds

    Raises:
        ValueError: If epochs < 10 or > 300
        ConnectionError: If cannot connect to Supabase

    Example:
        >>> results = train_yolo("ocean_fish_v1", epochs=100)
        >>> print(results['map50'])
        0.89
    """
    pass
```

### API Documentation

Update `docs/api-docs.md` when adding endpoints:

```markdown
## POST /api/videos

Upload a new video file.

**Request:**
```
POST /api/videos
Content-Type: multipart/form-data

file: <video file>
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "video.mp4",
  "status": "uploaded"
}
```

**Errors:**
- `400` - Invalid file type
- `413` - File too large
- `500` - Upload failed
```

---

## Collaboration Best Practices

### Communication

- **Daily Updates:** Post progress in team chat
- **Blockers:** Report immediately, don't wait
- **Questions:** Ask in team channel, don't struggle alone
- **Wins:** Share successes and learnings

### Code Reviews

When reviewing others' code:

- [ ] Run the code locally
- [ ] Run tests
- [ ] Check for security issues
- [ ] Suggest improvements kindly
- [ ] Approve if meets standards

When your code is reviewed:

- [ ] Respond to all comments
- [ ] Make requested changes
- [ ] Thank reviewers
- [ ] Learn from feedback

### Pair Programming

For complex checkpoints:

1. **Driver:** Writes the code
2. **Navigator:** Reviews, suggests, catches mistakes
3. Switch roles every 30 minutes

---

## Weekly Checklist

### Every Monday
- [ ] Review last week's progress
- [ ] Plan this week's checkpoints
- [ ] Update implementation plan
- [ ] Check GitHub issues

### Every Friday
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Review cost tracking (Modal, Supabase)
- [ ] Backup database
- [ ] Tag weekly release

---

## Monthly Tasks

- [ ] Review test coverage
- [ ] Update dependencies
- [ ] Clean up old branches
- [ ] Review and close completed issues
- [ ] Update cost projections
- [ ] Performance audit

---

## Emergency Procedures

### Critical Bug in Production

1. **Immediately:** Roll back to last known good version
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Create hotfix branch:**
   ```bash
   git checkout -b hotfix/critical-bug
   ```

3. **Fix, test, deploy:**
   ```bash
   # Fix bug
   # Test thoroughly
   git commit -m "fix: Critical bug in X"
   git checkout main
   git merge hotfix/critical-bug
   git push origin main
   ```

4. **Document:** Create incident report in `docs/incidents/`

### Data Loss

1. **Stop all operations immediately**
2. **Restore from last backup:**
   ```bash
   # Supabase: Use Point-in-Time Recovery
   # Local: Restore from backup
   ```
3. **Document what happened**
4. **Improve backup strategy**

### Exceeded Cost Budget

1. **Check Modal dashboard** for unexpected jobs
2. **Cancel running jobs:**
   ```bash
   modal app stop ocean-ml-training
   ```
3. **Review what went wrong**
4. **Update cost limits**

---

## Useful Scripts

### Quick Start Script

```bash
# scripts/dev.sh
#!/bin/bash

echo "🚀 Starting Ocean-ML development environment..."

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

### Test All Script

```bash
# scripts/test-all.sh
#!/bin/bash

echo "🧪 Running all tests..."

# Backend
echo "Testing backend..."
cd backend
pytest || exit 1

# Frontend
echo "Testing frontend..."
cd ../frontend
npm test || exit 1

# Desktop
echo "Testing desktop..."
cd ../desktop
pytest || exit 1

echo "✅ All tests passed!"
```

---

## Resources

### Documentation
- **Project Spec:** `docs/SPEC.md`
- **Implementation Plan:** `docs/IMPLEMENTATION_PLAN.md`
- **Testing Strategy:** `docs/TESTING_STRATEGY.md`
- **Getting Started:** `docs/GETTING_STARTED.md`

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Supabase Docs](https://supabase.com/docs)
- [Modal Docs](https://modal.com/docs)
- [YOLO Docs](https://docs.ultralytics.com/)

### Community
- **GitHub Repo:** https://github.com/christian-pebl/Ocean-ML
- **Issues:** https://github.com/christian-pebl/Ocean-ML/issues
- **Discussions:** https://github.com/christian-pebl/Ocean-ML/discussions

---

**Happy coding! 🌊**
