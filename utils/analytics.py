from __future__ import annotations

import numpy as np
import pandas as pd


def safe_mean(series: pd.Series) -> float:
    value = pd.to_numeric(series, errors="coerce").mean()
    return 0.0 if pd.isna(value) else float(value)


def safe_median(series: pd.Series) -> float:
    value = pd.to_numeric(series, errors="coerce").median()
    return 0.0 if pd.isna(value) else float(value)


def market_kpis(df: pd.DataFrame) -> dict[str, str]:
    if df.empty:
        return {}

    top_sector = df["sector"].mode().iat[0] if "sector" in df and not df["sector"].mode().empty else "NA"
    top_type = df["property_type"].mode().iat[0] if "property_type" in df and not df["property_type"].mode().empty else "NA"

    return {
        "total_properties": f"{len(df):,}",
        "avg_price": f"Rs {safe_mean(df['price']):.2f} Cr" if "price" in df else "NA",
        "median_price": f"Rs {safe_median(df['price']):.2f} Cr" if "price" in df else "NA",
        "avg_psf": f"Rs {safe_mean(df['price_per_sqft']):,.0f}" if "price_per_sqft" in df else "NA",
        "top_sector": str(top_sector).title(),
        "top_type": str(top_type).title(),
    }


def filter_properties(
    df: pd.DataFrame,
    sectors: list[str] | None = None,
    property_types: list[str] | None = None,
    bhks: list[float] | None = None,
    price_range: tuple[float, float] | None = None,
    area_range: tuple[float, float] | None = None,
    age_values: list[str] | None = None,
    furnishing_values: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()

    if sectors and "sector" in filtered:
        filtered = filtered[filtered["sector"].isin(sectors)]
    if property_types and "property_type" in filtered:
        filtered = filtered[filtered["property_type"].isin(property_types)]
    if bhks and "bedRoom" in filtered:
        filtered = filtered[filtered["bedRoom"].isin(bhks)]
    if price_range and "price" in filtered:
        filtered = filtered[filtered["price"].between(price_range[0], price_range[1], inclusive="both")]
    if area_range and "display_area" in filtered:
        filtered = filtered[filtered["display_area"].between(area_range[0], area_range[1], inclusive="both")]
    if age_values and "agePossession" in filtered:
        filtered = filtered[filtered["agePossession"].isin(age_values)]
    if furnishing_values and "furnishing_type" in filtered:
        filtered = filtered[filtered["furnishing_type"].isin(furnishing_values)]

    return filtered


def sector_scores(df: pd.DataFrame) -> pd.DataFrame:
    needed = {"sector", "price", "price_per_sqft", "display_area"}
    if df.empty or not needed.issubset(df.columns):
        return pd.DataFrame()

    grouped = (
        df.groupby("sector")
        .agg(
            availability=("sector", "size"),
            avg_price=("price", "mean"),
            median_price=("price", "median"),
            avg_psf=("price_per_sqft", "mean"),
            avg_area=("display_area", "mean"),
            avg_luxury=("luxury_score", "mean") if "luxury_score" in df else ("price", "size"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["availability"] >= 3].copy()
    if grouped.empty:
        return grouped

    grouped["affordability_score"] = 100 - percentile_rank(grouped["avg_psf"]) * 100
    grouped["liquidity_score"] = percentile_rank(grouped["availability"]) * 100
    grouped["luxury_score_norm"] = percentile_rank(grouped["avg_luxury"]) * 100
    grouped["area_score"] = percentile_rank(grouped["avg_area"]) * 100
    grouped["investment_score"] = (
        0.34 * grouped["affordability_score"]
        + 0.28 * grouped["liquidity_score"]
        + 0.22 * grouped["luxury_score_norm"]
        + 0.16 * grouped["area_score"]
    )
    grouped["market_health_score"] = (
        0.45 * grouped["liquidity_score"]
        + 0.25 * (100 - grouped["avg_price"].rank(pct=True) * 100)
        + 0.30 * grouped["luxury_score_norm"]
    )
    return grouped.sort_values("investment_score", ascending=False)


def percentile_rank(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0)
    if numeric.nunique() <= 1:
        return pd.Series(np.ones(len(numeric)) * 0.5, index=series.index)
    return numeric.rank(pct=True)


def society_scores(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "society" not in df:
        return pd.DataFrame()

    grouped = (
        df[df["society"].ne("Unknown")]
        .groupby("society")
        .agg(
            listings=("society", "size"),
            avg_price=("price", "mean"),
            median_psf=("price_per_sqft", "median"),
            avg_luxury=("luxury_score", "mean") if "luxury_score" in df else ("price", "size"),
            sector=("sector", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown"),
            property_type=("property_type", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["listings"] >= 2].copy()
    if grouped.empty:
        return grouped

    grouped["society_score"] = (
        percentile_rank(grouped["listings"]) * 30
        + percentile_rank(grouped["avg_luxury"]) * 35
        + percentile_rank(grouped["median_psf"]) * 20
        + percentile_rank(grouped["avg_price"]) * 15
    )
    return grouped.sort_values("society_score", ascending=False)


def outlier_properties(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty or "price_per_sqft" not in df:
        return pd.DataFrame(), pd.DataFrame()

    psf = pd.to_numeric(df["price_per_sqft"], errors="coerce")
    low = psf.quantile(0.05)
    high = psf.quantile(0.95)
    cols = [col for col in ["society", "sector", "property_type", "price", "price_per_sqft", "display_area", "luxury_score"] if col in df]
    return (
        df[psf <= low][cols].sort_values("price_per_sqft").head(20),
        df[psf >= high][cols].sort_values("price_per_sqft", ascending=False).head(20),
    )


def persona_recommendations(scores: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if scores.empty:
        return {}
    return {
        "First-time buyer": scores.sort_values(["affordability_score", "availability"], ascending=False).head(5),
        "Investor": scores.sort_values("investment_score", ascending=False).head(5),
        "Luxury buyer": scores.sort_values(["luxury_score_norm", "avg_price"], ascending=False).head(5),
        "Rental-yield focused buyer": scores.sort_values(["liquidity_score", "affordability_score"], ascending=False).head(5),
        "Family buyer": scores.sort_values(["area_score", "market_health_score"], ascending=False).head(5),
    }
