# FileGuard — File Tampering Detection Dashboard

A beginner-friendly Information Security mini project that detects file-content changes by comparing SHA-256 hashes.

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows
1. Extract the ZIP and open the `FileGuard` folder in VS Code.
2. Open Terminal > New Terminal.
3. (Recommended) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
4. Install Flask:
   ```powershell
   pip install -r requirements.txt
   ```
5. Run the application:
   ```powershell
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Run on macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then visit http://127.0.0.1:5000.

## Demonstrate tampering
1. Create `demo.txt` containing `Original trusted content`.
2. Register it in FileGuard.
3. Verify the unchanged file; result should be **UNCHANGED**.
4. Edit the file to say `Modified content` and save it.
5. Verify it again with the same filename; result should be **MODIFIED**.

The app hashes uploaded bytes and stores only the baseline metadata/hash, not the uploaded file contents. Baselines are stored in `baselines.json`, created automatically on first registration.

## Files
- `app.py` — Flask routes, hashing, baseline storage
- `templates/index.html` — dashboard
- `templates/result.html` — result screen
- `static/style.css` — styling
- `requirements.txt` — Python dependency

## Limitations and security notes
- This is a local educational demo, not an automatic folder-monitoring or production service.
- Baselines are stored in a local JSON file. If an attacker can alter both a file and its baseline, this simple version may not detect tampering. A production design would protect or sign the baseline store.
- A mismatch means the file differs from its registered version; it does not prove malicious activity.
- Keep the Flask development server local and do not expose it to the public internet.
