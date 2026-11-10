"""TM12 REST API - integrasi pendaftaran wisuda (lanjutan rancangan SOA TM11).
API_STAGE=1: latihan tanpa token. API_STAGE=2: semua /v1/* perlu Bearer token.
Ini SIMULASI lokal: empat domain memakai SQLite terpisah, digabung di satu aplikasi.
"""
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

APP_ROOT = Path(__file__).resolve().parent
DB_DIR = APP_ROOT / "database"
API_STAGE = os.getenv("API_STAGE", "2")
TOKEN_TTL = int(os.getenv("TOKEN_TTL", "900"))
# Kredensial hanya untuk praktikum lokal. Jangan pakai secret ini untuk deployment publik.
CLIENTS = {"portal-wisuda": "demo-portal-123", "admin-kampus": "demo-admin-123"}
TOKENS = {}  # token hanya disimpan di memori, hilang saat server restart

app = FastAPI(title="TM12 - RESTful API Pendaftaran Wisuda", version="1.0")


def db_connect(name):
    path = DB_DIR / f"{name}.db"
    if not path.exists():
        raise RuntimeError(f"Database {path.name} belum dibuat; jalankan python init_database.py")
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def read_one(name, sql, params=()):
    with db_connect(name) as db:
        row = db.execute(sql, params).fetchone()
        return dict(row) if row else None


def read_all(name, sql, params=()):
    with db_connect(name) as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]


def err(message, status=400):
    return JSONResponse({"error": message}, status_code=status)


def is_stock(v):
    return type(v) is int and v >= 0


@app.middleware("http")
async def auth_and_log(request: Request, call_next):
    # Tahap 1 menerima X-Client-ID untuk log, TETAPI belum terautentikasi.
    request.state.client_id = request.headers.get("X-Client-ID", "anonymous") if API_STAGE == "1" else "anonymous"
    request.state.authenticated = False
    path = request.url.path
    if API_STAGE == "2" and path.startswith("/v1/"):
        authorization = request.headers.get("Authorization", "")
        token = authorization[7:] if authorization.startswith("Bearer ") else None
        token_info = TOKENS.get(token) if token is not None else None
        if not token_info or token_info["expires_at"] <= time.time():
            response = err("Token tidak ada, tidak valid, atau kedaluwarsa", 401)
        else:
            request.state.client_id = token_info["client_id"]
            request.state.authenticated = True
            response = await call_next(request)
    else:
        response = await call_next(request)

    # Catat SEMUA request, termasuk 401. Jangan pernah menyimpan secret atau token.
    try:
        with db_connect("wisuda") as db:
            db.execute("""INSERT INTO audit_log
                (waktu_utc, client_id, authenticated, method, endpoint, status_code, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                request.state.client_id, int(request.state.authenticated),
                request.method, path, response.status_code,
                request.client.host if request.client else "unknown"
            ))
    except (sqlite3.Error, RuntimeError) as exc:
        print("WARNING: gagal menulis audit log:", exc)
    return response


@app.post("/oauth/token")
async def issue_token(request: Request):
    try:
        body = await request.json()
    except Exception:
        return err("Body harus berupa JSON", 400)
    if not isinstance(body, dict):
        return err("Body harus berupa objek JSON", 400)
    client_id = str(body.get("client_id", ""))
    client_secret = str(body.get("client_secret", ""))
    expected = CLIENTS.get(client_id)
    if not expected or not secrets.compare_digest(expected, client_secret):
        return err("Kredensial client tidak valid", 401)
    request.state.client_id = client_id
    request.state.authenticated = True
    token = secrets.token_urlsafe(32)
    TOKENS[token] = {"client_id": client_id, "expires_at": time.time() + TOKEN_TTL}
    return {"access_token": token, "token_type": "Bearer", "expires_in": TOKEN_TTL}


# === Latihan TM12 Tahap 1 dan Tahap 2: inventori barang ===
@app.get("/v1/barang")
def get_barang():
    items = read_all("inventori", "SELECT * FROM barang ORDER BY kode")
    return {i["kode"]: {"nama": i["nama"], "stok": i["stok"], "gudang": i["gudang"]} for i in items}


@app.get("/v1/barang/{kode}/stok")
def get_stok(kode: str):
    row = read_one("inventori", "SELECT stok, gudang FROM barang WHERE kode=?", (kode,))
    if row is None:
        return err("Barang tidak ditemukan", 404)
    return {"kodeBarang": kode, "stok": row["stok"], "gudang": row["gudang"]}


@app.post("/v1/barang", status_code=201)
async def create_barang(request: Request):
    try:
        body = await request.json()
    except Exception:
        return err("Body harus berupa JSON", 400)
    if not isinstance(body, dict):
        return err("Body harus berupa objek JSON", 400)
    kode, nama, stok = body.get("kode"), body.get("nama"), body.get("stok")
    if not isinstance(kode, str) or not kode.strip() or not isinstance(nama, str) or not nama.strip() or not is_stock(stok):
        return err("kode, nama, dan stok (bilangan bulat >= 0) wajib diisi", 400)
    with db_connect("inventori") as db:
        if db.execute("SELECT 1 FROM barang WHERE kode=?", (kode,)).fetchone():
            return err("Kode barang sudah ada", 409)
        db.execute("INSERT INTO barang VALUES (?, ?, ?, ?)", (kode, nama, stok, body.get("gudang", "-")))
    return JSONResponse({"kodeBarang": kode, "nama": nama, "stok": stok, "gudang": body.get("gudang", "-")}, status_code=201)


@app.put("/v1/barang/{kode}/stok")
async def update_stok(kode: str, request: Request):
    try:
        body = await request.json()
    except Exception:
        return err("Body harus berupa JSON", 400)
    if not isinstance(body, dict) or not is_stock(body.get("stok")):
        return err("stok harus berupa angka bulat >= 0", 400)
    with db_connect("inventori") as db:
        result = db.execute("UPDATE barang SET stok=? WHERE kode=?", (body["stok"], kode))
        if not result.rowcount:
            return err("Barang tidak ditemukan", 404)
    return {"kodeBarang": kode, "stok": body["stok"]}


@app.delete("/v1/barang/{kode}", status_code=204)
def delete_barang(kode: str):
    with db_connect("inventori") as db:
        result = db.execute("DELETE FROM barang WHERE kode=?", (kode,))
        if not result.rowcount:
            return err("Barang tidak ditemukan", 404)
    return Response(status_code=204)


# === Implementasi studi kasus TM11: AkademikService ===
def profil(nim):
    return read_one("akademik", "SELECT * FROM mahasiswa WHERE nim=?", (nim,))


def akademik_status(nim):
    student = profil(nim)
    if student is None:
        return None
    study = read_one("akademik", "SELECT sks_lulus, ipk FROM hasil_studi WHERE nim=?", (nim,))
    graduation = read_one("akademik", "SELECT lulus FROM status_kelulusan WHERE nim=?", (nim,))
    reasons = []
    if not graduation or not graduation["lulus"]:
        reasons.append("Status kelulusan belum terpenuhi")
    if not study or study["sks_lulus"] < 144:
        reasons.append("SKS lulus kurang dari 144")
    if not study or study["ipk"] < 2.0:
        reasons.append("IPK kurang dari 2.00")
    return {"nim": nim, "layak": not reasons, "alasan": reasons}


@app.get("/v1/akademik/mahasiswa/{nim}")
def get_mahasiswa(nim: str):
    value = profil(nim)
    return value if value else err("Mahasiswa tidak ditemukan", 404)


@app.get("/v1/akademik/mahasiswa/{nim}/kelayakan-wisuda")
def get_kelayakan(nim: str, periode: str = ""):
    if not periode:
        return err("Parameter periode wajib diisi", 400)
    value = akademik_status(nim)
    return {**value, "periode_id": periode} if value else err("Mahasiswa tidak ditemukan", 404)


# === KeuanganService ===
def keuangan_status(nim):
    # KeuanganService hanya membaca database keuangan miliknya sendiri.
    if not read_one("keuangan", "SELECT 1 AS ada FROM tagihan WHERE nim=? LIMIT 1", (nim,)):
        return None
    row = read_one("keuangan", """SELECT
        COALESCE((SELECT SUM(jumlah) FROM tagihan WHERE nim=?), 0) AS tagihan,
        COALESCE((SELECT SUM(p.jumlah) FROM pembayaran p JOIN tagihan t ON p.tagihan_id=t.id WHERE t.nim=?), 0) AS dibayar
        """, (nim, nim))
    tunggakan = max(0, row["tagihan"] - row["dibayar"])
    return {"nim": nim, "lunas": tunggakan == 0, "total_tunggakan": tunggakan}


@app.get("/v1/keuangan/mahasiswa/{nim}/kewajiban")
def get_kewajiban(nim: str):
    value = keuangan_status(nim)
    return value if value else err("Mahasiswa tidak ditemukan", 404)


# === PerpustakaanService ===
def pustaka_status(nim):
    # PerpustakaanService hanya membaca database perpustakaan miliknya sendiri.
    if not read_one("perpustakaan", "SELECT terdaftar FROM anggota WHERE nim=?", (nim,)):
        return None
    loans = read_one("perpustakaan", "SELECT COUNT(*) AS n FROM peminjaman WHERE nim=? AND dikembalikan=0", (nim,))["n"]
    fines = read_one("perpustakaan", "SELECT COALESCE(SUM(jumlah),0) AS n FROM denda WHERE nim=? AND lunas=0", (nim,))["n"]
    reasons = []
    if loans:
        reasons.append(f"{loans} peminjaman belum dikembalikan")
    if fines:
        reasons.append(f"Denda belum dibayar: Rp{fines}")
    return {"nim": nim, "bebas_pustaka": not reasons, "kendala": reasons}


@app.get("/v1/perpustakaan/mahasiswa/{nim}/bebas-pustaka")
def get_bebas_pustaka(nim: str):
    value = pustaka_status(nim)
    return value if value else err("Mahasiswa tidak ditemukan", 404)


# === WisudaService: demonstrasi orkestrasi fungsi lokal ===
@app.post("/v1/wisuda/pendaftaran", status_code=201)
async def daftar_wisuda(request: Request):
    try:
        body = await request.json()
    except Exception:
        return err("Body harus berupa JSON", 400)
    if not isinstance(body, dict) or not isinstance(body.get("nim"), str) or not isinstance(body.get("periode_id"), str) or not body["nim"] or not body["periode_id"]:
        return err("nim dan periode_id wajib diisi", 400)
    nim, periode = body["nim"], body["periode_id"]
    idem = request.headers.get("Idempotency-Key") or None
    if not profil(nim):
        return err("Mahasiswa tidak ditemukan", 404)
    if not read_one("wisuda", "SELECT * FROM periode_wisuda WHERE periode_id=? AND aktif=1", (periode,)):
        return err("Periode wisuda tidak tersedia", 400)
    with db_connect("wisuda") as db:
        if idem:
            prior = db.execute("SELECT id, nim, periode_id, status, verifikasi FROM pendaftaran_wisuda WHERE idempotency_key=?", (idem,)).fetchone()
            if prior:
                if prior["nim"] != nim or prior["periode_id"] != periode:
                    return err("Idempotency-Key sudah dipakai untuk permintaan berbeda", 409)
                return JSONResponse(dict(prior), status_code=200)
        prior = db.execute("SELECT id FROM pendaftaran_wisuda WHERE nim=? AND periode_id=?", (nim, periode)).fetchone()
        if prior:
            return err("Mahasiswa sudah terdaftar pada periode ini", 409)

    akademik, keuangan, pustaka = akademik_status(nim), keuangan_status(nim), pustaka_status(nim)
    failed = []
    if not akademik["layak"]:
        failed.extend(akademik["alasan"])
    if not keuangan["lunas"]:
        failed.append("Kewajiban keuangan belum lunas")
    if not pustaka["bebas_pustaka"]:
        failed.extend(pustaka["kendala"])
    if failed:
        return JSONResponse({"error": "Persyaratan wisuda belum terpenuhi", "nim": nim, "alasan": failed}, status_code=422)

    with db_connect("wisuda") as db:
        try:
            count = db.execute("SELECT COUNT(*) FROM pendaftaran_wisuda").fetchone()[0]
            # Implementasi demo tunggal; concurrency produksi memerlukan ID yang dihasilkan DB/UUID.
            registration_id = f"WD-{count+1:03d}"
            db.execute("""INSERT INTO pendaftaran_wisuda
                (id, nim, periode_id, status, verifikasi, idempotency_key, created_at)
                VALUES (?, ?, ?, 'TERDAFTAR', 'MEMENUHI', ?, ?)""", (
                registration_id, nim, periode, idem,
                datetime.now(timezone.utc).isoformat(timespec="seconds")
            ))
            for aspect in ("akademik", "keuangan", "perpustakaan"):
                db.execute("INSERT INTO hasil_verifikasi (pendaftaran_id, aspek, memenuhi, alasan) VALUES (?, ?, 1, '')", (registration_id, aspect))
        except sqlite3.IntegrityError:
            return err("Pendaftaran ganda terdeteksi", 409)
    return JSONResponse({"id": registration_id, "status": "TERDAFTAR", "verifikasi": "MEMENUHI"}, status_code=201)


@app.get("/v1/wisuda/pendaftaran/{registration_id}")
def status_pendaftaran(registration_id: str):
    row = read_one("wisuda", "SELECT id, nim, periode_id, status, verifikasi FROM pendaftaran_wisuda WHERE id=?", (registration_id,))
    return row if row else err("Pendaftaran tidak ditemukan", 404)


@app.get("/v1/audit-log")
def get_audit_log(request: Request, limit: int = 30):
    # Dalam tahap 1 tanpa auth, semua peserta dapat melihat log; tahap 2 hanya admin.
    if API_STAGE == "2" and request.state.client_id != "admin-kampus":
        return err("Hanya admin-kampus dapat membaca audit log", 403)
    limit = min(max(limit, 1), 200)
    rows = read_all("wisuda", "SELECT id, waktu_utc, client_id, authenticated, method, endpoint, status_code, ip_address FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
    return {"jumlah": len(rows), "logs": rows}


if __name__ == "__main__":
    import uvicorn
    print(f"Memulai TM12 API_STAGE={API_STAGE}; TOKEN_TTL={TOKEN_TTL} detik")
    uvicorn.run(app, host="0.0.0.0", port=5000)
