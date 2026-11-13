# Catatan perintah Tahap 1

Tanggal dokumentasi: 13 November 2026 (konteks proyek, Asia/Jakarta).

## Pemeriksaan awal

- `pwd`, `ls -la`, `git status --short`: workspace awal bukan checkout Git.
- Daftar repository melalui koneksi GitHub: repository IAK ditemukan.
- `git clone https://github.com/Primarizki21/IAK-REST-API-J.git /workspace/work/IAK-REST-API-J`: berhasil.
- `git status --short`, `git log -1`, pembacaan README, `.gitignore`, `pyproject.toml`, daftar file dan pencarian AGENTS.md: project FastAPI/SQLite, tidak ada Next.js atau instruksi AGENTS.md dalam checkout.
- `git switch -c feat/crm-foundation`: berhasil, berasal dari `b95ba5fa4bdd580e45a11e640bb7c5c7b30c7f81` pada `main`.
- `node --version`, `npm --version`: Node 24.22.1, npm 11.9.0.

## Instalasi dan pembuatan

Working directory untuk npm: `apps/crm`.

- `npm view next version` dan `npm view prisma@6 version` pertama gagal karena cache default `/home/agent/.npm` tidak dapat dibuat di sandbox. Tidak ada file project yang ditimpa.
- Diulang dengan `npm --cache /workspace/work/npm-cache view next version` dan `npm --cache /workspace/work/npm-cache view prisma@6 version`: berhasil, Next 16.4.6 dan Prisma 6.19.3 dipilih.
- `npm --cache /workspace/work/npm-cache install`: berhasil, 399 paket; postinstall `prisma generate` berhasil tanpa database. Lockfile disimpan.
- `npm exec -- prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script`: berhasil; SQL kemudian ditulis ke `prisma/migrations/20261113143000_init_customer/migration.sql`. Perintah ini menghasilkan SQL dari skema tanpa mengakses database.
- File dibuat melalui skrip Python sementara di workspace di luar repository; skrip sementara dan cache tidak masuk commit.

## Pemeriksaan

- `npm run lint` pertama: gagal karena satu warning `import/no-anonymous-default-export` pada PostCSS. Diperbaiki dengan variabel `config` sebelum export.
- `npm run lint` setelah perbaikan: exit 0, tanpa warning.
- `npm run typecheck`: exit 0. Script final `next typegen && tsc --noEmit`; diuji setelah memindahkan `.next` dan `next-env.d.ts` yang dihasilkan build sebelumnya ke folder sementara. Ini memastikan tidak bergantung pada hasil build lama.
- `npm run build` awal dan setelah perbaikan final: exit 0; kompilasi, TypeScript, dan prerender 9 halaman berhasil tanpa `DATABASE_URL`.
- `set -a`, `. ./.env.example`, `npm run db:validate`: exit 0. Placeholder dimuat hanya ke proses pemeriksaan untuk validasi struktur; bukan kredensial nyata dan tidak ada koneksi database.
- `npm ls --depth=0`: exit 0; mencatat dependency terpasang. Paket WASM opsional sharp/emnapi ditampilkan npm sebagai extraneous; lint/build berhasil.
- `git check-ignore .env .env.local node_modules .next`: seluruhnya diabaikan; `.env.example` tetap disertakan.
- Pemeriksaan diff staged menemukan baris kosong tambahan di akhir SQL migration; dirapikan. `git diff --cached --check` final tidak menemukan masalah whitespace.
- `npm --cache /workspace/work/npm-cache exec --yes --package=prettier@3.6.2 -- prettier --write ...`: memformat source/config/README untuk review. Prettier hanya alat sementara, bukan dependency aplikasi.

## Pemeriksaan yang belum dijalankan

- `db:deploy`, `db:migrate`, query/CRUD database: belum dijalankan karena layanan PostgreSQL dan kredensial tidak tersedia.
- Browser desktop/mobile: belum dijalankan karena `cua_repl.js` tidak tersedia. Sesuai panduan preview managed, tidak menjalankan server preview atau memasang browser alternatif. Build/prerender bukan bukti tampilan atau interaksi browser telah diuji.
- CI GitHub: hasil lokal bukan hasil Actions; periksa tab Checks pada PR setelah push.

## Commit dan Pull Request

- `git add README.md .github/workflows/crm-ci.yml apps/crm docs/crm`, `git diff --cached --check`: berhasil, 44 file tercakup.
- `git commit -m "feat(crm): add phase-one Next.js dashboard foundation"`: berhasil, commit implementasi `5b7363d`.
- `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push --set-upstream origin feat/crm-foundation`: berhasil melalui kredensial sesi tanpa menyimpan token dalam file.
- Draft PR dibuat melalui plugin GitHub: https://github.com/Primarizki21/IAK-REST-API-J/pull/1, base `main`, head `feat/crm-foundation`, tidak di-merge.
- `gh run list --repo Primarizki21/IAK-REST-API-J --branch feat/crm-foundation --limit 5 --json databaseId,name,status,conclusion,url`: workflow push/PR sedang berjalan pada pemeriksaan awal; lihat tab Checks untuk status terbaru.
- `git status --short`: bersih setelah commit implementasi. `git ls-remote --heads origin main`: main masih menunjuk commit awal.
- Catatan penyerahan ini disimpan dengan commit dokumentasi terpisah lalu dikirim ke feature branch yang sama.
