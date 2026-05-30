import numpy as np
import pandas as pd
import joblib
from pathlib import Path

# ---------------------------------------------------------------------------
# MODEL_ENABLED flag
# Set to True  → load real pkl files and run XGBoost inference
# Set to False → skip model loading, return mock prediction for every row
# ---------------------------------------------------------------------------
MODEL_ENABLED = False

_MODELS_DIR = Path(__file__).parent.parent / "models"

# Loaded once at startup (only when MODEL_ENABLED = True)
_label_encoder = None
_ohe = None
_scaler = None
_model = None

# Categorical value corrections from notebook preprocessing
_LOGIN_DEVICE_MAP = {"Phone": "Mobile Phone"}
_PAYMENT_MAP = {"CC": "Credit Card", "COD": "Cash on Delivery"}
_ORDER_CAT_MAP = {"Mobile": "Mobile Phone"}

# Exact column order expected by scaler and model
_FEATURE_COLUMNS = [
    "Tenure", "CityTier", "WarehouseToHome", "Gender", "HourSpendOnApp",
    "NumberOfDeviceRegistered", "SatisfactionScore", "NumberOfAddress",
    "Complain", "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount",
    "DaySinceLastOrder", "CashbackAmount", "Complain_x_Satisfaction",
    "CouponPerOrder", "CashbackPerOrder", "log_CouponUsed", "log_OrderCount",
    "log_WarehouseToHome", "log_DaySinceLastOrder", "log_CashbackAmount",
    "log_NumberOfAddress", "PreferredLoginDevice_Mobile Phone",
    "PreferredPaymentMode_Credit Card", "PreferredPaymentMode_Debit Card",
    "PreferredPaymentMode_E wallet", "PreferredPaymentMode_UPI",
    "PreferedOrderCat_Grocery", "PreferedOrderCat_Laptop & Accessory",
    "PreferedOrderCat_Mobile Phone", "PreferedOrderCat_Others",
    "MaritalStatus_Married", "MaritalStatus_Single",
]


def load_models():
    if not MODEL_ENABLED:
        return
    global _label_encoder, _ohe, _scaler, _model
    _label_encoder = joblib.load(_MODELS_DIR / "label_encoder.pkl")
    _ohe = joblib.load(_MODELS_DIR / "ohe_fe.pkl")
    _scaler = joblib.load(_MODELS_DIR / "scaler_fe.pkl")
    _model = joblib.load(_MODELS_DIR / "xgboost_churn_final.pkl")


def _fix_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "PreferredLoginDevice" in df.columns:
        df["PreferredLoginDevice"] = df["PreferredLoginDevice"].replace(_LOGIN_DEVICE_MAP)
    if "PreferredPaymentMode" in df.columns:
        df["PreferredPaymentMode"] = df["PreferredPaymentMode"].replace(_PAYMENT_MAP)
    if "PreferedOrderCat" in df.columns:
        df["PreferedOrderCat"] = df["PreferedOrderCat"].replace(_ORDER_CAT_MAP)
    return df


def _feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Complain_x_Satisfaction"] = df["Complain"] * df["SatisfactionScore"]
    df["CouponPerOrder"] = df["CouponUsed"] / (df["OrderCount"] + 1)
    df["CashbackPerOrder"] = df["CashbackAmount"] / (df["OrderCount"] + 1)
    df["log_CouponUsed"] = np.log1p(df["CouponUsed"])
    df["log_OrderCount"] = np.log1p(df["OrderCount"])
    df["log_WarehouseToHome"] = np.log1p(df["WarehouseToHome"])
    df["log_DaySinceLastOrder"] = np.log1p(df["DaySinceLastOrder"])
    df["log_CashbackAmount"] = np.log1p(df["CashbackAmount"])
    df["log_NumberOfAddress"] = np.log1p(df["NumberOfAddress"])
    return df


def _label_encode_gender(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Gender"] = _label_encoder.transform(df["Gender"])
    return df


def _one_hot_encode(df: pd.DataFrame) -> pd.DataFrame:
    ohe_cols = ["PreferredLoginDevice", "PreferredPaymentMode", "PreferedOrderCat", "MaritalStatus"]
    ohe_result = _ohe.transform(df[ohe_cols])
    ohe_df = pd.DataFrame(ohe_result, columns=_ohe.get_feature_names_out(), index=df.index)
    df = df.drop(columns=ohe_cols)
    df = pd.concat([df, ohe_df], axis=1)
    return df


def _scale(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Ensure correct column order; fill missing OHE cols with 0
    for col in _FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
    df = df[_FEATURE_COLUMNS]
    scaled = _scaler.transform(df)
    return pd.DataFrame(scaled, columns=_FEATURE_COLUMNS, index=df.index)


def _get_risk_level(prob: float) -> str:
    if prob < 0.3:
        return "Low"
    elif prob < 0.7:
        return "Medium"
    return "High"


def run_pipeline(df: pd.DataFrame) -> list[dict]:
    """
    Full inference pipeline.
    Input: raw DataFrame with 18 original feature columns.
    Returns: list of dicts with churn_label, churn_probability, risk_level.

    When MODEL_ENABLED = False, returns mock output for every row so the app
    stays fully functional without loading any .pkl files.
    """
    if not MODEL_ENABLED:
        return [
            {"churn_label": 0, "churn_probability": 0.0, "risk_level": "Low"}
            for _ in range(len(df))
        ]

    df = _fix_categoricals(df)
    df = _feature_engineering(df)
    df = _label_encode_gender(df)
    df = _one_hot_encode(df)
    df_scaled = _scale(df)

    probas = _model.predict_proba(df_scaled)[:, 1]
    labels = (probas >= 0.5).astype(int)

    results = []
    for label, prob in zip(labels, probas):
        results.append({
            "churn_label": int(label),
            "churn_probability": round(float(prob), 4),
            "risk_level": _get_risk_level(float(prob)),
        })
    return results


def predict_single(data: dict) -> dict:
    df = pd.DataFrame([data])
    results = run_pipeline(df)
    return results[0]


def predict_batch(df: pd.DataFrame) -> list[dict]:
    return run_pipeline(df)
