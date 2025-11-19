# Getting Started with Ocean-ML

This guide will help you set up Ocean-ML for the first time.

---

## For Users (Non-technical)

If you're a marine biologist who just wants to annotate videos, you only need:

### 1. Get Access
- Wait for invitation email from project administrator
- Click the link in the email

### 2. Sign In
- Click "Sign in with Google" (or use email)
- Grant permissions when prompted

### 3. Install Desktop App
- You'll see a banner: "Install desktop app to annotate videos"
- Click "Download for Windows" or "Download for Mac"
- Run the installer (5 MB download)
- That's it!

### 4. Start Annotating
- Browse videos in the dashboard
- Click "Annotate" on any video
- Desktop app will open automatically
- Draw boxes around fish
- Click "Save" when done

**You never need to touch code, terminal, or configuration files.**

---

## For Developers

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Git**
- **Supabase account** (free tier works)
- **Modal.com account** (pay-as-you-go)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Ocean-ML.git
cd Ocean-ML
```

### 2. Set Up Supabase

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project URL and anon key
3. In Supabase dashboard:
   - Go to **SQL Editor**
   - Run the schema from `docs/database-schema.sql` (you'll need to create this)
   - Go to **Storage**
   - Create buckets: `videos`, `annotations`, `models`, `inference`
   - Set appropriate policies (public read, authenticated write)

### 3. Set Up Modal.com

1. Go to [modal.com](https://modal.com) and sign up
2. Install Modal CLI:
   ```bash
   pip install modal
   modal setup
   ```
3. Create a new Modal app (this will generate a token)
4. Note your Modal token

### 4. Configure Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
MODAL_TOKEN=your-modal-token
```

Run the backend:
```bash
python main.py
```

Backend should be running at `http://localhost:8000`

### 5. Configure Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `.env`:
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
```

Run the frontend:
```bash
npm run dev
```

Frontend should be running at `http://localhost:3000`

### 6. Build Desktop App

```bash
cd desktop
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with same credentials.

Run in development:
```bash
python PYQT5_UI.py
```

Build installer:
```bash
python build_installer.py
```

---

## Testing the Full Workflow

### 1. Upload a Test Video

Using the backend API or Supabase dashboard:
1. Upload a video file to Supabase Storage (`videos` bucket)
2. Add an entry to the `videos` table

Or use the upload script:
```bash
python scripts/upload_videos.py --video path/to/video.mp4
```

### 2. Annotate Video

1. Open `http://localhost:3000` in browser
2. Sign in with your Supabase account
3. Click "Annotate" on the test video
4. Desktop app should launch (if installed)
5. Draw some bounding boxes
6. Click "Save"
7. Verify annotations appear in Supabase

### 3. Train Model

1. In dashboard, click "Train New Model"
2. Select model type and parameters
3. Click "Start Training"
4. Watch live logs as Modal trains the model
5. Wait for completion (will take a few minutes)

### 4. Run Inference

1. Upload a new video
2. Click "Run Inference"
3. Select trained model
4. Wait for results
5. View detections

---

## Troubleshooting

### Desktop App Doesn't Launch

**Symptom:** Clicking "Annotate" does nothing

**Solution:**
1. Check if desktop app is installed
2. Try manually opening: `oceanml://annotate?video=1&token=test`
3. On Windows: Check registry for `oceanml://` protocol handler
4. On Mac: Check `/Applications/OceanML.app` exists

### Backend Connection Error

**Symptom:** Frontend shows "Cannot connect to backend"

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/.env`
3. Check `VITE_API_URL` in `frontend/.env`

### Supabase Auth Error

**Symptom:** "Invalid JWT" or "Unauthorized"

**Solution:**
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Check Row Level Security policies in Supabase
3. Try signing out and back in

### Modal Training Fails

**Symptom:** Training shows "Failed" status

**Solution:**
1. Check Modal token is valid: `modal token set --token-id xxx --token-secret yyy`
2. Check Modal logs: `modal app logs ocean-ml-training`
3. Verify annotations are in correct format

---

## Next Steps

- Read [SPEC.md](../SPEC.md) for complete system architecture
- See [API Documentation](api-docs.md) for backend endpoints
- Check [User Guide](user-guide.md) for detailed feature documentation
- Join discussions on GitHub Issues

---

## Need Help?

- **GitHub Issues:** https://github.com/yourusername/Ocean-ML/issues
- **Email:** your-email@example.com
- **Docs:** Full specification in [SPEC.md](../SPEC.md)

---

**Welcome to Ocean-ML! 🌊**
