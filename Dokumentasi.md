# Dokumentasi Proyek — ChurnAI E-Commerce Churn Prediction

---

## Status Proyek Saat Ini

| Bagian | Status | Dikerjakan oleh |
|---|---|---|
| Backend (API, logika, ML pipeline) | ✅ Selesai | Backend Dev |
| Database / Penyimpanan Data | ✅ Selesai (in-memory) | Backend Dev |
| Endpoint prediksi & insight | ✅ Selesai & sudah diuji | Backend Dev |
| Frontend — Struktur & Integrasi | ✅ Selesai | Backend Dev |
| Frontend — Tampilan Visual & UI | 🎨 Belum dimulai | **UI Designer** |
| Deployment ke Vercel | ⏳ Menunggu UI selesai | Backend Dev |

---

## Apa yang Sudah Selesai

### 1. Aplikasi Berjalan Penuh
Aplikasi web ini sudah bisa dijalankan dari awal sampai akhir. Semua fitur berikut sudah bekerja:

- **Upload CSV** → sistem membaca file, memproses setiap baris, dan mengembalikan hasil prediksi
- **Prediksi Manual** → mengisi form 18 kolom, sistem langsung mengeluarkan hasil
- **Dashboard Insight** → menampilkan ringkasan data dan bisa difilter
- **Download Hasil** → hasil prediksi bisa diunduh kembali dalam format CSV
- **Swagger / API Docs** → dokumentasi API tersedia di `/docs`

### 2. Test Suite Sudah Lulus Semua (18/18)
Semua fitur sudah diuji otomatis dan hasilnya:
```
██████████████████  18/18 passed
```
Artinya tidak ada bug pada sisi backend.

### 3. Model ML Belum Ada
Saat ini aplikasi berjalan **tanpa model**. 
Setiap prediksi akan mengembalikan.
- Label: **Tidak Churn**
- Probabilitas: **0.0%**
- Risk Level: **Low**

### 4. Frontend Sudah Diubah ke Mode Wireframe
Tampilan aplikasi saat ini sengaja disederhanakan menjadi hitam-putih polos. Semua tombol, form, tabel, dan chart sudah ada — hanya tampilannya yang belum didesain.

---

## Struktur Folder (Yang Perlu Diketahui Front End)

```
DigitalSkola-ECommerce/
│
├── static/
│   ├── css/
│   │   └── dashboard.css        ← FILE UTAMA YANG PERLU DIDESAIN
│   └── js/
│       ├── charts.js            ← JANGAN DIUBAH
│       ├── upload.js            ← JANGAN DIUBAH
│       └── manual.js            ← JANGAN DIUBAH
│
├── templates/
│   ├── base.html                ← Layout utama (sidebar + navbar)
│   ├── dashboard.html           ← Halaman Dashboard
│   ├── predict.html             ← Halaman Predict
│   └── result.html              ← Halaman Results
│
└── app/                         ← JANGAN DIUBAH (backend)
```

---

## Panduan untuk UI Designer

### Cara Menjalankan Aplikasi (Wajib Dibaca Dulu)

Sebelum mulai mendesain, pastikan aplikasi bisa berjalan di komputer kamu:

**1. Install dependencies (cukup sekali)**
```bash
pip install -r requirements.txt
```

**2. Jalankan server**
```bash
uvicorn app.main:app --reload
```

**3. Buka browser ke:**
- Dashboard: http://localhost:8000
- Predict: http://localhost:8000/predict
- Results: http://localhost:8000/result
- API Docs: http://localhost:8000/docs

Setiap kamu simpan perubahan file CSS atau HTML, cukup refresh browser — server akan otomatis reload.

---

### Apa yang Boleh Kamu Ubah

#### ✅ File CSS — Bebas Diubah Sepenuhnya
**`static/css/dashboard.css`**

Ini adalah file utama styling. Kamu boleh:
- Ganti semua warna
- Ganti font (tambahkan Google Fonts di `base.html` bagian `<head>`)
- Ganti ukuran, padding, margin, border, shadow, gradient, animasi
- Tambah dark mode atau tema apapun
- Hapus semua isi file dan tulis ulang dari nol

**Satu hal yang WAJIB dipertahankan di CSS:**
CSS variables berikut harus tetap ada di `:root {}` karena dipakai oleh JavaScript:
```css
:root {
  --sidebar-w: 224px;   /* lebar sidebar */
  --navbar-h: 56px;     /* tinggi navbar */
  --high: ...;          /* warna badge High Risk */
  --medium: ...;        /* warna badge Medium Risk */
  --low: ...;           /* warna badge Low Risk */
}
```

Dan class-class ini harus tetap ada (boleh diubah tampilannya, tapi jangan dihapus):
- `.risk-badge.High`, `.risk-badge.Medium`, `.risk-badge.Low`
- `.label-badge.churn`, `.label-badge.no-churn`
- `.prob-bar-wrapper`, `.prob-bar-bg`, `.prob-bar-fill`, `.prob-value`
- `.page-btn`, `.page-btn.active`
- `.toast`, `.toast.success`, `.toast.error`, `.toast.info`
- `.loading-overlay`, `.spinner`

---

#### ✅ File HTML Template — Boleh Diubah (dengan batasan)

**`templates/base.html`** — Layout utama (sidebar & navbar)
- Boleh: ganti tampilan sidebar, warna, ikon, font, logo
- Boleh: tambah elemen dekoratif (gambar, ilustrasi, dll)
- **Jangan ubah:** href pada link navigasi (`/`, `/predict`, `/result`, `/docs`)

**`templates/dashboard.html`** — Halaman Dashboard
- Boleh: ganti tampilan card, warna, layout
- Boleh: ganti placeholder chart dengan desain yang menarik
- **Jangan ubah:** semua `id="..."` yang disebutkan di komentar `<!-- TODO -->`

**`templates/predict.html`** — Halaman Predict
- Boleh: ganti tampilan form, tab, tombol, warna
- **Jangan ubah:** `name="..."` pada setiap input dan select di dalam form
- **Jangan ubah:** `id="..."` dan `onclick="..."` pada semua tombol

**`templates/result.html`** — Halaman Results
- Boleh: ganti tampilan tabel, card, warna
- **Jangan hapus:** tag `{% block scripts %}` dan isinya di bagian paling bawah file

---

### Apa yang TIDAK Boleh Diubah

| File | Alasan |
|---|---|
| `static/js/charts.js` | Logika fetch data dari server dan render chart |
| `static/js/upload.js` | Logika upload CSV dan kirim ke API |
| `static/js/manual.js` | Logika form prediksi manual dan gauge chart |
| Semua file di folder `app/` | Backend — API, logika bisnis, koneksi data |
| `requirements.txt` | Daftar library Python yang dibutuhkan |
| `vercel.json` | Konfigurasi deployment |

---

### Panduan Per Halaman

#### Halaman 1: Dashboard (`/`)
Halaman ini menampilkan ringkasan semua prediksi yang sudah dilakukan.

**Komponen yang perlu didesain:**
- **4 Summary Card** (kiri ke kanan): Total Pelanggan, Total Churn, Churn Rate, High Risk
- **Filter Bar**: dropdown Gender, City Tier, Marital Status, dan input Tenure Min/Max
- **6 Area Chart**: semuanya saat ini tampil sebagai kotak placeholder bertuliskan "TODO"
- **Empty State**: tampil saat belum ada data prediksi

**Cara chart bekerja:**
Saat halaman dibuka, JavaScript akan otomatis mengambil data dari server dan menggambar chart ke dalam kotak placeholder. Kamu cukup desain kotaknya (card/container). Warna dan gaya chart bisa kamu ubah di file `static/js/charts.js`.

---

#### Halaman 2: Predict (`/predict`)
Halaman ini memiliki 2 tab:

**Tab 1 — Upload CSV:**
- Area drag-and-drop untuk upload file
- Tombol download template CSV
- Tabel preview hasil (muncul setelah prediksi)
- 4 quick stat card (Total, Churn, Medium Risk, High Risk)

**Tab 2 — Input Manual:**
- Form 18 kolom data pelanggan
- Panel hasil di sebelah kanan (muncul setelah submit):
  - Gauge chart (setengah lingkaran menunjukkan probabilitas)
  - Badge risk level
  - Teks insight

---

#### Halaman 3: Results (`/result`)
Halaman ini menampilkan tabel lengkap hasil prediksi batch.

**Komponen yang perlu didesain:**
- 4 Summary Card (sama seperti dashboard tapi dari data batch)
- 2 Chart (donut + bar) — saat ini placeholder
- Tabel dengan fitur sortir, pencarian, dan filter
- Pagination (navigasi halaman tabel)
- Tombol Download CSV

---

### Tips Umum untuk Designer

**Cara test tampilan:**
1. Jalankan server (lihat instruksi di atas)
2. Edit file CSS atau HTML
3. Simpan → refresh browser
4. Lihat hasilnya langsung

**Cara test prediksi (agar chart bisa terlihat datanya):**
1. Buka http://localhost:8000/predict
2. Klik tab "Upload CSV"
3. Klik "Download Template" untuk dapat contoh file
4. Upload file template tersebut
5. Klik "Jalankan Prediksi"
6. Sekarang buka http://localhost:8000 — chart sudah ada datanya

**Kalau ada yang error atau layar putih:**
- Buka DevTools di browser (klik kanan → Inspect → Console)
- Screenshot errornya dan kirim ke backend dev

**Kalau ingin reset data chart:**
- Di halaman Dashboard, klik tombol "Reset data"
- Konfirmasi dengan klik "Hapus"
- Dashboard kembali ke empty state

---

### Referensi ID Penting (Jangan Dihapus dari HTML)

Ini adalah daftar `id` yang dipakai JavaScript untuk mengisi data ke halaman. Pastikan elemen dengan ID ini tetap ada di HTML, meski tampilannya kamu ubah.

**Dashboard:**
| ID | Fungsi |
|---|---|
| `metricTotal` | Angka total pelanggan |
| `metricChurn` | Angka total churn |
| `metricChurnRate` | Persentase churn rate |
| `metricHighRisk` | Jumlah high risk |
| `filterGender` | Dropdown filter gender |
| `filterCityTier` | Dropdown filter kota |
| `filterMarital` | Dropdown filter status |
| `filterTenureMin` | Input tenure minimum |
| `filterTenureMax` | Input tenure maximum |
| `emptyState` | Container empty state |
| `chartSection` | Container semua chart |
| `chartDonut` | Canvas chart donut |
| `chartProbDist` | Canvas chart histogram |
| `chartTenure` | Canvas chart tenure |
| `chartCategory` | Canvas chart kategori |
| `chartMarital` | Canvas chart marital |
| `chartPayment` | Canvas chart payment |

**Predict:**
| ID | Fungsi |
|---|---|
| `uploadZone` | Area drag-drop |
| `csvFile` | Input file hidden |
| `btnPredict` | Tombol jalankan prediksi |
| `csvResultSection` | Container hasil CSV |
| `manualForm` | Form prediksi manual |
| `manualResultCard` | Container hasil manual |
| `gaugeChart` | Canvas gauge chart |

**Results:**
| ID | Fungsi |
|---|---|
| `resultBody` | Tbody tabel diisi JS |
| `pagination` | Container pagination |
| `searchInput` | Input pencarian |
| `riskFilter` | Dropdown filter risk |
| `churnFilter` | Dropdown filter label |
| `btnDownloadResult` | Tombol download |

---

---

## Kontak & Pembagian Tugas

| Bagian | PIC |
|---|---|
| Backend, API, pipeline, deployment | Backend Dev |
| CSS, HTML visual, layout, responsiveness | UI Designer |

Untuk pertanyaan seputar cara kerja data atau API → tanya Backend Dev.
Untuk pertanyaan seputar tampilan dan layout → keputusan UI Designer.
