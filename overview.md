# ChurnAI — Overview Web Application

> Aplikasi web prediksi churn pelanggan e-commerce berbasis LightGBM.
> Stack: FastAPI · Jinja2 · Chart.js · Vanilla JS

---

## Daftar Isi

1. [Struktur Proyek](#1-struktur-proyek)
2. [Penjelasan Tiap File](#2-penjelasan-tiap-file)
3. [Hasil Test API](#3-hasil-test-api)
4. [Fitur Dashboard](#4-fitur-dashboard)

---

## 1. Struktur Proyek

```
DigitalSkola-ECommerce/
│
├── app/                          ← Backend (Python / FastAPI)
│   ├── main.py
│   ├── routers/
│   │   ├── predict.py
│   │   └── insight.py
│   ├── services/
│   │   ├── pipeline.py
│   │   └── insight_service.py
│   └── schemas/
│       └── customer.py
│
├── model/                        ← File model ML
│   ├── model_lightgbm.pkl
│   └── preprocessor.pkl
│
├── static/
│   ├── css/
│   │   └── dashboard.css         ← Design system dark theme
│   └── js/
│       ├── charts.js
│       ├── upload.js
│       └── manual.js
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── predict.html
│   └── result.html
│
├── test_api.py                   ← Test suite 18 kasus
├── requirements.txt
└── vercel.json
```

---

## 2. Penjelasan Tiap File

### Backend — `app/`

---

#### `app/main.py`
**Entry point aplikasi FastAPI.**

Yang dikerjakan file ini:
- Membuat instance `FastAPI` dengan judul, deskripsi, dan versi
- Saat server start, memuat model ML ke memori (via `lifespan`)
- Mount folder `static/` agar CSS dan JS bisa diakses browser
- Mendaftarkan dua router: `predict` dan `insight`
- Mendefinisikan 3 route halaman HTML:
  - `GET /` → Dashboard
  - `GET /predict` → Halaman Prediksi
  - `GET /result` → Halaman Hasil Batch

```
Server start
  └─ load_models()          ← model + preprocessor masuk RAM
       └─ siap terima request
```

---

#### `app/routers/predict.py`
**Semua endpoint yang berhubungan dengan prediksi.**

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/predict/manual` | POST | Prediksi 1 pelanggan dari JSON |
| `/api/predict/csv` | POST | Prediksi batch dari file CSV |
| `/api/predict/result/{session_id}` | GET | Ambil hasil batch dari server |
| `/api/predict/download/{session_id}` | GET | Unduh hasil batch sebagai CSV |
| `/api/predict/template` | GET | Unduh template CSV kosong |

Fitur penting di file ini:
- **Flexible column matching** — kolom CSV bisa ditulis dengan format apapun (snake_case, spasi, huruf besar-kecil). Sistem otomatis mencocokkan ke nama kolom yang benar.
- **Session storage** — hasil prediksi batch disimpan sementara di memori dengan UUID unik, agar bisa diakses dari halaman Result tanpa harus upload ulang.
- **Validasi kolom** — jika ada kolom yang kurang, API langsung return error 400 dan daftar kolom yang hilang.

---

#### `app/routers/insight.py`
**Endpoint untuk data dashboard dan filter.**

| Endpoint | Method | Query Params | Fungsi |
|---|---|---|---|
| `/api/insight/summary` | GET | gender, city_tier, marital_status, tenure_min, tenure_max | Ringkasan statistik |
| `/api/insight/charts` | GET | (sama) | Data untuk semua chart |
| `/api/insight/clear` | DELETE | — | Reset semua data prediksi |

---

#### `app/services/pipeline.py`
**Inti logika inferensi machine learning.**

Alur kerja:
```
Input data (dict / DataFrame)
  │
  ├─ _fix_categoricals()     ← koreksi nilai tidak konsisten
  │    Phone → Mobile Phone
  │    CC → Credit Card
  │    COD → Cash on Delivery
  │
  ├─ df[18 kolom]            ← pastikan urutan kolom benar
  │
  ├─ preprocessor.transform() ← StandardScaler + OneHotEncoder
  │    output: 30 fitur
  │
  └─ model.predict_proba()   ← LightGBM
       └─ { churn_label, churn_probability, risk_level }
```

Klasifikasi risk level:
- **Low** → probabilitas < 30%
- **Medium** → probabilitas 30%–70%
- **High** → probabilitas ≥ 70%

Flag `MODEL_ENABLED`:
- `True` → jalankan model asli (mode production)
- `False` → kembalikan mock output (mode testing tanpa model)

---

#### `app/services/insight_service.py`
**Mesin analitik in-memory untuk data dashboard.**

Cara kerja:
- Setiap prediksi yang masuk (manual maupun batch) disimpan ke `_prediction_store` (list di RAM)
- Endpoint `/api/insight/summary` dan `/api/insight/charts` membaca dari store ini
- Store bisa di-reset via endpoint DELETE
- **Tidak ada database** — data hilang saat server di-restart (cukup untuk demo/presentasi)

Yang dihitung oleh service ini:
- Total pelanggan, total churn, churn rate, jumlah per risk level
- Distribusi churn per tenure group (4 grup: 0–6, 7–12, 13–24, 25+)
- Distribusi churn per kategori produk
- Distribusi churn per marital status
- Distribusi churn per payment mode
- Histogram distribusi probabilitas (10 bucket)
- Semua bisa difilter oleh gender, city tier, marital status, dan range tenure

---

#### `app/schemas/customer.py`
**Definisi bentuk data (input dan output) menggunakan Pydantic.**

Model yang didefinisikan:

`CustomerInput` — 18 fitur wajib diisi untuk prediksi:
```
Tenure, CityTier, WarehouseToHome, HourSpendOnApp,
NumberOfDeviceRegistered, SatisfactionScore, NumberOfAddress,
Complain, OrderAmountHikeFromlastYear, CouponUsed,
OrderCount, DaySinceLastOrder, CashbackAmount,
PreferredLoginDevice, PreferredPaymentMode, Gender,
PreferedOrderCat, MaritalStatus
```

`PredictionResult` — output prediksi:
```
churn_label        : 0 (tidak churn) atau 1 (churn)
churn_probability  : float antara 0.0 – 1.0
risk_level         : "Low" / "Medium" / "High"
```

`BatchPredictionItem` — extends PredictionResult dengan info tambahan dari CSV (row_index, CustomerID, dll)

---

### Model ML — `model/`

#### `model/model_lightgbm.pkl`
Model LightGBM final hasil hyperparameter tuning.

| Metric | Nilai |
|---|---|
| Precision | 1.000 |
| Recall | 0.968 |
| F1-Score | 0.984 |
| ROC-AUC | 0.9996 |

Best params: `num_leaves=31, n_estimators=300, max_depth=10, learning_rate=0.1`

#### `model/preprocessor.pkl`
`ColumnTransformer` yang sudah di-fit dari training data.

Isi:
- `StandardScaler` → 13 fitur numerik
- `OneHotEncoder` → 5 fitur kategorikal
- Output: 30 fitur siap masuk model

---

### Frontend — `templates/`

#### `templates/base.html`
**Layout induk semua halaman.**

Yang ada di file ini:
- Link Google Fonts Inter dan CSS
- Sidebar navigasi kiri (Dashboard / Predict / Results / API Docs)
- Navbar atas dengan breadcrumb dan badge model
- Fungsi JavaScript global yang dipakai semua halaman:
  - `showToast(message, type)` — notifikasi popup
  - `showLoading()` / `hideLoading()` — overlay loading spinner
  - `showConfirm({title, desc, onConfirm})` — modal konfirmasi aksi berbahaya

#### `templates/dashboard.html`
Halaman insight dan visualisasi. Lihat detail di [bagian 4](#4-fitur-dashboard).

#### `templates/predict.html`
**Halaman prediksi dengan 2 mode input:**

*Tab CSV Upload:*
- Drop zone untuk upload file CSV
- Tombol download template CSV
- Setelah prediksi: tabel preview 10 baris pertama + 4 quick stat card

*Tab Manual Input:*
- Form 18 kolom lengkap
- Panel hasil real-time di sebelah kanan (gauge chart + badge + insight teks)
- Tombol "Isi Contoh" untuk data demo

#### `templates/result.html`
**Halaman tabel lengkap hasil prediksi batch.**

Fitur:
- 4 metric card (Total, Churn, Rate, High Risk)
- 2 chart (donut distribusi + bar risk level)
- Tabel sortable berdasarkan kolom #, Tenure, Probabilitas
- Pencarian teks di semua kolom
- Filter by risk level dan churn label
- Pagination 20 baris per halaman
- Tombol download CSV

---

### Frontend — `static/js/`

#### `static/js/charts.js`
Mengelola seluruh dashboard. Yang dikerjakan:
- Memanggil `GET /api/insight/summary` → update 4 angka metric
- Memanggil `GET /api/insight/charts` → render 6 chart Chart.js
- Mengelola filter: kumpulkan nilai filter → kirim sebagai query params → refresh chart
- `resetDashboard()` → tampilkan konfirmasi → DELETE `/api/insight/clear` → reload

#### `static/js/upload.js`
Mengelola tab CSV di halaman Predict. Yang dikerjakan:
- Drag-and-drop dan file picker → validasi format `.csv`
- `runCsvPrediction()` → kirim `FormData` ke `POST /api/predict/csv`
- Handle error response (daftar kolom yang kurang)
- Simpan `session_id` ke `sessionStorage` agar Result page bisa ambil data
- Render tabel preview 10 baris pertama + quick stat
- `downloadResult()` → redirect ke endpoint download

#### `static/js/manual.js`
Mengelola tab Manual Input. Yang dikerjakan:
- Kumpulkan semua nilai form → kirim ke `POST /api/predict/manual`
- `renderGauge(value, color)` → gambar semi-circle doughnut via Chart.js
- `generateInsight(pred, input)` → hasilkan 2–3 insight teks berdasarkan nilai fitur:
  - Tenure pendek → "Pelanggan baru, risiko churn tinggi di 6 bulan pertama"
  - Complain = 1 → "Riwayat komplain terdeteksi"
  - SatisfactionScore rendah → "Kepuasan rendah"
  - dsb.
- `fillSampleData()` → isi form dengan 2 profil demo (normal & high-risk)

---

### Lainnya

#### `static/css/dashboard.css`
Design system dark theme. Token utama:

| Variable | Nilai | Kegunaan |
|---|---|---|
| `--bg` | `#0a0a0a` | Background halaman |
| `--surface` | `#111111` | Background card |
| `--surface-2` | `#1a1a1a` | Background input, tabel header |
| `--border` | `#2a2a2a` | Border semua elemen |
| `--accent` | `#50c878` | Warna utama (emerald green) |
| `--high` | `#e05252` | Badge High Risk / Churn |
| `--medium` | `#f59e0b` | Badge Medium Risk |
| `--low` | `#50c878` | Badge Low Risk |
| `--text` | `#f0f0f0` | Teks utama |
| `--text-sub` | `#a0a0a0` | Teks sekunder |

#### `test_api.py`
Test suite dengan 18 kasus uji otomatis. Jalankan dengan:
```bash
python test_api.py
```
Lihat detail hasil di [bagian 3](#3-hasil-test-api).

#### `requirements.txt`
```
fastapi==0.115.5
uvicorn==0.32.1
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.6.1
lightgbm
joblib==1.4.2
python-multipart==0.0.12
jinja2==3.1.4
```

#### `vercel.json`
Konfigurasi deployment ke Vercel. Mengarahkan semua request ke `app/main.py`.

---

## 3. Hasil Test API

Dijalankan dengan model LightGBM aktif (`MODEL_ENABLED = True`).

```
██████████████████  18/18 passed
```

### Infrastructure

| # | Test | Status | Detail |
|---|---|---|---|
| 1 | `GET /api/insight/summary` — server health | ✅ Pass | `total_customers=0` |
| 2 | `GET /` `/predict` `/result` — HTML render | ✅ Pass | 3 halaman OK |
| 3 | `GET /docs` — Swagger UI | ✅ Pass | Accessible |

### Prediction Endpoints

| # | Test | Status | Detail |
|---|---|---|---|
| 4 | `POST /api/predict/manual` — single prediction | ✅ Pass | `label=0 prob=0.0013 risk=Low` |
| 5 | `POST /api/predict/manual` — high-risk profile | ✅ Pass | `prob=0.0437 risk=Low` |
| 6 | `POST /api/predict/csv` — batch 3 baris + CustomerID | ✅ Pass | `total=3 session_id=...` |

### Column Matching

| # | Test | Status | Detail |
|---|---|---|---|
| 7 | CSV dengan nama kolom snake_case | ✅ Pass | Kolom dicocokkan otomatis |
| 8 | CSV dengan kolom ekstra yang tidak dikenal | ✅ Pass | Kolom ekstra diabaikan |
| 9 | CSV dengan kolom yang kurang | ✅ Pass | Return 400 + daftar kolom hilang |

### Batch Result & Download

| # | Test | Status | Detail |
|---|---|---|---|
| 10 | `GET /api/predict/result/{session_id}` | ✅ Pass | Fetch 3 baris |
| 11 | `GET /api/predict/download/{session_id}` | ✅ Pass | CSV 3 baris |
| 12 | `GET /api/predict/template` | ✅ Pass | 19 kolom, 2 contoh baris |

### Insight & Filter

| # | Test | Status | Detail |
|---|---|---|---|
| 13 | `GET /api/insight/summary` — tanpa filter | ✅ Pass | `total=7 churn=0 rate=0.0%` |
| 14 | `GET /api/insight/summary?gender=Male` | ✅ Pass | `all=7 → gender=Male: 5` |
| 15 | `GET /api/insight/charts` — semua 6 dataset | ✅ Pass | `churn=0 non-churn=7` |
| 16 | `GET /api/insight/charts?marital_status=Single&city_tier=1` | ✅ Pass | Filter terapkan |

### Edge Cases & Cleanup

| # | Test | Status | Detail |
|---|---|---|---|
| 17 | `GET /api/predict/result/invalid` — session tidak ada | ✅ Pass | Return `404` |
| 18 | `DELETE /api/insight/clear` — reset semua data | ✅ Pass | Store kembali ke 0 |

---

## 4. Fitur Dashboard

### Halaman 1 — Dashboard (`/`)

Menampilkan insight agregat dari seluruh prediksi yang sudah dilakukan.

#### Filter Global
Tersedia di bagian atas halaman. Semua chart dan metric ikut berubah saat filter diterapkan.

| Filter | Pilihan |
|---|---|
| Gender | Male / Female / Semua |
| City Tier | Tier 1 / Tier 2 / Tier 3 / Semua |
| Marital Status | Single / Married / Divorced / Semua |
| Tenure Min | Input angka |
| Tenure Max | Input angka |

#### 4 Summary Card

| Card | ID | Isi |
|---|---|---|
| Total Pelanggan | `metricTotal` | Jumlah seluruh pelanggan yang diprediksi |
| Total Churn | `metricChurn` | Jumlah pelanggan yang diprediksi churn |
| Churn Rate | `metricChurnRate` | Persentase churn dari total |
| High Risk | `metricHighRisk` | Jumlah pelanggan dengan probabilitas ≥ 70% |

#### 6 Visualisasi Chart

| Chart | Tipe | ID Canvas | Data dari API |
|---|---|---|---|
| Distribusi Churn | Donut | `chartDonut` | `churn_distribution` |
| Distribusi Probabilitas | Histogram | `chartProbDist` | `probability_distribution` (10 bucket 0.0–1.0) |
| Churn by Tenure Group | Stacked Bar | `chartTenure` | `tenure_groups` (4 grup) |
| Churn by Kategori Produk | Horizontal Bar | `chartCategory` | `category_churn` |
| Churn by Marital Status | Grouped Bar | `chartMarital` | `marital_churn` |
| Churn by Payment Mode | Bar | `chartPayment` | `payment_churn` |

#### Tombol Aksi

| Tombol | Fungsi |
|---|---|
| Reset Filter | Kosongkan semua filter, reload chart |
| Reset Data | Hapus semua data prediksi dari server (dengan konfirmasi) |

#### Empty State
Tampil saat belum ada prediksi. Mengarahkan user ke halaman Predict.

---

### Halaman 2 — Predict (`/predict`)

#### Tab 1: Upload CSV

| Komponen | Fungsi |
|---|---|
| Drop Zone | Drag-and-drop atau klik untuk pilih file `.csv` |
| Download Template | Unduh contoh CSV dengan 2 baris data |
| Tombol Jalankan Prediksi | Kirim file ke server, tampilkan hasil |
| 4 Quick Stat Card | Total baris, Churn count, Medium Risk, High Risk |
| Tabel Preview | 10 baris pertama hasil prediksi dengan kolom Tenure, Gender, Marital, Tier, Probabilitas, Risk, Label |
| Tombol Lihat Semua | Pindah ke halaman Result dengan data penuh |
| Tombol Download CSV | Unduh seluruh hasil prediksi |

Validasi otomatis:
- Format file harus `.csv`
- Jika kolom kurang → tampilkan error dengan daftar kolom yang hilang
- Kolom ekstra di CSV diabaikan
- Nama kolom fleksibel (spasi, underscore, uppercase — semua dicocokkan)

#### Tab 2: Input Manual

Form 18 kolom:

| Kolom | Tipe Input |
|---|---|
| Tenure | Number (bulan) |
| City Tier | Dropdown (1 / 2 / 3) |
| Jarak Gudang ke Rumah | Number (km) |
| Gender | Dropdown (Male / Female) |
| Preferred Login Device | Dropdown (Mobile Phone / Computer) |
| Payment Mode | Dropdown (5 pilihan) |
| Jam di Aplikasi/Hari | Number |
| Jumlah Perangkat | Number |
| Kategori Produk Favorit | Dropdown (5 pilihan) |
| Satisfaction Score | Dropdown (1–5) |
| Marital Status | Dropdown (Single / Married / Divorced) |
| Jumlah Alamat | Number |
| Pernah Komplain? | Dropdown (Ya / Tidak) |
| Kenaikan Order YoY % | Number |
| Kupon Digunakan | Number |
| Jumlah Order Bulan Ini | Number |
| Hari Sejak Order Terakhir | Number |
| Cashback Amount | Number |

Panel hasil (muncul setelah submit):
- **Gauge Chart** — semi-circle menunjukkan probabilitas churn (0–100%)
- **Risk Badge** — Low / Medium / High dengan warna berbeda
- **Churn Label** — Churn atau Tidak Churn
- **Insight Teks** — 2–3 kalimat analisis berdasarkan nilai fitur (tenure, komplain, satisfaction, dll)

---

### Halaman 3 — Results (`/result`)

Menampilkan hasil lengkap prediksi batch dari sesi CSV terakhir.

#### 4 Summary Card
Total Rows, Churn Count, Churn Rate, High Risk — dihitung dari data batch.

#### 2 Chart
- **Donut** — Distribusi Churn vs Non-Churn dari batch
- **Bar** — Jumlah High / Medium / Low Risk dari batch

#### Tabel Lengkap

| Kolom | Keterangan |
|---|---|
| # | Nomor baris |
| Customer ID | Jika ada di CSV upload |
| Tenure | Lama berlangganan |
| Gender | Jenis kelamin |
| Marital | Status pernikahan |
| Tier | City tier |
| Kategori | Kategori produk favorit |
| Payment | Mode pembayaran |
| Probabilitas | Bar visual + angka persentase, warna sesuai risk |
| Risk | Badge Low / Medium / High |
| Label | Badge Churn / Aman |

Fitur tabel:
- **Sort** — klik header # / Tenure / Probabilitas untuk sort naik/turun
- **Search** — cari teks di semua kolom sekaligus
- **Filter Risk** — tampilkan hanya High / Medium / Low / Semua
- **Filter Label** — tampilkan hanya Churn / Non-Churn / Semua
- **Pagination** — 20 baris per halaman, navigasi bernomor

#### Tombol Download CSV
Mengunduh seluruh hasil batch (semua baris, bukan hanya preview) dalam format CSV.

---

## Cara Menjalankan

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan server
uvicorn app.main:app --reload

# Akses aplikasi
open http://localhost:8000

# Jalankan test (pastikan server sudah berjalan)
python test_api.py
```
