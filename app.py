from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import hashlib, json

app = Flask(__name__)
app.secret_key = "local-demo-change-this-key"
ROOT = Path(__file__).resolve().parent
STORE = ROOT / "baselines.json"
MAX_SIZE = 10 * 1024 * 1024

def load_baselines():
    if not STORE.exists():
        return {}
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def save_baselines(data):
    STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def size_label(n):
    if n < 1024: return f"{n} B"
    if n < 1024 * 1024: return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.2f} MB"

@app.route("/")
def index():
    records = sorted(load_baselines().values(), key=lambda x: x.get("registered_at", ""), reverse=True)
    return render_template("index.html", records=records, total_files=len(records))

def read_upload():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        flash("Choose a file first.", "error")
        return None, None, None
    filename = secure_filename(uploaded.filename)
    if not filename:
        flash("Please rename this file and try again.", "error")
        return None, None, None
    content = uploaded.read(MAX_SIZE + 1)
    if len(content) > MAX_SIZE:
        flash("File is too large. Maximum size is 10 MB.", "error")
        return None, None, None
    return filename, content, sha256(content)

@app.route("/register", methods=["POST"])
def register():
    filename, content, digest = read_upload()
    if filename is None:
        return redirect(url_for("index"))
    data = load_baselines()
    data[filename] = {
        "filename": filename,
        "sha256": digest,
        "size_label": size_label(len(content)),
        "registered_at": datetime.now().astimezone().isoformat(timespec="seconds")
    }
    save_baselines(data)
    flash(f"Trusted baseline registered for {filename}.", "success")
    return redirect(url_for("index"))

@app.route("/verify", methods=["POST"])
def verify():
    filename, content, current_hash = read_upload()
    if filename is None:
        return redirect(url_for("index"))
    baseline = load_baselines().get(filename)
    if baseline is None:
        result = {"filename": filename, "status": "NOT REGISTERED", "kind": "unknown",
                  "current_hash": current_hash, "baseline_hash": None,
                  "message": "No trusted baseline exists for this filename. Register a known-good original first."}
    elif current_hash == baseline["sha256"]:
        result = {"filename": filename, "status": "UNCHANGED", "kind": "safe",
                  "current_hash": current_hash, "baseline_hash": baseline["sha256"],
                  "message": "The current hash matches the saved baseline. File contents appear unchanged."}
    else:
        result = {"filename": filename, "status": "MODIFIED", "kind": "danger",
                  "current_hash": current_hash, "baseline_hash": baseline["sha256"],
                  "message": "The hashes differ. The file changed or is not the same trusted version."}
    return render_template("result.html", result=result)

@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    filename = secure_filename(filename)
    data = load_baselines()
    if filename in data:
        del data[filename]
        save_baselines(data)
        flash(f"Baseline removed for {filename}.", "success")
    else:
        flash("Baseline not found.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Local classroom demo only. Do not expose the debug server to the internet.
    app.run(debug=True)
