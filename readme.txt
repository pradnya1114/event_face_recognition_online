====================================================
EVENT FACE SCAN SYSTEM — README
====================================================

Summary:
---------
This project is a browser-based face scanning system for event badge printing.
It scans attendee faces, matches them against a pre-registered database, and
automatically prints a branded badge. If the system fails to detect or match
a face, the operator can manually enter the attendee’s phone number as a fallback.

----------------------------------------------------
1. FEATURES
----------------------------------------------------
- Real-time face recognition via webcam or mobile camera.
- Automatic badge generation (photo, name, organization).
- Manual fallback: enter phone number if face not recognized.
- Batch registration and batch printing support.
- Clean branding (font, color, layout control).
- Works remotely via HTTPS using ngrok.
- Uses Python + Flask on backend and HTML/JS frontend.

----------------------------------------------------
2. QUICK START (LOCAL DEVELOPMENT)
----------------------------------------------------
1. Requirements:
   - Python 3.8+
   - pip
   - virtualenv (recommended)
   - ngrok (for external access)

2. Installation:
   > python -m venv venv
   > venv\Scripts\activate          (Windows)
   > pip install -r requirements.txt

3. Run Flask:
   > python app.py
   or
   > python run_online.py

   Flask will start on:
   http://127.0.0.1:5000

4. Test via browser:
   http://localhost:5000/preregister

----------------------------------------------------
3. ACCESS FROM ANY NETWORK (NGROK)
----------------------------------------------------
1. Download ngrok from https://ngrok.com/download
2. Add your auth token (from ngrok dashboard):
   > ngrok config add-authtoken YOUR_REAL_TOKEN_HERE
3. Run:
   > ngrok http 5000
4. Copy the HTTPS link shown (example):
   https://abcd-1234.ngrok-free.app
5. Open this link on your phone (mobile data or Wi-Fi).

----------------------------------------------------
4. IF FACE NOT SCANNED — PHONE NUMBER FALLBACK
----------------------------------------------------
When a scan fails to detect or match a face:
1. The operator will see a “Face Not Detected” prompt.
2. Enter the attendee’s phone number in the input box.
3. Click “Lookup”.
   - If found → badge is displayed.
   - If not found → system shows a registration form pre-filled
     with that phone number.
4. Once registered → badge is generated → ready for print.

Backend route (example):
   /lookup_by_phone?phone=+919900000000

----------------------------------------------------
5. BRANDING GUIDELINES
----------------------------------------------------
- Badge size: 256 x 369 px
- Font: Poppins (bold for Name, semibold for Org)
- Fallback font: Arial, Helvetica, sans-serif
- Colors:
    Text color: #FFFFFF (white)
    Accent (edit indicator): #0096FF
- Layout default positions:
    Photo: x=65, y=93
    Name:  x=24, y=227
    Org:   x=26, y=268
- Press “P” to unlock position edit mode (blue dashed outline).
  Move elements, press “P” again to lock and save.

----------------------------------------------------
6. PRINTING RECOMMENDATIONS
----------------------------------------------------
- Recommended resolution: 300 DPI
- Print format: PNG or PDF (preferred for bulk)
- Suggested badge export size: 768 x 1107 px
- Use “Print Badge” button for direct printing.
- For mass print: generate PDFs via /print_batch (optional).

Batch size recommendation: 20–50 badges per print job.

----------------------------------------------------
7. DATABASE & STORAGE
----------------------------------------------------
- Database: SQLite (pre_registered/database.db)
- Photos folder: pre_registered/photos/
- CSV record file: pre_registered/users.csv
- Table fields:
    id, name, organization, phone, email,
    photo_path, face_encoding

----------------------------------------------------
8. FACE MATCHING SETTINGS
----------------------------------------------------
- Default threshold: 0.65
- Adjust for glasses or lighting:
    0.7 = more lenient (fewer false negatives)
    0.5 = stricter (fewer false positives)
- Example environment variable:
    set THRESHOLD=0.7

----------------------------------------------------
9. COLORS & PRINT CLARITY
----------------------------------------------------
- Background: light or branded image
- Text: white or dark contrasting color
- Avoid overly dark photos; ensure bright, clear faces.
- For print: check printer color calibration (CMYK if possible).

----------------------------------------------------
10. BATCH REGISTRATION (CSV IMPORT)
----------------------------------------------------
CSV format (users.csv):
---------------------------------
Name,Organization,Phone,Email,PhotoPath
Alice Smith,ACME,+919900000000,alice@acme.com,photos/alice.png
---------------------------------

Import flow:
  - Upload CSV to /batch_upload (optional future endpoint)
  - Each record generates photo encoding
  - Database updated automatically

----------------------------------------------------
11. TROUBLESHOOTING
----------------------------------------------------
If face not recognized:
  - Ensure photo/lighting is clear
  - Adjust threshold to 0.7
  - Try registering again (clean face image)
If using glasses:
  - Avoid glare or reflections
If camera fails:
  - Use HTTPS (ngrok) or localhost for permissions
  - Clear browser camera permissions and reload

----------------------------------------------------
12. SECURITY NOTES
----------------------------------------------------
- Use HTTPS for all live camera pages
- Enable CORS only for trusted origins
- Protect admin routes with password or token
- Do not expose ngrok token publicly
- Rotate/revoke any leaked tokens immediately

----------------------------------------------------
13. RECOMMENDED COLORS FOR CLEAR PRINTS
----------------------------------------------------
Primary Background: #24305E (deep blue)
Text / Foreground:  #FFFFFF
Accent Color:       #0096FF
Alternate Brand:    #F5F5F5 (light gray)
These provide high contrast for both on-screen and printed badges.

----------------------------------------------------
14. CONTACT / CREDITS
----------------------------------------------------
Developed by: Mint Labs
Contact: info@mintlabs.in
Project Lead: Pradnya Jamadar
Version: 1.0.0
Python: 3.8+
License: Internal event deployment only

====================================================
END OF README
====================================================
