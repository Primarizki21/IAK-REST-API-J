# TM 12 — RESTful API Pendaftaran Wisuda | Kelompok Restful J

Universitas Airlangga | Integrasi Aplikasi Korporasi | 10 November 2026

**Anggota**: Muhammad Firdaus (164241030); Primarizki Ahmad Hariyono (164231062); Steven Malow Purba (164241101); Syachazriel Riezqa Zahran (164231049).

## Berkas submission
- `Laporan_Tugas_TM12_Kelompok_Restful_J.docx`: laporan terbaru dengan rekap 29/29 lulus dan dua screenshot pengujian yang dikirim kelompok.
- `server.py` dan `init_database.py`: server Python (FastAPI/Uvicorn) dan inisialisasi database SQLite.
- `client_common.py`, `client_tahap1.py`, `client_tahap2.py`, `client_tugas.py`, `client_bukti.py`: request client dan pengujian otomatis.
- `hasil_pengujian/*.csv`: tabel hasil pengujian tahap 1 (10), tahap 2 (7), dan tugas tambahan (12). Tabel dalam paket sesuai dengan keluaran terminal kelompok yang disampaikan pada 10 November 2026.
- `bukti_respons/*.png`: dua screenshot asli dari kelompok, untuk HTTP 401 dan 200.
- `database/*.db`: database simulasi, bukan data Universitas Airlangga yang sebenarnya. Dapat dibuat ulang dengan `python init_database.py --reset`.

## Cara menjalankan (Windows / VS Code / PowerShell)
Pada folder proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python init_database.py --reset
```

Jalankan server pada terminal A:
```powershell
$env:API_STAGE = '1'
python server.py
```
Pada terminal B:
```powershell
python client_tahap1.py
```

Hentikan server (`Ctrl+C`), kemudian terminal A:
```powershell
$env:API_STAGE = '2'
$env:TOKEN_TTL = '3'
python server.py
```
Terminal B:
```powershell
$env:TTL_FOR_TEST = '3'
python client_tahap2.py
```

Hentikan server, lalu terminal A:
```powershell
python init_database.py --reset
$env:API_STAGE = '2'
$env:TOKEN_TTL = '900'
python server.py
```
Terminal B:
```powershell
python client_tugas.py
python client_bukti.py
```

## Opsional: client di jaringan berbeda (ngrok)
Bila client tidak berada di Wi-Fi yang sama, buka tunnel ke port 5000:

```powershell
ngrok http 5000
```

Salin alamat `https://...` yang muncul, lalu jalankan skrip klien dengan `BASE_URL`:

```powershell
$env:BASE_URL = 'https://alamat-dari-ngrok.ngrok-free.app'
python client_tahap1.py
```

`client_common.py` sudah mengirim header `ngrok-skip-browser-warning`, sehingga halaman peringatan ngrok tidak ikut terbaca sebagai respons API. Alamat berubah setiap ngrok dijalankan ulang; hentikan tunnel setelah pengujian dan jangan menyebarkan alamatnya.

Dokumentasi API: `http://127.0.0.1:5000/docs`. Contoh kredensial pada kode hanya untuk praktik lokal; jangan dipakai untuk aplikasi publik.
