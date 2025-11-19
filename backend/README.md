# Backend - FastAPI REST API

## Overview

FastAPI backend that provides:
- Video library management
- Annotation coordination
- Modal.com GPU job orchestration
- Real-time WebSocket updates
- Supabase integration

## Structure

```
backend/
├── main.py                     # FastAPI application entry point
├── routers/
│   ├── videos.py              # Video CRUD endpoints
│   ├── annotations.py         # Annotation management
│   ├── training.py            # Training job orchestration
│   ├── inference.py           # Inference job orchestration
│   └── desktop.py             # Desktop app endpoints
├── services/
│   ├── supabase_client.py    # Supabase connection
│   ├── modal_client.py       # Modal job triggering
│   └── video_lock.py         # Video locking mechanism
├── models/
│   ├── video.py              # Pydantic models
│   ├── annotation.py
│   └── training.py
├── requirements.txt
└── .env.example
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key
- `MODAL_TOKEN` - Modal.com API token

### 3. Run Development Server

```bash
python main.py
```

Server runs at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Adding New Endpoints

1. Create router in `routers/`
2. Define Pydantic models in `models/`
3. Register router in `main.py`

### Testing

```bash
pytest tests/
```

## Deployment

See [docs/deployment.md](../docs/deployment.md) for deployment instructions.
