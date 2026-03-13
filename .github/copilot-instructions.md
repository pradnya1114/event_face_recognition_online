# AI Coding Agent Instructions for Event Face Recognition Online

## Project Overview
**Event Face Recognition Online** is a Flask-based web application for real-time facial recognition at events. It enables pre-registration of attendees with face encodings and live face scanning to identify arrivals.

### Core Architecture
- **Backend**: Flask server with SQLite database (`pre_registered/database.db`)
- **Frontend**: HTML/JavaScript with real-time camera feed
- **AI Engine**: `face_recognition` library (leveraging dlib) for facial encoding/matching
- **Data Pipeline**: Photos → Face encoding (pickle-serialized numpy arrays) → SQLite BLOB storage → Distance-based matching

### Key Components

| Component | Role | Location |
|-----------|------|----------|
| **app.py** | Main Flask server (pre-registration & scanning) | Root |
| **run_online.py** | Duplicate entry point for Render deployment | Root |
| **pre_register.html** | Registration form with camera/upload UI | `templates/` |
| **event.html** | Real-time batch scanning interface | `templates/` |
| **database.py** | (Implicit) SQLite schema: users table with face_encoding BLOB | `pre_registered/database.db` |

## Critical Developer Workflows

### Local Development
```bash
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```
Navigate to `/preregister` to register attendees, `/event` to scan.

### Deployment Notes
- **Procfile**: Runs `gunicorn app:app` on Render
- **Python 3.10.13** specified in `runtime.txt`
- ⚠️ **Filesystem Volatility**: Free cloud hosts discard uploaded photos/DB on redeploy. Consider migrating to PostgreSQL + cloud storage for production.

### Database Maintenance
- `scan.py`: Validates and removes corrupted face encodings from database
- `face_test.py`: Quick debugging tool to verify face detection pipeline

## Project-Specific Patterns & Conventions

### Face Recognition Workflow
1. **Encoding Generation** (Registration)
   - Load image → Extract first detected face → Generate 128D numpy array (face_encoding)
   - Serialize with pickle for storage in SQLite BLOB
   - Fallback: Delete photo if no face detected (validates input early)

2. **Matching Logic** (Scanning)
   - Capture frame → Extract face → Compare against all encodings via `face_recognition.face_distance()`
   - Threshold: **0.6** (hardcoded; values <0.6 = match)
   - Strategy: Select **best match** (lowest distance) to avoid duplicates in batch
   - Return user metadata only if match found; prevents false positives in real-time scanning

### Data Storage Patterns
- **Dual Logging**: SQLite (primary) + CSV (`pre_registered/users.csv`) for audit trail
- **Photo Paths**: Stored as relative paths (`pre_registered/photos/name_phone.png`), served via `send_from_directory()`
- **Face Encodings**: Pickle-serialized NumPy arrays in BLOB field; always validate deserialization before use

### Frontend Conventions
- **Camera Access**: Uses `navigator.mediaDevices.getUserMedia()` with fallback file upload
- **Image Transmission**: Base64-encoded PNG frames sent to `/scan_face` endpoint
- **Batch Management**: Client-side attendee cards accumulate in right panel; no persistence between page reloads
- **Error Handling**: User-friendly messages (e.g., "No face detected") returned via JSON

## Integration Points & Dependencies

### External Libraries (Critical)
- **face_recognition 1.3.0** (wraps dlib; slow on CPU, requires wheel build for Windows ARM64)
- **Flask** (routing, file serving)
- **SQLite3** (stdlib; no external dependency)
- **NumPy** (image arrays for face_recognition)
- **Pillow** (image format conversion)

### Image Format Flow
- User uploads JPEG/PNG → PIL converts to RGB → NumPy array → face_recognition processes → Results back to JSON

### Path Management
- All paths relative to `BASE_DIR` (project root)
- Key folders created on startup: `pre_registered/photos`, `pre_registered/` (for DB)
- Cross-platform handling: `os.path.join()` used everywhere; frontend converts `\` to `/` for web URLs

## Common Pitfalls & Solutions

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| "No face detected" during registration | Image too small, face obscured, or poor lighting | Retry with clear frontal shot |
| Matching fails after DB operations | Corrupted pickle serialization | Run `scan.py` to clean invalid encodings |
| Photos disappear on cloud redeploy | Ephemeral filesystem | Migrate to cloud storage (S3, GCS) + persistent DB |
| False positives in live scanning | Threshold too loose or lighting changes | Consider lowering 0.6 threshold or re-encode in similar lighting |

## File Organization Best Practices
- **Route logic** stays in `app.py` (single Flask file for simplicity)
- **Utility functions** (db operations, face encoding) could be extracted to `utils.py` if codebase grows
- **HTML templates** cleanly separated; client-side logic embedded in `<script>` tags (acceptable for small project)
- **CSV + SQLite dual logging** useful for manual audit; don't remove either without updating dependents

## Key Commands for Maintenance
- **Health check**: `python face_test.py` (verify face detection works)
- **DB validation**: `python scan.py` (remove corrupted records before deployment)
- **Local testing**: Visit `/preregister` → upload test photo → navigate to `/event` → capture frame

---

**Last Updated**: November 2025  
**Python Version**: 3.10.13  
**Framework**: Flask (lightweight routing)
