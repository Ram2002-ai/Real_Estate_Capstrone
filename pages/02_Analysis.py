import plotly.express as px
import streamlit as st

from utils.analytics import filter_properties, market_kpis
from utils.data_loader import load_properties
from utils.ui import hero, inject_global_css, interpretation, metric_card, page_config, shell_start


page_config("Market Analysis")
inject_global_css()
shell_start("Market Analysis")

hero(
    title="Analyze Market",
    accent="Market Signals",
    body=(
        "Explore pricing, supply, configuration, luxury, and society-level patterns with "
        "filters built for real buyer and investor decisions."
    ),
    image_url="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1000&q=80",
    eyebrow="Interactive market intelligence",
)

df = load_properties()
if df.empty:
    st.error("Could not load cleaned property data.")
    st.stop()

with st.sidebar:
    st.header("Market Filters")
    sectors = st.multiselect("Sector", sorted(df["sector"].dropna().unique().tolist()))
    property_types = st.multiselect("Property Type", sorted(df["property_type"].dropna().unique().tolist()))
    bhks = st.multiselect("BHK", sorted(df["bedRoom"].dropna().unique().tolist())) if "bedRoom" in df else []

    min_price, max_price = float(df["price"].min()), float(df["price"].max())
    price_range = st.slider("Price Range (Cr)", min_price, max_price, (min_price, max_price), step=0.05)

    area_series = df["display_area"].dropna()
    min_area, max_area = float(area_series.min()), float(area_series.max())
    area_range = st.slider("Area Range (sq ft)", min_area, max_area, (min_area, max_area), step=25.0)

    age_values = st.multiselect("Age / Possession", sorted(df["agePossession"].dropna().unique().tolist()))
    furnishing_values = (
        st.multiselect("Furnishing", sorted(df["furnishing_type"].dropna().unique().tolist()))
        if "furnishing_type" in df
        else []
    )

filtered = filter_properties(
    df,
    sectors=sectors,
    property_types=property_types,
    bhks=bhks,
    price_range=price_range,
    area_range=area_range,
    age_values=age_values,
    furnishing_values=furnishing_values,
)

if filtered.empty:
    st.warning("No listings match the selected filters. Broaden the filters to continue.")
    st.stop()

kpis = market_kpis(filtered)
k1, k2, k3, k4 = st.columns(4)
k1.markdown(metric_card("Filtered Listings", kpis["total_properties"], "Current selection"), unsafe_allow_html=True)
k2.markdown(metric_card("Average Price", kpis["avg_price"], "Filtered market"), unsafe_allow_html=True)
k3.markdown(metric_card("Median Price", kpis["median_price"], "Less sensitive to outliers"), unsafe_allow_html=True)
k4.markdown(metric_card("Avg Price / Sqft", kpis["avg_psf"], "Filtered efficiency"), unsafe_allow_html=True)

palette = ["#ff4b2b", "#ff8a4a", "#2b2726", "#8a5a44", "#f0b08a"]

st.markdown('<div class="section-title">Sector Pricing</div>', unsafe_allow_html=True)
sector_price = (
    filtered.groupby("sector")
    .agg(avg_price=("price", "mean"), avg_psf=("price_per_sqft", "mean"), listings=("sector", "size"))
    .reset_index()
)
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(
        sector_price.sort_values("avg_price", ascending=False).head(15),
        x="sector",
        y="avg_price",
        color="avg_price",
        color_continuous_scale=["#ffd8c7", "#ff4b2b", "#2b2726"],
        title="Highest Average Price By Sector",
        labels={"avg_price": "Avg Price (Cr)", "sector": "Sector"},
        template="plotly_white",
    )
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
    interpretation("Premium sectors typically combine scarcity, larger configurations, and stronger amenity positioning.")

with c2:
    fig = px.bar(
        sector_price.sort_values("avg_psf", ascending=False).head(15),
        x="sector",
        y="avg_psf",
        color="avg_psf",
        color_continuous_scale=["#ffe1d2", "#ff7a2b", "#2b2726"],
        title="Highest Price Per Sqft By Sector",
        labels={"avg_psf": "Avg Price / Sqft", "sector": "Sector"},
        template="plotly_white",
    )
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
    interpretation("Price per sqft is the cleanest cross-sector efficiency metric when area sizes vary heavily.")

st.markdown('<div class="section-title">Distribution And Mix</div>', unsafe_allow_html=True)
d1, d2 = st.columns(2)
with d1:
    fig = px.histogram(
        filtered,
        x="price",
        nbins=35,
        color="property_type",
        color_discrete_sequence=palette,
        title="Price Distribution",
        labels={"price": "Price (Cr)"},
        template="plotly_white",
    )
    fig.update_layout(height=410, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
with d2:
    fig = px.histogram(
        filtered,
        x="bedRoom",
        color="property_type",
        barmode="group",
        color_discrete_sequence=palette,
        title="BHK Availability",
        labels={"bedRoom": "Bedrooms"},
        template="plotly_white",
    )
    fig.update_layout(height=410, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
interpretation("The distribution view helps separate entry-level supply from family-size and premium inventory clusters.")

st.markdown('<div class="section-title">Area, Luxury, And Asset Type</div>', unsafe_allow_html=True)
a1, a2 = st.columns(2)
with a1:
    fig = px.scatter(
        filtered,
        x="display_area",
        y="price",
        color="bedRoom",
        size="bathroom" if "bathroom" in filtered else None,
        hover_data=[col for col in ["society", "sector", "property_type"] if col in filtered],
        title="Price vs Built-up Area",
        labels={"display_area": "Area (sq ft)", "price": "Price (Cr)"},
        template="plotly_white",
        color_continuous_scale=["#ffbf9d", "#ff4b2b", "#2b2726"],
    )
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
with a2:
    if "luxury_score" in filtered:
        fig = px.scatter(
            filtered,
            x="luxury_score",
            y="price",
            color="property_type",
            hover_data=[col for col in ["society", "sector"] if col in filtered],
            title="Luxury Score vs Price",
            labels={"luxury_score": "Luxury Score", "price": "Price (Cr)"},
            template="plotly_white",
            color_discrete_sequence=palette,
        )
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Luxury score is not available in this dataset.")
interpretation("Area explains baseline utility, while luxury score reveals willingness-to-pay premiums above pure size.")

st.markdown('<div class="section-title">Affordable And Premium Sectors</div>', unsafe_allow_html=True)
p1, p2, p3 = st.columns(3)
affordable = sector_price[sector_price["listings"] >= 3].sort_values("avg_psf").head(10)
premium = sector_price[sector_price["listings"] >= 3].sort_values("avg_price", ascending=False).head(10)
type_split = filtered["property_type"].value_counts().reset_index()
type_split.columns = ["property_type", "count"]
with p1:
    st.dataframe(affordable, width="stretch", hide_index=True)
with p2:
    st.dataframe(premium, width="stretch", hide_index=True)
with p3:
    fig = px.pie(
        type_split,
        names="property_type",
        values="count",
        hole=0.45,
        title="Property Type Split",
        color_discrete_sequence=palette,
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")

if "society" in filtered:
    st.markdown('<div class="section-title">Society-Level Comparison</div>', unsafe_allow_html=True)
    society_df = (
        filtered[filtered["society"].ne("Unknown")]
        .groupby("society")
        .agg(listings=("society", "size"), avg_price=("price", "mean"), avg_psf=("price_per_sqft", "mean"))
        .reset_index()
    )
    society_df = society_df[society_df["listings"] >= 2].sort_values("avg_price", ascending=False).head(20)
    if not society_df.empty:
        fig = px.bar(
            society_df,
            x="avg_price",
            y="society",
            orientation="h",
            color="avg_psf",
            color_continuous_scale=["#ffd8c7", "#ff4b2b", "#2b2726"],
            title="Top Societies By Average Price",
            labels={"avg_price": "Avg Price (Cr)", "society": "Society", "avg_psf": "Avg PSF"},
            template="plotly_white",
        )
        fig.update_layout(height=620, margin=dict(l=10, r=10, t=55, b=10), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")
        interpretation("Society-level comparisons are most reliable when a society has multiple available records.")
