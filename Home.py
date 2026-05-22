import pandas as pd
import plotly.express as px
import streamlit as st

from utils.analytics import market_kpis, sector_scores
from utils.data_loader import file_status, load_properties
from utils.ui import (
    BUILDING_IMAGES,
    hero,
    inject_global_css,
    metric_card,
    module_card,
    page_config,
    shell_start,
)


page_config("Realty Intelligence")
inject_global_css()
shell_start("Executive Dashboard")

df = load_properties()

hero(
    title="Real Estate",
    accent="Command Center",
    body=(
        "A buyer and investor intelligence platform for pricing, market analysis, "
        "property discovery, and sector-level decision signals."
    ),
    image_url=BUILDING_IMAGES[0],
    eyebrow="Production-grade analytics for property decisions",
)

if df.empty:
    st.error("Could not load the cleaned property dataset. Add the required data file to use the dashboard.")
    st.stop()

kpis = market_kpis(df)
st.markdown('<div class="section-title">Market Pulse</div>', unsafe_allow_html=True)
cols = st.columns(6)
cards = [
    ("Total Listings", kpis["total_properties"], "Cleaned property records"),
    ("Average Price", kpis["avg_price"], "Mean transaction ask"),
    ("Median Price", kpis["median_price"], "Typical market point"),
    ("Avg Price / Sqft", kpis["avg_psf"], "Across available listings"),
    ("Top Sector", kpis["top_sector"], "Highest listing density"),
    ("Dominant Type", kpis["top_type"], "Most common asset class"),
]
for col, (label, value, note) in zip(cols, cards):
    col.markdown(metric_card(label, value, note), unsafe_allow_html=True)

scores = sector_scores(df)
left, right = st.columns([1.15, 0.85])

with left:
    st.markdown('<div class="section-title">Market Snapshot</div>', unsafe_allow_html=True)
    top_snapshot = (
        df.groupby("sector")
        .agg(listings=("sector", "size"), avg_price=("price", "mean"), avg_psf=("price_per_sqft", "mean"))
        .reset_index()
        .sort_values("listings", ascending=False)
        .head(12)
    )
    fig = px.bar(
        top_snapshot,
        x="sector",
        y="listings",
        color="avg_price",
        color_continuous_scale=["#ffd8c7", "#ff4b2b", "#2b2726"],
        title="Most Active Sectors",
        labels={"sector": "Sector", "listings": "Listings", "avg_price": "Avg Price (Cr)"},
        template="plotly_white",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10), font=dict(color="#2b2726"))
    st.plotly_chart(fig, width="stretch")

with right:
    st.markdown('<div class="section-title">Decision Signals</div>', unsafe_allow_html=True)
    if not scores.empty:
        strongest = scores.iloc[0]
        affordable = scores.sort_values("affordability_score", ascending=False).iloc[0]
        premium = scores.sort_values("avg_price", ascending=False).iloc[0]
        st.markdown(
            metric_card(
                "Best Investment Signal",
                str(strongest["sector"]).title(),
                f"Score {strongest['investment_score']:.0f}/100 with {int(strongest['availability'])} listings",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_card(
                "Value Zone",
                str(affordable["sector"]).title(),
                f"Avg psf Rs {affordable['avg_psf']:,.0f}",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_card(
                "Premium Zone",
                str(premium["sector"]).title(),
                f"Avg price Rs {premium['avg_price']:.2f} Cr",
            ),
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-title">Product Modules</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
m1.markdown(
    module_card(
        "Price Prediction",
        "Estimate fair market value using the existing ML pipeline and production-style validation.",
        "ML Valuation",
    ),
    unsafe_allow_html=True,
)
m2.markdown(
    module_card(
        "Market Analysis",
        "Filter inventory and compare sectors, property types, price bands, and luxury signals.",
        "Analytics",
    ),
    unsafe_allow_html=True,
)
m3.markdown(
    module_card(
        "Recommendations",
        "Discover similar societies and location-radius matches with image-led property cards.",
        "Discovery",
    ),
    unsafe_allow_html=True,
)
m4.markdown(
    module_card(
        "Advanced Insights",
        "Use sector scoring, persona recommendations, outlier detection, and society rankings.",
        "Strategy",
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Deployment Readiness</div>', unsafe_allow_html=True)
status = file_status()
status_df = pd.DataFrame(
    [{"Artifact": name.replace("_", " ").title(), "Available": "Ready" if ok else "Missing"} for name, ok in status.items()]
)
st.dataframe(status_df, width="stretch", hide_index=True)
