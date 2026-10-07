import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, redirect, render_template, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
CORS(app)

DATA_DIR = Path(os.environ.get("DATA_DIR", "/var/data"))
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    DATA_DIR = Path("data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = DATA_DIR / "apks"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "launcher.db"

SEED_APPS = [
    ("Alphaplay", "com.chsz.efile.alphaplay", "a6.1.3", 23),
    ("BonitoTV", "com.android.bonito.stb", "1.0.3", 160),
    ("BRAS TV", "com.stream.bras", "5.2.9", 160),
    ("Cine Pipoca", "com.tv.client.droid.pipoca", "1.1.5", 160),
    ("Estrela Cinema", "com.tv.client.droid.estrela", "1.0.0", 160),
    ("EVO", "com.live.evo", "2.0.0", 6),
    ("HighTV", "com.tvfilmesseries.app", "2.9.21", 70),
    ("KORA TV", "com.iptv.kora", "5.2.9", 160),
    ("LUMA TV", "tv.lumatv.app", "2.4.6", 23),
    ("Lupi TV", "com.android.lupi.stb", "1.0.1", 160),
    ("Nexa TV", "com.apptv.android.nexabox", "1.2.2", 160),
    ("NEXOCINE", "com.tv.client.droid.nexocine", "1.1.7", 160),
    ("Nova Era (instável)", "com.newbox2p", "0.9.41", 160),
    ("NOVA TV", "com.mm.droid.livetv.otvstb", "1.2.5", 160),
    ("One TV", "com.brstudios.onetv", "1.0.50", 24),
    ("PotroPlay", "com.android.potroplay.stb", "1.0.4", 160),
    ("SolTV", "com.bx.soltv", "20260102", 160),
    ("STV", "com.bx.live.mobile", "8.18.18.mb", 160),
    ("Tudo TV", "com.szm.droid.tudotv.stb", "1.1.0", 160),
    ("UniCine", "com.vod.unicine.tvapp", "1.0.0", 160),
    ("UniTV", "com.global.unitviptv", "4.20.1", 70),
    ("UniTVnet", "com.unitvnet.tvod", "1.8.0", 70),
    ("YouCine", "com.world.youcinetv", "1.15.4", 70),
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            package TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL,
            url TEXT NOT NULL DEFAULT '',
            reclone_hours INTEGER NOT NULL DEFAULT 160,
            created_at TEXT NOT NULL
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM apps").fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        conn.executemany(
            "INSERT INTO apps (name, package, version, url, reclone_hours, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [(n, p, v, "", h, now) for n, p, v, h in SEED_APPS],
        )
    conn.commit()
    conn.close()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return fn(*args, **kwargs)
    return wrapper

def app_json(row):
    return {
        "name": row["name"],
        "package": row["package"],
        "version": row["version"],
        "url": row["url"],
        "recloneHours": row["reclone_hours"],
    }

init_db()

@app.get("/")
def index():
    return redirect("/admin")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/version")
def version():
    return jsonify({"version": os.environ.get("APP_VERSION", "1.0.6"), "url": os.environ.get("APP_UPDATE_URL", "")})

@app.get("/api/v2/store/apps")
@app.get("/api/store/apps")
def store_apps():
    conn = db()
    rows = conn.execute("SELECT * FROM apps ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify({"apps": [app_json(r) for r in rows]})

@app.post("/api/license/validate")
def validate_license():
    data = request.get_json(silent=True) or {}
    device_id = str(data.get("deviceId", "")).strip()
    pin = str(data.get("pin", "")).strip()
    if not device_id or not pin:
        return jsonify({"valid": False, "expiresAt": None}), 400
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    return jsonify({"valid": True, "expiresAt": expires.isoformat().replace("+00:00", "Z")})

@app.get("/api/uploads/apks/<path:filename>")
def apk_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.get("/admin/login")
def login():
    return render_template("login.html", error=None)

@app.post("/admin/login")
def login_post():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    expected_user = os.environ.get("ADMIN_USER", "admin")
    expected_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    expected_password = os.environ.get("ADMIN_PASSWORD", "")
    valid = username == expected_user and (
        (expected_hash and check_password_hash(expected_hash, password)) or
        (not expected_hash and expected_password and password == expected_password)
    )
    if valid:
        session["admin"] = True
        return redirect("/admin")
    return render_template("login.html", error="Usuário ou senha inválidos.")

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect("/admin/login")

@app.get("/admin")
@admin_required
def admin():
    conn = db()
    rows = conn.execute("SELECT * FROM apps ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", apps=rows)

@app.post("/admin/apps")
@admin_required
def create_app():
    name = request.form.get("name", "").strip()
    package = request.form.get("package", "").strip()
    version = request.form.get("version", "").strip()
    reclone = int(request.form.get("recloneHours", "160") or 160)
    apk = request.files.get("apk")
    if not name or not package or not version:
        return redirect("/admin?error=Preencha+nome%2C+pacote+e+versao")

    url = ""
    if apk and apk.filename:
        original = secure_filename(apk.filename)
        filename = f"{uuid.uuid4().hex}_{original}"
        apk.save(UPLOAD_DIR / filename)
        url = f"/api/uploads/apks/{filename}"

    conn = db()
    try:
        conn.execute(
            "INSERT INTO apps (name, package, version, url, reclone_hours, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, package, version, url, reclone, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return redirect("/admin?error=Pacote+ja+cadastrado")
    conn.close()
    return redirect("/admin")

@app.post("/admin/apps/<int:app_id>/delete")
@admin_required
def delete_app(app_id):
    conn = db()
    row = conn.execute("SELECT url FROM apps WHERE id=?", (app_id,)).fetchone()
    if row:
        url = row["url"] or ""
        if url.startswith("/api/uploads/apks/"):
            try:
                (UPLOAD_DIR / Path(url).name).unlink(missing_ok=True)
            except OSError:
                pass
        conn.execute("DELETE FROM apps WHERE id=?", (app_id,))
        conn.commit()
    conn.close()
    return redirect("/admin")

@app.post("/admin/apps/<int:app_id>")
@admin_required
def update_app(app_id):
    name = request.form.get("name", "").strip()
    version = request.form.get("version", "").strip()
    reclone = int(request.form.get("recloneHours", "160") or 160)
    apk = request.files.get("apk")
    conn = db()
    row = conn.execute("SELECT * FROM apps WHERE id=?", (app_id,)).fetchone()
    if not row:
        conn.close()
        return redirect("/admin")
    url = row["url"]
    if apk and apk.filename:
        if url.startswith("/api/uploads/apks/"):
            try:
                (UPLOAD_DIR / Path(url).name).unlink(missing_ok=True)
            except OSError:
                pass
        filename = f"{uuid.uuid4().hex}_{secure_filename(apk.filename)}"
        apk.save(UPLOAD_DIR / filename)
        url = f"/api/uploads/apks/{filename}"
    conn.execute(
        "UPDATE apps SET name=?, version=?, reclone_hours=?, url=? WHERE id=?",
        (name, version, reclone, url, app_id),
    )
    conn.commit()
    conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
