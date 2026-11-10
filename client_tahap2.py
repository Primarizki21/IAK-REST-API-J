"""Jalankan saat API_STAGE=2 dan TOKEN_TTL=3 untuk uji kadaluarsa cepat."""
import os
import time
from client_common import TestTable, send, token_for, OUT


def main():
    t = TestTable("tabel_tahap_2.csv")
    path = "/v1/barang/BRG-001/stok"
    r401 = send("GET", path)
    t.add("Tanpa Authorization", "GET", path, 401, r401)
    (OUT / "respons_401.json").write_text(r401.text, encoding="utf-8")
    t.add("Secret salah", "POST", "/oauth/token", 401,
          send("POST", "/oauth/token", payload={"client_id": "portal-wisuda", "client_secret": "salah"}))
    a = token_for()
    b = token_for()
    t.special("Token dua kali berbeda", "Token A != Token B", "Berbeda" if a != b else "Sama", a != b)
    r200 = send("GET", path, token=b)
    t.add("Token valid", "GET", path, 200, r200)
    (OUT / "respons_200.json").write_text(r200.text, encoding="utf-8")
    t.add("Token palsu", "GET", path, 401, send("GET", path, token="token-palsu-123"))
    ttl = int(os.getenv("TTL_FOR_TEST", "3"))
    print(f"Uji kedaluwarsa: menunggu {ttl + 1} detik; pastikan server TOKEN_TTL={ttl}.")
    time.sleep(ttl + 1)
    t.add("Token kedaluwarsa", "GET", path, 401, send("GET", path, token=b))
    t.add("Token baru setelah kedaluwarsa", "GET", path, 200, send("GET", path, token=token_for()))
    t.save()


if __name__ == "__main__":
    main()
