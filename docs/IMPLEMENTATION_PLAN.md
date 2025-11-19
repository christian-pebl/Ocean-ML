# Ocean-ML Implementation Plan

**Version:** 1.0
**Created:** 2025-11-19
**Status:** Planning Phase

---

## Overview

This document outlines a **safe, incremental implementation plan** for Ocean-ML with testing checkpoints at every step. Each phase is broken into small, testable units with clear success criteria.

### Guiding Principles

1. **Test Early, Test Often** - Every feature has automated tests before moving forward
2. **Document as You Go** - Create/update documentation with each step
3. **Incremental Progress** - Each step should take 2-4 hours maximum
4. **Rollback Safety** - Git commits after each successful checkpoint
5. **Validation Before Proceeding** - Never move to next step until current step passes all tests

---

## Phase 0: Foundation Setup (Week 1, Days 1-2)

### Step 0.1: Supabase Project Setup
**Time Estimate:** 1 hour
**Risk Level:** Low

#### Tasks
1. Create Supabase project
2. Set up database schema
3. Configure Row Level Security (RLS)
4. Create storage buckets
5. Test basic CRUD operations

#### Implementation
```bash
# Create docs/checkpoints/0.1-supabase-setup.md
# Document all Supabase configuration
```

#### Testing Checkpoint 0.1
- [ ] Can connect to Supabase from Python
- [ ] Can create/read/update/delete test record
- [ ] RLS policies prevent unauthorized access
- [ ] Storage buckets accessible with correct permissions
- [ ] Test user can sign up and log in

#### Success Criteria
- All tests pass
- Connection credentials documented in `.env`
- Database schema matches SPEC.md

#### Rollback Plan
- Delete Supabase project and recreate
- No code dependencies yet

**Documentation Output:** `docs/checkpoints/0.1-supabase-setup.md`

---

### Step 0.2: Modal.com Setup
**Time Estimate:** 1 hour
**Risk Level:** Low

#### Tasks
1. Create Modal account
2. Install Modal CLI
3. Authenticate Modal
4. Create test function
5. Run test GPU job

#### Implementation
```bash
modal setup
modal token new
modal app deploy test_app.py
```

#### Testing Checkpoint 0.2
- [ ] Modal CLI authenticated
- [ ] Can deploy test function
- [ ] Can invoke function and get response
- [ ] GPU function runs successfully (even if trivial)
- [ ] Logs stream to console

#### Success Criteria
- Test GPU function completes without errors
- Billing dashboard shows usage
- Modal token stored securely

#### Rollback Plan
- Delete Modal app
- No production dependencies yet

**Documentation Output:** `docs/checkpoints/0.2-modal-setup.md`

---

### Step 0.3: Local Development Environment
**Time Estimate:** 2 hours
**Risk Level:** Low

#### Tasks
1. Set up Python virtual environment for backend
2. Install backend dependencies
3. Set up Node.js environment for frontend
4. Install frontend dependencies
5. Configure environment variables
6. Verify all connections

#### Implementation
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Test connections
python backend/tests/test_connections.py
```

#### Testing Checkpoint 0.3
- [ ] Backend virtual environment activates
- [ ] All Python dependencies install without errors
- [ ] Frontend dependencies install without errors
- [ ] Can connect to Supabase from backend
- [ ] Can connect to Supabase from frontend
- [ ] Environment variables loaded correctly

#### Success Criteria
- All connection tests pass
- No dependency conflicts
- `.env` files configured

#### Rollback Plan
- Delete virtual environments
- Clear node_modules
- Reinstall from scratch

**Documentation Output:** `docs/checkpoints/0.3-dev-environment.md`

---

## Phase 1: Core Backend API (Week 1, Days 3-5)

### Step 1.1: Basic FastAPI Structure
**Time Estimate:** 2 hours
**Risk Level:** Low

#### Tasks
1. Create FastAPI application skeleton
2. Set up CORS middleware
3. Add health check endpoint
4. Add Supabase client initialization
5. Add basic error handling

#### Implementation
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ocean-ML API", version="0.1.0")

# CORS
app.add_middleware(CORSMiddleware, ...)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/supabase-test")
async def test_supabase():
    # Test Supabase connection
    pass
```

#### Testing Checkpoint 1.1
- [ ] FastAPI starts without errors
- [ ] Health endpoint returns 200
- [ ] Supabase test endpoint returns 200
- [ ] CORS headers present in responses
- [ ] OpenAPI docs accessible at /docs

#### Test Script
```python
# backend/tests/test_api_basic.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_supabase_connection():
    response = client.get("/supabase-test")
    assert response.status_code == 200
```

#### Success Criteria
- All tests pass with `pytest`
- API accessible at localhost:8000
- Swagger docs render correctly

#### Rollback Plan
- Revert to previous commit
- No database changes made

**Documentation Output:** `docs/checkpoints/1.1-fastapi-basic.md`

---

### Step 1.2: Video Endpoints (List & Get)
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Create Pydantic models for Video
2. Implement GET /api/videos (list all)
3. Implement GET /api/videos/{id} (get one)
4. Add database queries
5. Write unit tests

#### Implementation
```python
# backend/models/video.py
from pydantic import BaseModel
from datetime import datetime

class Video(BaseModel):
    id: str
    filename: str
    duration_seconds: int
    annotated: bool
    annotated_by: str | None
    # ... other fields

# backend/routers/videos.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.get("/")
async def list_videos():
    # Query Supabase videos table
    pass

@router.get("/{video_id}")
async def get_video(video_id: str):
    # Query single video
    pass
```

#### Testing Checkpoint 1.2
- [ ] Can list all videos (empty list initially)
- [ ] Can get specific video by ID
- [ ] Returns 404 for non-existent video
- [ ] Response matches Video schema
- [ ] Database queries use proper error handling

#### Test Script
```python
# backend/tests/test_videos.py
def test_list_videos_empty():
    response = client.get("/api/videos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_video_not_found():
    response = client.get("/api/videos/nonexistent")
    assert response.status_code == 404

def test_list_videos_with_data():
    # Insert test video via Supabase
    # Query via API
    # Verify response
    pass
```

#### Success Criteria
- All tests pass
- Can manually test with curl/Postman
- Error responses are consistent

#### Rollback Plan
- Revert router files
- No schema changes made yet

**Documentation Output:** `docs/checkpoints/1.2-video-endpoints.md`

---

### Step 1.3: Video Upload Endpoint
**Time Estimate:** 4 hours
**Risk Level:** Medium (file uploads can be tricky)

#### Tasks
1. Implement POST /api/videos (upload)
2. Validate file type and size
3. Upload to Supabase Storage
4. Create database record
5. Generate thumbnail
6. Write tests with test video file

#### Implementation
```python
# backend/routers/videos.py
from fastapi import UploadFile, File

@router.post("/")
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    # Validate file
    if not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")

    # Upload to Supabase Storage
    storage_path = f"videos/{uuid4()}.mp4"
    # ... upload logic

    # Create database record
    # ... insert into videos table

    return {"id": video_id, "status": "uploaded"}
```

#### Testing Checkpoint 1.3
- [ ] Can upload video file (<100MB)
- [ ] Video stored in Supabase Storage
- [ ] Database record created with correct metadata
- [ ] Rejects non-video files
- [ ] Rejects files over size limit
- [ ] Returns proper error messages

#### Test Script
```python
# backend/tests/test_video_upload.py
def test_upload_valid_video():
    with open("test_fixtures/sample_video.mp4", "rb") as f:
        response = client.post(
            "/api/videos",
            files={"file": ("test.mp4", f, "video/mp4")}
        )
    assert response.status_code == 200
    video_id = response.json()["id"]

    # Verify in database
    # Verify in storage

def test_upload_invalid_file_type():
    with open("test_fixtures/sample_image.jpg", "rb") as f:
        response = client.post(
            "/api/videos",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 400
```

#### Success Criteria
- All tests pass
- Can upload real video file (use one from your 73 videos)
- File accessible via Supabase Storage URL
- Database record has correct metadata

#### Rollback Plan
- Delete uploaded test files from Supabase Storage
- Delete test database records
- Revert code changes

**Documentation Output:** `docs/checkpoints/1.3-video-upload.md`

---

### Step 1.4: Video Locking Mechanism
**Time Estimate:** 3 hours
**Risk Level:** Medium

#### Tasks
1. Implement video lock acquisition
2. Implement lock release
3. Add lock expiration (auto-release after timeout)
4. Handle lock conflicts
5. Write concurrent access tests

#### Implementation
```python
# backend/services/video_lock.py
from datetime import datetime, timedelta

class VideoLockService:
    async def acquire_lock(self, video_id: str, user_id: str) -> bool:
        """Try to acquire lock. Returns False if already locked."""
        # Check if currently locked
        # If not locked or expired, create lock
        # Return success/failure
        pass

    async def release_lock(self, video_id: str, user_id: str):
        """Release lock if owned by user."""
        pass

    async def extend_lock(self, video_id: str, user_id: str):
        """Extend lock expiration."""
        pass

# backend/routers/annotations.py
@router.post("/annotate/{video_id}")
async def start_annotation(video_id: str, user_id: str = Depends(get_current_user)):
    # Try to acquire lock
    locked = await video_lock_service.acquire_lock(video_id, user_id)
    if not locked:
        raise HTTPException(409, "Video is currently being annotated by another user")

    # Return video download URL
    return {"video_url": get_download_url(video_id)}
```

#### Testing Checkpoint 1.4
- [ ] Can acquire lock on unlocked video
- [ ] Cannot acquire lock on locked video
- [ ] Lock auto-expires after timeout
- [ ] Can release lock
- [ ] Only lock owner can release lock
- [ ] Concurrent lock attempts handled correctly

#### Test Script
```python
# backend/tests/test_video_lock.py
import asyncio

async def test_lock_acquisition():
    # User A acquires lock
    success = await lock_service.acquire_lock("video_1", "user_a")
    assert success == True

    # User B tries to acquire same lock
    success = await lock_service.acquire_lock("video_1", "user_b")
    assert success == False

async def test_lock_expiration():
    # Acquire lock with 5 second timeout
    await lock_service.acquire_lock("video_1", "user_a")

    # Wait 6 seconds
    await asyncio.sleep(6)

    # User B should be able to acquire now
    success = await lock_service.acquire_lock("video_1", "user_b")
    assert success == True
```

#### Success Criteria
- All tests pass
- Can demonstrate concurrent access prevention
- Lock expiration works as expected

#### Rollback Plan
- Revert lock service
- Remove lock-related database columns
- Update API to not use locks

**Documentation Output:** `docs/checkpoints/1.4-video-locking.md`

---

### Step 1.5: Annotation Upload Endpoint
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Implement POST /api/annotations/complete
2. Validate annotation format (YOLO)
3. Upload annotations to Supabase Storage
4. Update video record (set annotated=true)
5. Release video lock
6. Write tests with sample annotations

#### Implementation
```python
# backend/routers/annotations.py
@router.post("/complete")
async def complete_annotation(
    video_id: str,
    annotation_data: str,
    detection_count: int,
    user_id: str = Depends(get_current_user)
):
    # Validate YOLO format
    validate_yolo_annotations(annotation_data)

    # Upload to Storage
    storage_path = f"annotations/{video_id}.txt"
    # ... upload

    # Update database
    # ... set annotated=true, annotated_by=user_id, etc.

    # Release lock
    await video_lock_service.release_lock(video_id, user_id)

    return {"status": "success"}
```

#### Testing Checkpoint 1.5
- [ ] Can upload valid YOLO annotations
- [ ] Annotations stored in Supabase Storage
- [ ] Video record updated correctly
- [ ] Lock released after upload
- [ ] Rejects invalid annotation format
- [ ] Handles upload errors gracefully

#### Test Script
```python
# backend/tests/test_annotations.py
def test_upload_valid_annotations():
    # First acquire lock
    # Then upload annotations
    response = client.post("/api/annotations/complete", json={
        "video_id": "test_video_1",
        "annotation_data": "0 0.5 0.5 0.1 0.1\n1 0.3 0.3 0.2 0.2",
        "detection_count": 2
    })
    assert response.status_code == 200

    # Verify video marked as annotated
    video = client.get("/api/videos/test_video_1").json()
    assert video["annotated"] == True

def test_upload_invalid_annotations():
    response = client.post("/api/annotations/complete", json={
        "video_id": "test_video_1",
        "annotation_data": "invalid format",
        "detection_count": 0
    })
    assert response.status_code == 400
```

#### Success Criteria
- All tests pass
- Can upload annotations from your existing PyQt5 app format
- Annotations accessible via Storage

#### Rollback Plan
- Delete test annotations from Storage
- Revert video records to unannotated state

**Documentation Output:** `docs/checkpoints/1.5-annotation-upload.md`

---

## Phase 2: Frontend Dashboard (Week 2, Days 1-3)

### Step 2.1: React Project Setup
**Time Estimate:** 2 hours
**Risk Level:** Low

#### Tasks
1. Initialize Vite + React + TypeScript project
2. Install dependencies (TailwindCSS, React Query, Supabase)
3. Configure TailwindCSS
4. Set up project structure
5. Create basic routing

#### Implementation
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @supabase/supabase-js @tanstack/react-query
npm run dev
```

#### Testing Checkpoint 2.1
- [ ] Vite dev server starts without errors
- [ ] Can access http://localhost:3000
- [ ] Hot reload works
- [ ] TailwindCSS classes apply correctly
- [ ] TypeScript compilation successful

#### Success Criteria
- React app renders
- No console errors
- TailwindCSS working

#### Rollback Plan
- Delete frontend directory
- Reinitialize with npm create vite

**Documentation Output:** `docs/checkpoints/2.1-react-setup.md`

---

### Step 2.2: Supabase Authentication UI
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Set up Supabase client
2. Create login page
3. Implement Google OAuth
4. Implement email/password auth
5. Add protected routes
6. Test auth flow

#### Implementation
```typescript
// frontend/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// frontend/src/components/Auth/LoginPage.tsx
import { Auth } from '@supabase/auth-ui-react'

export function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full">
        <h1>Ocean-ML</h1>
        <Auth
          supabaseClient={supabase}
          providers={['google']}
          appearance={{ theme: 'dark' }}
        />
      </div>
    </div>
  )
}
```

#### Testing Checkpoint 2.2
- [ ] Login page renders
- [ ] Can sign up with email/password
- [ ] Can sign in with email/password
- [ ] Can sign in with Google
- [ ] Session persists on page reload
- [ ] Can sign out
- [ ] Protected routes redirect to login

#### Test Procedure
1. Open app in incognito window
2. Try to access dashboard (should redirect to login)
3. Sign up with new email
4. Verify email (check Supabase inbox)
5. Sign in
6. Reload page (should stay signed in)
7. Sign out
8. Try Google sign-in

#### Success Criteria
- All manual tests pass
- Auth state persists correctly
- No console errors

#### Rollback Plan
- Revert auth components
- Keep Supabase client setup

**Documentation Output:** `docs/checkpoints/2.2-auth-ui.md`

---

### Step 2.3: Video Library Grid
**Time Estimate:** 4 hours
**Risk Level:** Low

#### Tasks
1. Create VideoGrid component
2. Create VideoCard component
3. Fetch videos from backend API
4. Display video metadata
5. Show annotation status
6. Add loading and error states

#### Implementation
```typescript
// frontend/src/components/VideoLibrary/VideoGrid.tsx
import { useQuery } from '@tanstack/react-query'
import { VideoCard } from './VideoCard'

export function VideoGrid() {
  const { data: videos, isLoading, error } = useQuery({
    queryKey: ['videos'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/videos`)
      return response.json()
    }
  })

  if (isLoading) return <div>Loading videos...</div>
  if (error) return <div>Error loading videos</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {videos.map(video => (
        <VideoCard key={video.id} video={video} />
      ))}
    </div>
  )
}

// frontend/src/components/VideoLibrary/VideoCard.tsx
export function VideoCard({ video }) {
  return (
    <div className="border rounded-lg p-4">
      <img src={video.thumbnail_path} alt={video.filename} />
      <h3>{video.filename}</h3>
      {video.annotated ? (
        <span className="text-green-500">✓ Annotated</span>
      ) : (
        <span className="text-gray-500">○ Not annotated</span>
      )}
      <button className="mt-2 w-full bg-blue-500 text-white rounded">
        Annotate
      </button>
    </div>
  )
}
```

#### Testing Checkpoint 2.3
- [ ] Video grid renders
- [ ] Shows loading state while fetching
- [ ] Shows error state on API failure
- [ ] Displays all videos from backend
- [ ] Cards show correct metadata
- [ ] Annotation status displays correctly
- [ ] Grid is responsive (mobile/desktop)

#### Test Procedure
1. Start backend with test videos
2. Open frontend
3. Verify videos display
4. Stop backend, verify error message
5. Test on mobile viewport
6. Test with 0 videos, 1 video, 50+ videos

#### Success Criteria
- Grid renders correctly
- No console errors
- Responsive on all screen sizes

#### Rollback Plan
- Revert VideoGrid components
- Keep API client setup

**Documentation Output:** `docs/checkpoints/2.3-video-grid.md`

---

### Step 2.4: Real-time Updates (WebSocket)
**Time Estimate:** 3 hours
**Risk Level:** Medium

#### Tasks
1. Set up Supabase Realtime subscription
2. Subscribe to video table changes
3. Update UI when videos change
4. Show notification when someone annotates
5. Test with multiple browser tabs

#### Implementation
```typescript
// frontend/src/hooks/useRealtimeVideos.ts
import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

export function useRealtimeVideos() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const channel = supabase
      .channel('videos')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'videos'
        },
        (payload) => {
          console.log('Video updated:', payload.new)

          // Invalidate videos query to refetch
          queryClient.invalidateQueries({ queryKey: ['videos'] })

          // Show notification
          showNotification(`Video ${payload.new.filename} annotated!`)
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [queryClient])
}

// Use in VideoGrid
export function VideoGrid() {
  useRealtimeVideos() // Subscribe to updates
  // ... rest of component
}
```

#### Testing Checkpoint 2.4
- [ ] Subscription established successfully
- [ ] UI updates when video changes (via backend API)
- [ ] Multiple tabs all update simultaneously
- [ ] Notifications appear on updates
- [ ] No memory leaks (subscription cleaned up)
- [ ] Works with intermittent connection

#### Test Procedure
1. Open dashboard in two browser tabs
2. In tab 1, trigger video update via backend/Supabase
3. Verify tab 2 updates automatically
4. Check browser console for subscription logs
5. Close tab, reopen, verify subscription reestablished
6. Monitor network tab for WebSocket connection

#### Success Criteria
- Real-time updates work reliably
- No performance degradation
- Clean reconnection after network loss

#### Rollback Plan
- Remove realtime hook
- Fall back to polling (refetch every 30s)

**Documentation Output:** `docs/checkpoints/2.4-realtime-updates.md`

---

## Phase 3: Desktop App Integration (Week 2-3, Days 4-7)

### Step 3.1: Protocol Handler Registration
**Time Estimate:** 4 hours
**Risk Level:** High (OS-level registry changes)

#### Tasks
1. Create protocol handler registration script
2. Test `oceanml://` URL handling
3. Handle URL parameters (video ID, token)
4. Add uninstall script
5. Test on Windows and Mac

#### Implementation
```python
# desktop/register_protocol.py
import sys
import winreg  # Windows
import subprocess  # Mac

def register_protocol_windows():
    """Register oceanml:// protocol on Windows"""
    key_path = r"Software\Classes\oceanml"

    # Create protocol key
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValue(key, "", winreg.REG_SZ, "URL:OceanML Protocol")
    winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

    # Create command key
    command_path = f"{key_path}\\shell\\open\\command"
    command_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path)

    # Set command to launch PYQT5_UI.py
    exe_path = sys.executable
    script_path = os.path.abspath("PYQT5_UI.py")
    command = f'"{exe_path}" "{script_path}" "%1"'
    winreg.SetValue(command_key, "", winreg.REG_SZ, command)

    print("✓ Protocol handler registered")

def register_protocol_mac():
    """Register oceanml:// protocol on Mac"""
    # Create Info.plist entry
    # Use LSSetDefaultHandlerForURLScheme
    pass

if __name__ == "__main__":
    if sys.platform == "win32":
        register_protocol_windows()
    elif sys.platform == "darwin":
        register_protocol_mac()
```

#### Testing Checkpoint 3.1
- [ ] Registration script runs without errors
- [ ] Can open `oceanml://test` URL
- [ ] Desktop app launches when URL opened
- [ ] URL parameters passed to app
- [ ] Uninstall script removes registration
- [ ] No leftover registry entries after uninstall

#### Test Procedure
1. Run registration script
2. Open browser
3. Navigate to `oceanml://test?video=123&token=abc`
4. Verify desktop app launches with parameters
5. Run uninstall script
6. Try opening URL again (should not work)
7. Check registry/plist for leftover entries

#### Success Criteria
- Protocol handler works reliably
- No security warnings
- Clean uninstall

#### Rollback Plan
- Run uninstall script
- Manually clean registry if needed
- Document manual cleanup steps

**Documentation Output:** `docs/checkpoints/3.1-protocol-handler.md`

**⚠️ SAFETY NOTE:** Before this step, create full system backup. Test on VM first if possible.

---

### Step 3.2: Desktop App URL Parsing
**Time Estimate:** 2 hours
**Risk Level:** Low

#### Tasks
1. Parse `oceanml://` URLs
2. Extract video ID and token
3. Validate token format
4. Handle malformed URLs
5. Write unit tests

#### Implementation
```python
# desktop/services/protocol_handler.py
from urllib.parse import urlparse, parse_qs

class ProtocolHandler:
    def parse_url(self, url: str) -> dict:
        """
        Parse oceanml:// URL
        Example: oceanml://annotate?video=123&token=eyJ...
        """
        parsed = urlparse(url)

        if parsed.scheme != "oceanml":
            raise ValueError("Invalid protocol")

        action = parsed.netloc  # 'annotate'
        params = parse_qs(parsed.query)

        return {
            "action": action,
            "video_id": params.get("video", [None])[0],
            "token": params.get("token", [None])[0]
        }

    def validate_token(self, token: str) -> bool:
        """Basic JWT format validation"""
        parts = token.split(".")
        return len(parts) == 3  # JWT has 3 parts

# desktop/PYQT5_UI.py
import sys
from protocol_handler import ProtocolHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Check for protocol URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
        handler = ProtocolHandler()

        try:
            params = handler.parse_url(url)
            print(f"Action: {params['action']}")
            print(f"Video ID: {params['video_id']}")
            print(f"Token: {params['token'][:20]}...")

            # Launch annotation window
            window = AnnotationWindow(params['video_id'], params['token'])
            window.show()
        except Exception as e:
            print(f"Error parsing URL: {e}")

    sys.exit(app.exec_())
```

#### Testing Checkpoint 3.2
- [ ] Can parse valid URLs
- [ ] Extracts video ID correctly
- [ ] Extracts token correctly
- [ ] Handles missing parameters
- [ ] Handles malformed URLs
- [ ] Token validation works

#### Test Script
```python
# desktop/tests/test_protocol_handler.py
import pytest
from services.protocol_handler import ProtocolHandler

def test_parse_valid_url():
    handler = ProtocolHandler()
    result = handler.parse_url("oceanml://annotate?video=123&token=abc")

    assert result["action"] == "annotate"
    assert result["video_id"] == "123"
    assert result["token"] == "abc"

def test_parse_missing_params():
    handler = ProtocolHandler()
    result = handler.parse_url("oceanml://annotate")

    assert result["video_id"] is None

def test_parse_invalid_protocol():
    handler = ProtocolHandler()
    with pytest.raises(ValueError):
        handler.parse_url("http://example.com")
```

#### Success Criteria
- All unit tests pass
- Can parse URLs from browser
- Proper error handling

#### Rollback Plan
- Revert protocol_handler.py
- Keep manual URL input as backup

**Documentation Output:** `docs/checkpoints/3.2-url-parsing.md`

---

### Step 3.3: Video Download with Progress
**Time Estimate:** 4 hours
**Risk Level:** Medium

#### Tasks
1. Create video downloader service
2. Show progress dialog
3. Download video from Supabase Storage
4. Cache videos locally
5. Handle download failures
6. Implement resume/retry

#### Implementation
```python
# desktop/services/video_downloader.py
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class VideoDownloader(QThread):
    progress = pyqtSignal(int)  # Progress percentage
    finished = pyqtSignal(str)  # Local file path
    error = pyqtSignal(str)     # Error message

    def __init__(self, video_url: str, local_path: str):
        super().__init__()
        self.video_url = video_url
        self.local_path = local_path

    def run(self):
        try:
            response = requests.get(self.video_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(self.local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Emit progress
                    progress_pct = int((downloaded / total_size) * 100)
                    self.progress.emit(progress_pct)

            self.finished.emit(self.local_path)
        except Exception as e:
            self.error.emit(str(e))

# desktop/ui/download_dialog.py
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel

class DownloadDialog(QDialog):
    def __init__(self, video_id: str):
        super().__init__()
        self.setWindowTitle("Downloading Video")

        self.label = QLabel(f"Downloading video {video_id}...")
        self.progress_bar = QProgressBar()

        # Layout setup...

    def update_progress(self, percentage: int):
        self.progress_bar.setValue(percentage)
```

#### Testing Checkpoint 3.3
- [ ] Download dialog appears
- [ ] Progress bar updates smoothly
- [ ] Video downloads completely
- [ ] File saved to correct location
- [ ] Handles network interruption gracefully
- [ ] Can retry failed download
- [ ] Already-downloaded videos load from cache

#### Test Procedure
1. Trigger video download
2. Monitor progress bar (should go 0% → 100%)
3. Interrupt network mid-download
4. Verify error handling
5. Retry download
6. Download same video again (should use cache)
7. Check cache directory size
8. Test with large video (>100MB)

#### Success Criteria
- Smooth download experience
- Reliable error recovery
- Cache works correctly

#### Rollback Plan
- Revert downloader service
- Use synchronous download (blocking)

**Documentation Output:** `docs/checkpoints/3.3-video-download.md`

---

### Step 3.4: Connect Frontend "Annotate" Button to Desktop
**Time Estimate:** 3 hours
**Risk Level:** Medium

#### Tasks
1. Add "Annotate" button click handler
2. Generate signed URL for video
3. Open `oceanml://` URL from browser
4. Pass auth token securely
5. Test full flow: browser → desktop

#### Implementation
```typescript
// frontend/src/components/VideoLibrary/VideoCard.tsx
export function VideoCard({ video }) {
  const handleAnnotate = async () => {
    try {
      // Call backend to get video URL and lock
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/annotate/${video.id}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        }
      )

      const data = await response.json()

      if (response.status === 409) {
        alert("Video is currently being annotated by another user")
        return
      }

      // Open desktop app
      const url = `oceanml://annotate?video=${video.id}&token=${session.access_token}`
      window.location.href = url

      // Show "waiting" state
      setAnnotationStatus('in_progress')
    } catch (error) {
      console.error("Error starting annotation:", error)
      alert("Failed to start annotation")
    }
  }

  return (
    <div className="video-card">
      {/* ... */}
      <button onClick={handleAnnotate}>Annotate</button>
    </div>
  )
}
```

#### Testing Checkpoint 3.4
- [ ] Click "Annotate" button in browser
- [ ] Desktop app launches automatically
- [ ] Video ID passed correctly
- [ ] Auth token passed correctly
- [ ] Lock acquired successfully
- [ ] Browser shows "in progress" state
- [ ] Works on first try (no manual intervention)

#### Test Procedure
1. Log into web dashboard
2. Click "Annotate" on video
3. Verify desktop app launches
4. Check desktop app shows correct video
5. Try clicking "Annotate" on same video in another tab
6. Verify lock prevents second annotation

#### Success Criteria
- Seamless browser → desktop flow
- No manual URL copying
- Lock mechanism works

#### Rollback Plan
- Add "Copy URL" button as fallback
- Allow manual desktop app launch

**Documentation Output:** `docs/checkpoints/3.4-browser-to-desktop.md`

---

## Phase 4: Modal Training Integration (Week 3-4)

### Step 4.1: Basic Modal Training Function
**Time Estimate:** 4 hours
**Risk Level:** Medium

#### Tasks
1. Create Modal training function
2. Download test annotations from Supabase
3. Train YOLO model on minimal dataset
4. Upload trained weights
5. Test end-to-end

#### Implementation
```python
# modal_functions/training.py
import modal

app = modal.App("ocean-ml-training")

image = (
    modal.Image.debian_slim()
    .pip_install("ultralytics", "supabase-py")
)

@app.function(
    gpu="T4",  # Start with cheaper GPU
    timeout=600,  # 10 minutes for test
    image=image,
    secrets=[modal.Secret.from_name("supabase")]
)
def train_yolo_test(dataset_id: str):
    """Test training function with minimal dataset"""
    from ultralytics import YOLO
    import os

    print("🚀 Starting test training...")

    # Create minimal dataset (1-2 videos)
    # ... prepare data

    # Train for just 5 epochs
    model = YOLO("yolov8n.pt")
    results = model.train(
        data="dataset.yaml",
        epochs=5,
        imgsz=640,
        device=0
    )

    print("✓ Training complete!")
    return {"status": "success"}
```

#### Testing Checkpoint 4.1
- [ ] Modal function deploys successfully
- [ ] Can invoke function from local Python
- [ ] Function downloads annotations from Supabase
- [ ] Training starts without errors
- [ ] Training completes (even if accuracy is poor)
- [ ] Logs stream to console
- [ ] Cost is reasonable (<$1)

#### Test Procedure
```bash
# Deploy function
modal deploy modal_functions/training.py

# Test invocation
modal run modal_functions/training.py::train_yolo_test --dataset-id test_dataset
```

Watch logs in real-time, verify it completes.

#### Success Criteria
- Function runs to completion
- No GPU errors
- Weights file generated

#### Rollback Plan
- Delete Modal app
- No production dependencies yet

**Documentation Output:** `docs/checkpoints/4.1-modal-training-basic.md`

---

### Step 4.2: Backend Training Orchestration
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Create training endpoint in backend
2. Trigger Modal function from API
3. Store training run metadata
4. Return job ID to frontend
5. Test triggering from Postman

#### Implementation
```python
# backend/routers/training.py
from fastapi import APIRouter
import modal

router = APIRouter(prefix="/api/train", tags=["training"])

@router.post("/")
async def start_training(config: TrainingConfig):
    """Trigger training on Modal"""

    # Create training run record
    training_run = await db.create_training_run(config)

    # Get Modal function
    fn = modal.Function.lookup("ocean-ml-training", "train_yolo_test")

    # Spawn async call
    call = fn.spawn(dataset_id=config.dataset_id)

    # Store Modal call ID
    await db.update_training_run(training_run.id, {
        "modal_call_id": call.object_id,
        "status": "running"
    })

    return {
        "training_run_id": training_run.id,
        "status": "started"
    }

@router.get("/{training_run_id}")
async def get_training_status(training_run_id: str):
    """Get training run status"""
    run = await db.get_training_run(training_run_id)
    return run
```

#### Testing Checkpoint 4.2
- [ ] Can POST to /api/train
- [ ] Training run record created in database
- [ ] Modal function triggered
- [ ] Job ID returned to client
- [ ] Can GET training status
- [ ] Status updates as training progresses

#### Test Script
```python
# backend/tests/test_training.py
def test_start_training():
    response = client.post("/api/train", json={
        "dataset_id": "test_dataset",
        "model_type": "yolov8n",
        "epochs": 5
    })

    assert response.status_code == 200
    training_run_id = response.json()["training_run_id"]

    # Check status
    status = client.get(f"/api/train/{training_run_id}").json()
    assert status["status"] in ["running", "completed"]
```

#### Success Criteria
- API triggers Modal successfully
- Database tracks training runs
- Status endpoint works

#### Rollback Plan
- Revert training router
- Keep Modal function separate

**Documentation Output:** `docs/checkpoints/4.2-training-orchestration.md`

---

### Step 4.3: Live Log Streaming (WebSocket)
**Time Estimate:** 4 hours
**Risk Level:** Medium

#### Tasks
1. Set up WebSocket endpoint in backend
2. Stream Modal logs to WebSocket
3. Frontend subscribes to logs
4. Display logs in real-time
5. Handle reconnection

#### Implementation
```python
# backend/routers/training.py
from fastapi import WebSocket

@router.websocket("/{training_run_id}/logs")
async def stream_training_logs(websocket: WebSocket, training_run_id: str):
    await websocket.accept()

    try:
        # Get Modal call
        call_id = await db.get_training_run_call_id(training_run_id)
        call = modal.Function.lookup("ocean-ml-training", "train_yolo_test").call(call_id)

        # Stream logs
        for log_line in call.get_logs():
            await websocket.send_text(log_line)

        # Send completion
        await websocket.send_json({"status": "complete"})
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
```

```typescript
// frontend/src/hooks/useTrainingLogs.ts
export function useTrainingLogs(trainingRunId: string) {
  const [logs, setLogs] = useState<string[]>([])
  const [status, setStatus] = useState<'connecting' | 'streaming' | 'complete'>('connecting')

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/api/train/${trainingRunId}/logs`)

    ws.onopen = () => {
      setStatus('streaming')
    }

    ws.onmessage = (event) => {
      const data = event.data
      if (typeof data === 'string') {
        setLogs(prev => [...prev, data])
      } else {
        const json = JSON.parse(data)
        if (json.status === 'complete') {
          setStatus('complete')
        }
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => ws.close()
  }, [trainingRunId])

  return { logs, status }
}
```

#### Testing Checkpoint 4.3
- [ ] WebSocket connection establishes
- [ ] Logs stream in real-time
- [ ] Frontend displays logs as they arrive
- [ ] Connection handles disconnection gracefully
- [ ] Multiple clients can watch same logs
- [ ] Logs persist after training completes

#### Test Procedure
1. Start training from frontend
2. Watch logs appear in real-time
3. Disconnect network mid-training
4. Reconnect (logs should resume)
5. Open dashboard in second tab
6. Verify both tabs show same logs

#### Success Criteria
- Smooth log streaming
- No missed log lines
- Reliable reconnection

#### Rollback Plan
- Fall back to polling (GET /api/train/{id}/logs every 2s)

**Documentation Output:** `docs/checkpoints/4.3-log-streaming.md`

---

### Step 4.4: Full Training Pipeline
**Time Estimate:** 6 hours
**Risk Level:** Medium

#### Tasks
1. Upgrade Modal function for production training
2. Download all annotations from Supabase
3. Prepare full YOLO dataset
4. Train with proper hyperparameters
5. Upload weights to Supabase
6. Update database with results
7. Test with real dataset (your 73 videos)

#### Implementation
```python
# modal_functions/training.py
@app.function(
    gpu="A100",  # Upgrade to A100
    timeout=3600,  # 1 hour
    image=image,
    secrets=[modal.Secret.from_name("supabase")]
)
def train_yolo_production(
    dataset_id: str,
    model_type: str,
    epochs: int,
    training_run_id: str
):
    """Production training with full dataset"""
    from ultralytics import YOLO
    from supabase import create_client
    import os

    print(f"🚀 Starting training: {model_type} for {epochs} epochs")

    # Connect to Supabase
    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

    # Download all annotations
    print("📥 Downloading annotations...")
    annotations = download_all_annotations(supabase, dataset_id)

    # Prepare YOLO dataset structure
    print("📦 Preparing dataset...")
    prepare_yolo_dataset(annotations)

    # Train model
    print(f"🎯 Training {model_type}...")
    model = YOLO(f"{model_type}.pt")
    results = model.train(
        data="dataset.yaml",
        epochs=epochs,
        imgsz=640,
        device=0,
        batch=16,
        workers=8,
        verbose=True
    )

    # Upload trained weights
    print("📤 Uploading model weights...")
    with open("runs/detect/train/weights/best.pt", "rb") as f:
        supabase.storage.from_('models').upload(
            f"training_runs/{training_run_id}/best.pt",
            f.read()
        )

    # Update database
    print("💾 Updating database...")
    metrics = {
        "map50": float(results.results_dict['metrics/mAP50(B)']),
        "map50_95": float(results.results_dict['metrics/mAP50-95(B)']),
        "precision": float(results.results_dict['metrics/precision(B)']),
        "recall": float(results.results_dict['metrics/recall(B)']),
    }

    supabase.table('training_runs').update({
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        **metrics
    }).eq('id', training_run_id).execute()

    print("✅ Training complete!")
    return metrics
```

#### Testing Checkpoint 4.4
- [ ] Downloads all annotations correctly
- [ ] Prepares valid YOLO dataset format
- [ ] Training starts and progresses
- [ ] Training completes successfully
- [ ] Achieves reasonable accuracy (mAP > 0.5)
- [ ] Uploads weights to Supabase
- [ ] Updates database with correct metrics
- [ ] Total cost < $5

#### Test Procedure
1. Ensure you have 5-10 annotated videos minimum
2. Trigger training from dashboard
3. Watch logs in real-time
4. Wait for completion (~30 mins)
5. Check Supabase Storage for weights file
6. Check database for updated metrics
7. Verify cost in Modal dashboard

#### Success Criteria
- Training completes without errors
- Model weights accessible
- Metrics reasonable
- Cost within budget

#### Rollback Plan
- Keep test training function
- Debug issues with test datasets first

**Documentation Output:** `docs/checkpoints/4.4-full-training-pipeline.md`

---

## Phase 5: Training UI (Week 4)

### Step 5.1: Training Configuration Modal
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Create training config modal/dialog
2. Allow model selection (yolov8n/s/m)
3. Set epoch count
4. Show cost estimate
5. Wire up to API

#### Implementation
```typescript
// frontend/src/components/Training/TrainingConfigModal.tsx
export function TrainingConfigModal({ isOpen, onClose, onStart }) {
  const [modelType, setModelType] = useState('yolov8s')
  const [epochs, setEpochs] = useState(100)

  const costEstimate = calculateCost(modelType, epochs)
  const timeEstimate = calculateTime(modelType, epochs)

  const handleStart = async () => {
    await onStart({ modelType, epochs })
    onClose()
  }

  return (
    <Dialog open={isOpen} onClose={onClose}>
      <h2>Train New Model</h2>

      <div>
        <label>Model Type:</label>
        <select value={modelType} onChange={e => setModelType(e.target.value)}>
          <option value="yolov8n">Fast (YOLOv8n) - Smaller, faster</option>
          <option value="yolov8s">Balanced (YOLOv8s) - Good accuracy</option>
          <option value="yolov8m">Accurate (YOLOv8m) - Best accuracy</option>
        </select>
      </div>

      <div>
        <label>Training Epochs:</label>
        <input
          type="number"
          value={epochs}
          onChange={e => setEpochs(parseInt(e.target.value))}
          min={10}
          max={300}
        />
      </div>

      <div className="estimates">
        <p>Estimated cost: ${costEstimate.toFixed(2)}</p>
        <p>Estimated time: {timeEstimate} minutes</p>
      </div>

      <button onClick={handleStart}>Start Training</button>
      <button onClick={onClose}>Cancel</button>
    </Dialog>
  )
}
```

#### Testing Checkpoint 5.1
- [ ] Modal opens when "Train Model" clicked
- [ ] Can select model type
- [ ] Can set epoch count
- [ ] Cost estimate updates correctly
- [ ] Time estimate reasonable
- [ ] Can start training
- [ ] Can cancel

#### Success Criteria
- UI is intuitive
- Estimates are accurate (±20%)
- Validation prevents invalid inputs

#### Rollback Plan
- Use simple form instead of modal

**Documentation Output:** `docs/checkpoints/5.1-training-config-modal.md`

---

### Step 5.2: Live Training Dashboard
**Time Estimate:** 4 hours
**Risk Level:** Low

#### Tasks
1. Create training dashboard component
2. Show current training progress
3. Display metrics (loss, mAP)
4. Show progress bar
5. Display live logs
6. Add stop button

#### Implementation
```typescript
// frontend/src/components/Training/TrainingDashboard.tsx
import { useTrainingLogs } from '../../hooks/useTrainingLogs'

export function TrainingDashboard({ trainingRunId }) {
  const { logs, status } = useTrainingLogs(trainingRunId)
  const { data: trainingRun } = useQuery({
    queryKey: ['training-run', trainingRunId],
    queryFn: () => fetchTrainingRun(trainingRunId),
    refetchInterval: 5000  // Poll every 5s
  })

  const progress = trainingRun ? (trainingRun.current_epoch / trainingRun.total_epochs) * 100 : 0

  return (
    <div className="training-dashboard">
      <h2>Training in Progress</h2>

      <div className="progress">
        <ProgressBar value={progress} />
        <span>Epoch {trainingRun?.current_epoch} / {trainingRun?.total_epochs}</span>
      </div>

      <div className="metrics">
        <MetricCard label="Loss" value={trainingRun?.current_loss} />
        <MetricCard label="mAP50" value={trainingRun?.current_map} />
        <MetricCard label="Time Elapsed" value={formatDuration(trainingRun?.elapsed_seconds)} />
        <MetricCard label="Cost" value={`$${trainingRun?.current_cost?.toFixed(2)}`} />
      </div>

      <div className="logs">
        <h3>Live Logs</h3>
        <div className="log-output">
          {logs.map((log, i) => (
            <div key={i} className="log-line">{log}</div>
          ))}
        </div>
      </div>

      <button onClick={() => stopTraining(trainingRunId)} className="danger">
        Stop Training
      </button>
    </div>
  )
}
```

#### Testing Checkpoint 5.2
- [ ] Dashboard renders during training
- [ ] Progress bar updates in real-time
- [ ] Metrics update every few seconds
- [ ] Logs scroll automatically
- [ ] Stop button works
- [ ] Dashboard updates when training completes
- [ ] Shows final results after completion

#### Test Procedure
1. Start training
2. Open training dashboard
3. Watch progress bar move
4. Verify metrics update
5. Scroll through logs
6. Test stop button (on separate run)
7. Let training complete, check final state

#### Success Criteria
- Real-time updates smooth
- No UI freezes
- Accurate metrics

#### Rollback Plan
- Use simpler static progress page
- Poll status every 10s instead of WebSocket

**Documentation Output:** `docs/checkpoints/5.2-training-dashboard.md`

---

## Phase 6: Model Management (Week 5)

### Step 6.1: Model List & Comparison
**Time Estimate:** 3 hours
**Risk Level:** Low

#### Tasks
1. Create models list page
2. Display all trained models
3. Show key metrics (mAP, cost, date)
4. Add comparison view
5. Allow model selection

#### Implementation
```typescript
// frontend/src/components/Models/ModelList.tsx
export function ModelList() {
  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: fetchModels
  })

  return (
    <div className="models-list">
      <h1>Trained Models</h1>

      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>Date</th>
            <th>mAP50</th>
            <th>Epochs</th>
            <th>Cost</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {models?.map(model => (
            <tr key={model.id}>
              <td>{model.model_type}</td>
              <td>{formatDate(model.created_at)}</td>
              <td>{model.map50?.toFixed(3)}</td>
              <td>{model.epochs}</td>
              <td>${model.cost_usd?.toFixed(2)}</td>
              <td>
                <button onClick={() => downloadModel(model.id)}>Download</button>
                <button onClick={() => runInference(model.id)}>Run Inference</button>
                <button onClick={() => deleteModel(model.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

#### Testing Checkpoint 6.1
- [ ] Models list displays correctly
- [ ] Shows accurate metrics
- [ ] Can download model weights
- [ ] Can trigger inference
- [ ] Can delete model
- [ ] Comparison view works (if implemented)

#### Success Criteria
- Clean, readable table
- All actions work
- Data accurate

#### Rollback Plan
- Use simple list instead of table

**Documentation Output:** `docs/checkpoints/6.1-model-list.md`

---

## Phase 7: End-to-End Testing (Week 5)

### Step 7.1: Complete Workflow Test
**Time Estimate:** 4 hours
**Risk Level:** Critical

#### Test Procedure

**Test Case 1: New User Onboarding**
1. [ ] User receives invitation email
2. [ ] Click link opens dashboard
3. [ ] Sign in with Google works
4. [ ] Desktop app download prompt appears
5. [ ] Download and install desktop app
6. [ ] App launches successfully
7. [ ] User sees video library

**Test Case 2: Annotation Workflow**
1. [ ] User clicks "Annotate" on video
2. [ ] Desktop app launches automatically
3. [ ] Video downloads with progress bar
4. [ ] Video loads in annotation interface
5. [ ] User draws bounding boxes
6. [ ] User saves annotations
7. [ ] Annotations upload to Supabase
8. [ ] Dashboard updates to show video annotated
9. [ ] Other users see update in real-time

**Test Case 3: Training Workflow**
1. [ ] User clicks "Train New Model"
2. [ ] Config modal appears
3. [ ] User selects model and epochs
4. [ ] Training starts on Modal
5. [ ] Live logs stream to dashboard
6. [ ] Metrics update in real-time
7. [ ] Training completes successfully
8. [ ] Model appears in models list
9. [ ] Weights downloadable

**Test Case 4: Collaboration**
1. [ ] User A starts annotating video 1
2. [ ] User B tries to annotate video 1 (should be locked)
3. [ ] User B annotates video 2 instead
4. [ ] Both users see each other's progress
5. [ ] User A finishes, lock releases
6. [ ] User B can now annotate video 1

**Test Case 5: Error Handling**
1. [ ] Disconnect network during video download (should retry)
2. [ ] Stop training mid-run (should cancel gracefully)
3. [ ] Try to upload invalid annotation format (should reject)
4. [ ] Exceed video size limit (should reject)
5. [ ] Supabase goes down (should show error message)

#### Success Criteria
- All test cases pass without manual intervention
- Error handling is graceful
- User experience is smooth

#### Documentation Output
- Create detailed test report: `docs/TEST_REPORT.md`
- Document any issues found
- Create regression test suite

**Documentation Output:** `docs/checkpoints/7.1-end-to-end-test.md`

---

## Documentation Standards

### For Each Checkpoint

Create a markdown file: `docs/checkpoints/X.Y-name.md`

**Template:**

```markdown
# Checkpoint X.Y: [Name]

**Date:** YYYY-MM-DD
**Status:** ✅ Passed / ❌ Failed
**Time Spent:** X hours

## Objective
[What we're building in this checkpoint]

## Implementation Notes
[Key decisions made, challenges faced]

## Test Results
- [ ] Test 1: Description - ✅ Passed
- [ ] Test 2: Description - ✅ Passed
- [ ] Test 3: Description - ❌ Failed

## Issues Encountered
1. **Issue:** [Description]
   **Solution:** [How it was resolved]

2. **Issue:** [Description]
   **Solution:** [Still investigating]

## Learnings
- [Key insight #1]
- [Key insight #2]

## Next Steps
- [What needs to be done before next checkpoint]

## Rollback Instructions
[If this checkpoint needs to be undone]

## Related Files
- `path/to/file.py`
- `path/to/test.py`

## Git Commit
Commit hash: [abc123]
Commit message: [...]
```

---

## Risk Mitigation

### High-Risk Steps
1. **Protocol Handler Registration (3.1)**
   - Test on VM first
   - Create system backup
   - Document manual uninstall

2. **Full Training Pipeline (4.4)**
   - Start with 5 videos, not 73
   - Monitor costs closely
   - Set Modal spending limit

3. **End-to-End Testing (7.1)**
   - Use test/staging environment
   - Don't test on production data
   - Have rollback plan ready

### General Safety Practices
- **Git commit after each checkpoint**
- **Tag releases:** `git tag v0.1-checkpoint-X.Y`
- **Keep notes:** Document everything in checkpoint files
- **Test incrementally:** Never skip checkpoints
- **Monitor costs:** Check Modal/Supabase billing daily
- **Backup data:** Export Supabase database weekly

---

## Progress Tracking

### Checkpoint Status

Update this table as you complete checkpoints:

| Phase | Checkpoint | Status | Date | Time | Notes |
|-------|-----------|--------|------|------|-------|
| 0.1 | Supabase Setup | ⏳ Pending | - | - | - |
| 0.2 | Modal Setup | ⏳ Pending | - | - | - |
| 0.3 | Dev Environment | ⏳ Pending | - | - | - |
| 1.1 | FastAPI Basic | ⏳ Pending | - | - | - |
| 1.2 | Video Endpoints | ⏳ Pending | - | - | - |
| ... | ... | ... | ... | ... | ... |

**Legend:**
- ⏳ Pending
- 🔄 In Progress
- ✅ Passed
- ⚠️ Passed with Issues
- ❌ Failed
- 🔁 Needs Retry

---

## Cost Tracking

Track costs for each phase:

| Phase | Service | Estimated | Actual | Notes |
|-------|---------|-----------|--------|-------|
| 0 | Supabase | $0 | $0 | Free tier |
| 4 | Modal (test training) | $0.50 | - | T4 GPU, 5 epochs |
| 4 | Modal (full training) | $3-5 | - | A100, 100 epochs |

**Total Budget:** $50
**Total Spent:** $0

---

## Weekly Schedule

### Week 1: Foundation & Backend
- Day 1: Phase 0 (Setup)
- Day 2-3: Phase 1.1-1.3 (Basic API)
- Day 4-5: Phase 1.4-1.5 (Locking & Annotations)

### Week 2: Frontend & Desktop
- Day 1-2: Phase 2.1-2.3 (React UI)
- Day 3: Phase 2.4 (Real-time)
- Day 4-5: Phase 3.1-3.2 (Protocol handler)

### Week 3: Desktop & Training
- Day 1-2: Phase 3.3-3.4 (Video download, browser integration)
- Day 3-4: Phase 4.1-4.2 (Modal training)
- Day 5: Phase 4.3 (Log streaming)

### Week 4: Training Pipeline
- Day 1-3: Phase 4.4 (Full training)
- Day 4: Phase 5.1 (Training UI)
- Day 5: Phase 5.2 (Training dashboard)

### Week 5: Polish & Testing
- Day 1: Phase 6.1 (Model management)
- Day 2-3: Phase 7.1 (End-to-end testing)
- Day 4: Bug fixes
- Day 5: Documentation & deployment prep

---

## Appendix: Test Data

### Sample Videos
- Keep 3-5 short videos (<30s) for testing
- Use different resolutions
- Include edge cases (dark, blurry, etc.)

### Sample Annotations
- Create 2-3 fully annotated test videos
- Include various species
- Test with 0 detections, 1 detection, 100+ detections

### Test Users
- Create 2-3 test accounts
- Use for collaboration testing
- Different permission levels

---

**This is a living document. Update after each checkpoint!**

---

**End of Implementation Plan**
