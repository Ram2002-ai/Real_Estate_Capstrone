from __future__ import annotations

import numpy as np
import pandas as pd


def recommend_properties(
    location_df: pd.DataFrame,
    cosine_sim1: np.ndarray,
    cosine_sim2: np.ndarray,
    cosine_sim3: np.ndarray,
    property_name: str,
    top_n: int = 5,
) -> pd.DataFrame:
    if location_df is None or property_name not in location_df.index:
        return pd.DataFrame()

    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + cosine_sim3
    idx = location_df.index.get_loc(property_name)
    sorted_scores = sorted(enumerate(cosine_sim_matrix[idx]), key=lambda x: x[1], reverse=True)
    top = sorted_scores[1 : top_n + 1]
    return pd.DataFrame(
        {
            "PropertyName": [location_df.index[i].title() for i, _ in top],
            "SimilarityScore": [float(score) for _, score in top],
        }
    )


def nearby_properties(location_df: pd.DataFrame, landmark: str, radius_km: float) -> pd.DataFrame:
    if location_df is None or landmark not in location_df.columns:
        return pd.DataFrame()

    distances = location_df[location_df[landmark] < radius_km * 1000][landmark].sort_values()
    return pd.DataFrame(
        {
            "PropertyName": [str(name).title() for name in distances.index],
            "DistanceKm": [float(distance) / 1000 for distance in distances.values],
        }
    )


def enrich_recommendations(recommendations: pd.DataFrame, properties: pd.DataFrame) -> pd.DataFrame:
    if recommendations.empty:
        return recommendations

    enriched = recommendations.copy()
    if properties.empty or "society" not in properties:
        return enriched

    lookup = properties.copy()
    lookup["_society_key"] = lookup["society"].astype(str).str.lower().str.strip()

    rows = []
    for _, rec in enriched.iterrows():
        key = str(rec["PropertyName"]).lower().strip()
        match = lookup[lookup["_society_key"].eq(key)]
        if match.empty:
            contains = lookup[lookup["_society_key"].str.contains(key, regex=False, na=False)]
            match = contains

        item = rec.to_dict()
        if not match.empty:
            row = match.iloc[0]
            for col in ["sector", "property_type", "price", "price_per_sqft", "luxury_score", "display_area"]:
                if col in row.index:
                    item[col] = row[col]
        rows.append(item)

    return pd.DataFrame(rows)


def recommendation_tags(row: pd.Series) -> list[str]:
    tags = ["Similar Lifestyle"]
    score = row.get("SimilarityScore")
    if pd.notna(score) and score >= 0.7:
        tags.append("Strong Match")
    if pd.notna(row.get("DistanceKm")):
        tags.append("Strong Location Match")
    if pd.notna(row.get("luxury_score")) and float(row.get("luxury_score")) >= 75:
        tags.append("Premium Amenities")
    price = row.get("price")
    if pd.notna(price) and float(price) <= 1.25:
        tags.append("Value Pick")
    return tags
