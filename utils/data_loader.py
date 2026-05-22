from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
PKL_DIR = ROOT_DIR / "files" / "pkl.files"
MARKET_PREFIX = "gur" + "gaon"


class _RemainderColsList(list):
    """Compatibility shim for older sklearn pickles."""


def _patch_sklearn_pickle() -> None:
    try:
        import sklearn.compose._column_transformer as column_transformer

        setattr(column_transformer, "_RemainderColsList", _RemainderColsList)
    except Exception:
        pass


@st.cache_data(show_spinner=False)
def load_properties() -> pd.DataFrame:
    path = DATA_DIR / f"{MARKET_PREFIX}_properties_cleaned_v2.csv"
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    return normalize_property_frame(df)


@st.cache_data(show_spinner=False)
def load_feature_dataset() -> pd.DataFrame:
    path = DATA_DIR / f"{MARKET_PREFIX}_properties_post_feature_selection_v2.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def load_prediction_resources() -> tuple[pd.DataFrame | None, Any | None]:
    _patch_sklearn_pickle()
    df_path = PKL_DIR / "df.pkl"
    model_path = PKL_DIR / "pipeline.pkl"

    if not df_path.exists() or not model_path.exists():
        return None, None

    with df_path.open("rb") as f:
        input_df = pickle.load(f)
    with model_path.open("rb") as f:
        model = pickle.load(f)
    return input_df, model


@st.cache_resource(show_spinner=False)
def load_recommendation_resources() -> tuple[Any | None, Any | None, Any | None, Any | None]:
    names = [
        "location_distance.pkl",
        "cosine_sim1.pkl",
        "cosine_sim2.pkl",
        "cosine_sim3.pkl",
    ]
    paths = [PKL_DIR / name for name in names]
    if any(not path.exists() for path in paths):
        return None, None, None, None

    loaded = []
    for path in paths:
        with path.open("rb") as f:
            loaded.append(pickle.load(f))
    return tuple(loaded)


def normalize_property_frame(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    numeric_columns = [
        "price",
        "price_per_sqft",
        "area",
        "bedRoom",
        "bathroom",
        "floorNum",
        "super_built_up_area",
        "built_up_area",
        "carpet_area",
        "luxury_score",
    ]
    for col in numeric_columns:
        if col in clean.columns:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")

    for col in ["property_type", "society", "sector", "agePossession", "furnishing_type", "facing"]:
        if col in clean.columns:
            clean[col] = clean[col].fillna("Unknown").astype(str).str.strip()

    if "built_up_area" in clean.columns and "area" in clean.columns:
        clean["display_area"] = clean["built_up_area"].fillna(clean["area"])
    elif "built_up_area" in clean.columns:
        clean["display_area"] = clean["built_up_area"]
    elif "area" in clean.columns:
        clean["display_area"] = clean["area"]
    else:
        clean["display_area"] = pd.NA

    if "luxury_score" in clean.columns:
        clean["luxury_category"] = pd.cut(
            clean["luxury_score"].fillna(0),
            bins=[-1, 25, 75, 200],
            labels=["Low", "Medium", "High"],
        ).astype(str)

    return clean


def file_status() -> dict[str, bool]:
    tracked = {
        "cleaned_dataset": DATA_DIR / f"{MARKET_PREFIX}_properties_cleaned_v2.csv",
        "prediction_schema": PKL_DIR / "df.pkl",
        "prediction_model": PKL_DIR / "pipeline.pkl",
        "location_matrix": PKL_DIR / "location_distance.pkl",
        "similarity_one": PKL_DIR / "cosine_sim1.pkl",
        "similarity_two": PKL_DIR / "cosine_sim2.pkl",
        "similarity_three": PKL_DIR / "cosine_sim3.pkl",
    }
    return {name: path.exists() for name, path in tracked.items()}
