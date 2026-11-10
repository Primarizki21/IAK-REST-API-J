"""Menampilkan respons JSON 401 dan 200 untuk di-screenshot di terminal."""
import json
from client_common import send, token_for

path = "/v1/akademik/mahasiswa/MHS001"

print("\n===== BUKTI 1: REQUEST TANPA TOKEN =====")
r1 = send("GET", path)
print("GET", path)
print("HTTP STATUS:", r1.status_code)
print("RESPONSE JSON:", json.dumps(r1.json(), ensure_ascii=False, indent=2))
assert r1.status_code == 401, "Pastikan server sedang berjalan dalam API_STAGE=2"

print("\n===== BUKTI 2: REQUEST DENGAN TOKEN VALID =====")
token = token_for("portal-wisuda")
r2 = send("GET", path, token=token)
print("GET", path)
print("Authorization: Bearer [TOKEN DISEMBUNYIKAN]")
print("HTTP STATUS:", r2.status_code)
print("RESPONSE JSON:", json.dumps(r2.json(), ensure_ascii=False, indent=2))
assert r2.status_code == 200, "Token atau server bermasalah"
