"""Utilitas client dan ekspor bukti pengujian ke CSV."""
import csv
import json
import os
from pathlib import Path
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "hasil_pengujian"
OUT.mkdir(exist_ok=True)


def send(method, path, *, token=None, client_id=None, payload=None, headers=None):
    all_headers = {"Accept": "application/json", "ngrok-skip-browser-warning": "true"}
    if token:
        all_headers["Authorization"] = f"Bearer {token}"
    if client_id:
        all_headers["X-Client-ID"] = client_id
    if headers:
        all_headers.update(headers)
    return requests.request(method, BASE + path, headers=all_headers, json=payload, timeout=10)


def token_for(client_id="portal-wisuda", secret=None):
    default = {"portal-wisuda": "demo-portal-123", "admin-kampus": "demo-admin-123"}
    r = send("POST", "/oauth/token", payload={"client_id": client_id, "client_secret": secret or default[client_id]})
    r.raise_for_status()
    return r.json()["access_token"]


class TestTable:
    def __init__(self, filename):
        self.filename = filename
        self.rows = []

    def add(self, scenario, method, path, expected, response, condition=True):
        status = response.status_code
        passed = status == expected and condition
        self.rows.append({
            "Skenario": scenario, "Metode": method, "Endpoint": path,
            "Status Diharapkan": expected, "Status Aktual": status,
            "Hasil": "LULUS" if passed else "GAGAL",
            "Ringkasan Respons": "" if status == 204 else json.dumps(response.json(), ensure_ascii=False)[:250]
        })
        print(f"{'LULUS' if passed else 'GAGAL':5} | {status:3} | {method:6} {path:56} | {scenario}")
        return response

    def special(self, scenario, expected, actual, passed):
        self.rows.append({
            "Skenario": scenario, "Metode": "-", "Endpoint": "-",
            "Status Diharapkan": expected, "Status Aktual": actual,
            "Hasil": "LULUS" if passed else "GAGAL", "Ringkasan Respons": ""
        })
        print(f"{'LULUS' if passed else 'GAGAL':5} | {scenario}: {actual}")

    def save(self):
        file = OUT / self.filename
        with file.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.rows[0].keys()))
            writer.writeheader()
            writer.writerows(self.rows)
        passed = sum(row["Hasil"] == "LULUS" for row in self.rows)
        print(f"HASIL: {passed}/{len(self.rows)} lulus. CSV: {file}")
        if passed != len(self.rows):
            raise SystemExit("Ada pengujian gagal; periksa konfigurasi atau data sebelum submit.")
