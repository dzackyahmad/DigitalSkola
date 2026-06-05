# E-Commerce Customer Churn Prediction
## Dokumentasi Proses Pengerjaan (CRISP-DM)

---

## 1. Business Understanding

**Masalah:** Perusahaan e-commerce tidak tahu pelanggan mana yang akan pergi (churn) sebelum kejadian terjadi. Akibatnya, anggaran retensi tersebar merata ke semua pelanggan — tidak efisien.

**Solusi:** Bangun model yang bisa memprediksi siapa yang akan churn, sehingga tim bisnis bisa fokus ke pelanggan berisiko tinggi saja.

**Target model:**
- Recall ≥ 80% — lebih penting ketemu churner daripada salah alarm
- F1-Score ≥ 80% — keseimbangan antara precision dan recall
- ROC-AUC ≥ 0.85 — kemampuan model membedakan churner vs non-churner

**Kenapa Recall diprioritaskan?**
Biaya kehilangan pelanggan (false negative) jauh lebih mahal daripada biaya salah kirim promo ke pelanggan yang sebenarnya tidak akan churn (false positive).

---

## 2. Data Understanding

**Dataset:** 5.630 pelanggan, 20 kolom (18 fitur + 1 target + 1 ID)

**Temuan penting:**

| Temuan | Detail |
|---|---|
| Missing values | 7 kolom numerik, 251–307 per kolom (~5%) |
| Duplikat | Tidak ada |
| Class imbalance | Non-Churn 83.2% vs Churn 16.8% |
| Inkonsistensi kategorikal | 3 kolom perlu diseragamkan |
| Outlier | 4 kolom dengan outlier signifikan |

**Fitur paling relevan terhadap churn:**
- `Tenure` — pelanggan baru (0–6 bulan) churn rate 25.9%, pelanggan 24+ bulan tidak ada yang churn
- `Complain` — pelanggan yang komplain churn rate 38.8%
- `CashbackAmount` — korelasi negatif, cashback rendah → lebih berisiko churn
- `MaritalStatus` — Single churn rate tertinggi (26.7%)

---

## 3. Data Preparation

**Prinsip utama:** Semua transformasi dilakukan setelah split data untuk menghindari data leakage.

### Urutan proses:

**Step 1 — Fix Inkonsistensi Kategorikal**
Dilakukan sebelum split karena ini hanya perbaikan penulisan, bukan transformasi statistik.
- `Phone` → `Mobile Phone`
- `CC` → `Credit Card`, `COD` → `Cash on Delivery`
- `Mobile Phone` → `Mobile`, `Laptop & Accessory` → `Laptop & Accessories`

**Step 2 — Feature Separation & Train-Test Split**
- Target (`Churn`) dan identifier (`CustomerID`) dipisahkan
- Split 80/20 dengan stratify — proporsi churn dijaga sama di train dan test

**Step 3 — Imputasi Missing Values**
- Menggunakan median dari `X_train` saja
- Diterapkan ke `X_train` dan `X_test`
- **Kenapa median dari train saja?** Karena di dunia nyata, data baru tidak punya statistik sendiri — harus menggunakan statistik yang dipelajari dari data historis (train)

**Step 4 — IQR Capping**
- Batas atas/bawah dihitung dari `X_train`
- Outlier di-cap ke batas tersebut, tidak dihapus
- **Kenapa capping, bukan drop?** Data outlier masih mengandung informasi perilaku pelanggan ekstrem yang valid

**Step 5 — Encoding & Scaling**
- StandardScaler untuk fitur numerik
- OneHotEncoder untuk fitur kategorikal
- Preprocessor di-fit dari `X_train`, di-transform ke `X_train` dan `X_test`

**Step 6 — SMOTE**
- Diterapkan hanya ke `X_train_processed`
- Train set menjadi balance: 3.746 Non-Churn, 3.746 Churn
- Test set tidak disentuh SMOTE — tetap distribusi asli

**Tidak ada Feature Engineering tambahan** — fitur yang ada sudah cukup informatif berdasarkan analisis korelasi dan distribusi.

---

## 4. Modeling

### 4.1 Baseline Model

8 model dilatih di `X_train_smote` dan dievaluasi di `X_test_processed`:

| Model | F1 Score | ROC-AUC |
|---|---|---|
| XGBoost | 0.960 | 0.999 |
| CatBoost | 0.920 | 0.997 |
| Random Forest | 0.898 | 0.995 |
| LightGBM | 0.876 | 0.990 |
| Decision Tree | 0.841 | 0.916 |
| SVC | 0.799 | 0.965 |
| KNN | 0.765 | 0.986 |
| Logistic Regression | 0.575 | 0.882 |

### 4.2 Cross-Validation

**Kenapa CV dilakukan ulang dengan pipeline?**

CV awal yang dilakukan di `X_train_smote` menghasilkan score inflated (~98%) karena SMOTE sudah bocor ke fold test. CV yang benar menggunakan pipeline `SMOTE → model` di dalam setiap fold dengan input `X_train_processed`.

Hasil CV yang benar (reliable):

| Model | CV F1 | CV Recall | CV ROC-AUC |
|---|---|---|---|
| XGBoost | 0.858 | 0.819 | 0.973 |
| CatBoost | 0.842 | 0.793 | 0.973 |
| LightGBM | 0.823 | 0.768 | 0.970 |
| Random Forest | 0.819 | 0.752 | 0.972 |

### 4.3 Hyperparameter Tuning

- Menggunakan `RandomizedSearchCV` dengan pipeline `SMOTE → model`
- Input: `X_train_processed` dan `y_train` — bukan `X_train_smote`
- CV: StratifiedKFold 5-fold
- Scoring: F1

**Kenapa tuning pakai pipeline juga?**
Sama seperti CV — SMOTE harus di-apply per fold di dalam tuning, bukan sebelumnya. Kalau di luar, best params yang dipilih berdasarkan score yang tidak jujur.

Hasil tuning:

| Model | Best CV F1 |
|---|---|
| LightGBM | 0.882 |
| SVC | 0.877 |
| XGBoost | 0.861 |
| CatBoost | 0.858 |

SVC tidak dipilih sebagai final model karena tidak memiliki feature importance — tidak bisa support business insight.

### 4.4 Final Model

Top-3 kandidat di-retrain dengan best params di `X_train_smote` dan dievaluasi di test set:

| Model | Precision | Recall | F1 Score | ROC-AUC |
|---|---|---|---|---|
| **LightGBM** | **1.000** | **0.968** | **0.984** | **0.9996** |
| XGBoost | 0.974 | 0.968 | 0.971 | 0.998 |
| CatBoost | 0.956 | 0.911 | 0.933 | 0.998 |

**Final model: LightGBM**

Best params:
```
num_leaves=31, n_estimators=300, max_depth=10, learning_rate=0.1
```

---

## 5. Evaluasi Final

### Confusion Matrix — LightGBM

|  | Predicted Non-Churn | Predicted Churn |
|---|---|---|
| **Actual Non-Churn** | 936 | 0 |
| **Actual Churn** | 6 | 184 |

- **936 True Negative** — Non-churner teridentifikasi dengan benar
- **0 False Positive** — Tidak ada pelanggan loyal yang salah di-flag
- **6 False Negative** — Hanya 6 churner yang tidak terdeteksi
- **184 True Positive** — Churner teridentifikasi dengan benar

### Feature Importance — LightGBM (Top 10)

| Fitur | Importance |
|---|---|
| Tenure | 0.129 |
| PreferedOrderCat_Mobile | 0.091 |
| Complain | 0.070 |
| PreferedOrderCat_Fashion | 0.066 |
| NumberOfDeviceRegistered | 0.048 |
| PreferedOrderCat_Laptop & Accessories | 0.044 |
| MaritalStatus_Married | 0.043 |
| PreferredPaymentMode_E-Wallet | 0.043 |
| MaritalStatus_Single | 0.040 |
| NumberOfAddress | 0.033 |

### Success Criteria — Terpenuhi

| Metric | Target | Hasil |
|---|---|---|
| Recall | ≥ 80% | 96.8% ✓ |
| F1-Score | ≥ 80% | 98.4% ✓ |
| ROC-AUC | ≥ 0.85 | 0.9996 ✓ |

---

## 6. Business Insight

1. **Tenure adalah faktor terkuat** — Fokus retensi pada 6 bulan pertama pelanggan baru. Program onboarding dan loyalty reward di awal masa berlangganan dapat menekan churn secara signifikan.

2. **Komplain = sinyal bahaya** — Pelanggan yang komplain memiliki churn rate 38.8%. Resolusi komplain yang cepat dan proaktif adalah intervensi retensi paling langsung.

3. **Kategori Mobile mendominasi churn** — Pelanggan yang membeli produk Mobile/Mobile Phone lebih berisiko churn. Perlu strategi retensi khusus untuk segmen ini.

4. **Pelanggan Single lebih berisiko** — Churn rate 26.7% vs Married 11.5%. Program retensi dapat disesuaikan berdasarkan segmen demografis ini.

5. **E-Wallet payment mode** — Masuk top feature importance. Pelanggan dengan metode pembayaran tertentu memiliki pola churn berbeda — perlu dianalisis lebih dalam.

---

## 7. Artifact yang Dihasilkan

| File | Deskripsi |
|---|---|
| `model_lightgbm.pkl` | Final model LightGBM siap deployment |
| `preprocessor.pkl` | ColumnTransformer (StandardScaler + OHE) |
| `X_train_smote.csv` | Training data setelah SMOTE |
| `X_test_processed.csv` | Test data setelah preprocessing |
| `y_train_smote.csv` | Label training setelah SMOTE |
| `y_test.csv` | Label test (distribusi asli) |

**Alur deployment:**
```
Data baru → preprocessor.pkl → transform → model_lightgbm.pkl → prediksi Churn + probabilitas
```
