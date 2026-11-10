# IAK REST API — TM 12 (Kelompok Restful J)

Server FastAPI + lima database SQLite untuk latihan REST API (inventori) dan
studi kasus pendaftaran wisuda. Instruksi submission untuk penilai ada di
[`README_SUBMISSION.md`](README_SUBMISSION.md); berkas ini adalah runbook untuk
menjalankan ulang pengujian.

## Prasyarat

```bash
uv sync
uv run python init_database.py --reset
```

`--reset` menghapus lalu men-seed lima database di `database/`. Wajib dijalankan
sebelum jalur tugas tambahan karena pendaftaran wisuda bersifat persisten.

## Jalur lokal

### Tahap 1 — tanpa token

Terminal A:

```bash
API_STAGE=1 uv run python server.py
```

Terminal B:

```bash
uv run python client_tahap1.py     # HASIL: 10/10 lulus
```

### Tahap 2 — bearer token dan kedaluwarsa

Terminal A:

```bash
API_STAGE=2 TOKEN_TTL=3 uv run python server.py
```

Terminal B:

```bash
TTL_FOR_TEST=3 uv run python client_tahap2.py   # HASIL: 7/7 lulus, menunggu ~4 detik
```

### Tugas tambahan — API wisuda dan audit log

Terminal A:

```bash
uv run python init_database.py --reset
API_STAGE=2 uv run python server.py
```

Terminal B:

```bash
uv run python client_tugas.py      # HASIL: 12/12 lulus
uv run python client_bukti.py      # mencetak respons 401 lalu 200
```

## Jalur ngrok — client di jaringan berbeda

Sekali saja:

```bash
ngrok config add-authtoken "<AUTHTOKEN>"
```

Terminal A (server):

```bash
uv run python init_database.py --reset
API_STAGE=1 uv run python server.py
```

Terminal B (tunnel):

```bash
ngrok http 5000
```

Salin alamat `https://<acak>.ngrok-free.app` dari terminal B, lalu:

```bash
# terminal C
BASE_URL=https://<acak>.ngrok-free.app uv run python client_tahap1.py
```

Untuk tahap 2 dan tugas, ganti env server lalu jalankan klien dengan `BASE_URL`:

```bash
# terminal A
API_STAGE=2 TOKEN_TTL=3 uv run python server.py

# terminal C
BASE_URL=https://<acak>.ngrok-free.app TTL_FOR_TEST=3 uv run python client_tahap2.py
```

```bash
# terminal A
uv run python init_database.py --reset
API_STAGE=2 uv run python server.py

# terminal C
BASE_URL=https://<acak>.ngrok-free.app uv run python client_tugas.py
BASE_URL=https://<acak>.ngrok-free.app uv run python client_bukti.py
```

Tutup tunnel dengan `Ctrl+C` setelah selesai. Alamat gratis berubah setiap
`ngrok http 5000` dijalankan ulang, dan selama tunnel hidup API dapat dipanggil
siapa pun yang tahu alamatnya — gunakan `API_STAGE=2` bila pengujian berlangsung
lebih dari beberapa menit.

## Variabel lingkungan

| Variabel | Default | Fungsi |
|---|---|---|
| `API_STAGE` | `2` | `1` tanpa autentikasi, `2` wajib `Authorization: Bearer` untuk `/v1/*`. |
| `TOKEN_TTL` | `900` | Masa berlaku token dalam detik. |
| `TTL_FOR_TEST` | `3` | Lama tunggu di `client_tahap2.py`; harus `TOKEN_TTL + 1`. |
| `BASE_URL` | `http://127.0.0.1:5000` | Alamat server, dipakai saat lewat ngrok. |

## Keluaran

- `hasil_pengujian/tabel_tahap_1.csv`, `tabel_tahap_2.csv`, `tabel_tugas_tambahan.csv`
  ditimpa setiap run (UTF-8 BOM agar rapi di Excel).
- `hasil_pengujian/respons_401.json` dan `respons_200.json` ditulis oleh
  `client_tahap2.py`.
- Skrip berhenti dengan `SystemExit` bila ada baris `GAGAL`; exit code 0 berarti
  semua skenario lulus.
- Dokumentasi interaktif: `http://127.0.0.1:5000/docs`.

## Catatan

- Token disimpan di memori; restart server membatalkan semua token.
- Jangan menaruh token atau `client_secret` di `audit_log`; kode sudah menjaga itu.
- `client_tahap1.py` aman dijalankan berulang karena `BRG-003` dihapus di akhir
  setiap run, tetapi `client_tugas.py` butuh `init_database.py --reset` lebih dulu.
