"""Buat lima database SQLite berisi data CONTOH untuk praktikum TM12.
Empat database pertama sesuai rancangan TM11; inventory untuk uji TM12 tahap 1.
"""
import argparse
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "database"
NAMES = ("akademik", "keuangan", "perpustakaan", "wisuda", "inventori")


def setup(reset=False):
    DB.mkdir(exist_ok=True)
    if reset:
        for name in NAMES:
            (DB / f"{name}.db").unlink(missing_ok=True)

    with sqlite3.connect(DB / "akademik.db") as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim TEXT PRIMARY KEY, nama TEXT NOT NULL, status_akademik TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS hasil_studi (
            nim TEXT PRIMARY KEY, sks_lulus INTEGER NOT NULL, ipk REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS status_kelulusan (
            nim TEXT PRIMARY KEY, lulus INTEGER NOT NULL
        );
        """)
        con.executemany("INSERT OR IGNORE INTO mahasiswa VALUES (?, ?, ?)", [
            ("MHS001", "Alya Pratama", "LULUS"),
            ("MHS002", "Bima Santoso", "LULUS"),
            ("MHS003", "Citra Mahendra", "LULUS"),
        ])
        con.executemany("INSERT OR IGNORE INTO hasil_studi VALUES (?, ?, ?)", [
            ("MHS001", 148, 3.67), ("MHS002", 146, 3.31), ("MHS003", 150, 3.55)
        ])
        con.executemany("INSERT OR IGNORE INTO status_kelulusan VALUES (?, ?)", [
            ("MHS001", 1), ("MHS002", 1), ("MHS003", 1)
        ])

    with sqlite3.connect(DB / "keuangan.db") as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS tagihan (
            id INTEGER PRIMARY KEY, nim TEXT NOT NULL, jumlah INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pembayaran (
            id INTEGER PRIMARY KEY, tagihan_id INTEGER NOT NULL, jumlah INTEGER NOT NULL
        );
        """)
        con.executemany("INSERT OR IGNORE INTO tagihan VALUES (?, ?, ?)", [
            (1, "MHS001", 3000000), (2, "MHS002", 4000000), (3, "MHS003", 2500000)
        ])
        con.executemany("INSERT OR IGNORE INTO pembayaran VALUES (?, ?, ?)", [
            (1, 1, 3000000), (2, 2, 2000000), (3, 3, 2500000)
        ])

    with sqlite3.connect(DB / "perpustakaan.db") as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS anggota (
            nim TEXT PRIMARY KEY, terdaftar INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS peminjaman (
            id INTEGER PRIMARY KEY, nim TEXT NOT NULL, dikembalikan INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS denda (
            id INTEGER PRIMARY KEY, nim TEXT NOT NULL, jumlah INTEGER NOT NULL, lunas INTEGER NOT NULL
        );
        """)
        con.executemany("INSERT OR IGNORE INTO anggota VALUES (?, ?)", [
            ("MHS001", 1), ("MHS002", 1), ("MHS003", 1)
        ])
        con.executemany("INSERT OR IGNORE INTO peminjaman VALUES (?, ?, ?)", [
            (1, "MHS001", 1), (2, "MHS002", 1), (3, "MHS003", 0)
        ])
        con.executemany("INSERT OR IGNORE INTO denda VALUES (?, ?, ?, ?)", [
            (1, "MHS001", 0, 1), (2, "MHS003", 50000, 0)
        ])

    with sqlite3.connect(DB / "wisuda.db") as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS periode_wisuda (
            periode_id TEXT PRIMARY KEY, aktif INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pendaftaran_wisuda (
            id TEXT PRIMARY KEY, nim TEXT NOT NULL, periode_id TEXT NOT NULL,
            status TEXT NOT NULL, verifikasi TEXT NOT NULL,
            idempotency_key TEXT UNIQUE, created_at TEXT NOT NULL,
            UNIQUE (nim, periode_id)
        );
        CREATE TABLE IF NOT EXISTS hasil_verifikasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pendaftaran_id TEXT NOT NULL, aspek TEXT NOT NULL,
            memenuhi INTEGER NOT NULL, alasan TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu_utc TEXT NOT NULL, client_id TEXT NOT NULL,
            authenticated INTEGER NOT NULL, method TEXT NOT NULL,
            endpoint TEXT NOT NULL, status_code INTEGER NOT NULL,
            ip_address TEXT
        );
        """)
        con.execute("INSERT OR IGNORE INTO periode_wisuda VALUES (?, ?)", ("WIS-2026-2", 1))

    with sqlite3.connect(DB / "inventori.db") as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS barang (
            kode TEXT PRIMARY KEY, nama TEXT NOT NULL,
            stok INTEGER NOT NULL CHECK(stok >= 0), gudang TEXT NOT NULL
        );
        """)
        con.executemany("INSERT OR IGNORE INTO barang VALUES (?, ?, ?, ?)", [
            ("BRG-001", "Pulpen", 42, "Jakarta"),
            ("BRG-002", "Buku tulis", 15, "Surabaya"),
        ])

    print("Database siap:", ", ".join(f"{name}.db" for name in NAMES))
    print("Data yang dibuat hanya simulasi untuk praktikum, bukan database kampus asli.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Hapus data demo lama lalu seed ulang")
    setup(parser.parse_args().reset)
