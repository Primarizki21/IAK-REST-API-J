## Perubahan

Menambahkan fondasi CRM telekomunikasi di `apps/crm` agar dapat dikembangkan tanpa mengganggu tugas FastAPI/SQLite yang sudah ada. Dashboard responsif menampilkan data contoh, navigasi mobile, pencarian tabel, pilihan periode grafik, dan halaman penanda modul berikutnya.

Menyiapkan Next.js App Router, TypeScript strict, Tailwind CSS, Prisma/PostgreSQL dengan model awal pelanggan dan migration, `.env.example`, struktur modular, README lokal, serta CI terpisah. Belum ada autentikasi, CRUD, atau integrasi API.

## Validasi

Hasil aktual lint, pemeriksaan TypeScript, build, dan validasi Prisma dicatat di `docs/crm/TAHAP-1.md`. Database PostgreSQL belum tersedia, sehingga migration/koneksi langsung belum diuji. QA browser interaktif dibatasi ketersediaan infrastruktur preview.

## Review

Periksa tampilan desktop/mobile dengan instruksi `apps/crm/README.md`, scope fondasi, dan pemisahan dari tugas lama. Merge ke `main` tetap melalui review kelompok.
