"""Uji API wisuda hasil pengembangan tugas TM11; jalankan saat API_STAGE=2."""
from client_common import TestTable, send, token_for


def main():
    t = TestTable("tabel_tugas_tambahan.csv")
    token = token_for("portal-wisuda")
    admin = token_for("admin-kampus")
    x = "/v1/akademik/mahasiswa/MHS001"
    t.add("Profil mahasiswa", "GET", x, 200, send("GET", x, token=token))
    x = "/v1/akademik/mahasiswa/MHS001/kelayakan-wisuda?periode=WIS-2026-2"
    r = send("GET", x, token=token)
    t.add("Verifikasi akademik", "GET", x, 200, r, r.json().get("layak") is True)
    x = "/v1/keuangan/mahasiswa/MHS002/kewajiban"
    r = send("GET", x, token=token)
    t.add("Tunggakan MHS002", "GET", x, 200, r, r.json().get("lunas") is False)
    x = "/v1/perpustakaan/mahasiswa/MHS003/bebas-pustaka"
    r = send("GET", x, token=token)
    t.add("Bebas pustaka MHS003", "GET", x, 200, r, r.json().get("bebas_pustaka") is False)
    x = "/v1/wisuda/pendaftaran"
    p = {"nim": "MHS001", "periode_id": "WIS-2026-2"}
    r = send("POST", x, token=token, payload=p, headers={"Idempotency-Key": "req-tm12-001"})
    t.add("Pendaftaran yang memenuhi syarat", "POST", x, 201, r)
    if r.status_code != 201:
        t.save()
        return
    registration_id = r.json()["id"]
    y = f"/v1/wisuda/pendaftaran/{registration_id}"
    t.add("Lihat status pendaftaran", "GET", y, 200, send("GET", y, token=token))
    r = send("POST", x, token=token, payload=p, headers={"Idempotency-Key": "req-tm12-001"})
    t.add("Idempotency-Key yang sama", "POST", x, 200, r)
    t.add("Pendaftaran duplikat dengan key baru", "POST", x, 409,
          send("POST", x, token=token, payload=p, headers={"Idempotency-Key": "req-tm12-002"}))
    t.add("Pendaftaran belum lunas", "POST", x, 422,
          send("POST", x, token=token, payload={"nim": "MHS002", "periode_id": "WIS-2026-2"}))
    t.add("Tanpa token endpoint Wisuda", "GET", y, 401, send("GET", y))
    t.add("Portal dilarang membaca audit", "GET", "/v1/audit-log", 403,
          send("GET", "/v1/audit-log", token=token))
    r = send("GET", "/v1/audit-log?limit=100", token=admin)
    t.add("Admin membaca audit log", "GET", "/v1/audit-log?limit=100", 200, r,
          any(it["client_id"] == "portal-wisuda" and it["endpoint"] == "/v1/wisuda/pendaftaran" for it in r.json().get("logs", [])))
    t.save()


if __name__ == "__main__":
    main()
