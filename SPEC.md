# Ocean-ML Application Specification

**Version:** 1.0
**Date:** 2025-11-19
**Status:** Design Phase

---

## Executive Summary

Ocean-ML is a collaborative fish detection and annotation platform designed for marine biologists. It combines a web-based management dashboard with a high-performance desktop annotation tool, leveraging cloud infrastructure for GPU-accelerated training and inference.

### Key Goals
- **Simplicity:** Non-technical users can annotate videos with zero setup
- **Performance:** Smooth 1920×1080 video scrubbing for precise annotation
- **Collaboration:** Multiple users can work on different videos simultaneously
- **Cloud-Powered:** Training and inference run on cloud GPUs (Modal.com)
- **Accessibility:** Monitor progress and manage models from any device

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER EXPERIENCE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Web Browser (Any Device)                                  │
│  ├─ Dashboard: Video library, progress tracking            │
│  ├─ Training: Start/monitor ML training runs               │
│  ├─ Models: Compare performance, download weights          │
│  └─ History: Complete annotation & training timeline       │
│                                                             │
│  Desktop App (Windows/Mac) - Auto-launched                 │
│  ├─ Video annotation with smooth frame scrubbing           │
│  ├─ YOLO bounding box drawing                              │
│  └─ Automatic sync back to cloud                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FastAPI Backend (Local or Cloud-hosted)                   │
│  ├─ REST API for video library                             │
│  ├─ WebSocket for real-time updates                        │
│  ├─ Protocol handler for desktop app launch                │
│  └─ Job orchestration (Modal triggers)                     │
│                                                             │
│  Supabase (Cloud Database & Storage)                       │
│  ├─ PostgreSQL: metadata, annotations, users               │
│  ├─ Storage: videos, model weights, annotations            │
│  ├─ Auth: Google/email authentication                      │
│  └─ Real-time: WebSocket subscriptions                     │
│                                                             │
│  Modal.com (Cloud GPU Compute)                             │
│  ├─ YOLO training on A100/A10G GPUs                        │
│  ├─ Batch inference on T4 GPUs                             │
│  ├─ Pay-per-second billing                                 │
│  └─ Log streaming to dashboard                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## User Workflows

### 1. First-Time Setup (Marine Biologist)

**Onboarding Flow:**

1. User receives email with link: `https://ocean-ml.app`
2. Opens link → Sees landing page
3. Clicks "Sign in with Google"
4. After authentication, sees banner: "Install desktop app (one-time)"
5. Clicks "Download for Windows/Mac"
6. Downloads `OceanML-Setup.exe` (5-6 MB)
7. Runs installer → Installs in 30 seconds
8. Desktop app registered as `oceanml://` protocol handler
9. Ready to annotate!

**Technical Details:**
- Installer built with PyInstaller + NSIS (Windows) / DMG (Mac)
- Protocol handler registration in system registry
- No manual configuration required
- Auto-updates on launch

---

### 2. Daily Annotation Workflow

**User Experience:**

1. **Open dashboard:** `https://ocean-ml.app`
   - Already logged in (persistent session)
   - Sees video library with status indicators:
     - ✓ Annotated (green) with annotator name
     - ○ Not annotated (gray)
     - 🔵 In progress (blue) with current user

2. **Select video:** Click "Annotate" button
   - Dashboard checks: is someone else annotating this?
   - If available: triggers desktop app launch
   - If locked: shows "Sarah is currently working on this video"

3. **Desktop app auto-launches:**
   - Receives URL: `oceanml://annotate?video=3&token=eyJ...`
   - Shows download progress dialog
   - Downloads video from Supabase Storage to local cache
   - Loads annotation interface

4. **Annotate video:**
   - Smooth frame-by-frame scrubbing
   - Draw bounding boxes around fish
   - Select species from dropdown
   - Navigate with keyboard shortcuts
   - Progress auto-saved locally

5. **Save and close:**
   - Click "Save" button
   - Uploads annotations to Supabase
   - Updates database metadata
   - Desktop app closes automatically

6. **Dashboard updates in real-time:**
   - Video status changes to ✓ Annotated
   - Shows detection count and timestamp
   - Other users see update immediately (WebSocket)

---

### 3. Model Training Workflow

**User Experience:**

1. **Trigger training:** Click "Train New Model" in dashboard

2. **Configure training:**
   ```
   Model Selection:
   ○ Fast (YOLOv8n)       - $2, 20 mins, mAP ~0.85
   ● Balanced (YOLOv8s)   - $4, 30 mins, mAP ~0.89
   ○ Accurate (YOLOv8m)   - $8, 45 mins, mAP ~0.92

   Training Epochs: [100]
   Dataset: All 45 annotated videos

   Estimated cost: $4.20
   Estimated time: 30 minutes

   [Start Training]
   ```

3. **Monitor live progress:**
   - Dashboard shows real-time training metrics
   - Live log streaming from Modal
   - Epoch progress, loss curves, mAP scores
   - GPU time and cost accumulation
   - Can be monitored from any device (phone, tablet)

4. **Training completes:**
   - Notification: "Training complete! mAP: 0.89"
   - Model weights auto-saved to Supabase
   - Metadata recorded (accuracy, cost, timestamp)
   - Available for download or inference

---

### 4. Inference Workflow

**User Experience:**

1. **Upload new video:** Drag-and-drop or file picker
2. **Select model:** Choose from trained models
3. **Run inference:** Click "Analyze Video"
4. **Modal processes:**
   - Downloads video and model weights
   - Runs YOLO inference on T4 GPU
   - Uploads results (JSON + annotated video)
5. **View results:**
   - Detection count and confidence scores
   - Downloadable results
   - Playback with overlaid bounding boxes

---

## Technical Architecture

### Frontend (React + TypeScript)

**Tech Stack:**
- React 18 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Supabase Auth UI components
- React Query for data fetching
- WebSocket for real-time updates

**Key Components:**

```typescript
src/
├── components/
│   ├── VideoLibrary/
│   │   ├── VideoGrid.tsx          // Grid of video cards
│   │   ├── VideoCard.tsx          // Individual video with status
│   │   └── VideoFilters.tsx       // Filter by status/user
│   ├── Training/
│   │   ├── TrainingDashboard.tsx  // Active training runs
│   │   ├── TrainingConfig.tsx     // Model selection form
│   │   ├── LiveLogs.tsx           // Streaming logs from Modal
│   │   └── ModelComparison.tsx    // Compare model performance
│   ├── History/
│   │   ├── ActivityTimeline.tsx   // Chronological activity
│   │   └── UserStats.tsx          // Per-user statistics
│   └── Auth/
│       ├── LoginPage.tsx          // Landing page
│       └── DesktopAppBanner.tsx   // Install prompt
├── hooks/
│   ├── useRealtimeVideos.ts       // Subscribe to video updates
│   ├── useTrainingLogs.ts         // Stream training logs
│   └── useAuth.ts                 // Supabase authentication
├── lib/
│   ├── supabase.ts                // Supabase client
│   └── api.ts                     // FastAPI client
└── App.tsx
```

**Key Features:**
- Real-time updates via Supabase subscriptions
- Optimistic UI updates
- Desktop app detection and download prompts
- Protocol handler launching: `oceanml://annotate?video=X`

---

### Backend (FastAPI + Python)

**Tech Stack:**
- FastAPI for REST API
- WebSocket support for real-time logs
- Supabase Python client
- Modal Python SDK

**API Endpoints:**

```python
# Video Management
GET    /api/videos              # List all videos with metadata
GET    /api/videos/{id}         # Get specific video details
POST   /api/videos              # Upload new video
PUT    /api/videos/{id}         # Update metadata
DELETE /api/videos/{id}         # Delete video

# Annotation
POST   /api/annotate/{video_id} # Lock video and return download URL
POST   /api/annotations/complete # Upload annotations, unlock video
GET    /api/annotations/{video_id} # Get annotations for video

# Training
POST   /api/train               # Trigger Modal training job
GET    /api/train/{job_id}      # Get training status
GET    /api/train/{job_id}/logs # WebSocket: stream live logs
POST   /api/train/{job_id}/stop # Cancel training

# Inference
POST   /api/inference           # Run inference on video
GET    /api/inference/{job_id}  # Get inference status
GET    /api/inference/{job_id}/results # Download results

# Models
GET    /api/models              # List trained models
GET    /api/models/{id}/download # Download model weights
DELETE /api/models/{id}         # Delete model

# Desktop App
GET    /api/desktop-version     # Check for updates
GET    /downloads/OceanML-Setup-{platform}.exe # Download installer
```

**Project Structure:**

```python
backend/
├── main.py                      # FastAPI application
├── routers/
│   ├── videos.py               # Video endpoints
│   ├── annotations.py          # Annotation endpoints
│   ├── training.py             # Training orchestration
│   ├── inference.py            # Inference orchestration
│   └── desktop.py              # Desktop app endpoints
├── services/
│   ├── supabase_client.py     # Supabase connection
│   ├── modal_client.py        # Modal job triggering
│   └── video_lock.py          # Video locking mechanism
├── models/
│   ├── video.py               # Pydantic models
│   ├── annotation.py
│   └── training.py
└── requirements.txt
```

---

### Desktop App (PyQt5 + Python)

**Tech Stack:**
- PyQt5 for UI
- OpenCV for video processing
- Supabase Python client
- PyInstaller for packaging

**Key Features:**

1. **Protocol Handler:**
   - Receives: `oceanml://annotate?video=3&token=abc`
   - Parses video ID and auth token
   - Downloads video from Supabase

2. **Video Player:**
   - Smooth frame scrubbing (1920×1080 @ 30fps)
   - Keyboard shortcuts (←/→ for frames, Space for play/pause)
   - Timeline with annotation markers

3. **Annotation Tools:**
   - Click and drag to draw bounding boxes
   - Species dropdown (Tuna, Salmon, Bass, etc.)
   - Delete/edit existing boxes
   - Confidence scores (if from inference)

4. **Sync:**
   - Auto-save annotations locally (backup)
   - Upload to Supabase on "Save"
   - Update database metadata
   - Report completion to FastAPI

**Project Structure:**

```python
desktop/
├── PYQT5_UI.py                 # Main application entry
├── ui/
│   ├── main_window.py          # Main window layout
│   ├── video_player.py         # Video player widget
│   ├── annotation_canvas.py   # Drawing canvas overlay
│   └── toolbar.py              # Annotation tools
├── services/
│   ├── video_downloader.py    # Download with progress
│   ├── annotation_sync.py     # Upload annotations
│   └── protocol_handler.py    # Parse oceanml:// URLs
├── models/
│   └── annotation.py          # YOLO format annotation
├── requirements.txt
└── build_installer.py         # PyInstaller + NSIS script
```

**Installer:**
- PyInstaller bundles Python + dependencies into single .exe
- NSIS creates installer with protocol handler registration
- Auto-update check on launch
- Size: ~5-6 MB (compressed)

---

### Cloud Compute (Modal.com)

**Training Function:**

```python
# modal_training.py
import modal

app = modal.App("ocean-ml-training")

image = modal.Image.debian_slim().pip_install(
    "ultralytics",
    "supabase-py",
    "opencv-python"
)

@app.function(
    gpu="A100",           # or "A10G" for cheaper option
    timeout=3600,         # 1 hour max
    image=image,
    secrets=[modal.Secret.from_name("supabase")]
)
def train_yolo(dataset_id: str, model_type: str, epochs: int):
    """
    Train YOLO model on Modal GPU

    1. Download annotations from Supabase
    2. Download videos (or frames) from Supabase
    3. Prepare YOLO dataset format
    4. Train model with specified parameters
    5. Upload trained weights to Supabase
    6. Update database with results
    """

    from ultralytics import YOLO
    from supabase import create_client
    import os

    # Connect to Supabase
    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"]
    )

    # Download dataset
    print("📥 Downloading annotations...")
    annotations = download_annotations(supabase, dataset_id)

    print("📦 Preparing YOLO dataset...")
    prepare_dataset(annotations)

    # Train
    print(f"🚀 Training {model_type} for {epochs} epochs...")
    model = YOLO(f"{model_type}.pt")
    results = model.train(
        data="dataset.yaml",
        epochs=epochs,
        imgsz=640,
        device=0,
        verbose=True
    )

    # Upload results
    print("📤 Uploading trained model...")
    upload_model(supabase, results, dataset_id)

    return {
        "status": "success",
        "map50": results.results_dict['metrics/mAP50(B)'],
        "map50_95": results.results_dict['metrics/mAP50-95(B)']
    }
```

**Inference Function:**

```python
@app.function(
    gpu="T4",             # Cheaper GPU for inference
    timeout=600,          # 10 minutes
    image=image,
    secrets=[modal.Secret.from_name("supabase")]
)
def run_inference(video_id: str, model_id: str):
    """
    Run YOLO inference on video

    1. Download video from Supabase
    2. Download model weights from Supabase
    3. Run inference
    4. Upload results (JSON + annotated video)
    """

    from ultralytics import YOLO

    # Download assets
    video_path = download_video(video_id)
    model_path = download_model(model_id)

    # Run inference
    model = YOLO(model_path)
    results = model.predict(
        source=video_path,
        save=True,
        conf=0.5,
        iou=0.45
    )

    # Upload results
    upload_results(video_id, results)

    return {
        "detections": len(results),
        "confidence_avg": results.mean_confidence()
    }
```

---

### Database Schema (Supabase/PostgreSQL)

```sql
-- Users table (managed by Supabase Auth)
-- id, email, created_at automatically provided

-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,              -- Supabase Storage path
    thumbnail_path TEXT,                      -- Thumbnail image
    duration_seconds INTEGER,
    frame_count INTEGER,
    resolution TEXT,                          -- e.g., "1920x1080"
    fps FLOAT,
    file_size_bytes BIGINT,
    uploaded_by UUID REFERENCES auth.users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Annotation status
    annotated BOOLEAN DEFAULT FALSE,
    annotated_by UUID REFERENCES auth.users(id),
    annotated_at TIMESTAMP WITH TIME ZONE,
    annotation_storage_path TEXT,            -- Path to annotation file
    detection_count INTEGER DEFAULT 0,

    -- Locking mechanism (prevent concurrent annotation)
    locked_by UUID REFERENCES auth.users(id),
    locked_at TIMESTAMP WITH TIME ZONE,
    lock_expires_at TIMESTAMP WITH TIME ZONE
);

-- Annotations table (metadata, actual annotations in Storage)
CREATE TABLE annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    annotated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    frames_annotated INTEGER,
    detection_count INTEGER,
    species_counts JSONB,                    -- {"tuna": 5, "salmon": 3}
    annotation_format TEXT DEFAULT 'yolo',   -- 'yolo', 'coco', etc.
    storage_path TEXT NOT NULL,

    UNIQUE(video_id)                         -- One annotation per video
);

-- Training runs table
CREATE TABLE training_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_by UUID REFERENCES auth.users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Configuration
    model_type TEXT NOT NULL,                -- 'yolov8n', 'yolov8s', etc.
    epochs INTEGER NOT NULL,
    dataset_id TEXT NOT NULL,                -- Identifier for dataset version
    video_ids UUID[],                        -- Videos used in training

    -- Results
    status TEXT DEFAULT 'pending',           -- 'pending', 'running', 'completed', 'failed'
    modal_job_id TEXT,                       -- Modal call ID
    map50 FLOAT,
    map50_95 FLOAT,
    precision FLOAT,
    recall FLOAT,
    final_loss FLOAT,

    -- Resource usage
    gpu_type TEXT,                           -- 'A100', 'T4', etc.
    training_time_seconds INTEGER,
    cost_usd FLOAT,

    -- Model storage
    model_storage_path TEXT,                 -- Supabase Storage path to weights
    logs_storage_path TEXT                   -- Training logs
);

-- Inference runs table
CREATE TABLE inference_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_by UUID REFERENCES auth.users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    video_id UUID REFERENCES videos(id),
    model_id UUID REFERENCES training_runs(id),

    status TEXT DEFAULT 'pending',
    modal_job_id TEXT,

    detection_count INTEGER,
    average_confidence FLOAT,
    results_storage_path TEXT,               -- JSON results
    annotated_video_path TEXT,               -- Video with bboxes drawn

    processing_time_seconds INTEGER,
    cost_usd FLOAT
);

-- Activity log (for timeline view)
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),
    action_type TEXT NOT NULL,               -- 'video_uploaded', 'video_annotated', 'training_started', etc.
    resource_type TEXT,                      -- 'video', 'annotation', 'training_run', etc.
    resource_id UUID,
    metadata JSONB                           -- Additional details
);
```

**Indexes:**
```sql
CREATE INDEX idx_videos_annotated ON videos(annotated);
CREATE INDEX idx_videos_uploaded_by ON videos(uploaded_by);
CREATE INDEX idx_training_runs_status ON training_runs(status);
CREATE INDEX idx_activity_log_timestamp ON activity_log(timestamp DESC);
```

**Row Level Security (RLS):**
```sql
-- Users can only see videos they have access to
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view all videos"
    ON videos FOR SELECT
    USING (true);

CREATE POLICY "Users can insert videos"
    ON videos FOR INSERT
    WITH CHECK (auth.uid() = uploaded_by);

-- Similar policies for other tables...
```

---

## Storage Structure (Supabase Storage)

```
ocean-ml-storage/
├── videos/
│   ├── {video_id}.mp4                      -- Original videos
│   └── thumbnails/
│       └── {video_id}.jpg                  -- Video thumbnails
├── annotations/
│   └── {video_id}/
│       ├── annotations.txt                 -- YOLO format
│       └── metadata.json                   -- Additional info
├── models/
│   └── {training_run_id}/
│       ├── best.pt                         -- Trained weights
│       ├── last.pt                         -- Latest checkpoint
│       └── training_logs.txt               -- Full logs
└── inference/
    └── {inference_run_id}/
        ├── results.json                    -- Detection results
        └── annotated_video.mp4             -- Video with bboxes
```

---

## Deployment Strategy

### Option 1: Hybrid (Recommended for 1-2 users)

**Local Machine:**
- FastAPI backend: `http://localhost:8000`
- React frontend: `http://localhost:3000`
- Desktop app: Installed locally
- Videos: Keep locally (no upload to Supabase)

**Cloud:**
- Supabase: Annotations + metadata only
- Modal: Training + inference

**Pros:**
- Free (except Modal usage)
- Fast annotation (local videos)
- Simple setup

**Cons:**
- Must run FastAPI locally
- Can't access from other devices
- Videos not backed up

---

### Option 2: Fully Cloud-Hosted (Recommended for 3+ users)

**Cloud Hosting (Fly.io / Railway / DigitalOcean):**
- FastAPI + React: `https://ocean-ml.app`
- Publicly accessible
- Auto-scaling

**Supabase:**
- All videos uploaded
- All annotations and metadata
- User authentication

**Modal:**
- Training + inference

**Pros:**
- Access from anywhere
- True collaboration
- Professional setup
- Centralized backups

**Cons:**
- Hosting cost: ~$10-25/month
- Video upload required (one-time)
- Slower annotation (download videos)

**Deployment Steps:**

```bash
# 1. Deploy FastAPI + React to Fly.io
fly launch
fly deploy

# 2. Set environment variables
fly secrets set SUPABASE_URL=https://xxx.supabase.co
fly secrets set SUPABASE_KEY=xxx
fly secrets set MODAL_TOKEN=xxx

# 3. Upload videos to Supabase Storage
python scripts/upload_videos.py

# 4. Build and host desktop app installers
python desktop/build_installer.py
# Upload OceanML-Setup.exe to Fly.io static files
```

---

## Security Considerations

### Authentication
- Supabase Auth handles all user management
- JWT tokens for API authentication
- Row-level security (RLS) in database
- No passwords stored in application

### Desktop App Security
- Auth tokens passed via protocol handler (encrypted HTTPS)
- Tokens stored in OS keychain (not plaintext)
- Token refresh handled automatically
- Desktop app verifies token with backend before accessing data

### API Security
- All endpoints require authentication
- Rate limiting on sensitive endpoints
- Video locking prevents race conditions
- File uploads validated (type, size)

### Data Privacy
- Videos can contain sensitive marine research data
- Optional: Encrypt videos at rest in Supabase
- Optional: Add data retention policies
- Activity logging for audit trail

---

## Cost Estimates

### Infrastructure Costs

**Supabase (Cloud Database + Storage):**
- Free tier: 500MB storage, 2GB bandwidth/month
- Pro tier: $25/month (100GB storage, 250GB bandwidth)
- Estimated: **$25/month** for 73 videos + annotations

**Fly.io (Backend Hosting):**
- Free tier: 3 shared CPUs, 256MB RAM
- Paid tier: $5/month (1 dedicated CPU, 512MB RAM)
- Estimated: **$0-5/month** (free tier likely sufficient)

**Modal.com (GPU Compute):**
- A100 GPU: ~$3.50/hour
- T4 GPU: ~$0.60/hour
- Training run (30 mins on A100): **$1.75-4.00**
- Inference per video (2 mins on T4): **$0.02**

**Total Monthly:**
- **Fixed:** $25-30/month (Supabase + Fly.io)
- **Variable:** $5-20/month (Modal usage based on training frequency)
- **Total:** $30-50/month for active development

---

## Development Timeline

### Phase 1: Core Functionality (Week 1-2)
- [ ] Set up Supabase project (database + storage)
- [ ] Build FastAPI backend with video library endpoints
- [ ] Create React dashboard with video grid
- [ ] Implement Supabase authentication
- [ ] Package PyQt5 as desktop app with protocol handler
- [ ] Test full annotation workflow (web → desktop → sync)

**Deliverable:** Working annotation system with manual video upload

---

### Phase 2: Cloud Training (Week 3)
- [ ] Set up Modal.com account and secrets
- [ ] Create Modal training function
- [ ] Build training configuration UI
- [ ] Implement live log streaming (WebSocket)
- [ ] Add training history and model comparison
- [ ] Test full training workflow

**Deliverable:** Can train models from web dashboard

---

### Phase 3: Inference & Polish (Week 4)
- [ ] Create Modal inference function
- [ ] Build inference UI and results viewer
- [ ] Add batch inference support
- [ ] Implement cost tracking
- [ ] Polish UI/UX
- [ ] Add user documentation

**Deliverable:** Complete system with training + inference

---

### Phase 4: Collaboration Features (Week 5)
- [ ] Real-time video locking
- [ ] Activity timeline
- [ ] User statistics
- [ ] Notifications
- [ ] Desktop app auto-updates
- [ ] Admin panel

**Deliverable:** Production-ready collaborative platform

---

## Success Metrics

### User Experience
- ✅ Non-technical user can start annotating within 5 minutes
- ✅ Desktop app launches automatically when clicking "Annotate"
- ✅ Annotation saves successfully 100% of the time
- ✅ Dashboard updates in <2 seconds

### Performance
- ✅ Video scrubbing at 30fps without lag
- ✅ Desktop app launch in <10 seconds (including download)
- ✅ Training starts on Modal within 30 seconds
- ✅ Real-time log streaming with <1 second latency

### Collaboration
- ✅ Multiple users can annotate different videos simultaneously
- ✅ No annotation conflicts or data loss
- ✅ Activity visible to all users in real-time
- ✅ Clear indication of who is working on what

### Cost Efficiency
- ✅ Training cost <$5 per run
- ✅ Infrastructure cost <$50/month
- ✅ No wasted GPU hours
- ✅ Automatic cost tracking and reporting

---

## Future Enhancements

### Version 2.0
- **Active learning:** Suggest videos that need annotation
- **Model-assisted annotation:** Pre-fill boxes from previous model
- **Annotation quality control:** Flagging and review system
- **Export formats:** COCO, Pascal VOC, etc.
- **Integrations:** Slack notifications, webhooks

### Version 3.0
- **Video preprocessing:** Auto-extract interesting frames
- **Advanced analytics:** Species distribution, temporal patterns
- **Multi-modal:** Support images, not just videos
- **Mobile app:** Annotation on iPad
- **API access:** Programmatic access for researchers

---

## Reference: Legacy System

**Current Setup (PyQt5-only):**
- Desktop application: `Windows_DAT/PYQT5_UI.py`
- Local video files: 73 videos @ 25MB each
- Local annotation files: `.txt` format (YOLO)
- No collaboration
- No cloud storage
- No training integration

**Migration Path:**
- Keep current system as reference
- New system in `Ocean-ML/` repo
- Gradual migration of videos
- Import existing annotations to Supabase
- Parallel operation during development

---

## Appendix: Technology Stack Summary

### Frontend
- **Framework:** React 18 + TypeScript
- **Build:** Vite
- **Styling:** TailwindCSS
- **State:** React Query + Zustand
- **Auth:** Supabase Auth UI
- **Real-time:** Supabase Realtime / WebSocket

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (via Supabase)
- **Storage:** Supabase Storage
- **GPU Compute:** Modal.com
- **WebSocket:** FastAPI WebSocket support

### Desktop
- **UI:** PyQt5
- **Video:** OpenCV
- **Packaging:** PyInstaller + NSIS/DMG
- **Updates:** Custom update checker

### Infrastructure
- **Database:** Supabase PostgreSQL
- **Storage:** Supabase Storage (S3-compatible)
- **Auth:** Supabase Auth
- **Hosting:** Fly.io / Railway
- **GPU:** Modal.com
- **Monitoring:** Sentry (optional)

---

## Contact & Support

**Project Lead:** Christian Abulhawa
**Repository:** https://github.com/christianabulhawa/Ocean-ML
**Documentation:** https://ocean-ml.app/docs
**Issues:** https://github.com/christianabulhawa/Ocean-ML/issues

---

**End of Specification**
