# 🌊 Ocean-ML

**Collaborative Fish Detection & Annotation Platform**

A modern web-based platform for marine biologists to annotate fish detection videos, train YOLO models on cloud GPUs, and run inference—all without touching code.

---

## ✨ Features

- **🎨 Web Dashboard:** Manage videos, track progress, monitor training runs
- **🖥️ Desktop Annotation Tool:** Smooth video scrubbing with PyQt5 (auto-launches from browser)
- **☁️ Cloud Training:** Train YOLO models on Modal.com GPUs (A100/T4)
- **🤝 Real-time Collaboration:** Multiple users can annotate different videos simultaneously
- **📊 Model Management:** Compare models, track performance, download weights
- **💰 Cost Tracking:** Monitor GPU usage and training costs

---

## 🏗️ Architecture

```
Web Browser (React)
    ↓
FastAPI Backend
    ↓
Supabase (Database + Storage)
    ↓
Modal.com (GPU Training/Inference)
```

**Desktop App:** PyQt5 application auto-launched via protocol handler (`oceanml://`)

---

## 📁 Project Structure

```
Ocean-ML/
├── backend/              # FastAPI REST API
│   ├── main.py
│   ├── routers/
│   ├── services/
│   └── models/
├── frontend/             # React + TypeScript dashboard
│   ├── src/
│   ├── public/
│   └── package.json
├── desktop/              # PyQt5 annotation tool
│   ├── PYQT5_UI.py
│   ├── ui/
│   ├── services/
│   └── build_installer.py
├── modal_functions/      # Modal.com GPU functions
│   ├── training.py
│   └── inference.py
├── scripts/              # Utility scripts
│   └── upload_videos.py
├── docs/                 # Documentation
│   ├── setup.md
│   ├── user-guide.md
│   └── api-docs.md
└── SPEC.md              # Complete specification
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account
- Modal.com account

### 1. Clone Repository

```bash
git clone https://github.com/christianabulhawa/Ocean-ML.git
cd Ocean-ML
```

### 2. Set Up Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase credentials
python main.py
```

Backend runs at `http://localhost:8000`

### 3. Set Up Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your Supabase credentials
npm run dev
```

Frontend runs at `http://localhost:3000`

### 4. Build Desktop App

```bash
cd desktop
pip install -r requirements.txt
python build_installer.py
```

Installer created at `dist/OceanML-Setup.exe`

---

## 📖 User Guide

### For Marine Biologists (Non-technical)

1. **Get Access:**
   - Receive invitation email with link
   - Click link → Sign in with Google
   - Download desktop app (one-time, 5 MB)

2. **Annotate Videos:**
   - Open dashboard in browser
   - Click "Annotate" on any video
   - Desktop app auto-launches
   - Draw boxes around fish
   - Click "Save" when done

3. **Train Models:**
   - Click "Train New Model"
   - Choose model type (Fast/Balanced/Accurate)
   - Click "Start Training"
   - Watch live progress in browser

4. **That's it!** No terminal, no code, no configuration.

---

## 🔧 For Developers

### Backend API

See [API Documentation](docs/api-docs.md) for full endpoint reference.

**Key Endpoints:**
- `GET /api/videos` - List all videos
- `POST /api/annotate/{video_id}` - Start annotation session
- `POST /api/train` - Trigger training on Modal
- `GET /api/models` - List trained models

### Database Schema

See [SPEC.md](SPEC.md) for complete database schema.

**Key Tables:**
- `videos` - Video metadata and annotation status
- `annotations` - Annotation metadata (files in Storage)
- `training_runs` - Training job history
- `inference_runs` - Inference job history

### Desktop Protocol Handler

The desktop app registers `oceanml://` protocol handler.

**Example:**
```
oceanml://annotate?video=123&token=eyJ...
```

Launches desktop app with video ID and auth token.

---

## 🌩️ Cloud Infrastructure

### Supabase (Database + Storage)

- **Database:** PostgreSQL with Row Level Security
- **Storage:** Video files, annotations, model weights
- **Auth:** User authentication (Google/email)
- **Realtime:** WebSocket subscriptions for live updates

### Modal.com (GPU Compute)

- **Training:** A100/A10G GPUs for YOLO training
- **Inference:** T4 GPUs for batch inference
- **Billing:** Pay-per-second usage
- **Cost:** ~$2-5 per training run, ~$0.02 per inference

---

## 💵 Cost Breakdown

**Monthly Fixed Costs:**
- Supabase Pro: $25/month (100GB storage, 250GB bandwidth)
- Fly.io Hosting: $0-5/month (free tier may suffice)

**Variable Costs:**
- Modal training: $2-5 per run
- Modal inference: $0.02 per video

**Total:** ~$30-50/month for active development

---

## 📊 Development Status

**Phase 1: Core Functionality** (In Progress)
- [ ] Supabase setup
- [ ] FastAPI backend
- [ ] React dashboard
- [ ] Desktop app with protocol handler
- [ ] Basic annotation workflow

**Phase 2: Cloud Training** (Planned)
- [ ] Modal training integration
- [ ] Live log streaming
- [ ] Model comparison UI

**Phase 3: Inference & Polish** (Planned)
- [ ] Modal inference integration
- [ ] Result visualization
- [ ] Cost tracking

**Phase 4: Collaboration** (Planned)
- [ ] Real-time locking
- [ ] Activity timeline
- [ ] User notifications

---

## 🤝 Contributing

This is a research project for marine biology applications. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 📞 Contact

**Project Lead:** Christian Abulhawa

**Issues:** [GitHub Issues](https://github.com/christianabulhawa/Ocean-ML/issues)

**Documentation:** [Full Specification](SPEC.md)

---

## 🙏 Acknowledgments

- Built with [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- Cloud compute by [Modal.com](https://modal.com)
- Backend by [Supabase](https://supabase.com)
- UI framework by [React](https://react.dev)

---

**Status:** 🚧 In Development | **Version:** 0.1.0 | **Last Updated:** 2025-11-19
