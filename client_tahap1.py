"""Jalankan saat API_STAGE=1. Mengikuti skenario inventori dari slide TM12."""
from client_common import TestTable, send


def main():
    t = TestTable("tabel_tahap_1.csv")
    h = {"client_id": "portal-wisuda"}
    r = send("GET", "/v1/barang", **h)
    t.add("GET daftar barang", "GET", "/v1/barang", 200, r, {"BRG-001", "BRG-002"} <= set(r.json()))
    t.add("GET stok barang ada", "GET", "/v1/barang/BRG-001/stok", 200, send("GET", "/v1/barang/BRG-001/stok", **h))
    t.add("GET barang tidak ada", "GET", "/v1/barang/BRG-999/stok", 404, send("GET", "/v1/barang/BRG-999/stok", **h))
    body = {"kode": "BRG-003", "nama": "Penghapus", "stok": 30, "gudang": "Jakarta"}
    t.add("POST barang lengkap", "POST", "/v1/barang", 201, send("POST", "/v1/barang", payload=body, **h))
    t.add("POST kode duplikat", "POST", "/v1/barang", 409, send("POST", "/v1/barang", payload=body, **h))
    t.add("POST tanpa nama", "POST", "/v1/barang", 400, send("POST", "/v1/barang", payload={"kode": "BRG-004", "stok": 5}, **h))
    t.add("PUT stok teks", "PUT", "/v1/barang/BRG-003/stok", 400, send("PUT", "/v1/barang/BRG-003/stok", payload={"stok": "banyak"}, **h))
    t.add("PUT stok valid", "PUT", "/v1/barang/BRG-003/stok", 200, send("PUT", "/v1/barang/BRG-003/stok", payload={"stok": 25}, **h))
    t.add("DELETE pertama", "DELETE", "/v1/barang/BRG-003", 204, send("DELETE", "/v1/barang/BRG-003", **h))
    t.add("DELETE kedua", "DELETE", "/v1/barang/BRG-003", 404, send("DELETE", "/v1/barang/BRG-003", **h))
    t.save()


if __name__ == "__main__":
    main()
