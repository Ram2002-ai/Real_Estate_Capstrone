import pandas as pd
import streamlit as st

from utils.data_loader import load_properties, load_recommendation_resources
from utils.recommender import enrich_recommendations, nearby_properties, recommend_properties, recommendation_tags
from utils.ui import hero, image_for_name, inject_global_css, page_config, property_card, shell_start


page_config("Smart Recommendations")
inject_global_css()
shell_start("Property Recommendations")

hero(
    title="Find Better",
    accent="Property Matches",
    body=(
        "Search near landmarks or start from a society you like. The recommender blends "
        "location distance and multiple similarity matrices to surface practical alternatives."
    ),
    image_url="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    eyebrow="Similarity and location based discovery",
)

properties = load_properties()
location_df, cosine_sim1, cosine_sim2, cosine_sim3 = load_recommendation_resources()

if location_df is None:
    st.error("Recommendation resources are missing. Please ensure location and cosine similarity pickles exist.")
    st.stop()

tab1, tab2 = st.tabs(["Location Radius Search", "Similar Society Recommendations"])

with tab1:
    st.markdown('<div class="section-title">Properties Near A Landmark</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        selected_location = st.selectbox("Landmark / Location", sorted(location_df.columns.tolist()))
    with c2:
        radius = st.slider("Radius (km)", 1, 50, 5)
    with c3:
        limit = st.slider("Results", 5, 30, 10, key="nearby_limit")

    if st.button("Search Nearby Properties"):
        nearby = nearby_properties(location_df, selected_location, radius).head(limit)
        enriched = enrich_recommendations(nearby, properties)
        if enriched.empty:
            st.info("No properties found in this radius. Increase the radius or choose another landmark.")
        else:
            st.success(f"Found {len(enriched)} properties within {radius} km of {selected_location}.")
            for _, row in enriched.iterrows():
                name = row["PropertyName"]
                prop_type = str(row.get("property_type", "flat"))
                meta = [
                    f"{row.get('DistanceKm', 0):.2f} km from {selected_location}",
                    f"Sector: {str(row.get('sector', 'Unknown')).title()}",
                    f"Type: {prop_type.title()}",
                ]
                if pd.notna(row.get("price")):
                    meta.append(f"Indicative avg price: Rs {float(row['price']):.2f} Cr")
                st.markdown(
                    property_card(
                        name,
                        meta,
                        recommendation_tags(row),
                        image_for_name(name, prop_type),
                    ),
                    unsafe_allow_html=True,
                )

            table_cols = [col for col in ["PropertyName", "DistanceKm", "sector", "property_type", "price", "price_per_sqft"] if col in enriched]
            st.markdown('<div class="section-title">Comparison Table</div>', unsafe_allow_html=True)
            st.dataframe(enriched[table_cols], width="stretch", hide_index=True)

with tab2:
    st.markdown('<div class="section-title">Similar Properties</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        selected_property = st.selectbox("Reference Society / Property", sorted(location_df.index.astype(str).tolist()))
    with c2:
        top_n = st.slider("Recommendations", 3, 15, 6)

    if st.button("Get Similar Recommendations"):
        recs = recommend_properties(location_df, cosine_sim1, cosine_sim2, cosine_sim3, selected_property, top_n=top_n)
        enriched = enrich_recommendations(recs, properties)

        if enriched.empty:
            st.info("No similar recommendations could be generated for this property.")
        else:
            st.success(f"Showing properties similar to {selected_property.title()}.")
            for _, row in enriched.iterrows():
                name = row["PropertyName"]
                prop_type = str(row.get("property_type", "flat"))
                meta = [
                    f"Sector: {str(row.get('sector', 'Unknown')).title()}",
                    f"Type: {prop_type.title()}",
                ]
                if pd.notna(row.get("price")):
                    meta.append(f"Indicative avg price: Rs {float(row['price']):.2f} Cr")
                if pd.notna(row.get("price_per_sqft")):
                    meta.append(f"Avg psf: Rs {float(row['price_per_sqft']):,.0f}")

                st.markdown(
                    property_card(
                        name,
                        meta,
                        recommendation_tags(row),
                        image_for_name(name, prop_type),
                        score=float(row.get("SimilarityScore", 0)),
                    ),
                    unsafe_allow_html=True,
                )

            table_cols = [
                col
                for col in ["PropertyName", "SimilarityScore", "sector", "property_type", "price", "price_per_sqft", "luxury_score"]
                if col in enriched
            ]
            st.markdown('<div class="section-title">Recommendation Comparison</div>', unsafe_allow_html=True)
            st.dataframe(enriched[table_cols], width="stretch", hide_index=True)
