# Testing Strategy

**Project:** Ocean-ML
**Version:** 1.0
**Last Updated:** 2025-11-19

---

## Overview

This document outlines the comprehensive testing strategy for Ocean-ML, ensuring reliability, safety, and quality throughout development.

---

## Testing Pyramid

```
           /\
          /  \
         /  E2E \ ←─── End-to-End Tests (10%)
        /────────\
       /          \
      / Integration\ ←─── Integration Tests (30%)
     /──────────────\
    /                \
   /   Unit Tests     \ ←─── Unit Tests (60%)
  /____________________\
```

### Unit Tests (60%)
- Test individual functions and methods
- Fast execution (<1s per test)
- No external dependencies
- Run on every code change

### Integration Tests (30%)
- Test component interactions
- Backend ↔ Supabase
- Frontend ↔ Backend API
- Desktop ↔ Supabase
- Run before commits

### End-to-End Tests (10%)
- Test complete user workflows
- Browser → Desktop → Cloud
- Run before releases
- Include manual testing

---

## Test Coverage Goals

| Component | Target Coverage | Rationale |
|-----------|----------------|-----------|
| Backend API | 80%+ | Critical business logic |
| Frontend Components | 70%+ | UI can be tested manually |
| Desktop App | 60%+ | PyQt5 testing is complex |
| Modal Functions | 90%+ | Expensive to debug in cloud |

---

## Backend Testing

### Setup

```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app
from supabase import create_client

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def supabase_test():
    """Supabase test client (uses test project)"""
    return create_client(
        os.getenv("SUPABASE_TEST_URL"),
        os.getenv("SUPABASE_TEST_KEY")
    )

@pytest.fixture(autouse=True)
def cleanup_database(supabase_test):
    """Clean up test data after each test"""
    yield
    # Delete test records
    supabase_test.table('videos').delete().neq('id', '').execute()
    supabase_test.table('annotations').delete().neq('id', '').execute()
```

### Test Structure

```
backend/tests/
├── conftest.py                # Shared fixtures
├── test_api_health.py        # Health checks
├── test_videos.py            # Video endpoints
├── test_annotations.py       # Annotation endpoints
├── test_training.py          # Training endpoints
├── test_auth.py              # Authentication
└── test_video_lock.py        # Locking mechanism
```

### Sample Tests

```python
# backend/tests/test_videos.py
def test_list_videos_empty(client):
    """Test listing videos when none exist"""
    response = client.get("/api/videos")
    assert response.status_code == 200
    assert response.json() == []

def test_upload_video(client, test_video_file):
    """Test video upload"""
    with open(test_video_file, "rb") as f:
        response = client.post(
            "/api/videos",
            files={"file": ("test.mp4", f, "video/mp4")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.mp4"

def test_upload_invalid_file_type(client):
    """Test rejection of non-video files"""
    with open("test.jpg", "rb") as f:
        response = client.post(
            "/api/videos",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 400
    assert "must be a video" in response.json()["detail"].lower()

def test_get_video_not_found(client):
    """Test 404 for non-existent video"""
    response = client.get("/api/videos/nonexistent-id")
    assert response.status_code == 404
```

### Running Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_videos.py

# Run specific test
pytest tests/test_videos.py::test_upload_video

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

---

## Frontend Testing

### Setup

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts'
  }
})
```

### Test Structure

```
frontend/src/
├── components/
│   ├── VideoLibrary/
│   │   ├── VideoGrid.tsx
│   │   └── VideoGrid.test.tsx      # Component tests
│   └── Auth/
│       ├── LoginPage.tsx
│       └── LoginPage.test.tsx
├── hooks/
│   ├── useRealtimeVideos.ts
│   └── useRealtimeVideos.test.ts   # Hook tests
└── test/
    ├── setup.ts                     # Test configuration
    └── mocks/                       # Mock data
        ├── videos.ts
        └── supabase.ts
```

### Sample Tests

```typescript
// frontend/src/components/VideoLibrary/VideoGrid.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { VideoGrid } from './VideoGrid'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

describe('VideoGrid', () => {
  it('renders loading state initially', () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <VideoGrid />
      </QueryClientProvider>
    )

    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('renders video cards when data loads', async () => {
    // Mock API response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve([
          { id: '1', filename: 'video1.mp4', annotated: false },
          { id: '2', filename: 'video2.mp4', annotated: true }
        ])
      })
    )

    render(
      <QueryClientProvider client={new QueryClient()}>
        <VideoGrid />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('video1.mp4')).toBeInTheDocument()
      expect(screen.getByText('video2.mp4')).toBeInTheDocument()
    })
  })

  it('renders error state on fetch failure', async () => {
    global.fetch = vi.fn(() => Promise.reject('API error'))

    render(
      <QueryClientProvider client={new QueryClient()}>
        <VideoGrid />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/error loading videos/i)).toBeInTheDocument()
    })
  })
})
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test VideoGrid.test.tsx
```

---

## Desktop App Testing

### Setup

```python
# desktop/tests/conftest.py
import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests"""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def mock_video_file(tmp_path):
    """Create temporary video file for testing"""
    video_file = tmp_path / "test_video.mp4"
    # Create minimal valid MP4 file
    video_file.write_bytes(b"mock video data")
    return str(video_file)
```

### Test Structure

```
desktop/tests/
├── conftest.py
├── test_protocol_handler.py
├── test_video_downloader.py
├── test_annotation_sync.py
└── test_ui/
    ├── test_video_player.py
    └── test_annotation_canvas.py
```

### Sample Tests

```python
# desktop/tests/test_protocol_handler.py
from services.protocol_handler import ProtocolHandler

def test_parse_valid_url():
    handler = ProtocolHandler()
    result = handler.parse_url("oceanml://annotate?video=123&token=abc")

    assert result["action"] == "annotate"
    assert result["video_id"] == "123"
    assert result["token"] == "abc"

def test_parse_missing_video_id():
    handler = ProtocolHandler()
    result = handler.parse_url("oceanml://annotate?token=abc")

    assert result["video_id"] is None
    assert result["token"] == "abc"

def test_parse_invalid_protocol():
    handler = ProtocolHandler()

    with pytest.raises(ValueError, match="Invalid protocol"):
        handler.parse_url("http://example.com")

# desktop/tests/test_video_downloader.py
def test_download_video_success(mock_video_file, tmp_path):
    """Test successful video download"""
    downloader = VideoDownloader(
        video_url="http://example.com/video.mp4",
        local_path=str(tmp_path / "downloaded.mp4")
    )

    # Mock requests
    with patch('requests.get') as mock_get:
        mock_get.return_value.headers = {'content-length': '1000'}
        mock_get.return_value.iter_content.return_value = [b'x' * 100] * 10

        downloader.run()

    assert (tmp_path / "downloaded.mp4").exists()

def test_download_progress_updates(qtbot):
    """Test that progress signal emits correctly"""
    downloader = VideoDownloader(
        video_url="http://example.com/video.mp4",
        local_path="/tmp/video.mp4"
    )

    with qtbot.waitSignal(downloader.progress, timeout=5000) as blocker:
        downloader.run()

    assert blocker.args[0] >= 0  # Progress percentage
```

### Running Desktop Tests

```bash
cd desktop

# Run all tests
pytest

# Run with GUI (for Qt tests)
pytest --no-xvfb

# Run specific test
pytest tests/test_protocol_handler.py

# Generate coverage
pytest --cov=. --cov-report=html
```

---

## Modal Function Testing

### Setup

```python
# modal_functions/tests/conftest.py
import modal
import pytest

@pytest.fixture
def modal_app():
    """Modal app for testing"""
    return modal.App("ocean-ml-test")

@pytest.fixture
def mock_annotations():
    """Mock annotation data"""
    return {
        "video_1": "0 0.5 0.5 0.1 0.1\n1 0.3 0.3 0.2 0.2",
        "video_2": "0 0.2 0.2 0.15 0.15"
    }
```

### Test Structure

```
modal_functions/
├── training.py
├── inference.py
└── tests/
    ├── conftest.py
    ├── test_training.py
    ├── test_inference.py
    └── test_data_preparation.py
```

### Sample Tests

```python
# modal_functions/tests/test_training.py
def test_prepare_dataset(mock_annotations, tmp_path):
    """Test YOLO dataset preparation"""
    prepare_yolo_dataset(mock_annotations, str(tmp_path))

    # Check directory structure
    assert (tmp_path / "images" / "train").exists()
    assert (tmp_path / "labels" / "train").exists()

    # Check dataset.yaml
    assert (tmp_path / "dataset.yaml").exists()

def test_training_minimal_dataset(modal_app):
    """Test training on minimal dataset (fast)"""
    # Deploy test function
    with modal_app.run():
        result = train_yolo_test.remote("test_dataset")

    assert result["status"] == "success"
    assert "map50" in result

@pytest.mark.expensive  # Mark as expensive test
def test_training_full_dataset(modal_app):
    """Test training on full dataset (slow, expensive)"""
    # Only run this manually or on CI
    with modal_app.run():
        result = train_yolo_production.remote(
            dataset_id="full_dataset",
            model_type="yolov8n",
            epochs=10
        )

    assert result["status"] == "success"
    assert result["map50"] > 0.5  # Expect reasonable accuracy
```

### Running Modal Tests

```bash
cd modal_functions

# Run fast tests only
pytest -m "not expensive"

# Run all tests (including expensive GPU tests)
pytest

# Run specific test
pytest tests/test_training.py::test_prepare_dataset
```

---

## Integration Testing

### Backend ↔ Supabase

```python
# tests/integration/test_backend_supabase.py
def test_video_upload_and_retrieval(client, supabase_test):
    """Test full video upload flow"""

    # Upload video via API
    with open("test_fixtures/sample.mp4", "rb") as f:
        response = client.post(
            "/api/videos",
            files={"file": ("sample.mp4", f, "video/mp4")}
        )

    video_id = response.json()["id"]

    # Verify in Supabase
    video_record = supabase_test.table('videos').select('*').eq('id', video_id).execute()
    assert len(video_record.data) == 1

    # Verify in Storage
    files = supabase_test.storage.from_('videos').list()
    assert any(f['name'] == f"{video_id}.mp4" for f in files)

    # Retrieve via API
    response = client.get(f"/api/videos/{video_id}")
    assert response.status_code == 200
    assert response.json()["filename"] == "sample.mp4"
```

### Frontend ↔ Backend

```typescript
// tests/integration/api.test.ts
describe('API Integration', () => {
  beforeAll(async () => {
    // Start test backend
    await startTestBackend()
  })

  it('fetches videos from backend', async () => {
    const response = await fetch('http://localhost:8000/api/videos')
    const videos = await response.json()

    expect(Array.isArray(videos)).toBe(true)
  })

  it('uploads video and retrieves it', async () => {
    const formData = new FormData()
    formData.append('file', new File(['test'], 'test.mp4', { type: 'video/mp4' }))

    const uploadResponse = await fetch('http://localhost:8000/api/videos', {
      method: 'POST',
      body: formData
    })

    const { id } = await uploadResponse.json()

    const getResponse = await fetch(`http://localhost:8000/api/videos/${id}`)
    const video = await getResponse.json()

    expect(video.filename).toBe('test.mp4')
  })
})
```

---

## End-to-End Testing

### Manual Test Scripts

Create checklist-based test scripts for complete workflows:

```markdown
# Test Script: Complete Annotation Workflow

**Tester:** ___________
**Date:** ___________
**Environment:** Development / Staging / Production

## Prerequisites
- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] Desktop app installed
- [ ] Test user account created

## Steps

### 1. Login
- [ ] Open http://localhost:3000
- [ ] Click "Sign in with Google"
- [ ] Successfully authenticated
- [ ] Redirected to dashboard

### 2. View Video Library
- [ ] Dashboard loads without errors
- [ ] Video grid displays correctly
- [ ] Can see video thumbnails
- [ ] Annotation status is visible

### 3. Start Annotation
- [ ] Click "Annotate" on a video
- [ ] Desktop app launches automatically (no manual intervention)
- [ ] Video download progress appears
- [ ] Download completes successfully
- [ ] Video loads in annotation interface

### 4. Annotate Video
- [ ] Can scrub through video frames smoothly
- [ ] Can draw bounding box
- [ ] Can select species from dropdown
- [ ] Can edit existing box
- [ ] Can delete box
- [ ] Can navigate with keyboard (←/→)

### 5. Save Annotations
- [ ] Click "Save" button
- [ ] Upload progress shown
- [ ] Success message appears
- [ ] Desktop app closes

### 6. Verify Dashboard Update
- [ ] Return to browser dashboard
- [ ] Video now shows "✓ Annotated"
- [ ] Annotation count is correct
- [ ] Timestamp is recent

### 7. Real-time Update Test
- [ ] Open dashboard in second browser tab
- [ ] In first tab, annotate another video
- [ ] Second tab updates automatically (no refresh needed)

## Results

**Total Steps:** 30
**Passed:** ___
**Failed:** ___
**Success Rate:** ___%

## Issues Found

| Step | Issue | Severity | Notes |
|------|-------|----------|-------|
|      |       |          |       |

## Sign-off

- [ ] All critical paths work
- [ ] Ready for next phase

**Tester Signature:** ___________
**Date:** ___________
```

### Automated E2E Tests (Playwright)

```typescript
// tests/e2e/annotation-workflow.spec.ts
import { test, expect } from '@playwright/test'

test('complete annotation workflow', async ({ page, context }) => {
  // Login
  await page.goto('http://localhost:3000')
  await page.click('text=Sign in with Google')
  await page.fill('input[type="email"]', 'test@example.com')
  await page.fill('input[type="password"]', 'password')
  await page.click('button:has-text("Sign in")')

  // Wait for dashboard
  await expect(page.locator('h1:has-text("Videos")')).toBeVisible()

  // Click annotate
  await page.click('button:has-text("Annotate")')

  // Note: Desktop app launch cannot be tested in Playwright
  // This would need to be a manual test

  // Verify video locked in another tab
  const secondTab = await context.newPage()
  await secondTab.goto('http://localhost:3000')

  const lockedVideo = secondTab.locator('text=Currently being annotated')
  await expect(lockedVideo).toBeVisible()
})
```

---

## Performance Testing

### Load Testing Backend

```python
# tests/performance/load_test.py
from locust import HttpUser, task, between

class OceanMLUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_videos(self):
        self.client.get("/api/videos")

    @task(2)
    def get_video(self):
        self.client.get("/api/videos/test-video-id")

    @task(1)
    def upload_video(self):
        with open("test_fixtures/small_video.mp4", "rb") as f:
            self.client.post(
                "/api/videos",
                files={"file": ("test.mp4", f, "video/mp4")}
            )
```

Run load test:
```bash
locust -f tests/performance/load_test.py --host http://localhost:8000
```

### Performance Benchmarks

| Endpoint | Target | Current | Status |
|----------|--------|---------|--------|
| GET /api/videos | <200ms | - | ⏳ |
| POST /api/videos | <5s | - | ⏳ |
| POST /api/train | <500ms | - | ⏳ |
| WebSocket /api/train/{id}/logs | <100ms latency | - | ⏳ |

---

## Test Data Management

### Fixtures

```
tests/fixtures/
├── videos/
│   ├── small_video.mp4        # 5 MB, 10s
│   ├── medium_video.mp4       # 25 MB, 30s
│   └── large_video.mp4        # 100 MB, 2min
├── annotations/
│   ├── video_1_annotations.txt
│   └── video_2_annotations.txt
└── models/
    └── test_model_weights.pt
```

### Test Database

Use separate Supabase project for testing:

```bash
# .env.test
SUPABASE_TEST_URL=https://test-project.supabase.co
SUPABASE_TEST_KEY=test-anon-key
```

Reset test database before each test run:

```python
# tests/reset_test_db.py
from supabase import create_client

supabase = create_client(TEST_URL, TEST_KEY)

# Delete all test data
supabase.table('videos').delete().neq('id', '').execute()
supabase.table('annotations').delete().neq('id', '').execute()
supabase.table('training_runs').delete().neq('id', '').execute()

# Clear storage
supabase.storage.from_('videos').empty()
supabase.storage.from_('annotations').empty()
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        env:
          SUPABASE_TEST_URL: ${{ secrets.SUPABASE_TEST_URL }}
          SUPABASE_TEST_KEY: ${{ secrets.SUPABASE_TEST_KEY }}
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

  desktop-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd desktop
          pip install -r requirements.txt
          pip install pytest pytest-qt
      - name: Run tests
        run: |
          cd desktop
          pytest
```

---

## Test Reporting

### Coverage Reports

Generate HTML coverage reports after each test run:

```bash
# Backend
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm test -- --coverage
open coverage/index.html
```

### Test Result Summary

Create a test summary script:

```python
# scripts/test_summary.py
import subprocess
import json

def run_tests():
    results = {}

    # Backend tests
    backend_result = subprocess.run(
        ["pytest", "--json-report", "--json-report-file=results.json"],
        cwd="backend",
        capture_output=True
    )
    with open("backend/results.json") as f:
        results["backend"] = json.load(f)

    # Frontend tests
    frontend_result = subprocess.run(
        ["npm", "test", "--", "--json"],
        cwd="frontend",
        capture_output=True
    )
    results["frontend"] = json.loads(frontend_result.stdout)

    # Generate summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Backend: {results['backend']['summary']['passed']} passed, {results['backend']['summary']['failed']} failed")
    print(f"Frontend: {results['frontend']['numPassedTests']} passed, {results['frontend']['numFailedTests']} failed")
    print("=" * 50)

    return results

if __name__ == "__main__":
    run_tests()
```

---

## Debugging Failed Tests

### Backend Debugging

```python
# Add to conftest.py
@pytest.fixture(autouse=True)
def log_test_name(request):
    print(f"\n▶️  Running: {request.node.name}")
    yield
    print(f"✅ Completed: {request.node.name}")

# Use pytest-pdb for debugging
# Run: pytest --pdb
# Test will drop into debugger on failure
```

### Frontend Debugging

```typescript
// Enable debug mode in tests
import { debug } from '@testing-library/react'

it('some test', () => {
  const { container } = render(<MyComponent />)
  debug(container) // Prints HTML to console
})
```

### Desktop Debugging

```python
# Use pytest-qt for GUI debugging
def test_ui(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Take screenshot on failure
    qtbot.wait(1000)
    widget.grab().save("test_screenshot.png")
```

---

## Test Maintenance

### Regular Tasks

- **Daily:** Run unit tests before committing
- **Weekly:** Run full test suite including integration tests
- **Monthly:** Review test coverage and add tests for uncovered code
- **Per Release:** Run full E2E tests and update test documentation

### Updating Tests

When modifying code, update tests in same commit:

```bash
# Make code change
git add src/feature.py

# Update corresponding test
git add tests/test_feature.py

# Commit together
git commit -m "feat: Add new feature with tests"
```

---

**Remember: Tests are not optional. No checkpoint is complete until tests pass!**

---

**End of Testing Strategy**
