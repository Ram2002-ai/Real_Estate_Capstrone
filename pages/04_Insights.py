import pandas as pd
import plotly.express as px
import streamlit as st

from utils.analytics import filter_properties, outlier_properties, sector_scores, society_scores
from utils.data_loader import load_properties
from utils.ui import hero, inject_global_css, insight_card, metric_card, page_config, shell_start, table_card


page_config("Advanced Insights")
inject_global_css()
shell_start("Advanced Insights")

hero(
    title="Buyer",
    accent="Decision Studio",
    body=(
        "Convert listings into a practical buying plan: set your goal and budget, compare sectors, "
        "shortlist societies, spot risk, and export the exact records behind the recommendation."
    ),
    image_url="https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80",
    eyebrow="Personalized property decision workflow",
)

df = load_properties()
if df.empty:
    st.error("Could not load cleaned property data.")
    st.stop()


def title_case(value: object) -> str:
    return str(value).replace("_", " ").title()


def money_cr(value: float) -> str:
    return f"Rs {value:.2f} Cr"


def psf(value: float) -> str:
    return f"Rs {value:,.0f}"


def readable_sector_table(data: pd.DataFrame) -> pd.DataFrame:
    cols = ["sector", "avg_price", "avg_psf", "availability", "investment_score", "market_health_score", "avg_area"]
    available = [col for col in cols if col in data]
    table = data[available].copy()
    rename = {
        "sector": "Sector",
        "avg_price": "Avg Price",
        "avg_psf": "Avg Price/Sqft",
        "availability": "Listings",
        "investment_score": "Investment",
        "market_health_score": "Health",
        "avg_area": "Avg Area",
    }
    table = table.rename(columns=rename)
    if "Sector" in table:
        table["Sector"] = table["Sector"].map(title_case)
    if "Avg Price" in table:
        table["Avg Price"] = table["Avg Price"].map(money_cr)
    if "Avg Price/Sqft" in table:
        table["Avg Price/Sqft"] = table["Avg Price/Sqft"].map(psf)
    for col in ["Investment", "Health"]:
        if col in table:
            table[col] = table[col].round(0).astype(int).astype(str) + "/100"
    if "Avg Area" in table:
        table["Avg Area"] = table["Avg Area"].round(0).astype("Int64").astype(str) + " sq ft"
    return table


def readable_property_table(data: pd.DataFrame) -> pd.DataFrame:
    cols = ["society", "sector", "property_type", "price", "price_per_sqft", "display_area", "bedRoom", "luxury_score"]
    available = [col for col in cols if col in data]
    table = data[available].copy()
    table = table.rename(
        columns={
            "society": "Society",
            "sector": "Sector",
            "property_type": "Type",
            "price": "Price",
            "price_per_sqft": "Price/Sqft",
            "display_area": "Area",
            "bedRoom": "BHK",
            "luxury_score": "Luxury",
        }
    )
    for col in ["Society", "Sector", "Type"]:
        if col in table:
            table[col] = table[col].map(title_case)
    if "Price" in table:
        table["Price"] = table["Price"].map(money_cr)
    if "Price/Sqft" in table:
        table["Price/Sqft"] = table["Price/Sqft"].map(psf)
    if "Area" in table:
        table["Area"] = table["Area"].round(0).astype("Int64").astype(str) + " sq ft"
    if "BHK" in table:
        table["BHK"] = table["BHK"].round(0).astype("Int64").astype(str)
    if "Luxury" in table:
        table["Luxury"] = table["Luxury"].round(0).astype("Int64").astype(str)
    return table


with st.sidebar:
    st.header("Decision Inputs")
    goal = st.selectbox(
        "Buying Goal",
        ["Balanced shortlist", "First home", "Investment", "Luxury upgrade", "Family home", "Value hunting"],
    )
    budget = st.slider("Maximum Budget (Cr)", 0.25, float(df["price"].quantile(0.98)), 2.0, step=0.05)
    min_bhk = st.slider("Minimum BHK", 1, int(max(1, df["bedRoom"].max())), 2)
    min_area = st.slider("Minimum Area (sq ft)", 250, int(df["display_area"].quantile(0.98)), 900, step=50)
    preferred_types = st.multiselect("Property Type", sorted(df["property_type"].dropna().unique().tolist()))
    selected_sectors = st.multiselect("Preferred Sectors", sorted(df["sector"].dropna().unique().tolist()))

filtered = filter_properties(
    df,
    sectors=selected_sectors,
    property_types=preferred_types,
    price_range=(float(df["price"].min()), budget),
    area_range=(float(min_area), float(df["display_area"].max())),
)
if "bedRoom" in filtered:
    filtered = filtered[filtered["bedRoom"] >= min_bhk]

if filtered.empty:
    st.warning("No properties match your current decision inputs. Increase budget, reduce BHK/area, or clear sector filters.")
    st.stop()

scores = sector_scores(filtered)
societies = society_scores(filtered)

target_map = {
    "Balanced shortlist": ("investment_score", False, "Balanced value, health, supply, and quality."),
    "First home": ("affordability_score", False, "Prioritizes lower price per sqft and enough available supply."),
    "Investment": ("investment_score", False, "Prioritizes value plus liquidity and quality signals."),
    "Luxury upgrade": ("luxury_score_norm", False, "Prioritizes stronger luxury signals and premium positioning."),
    "Family home": ("area_score", False, "Prioritizes larger average area and livability signals."),
    "Value hunting": ("affordability_score", False, "Prioritizes sectors that look cheaper on price per sqft."),
}
sort_col, _, goal_reason = target_map[goal]

st.markdown('<div class="section-title">Your Decision Summary</div>', unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
d1.markdown(metric_card("Matching Listings", f"{len(filtered):,}", "After your filters"), unsafe_allow_html=True)
d2.markdown(metric_card("Budget Ceiling", money_cr(budget), goal), unsafe_allow_html=True)
d3.markdown(metric_card("Median Match Price", money_cr(filtered["price"].median()), "Current shortlist"), unsafe_allow_html=True)
d4.markdown(metric_card("Median Price/Sqft", psf(filtered["price_per_sqft"].median()), "Value benchmark"), unsafe_allow_html=True)

if not scores.empty:
    best = scores.sort_values(sort_col, ascending=False).iloc[0]
    safest = scores.sort_values("market_health_score", ascending=False).iloc[0]
    value = scores.sort_values("affordability_score", ascending=False).iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        insight_card(
            "Best Fit For Your Goal",
            f"{title_case(best['sector'])} ranks strongest for '{goal.lower()}'. {goal_reason}",
            "Shortlist",
        ),
        unsafe_allow_html=True,
    )
    c2.markdown(
        insight_card(
            "Lowest Friction Market",
            f"{title_case(safest['sector'])} has the strongest market health score, suggesting better liquidity and comparison depth.",
            "Confidence",
        ),
        unsafe_allow_html=True,
    )
    c3.markdown(
        insight_card(
            "Best Value Signal",
            f"{title_case(value['sector'])} currently offers the strongest affordability signal among matching listings.",
            "Value",
        ),
        unsafe_allow_html=True,
    )

    table_card("Recommended Sector Shortlist", "Ranked by the buying goal you selected, with only the columns a buyer actually needs first.")
    ranked = scores.sort_values(sort_col, ascending=False).head(12)
    st.dataframe(readable_sector_table(ranked), width="stretch", hide_index=True, row_height=38)

    fig = px.scatter(
        scores,
        x="avg_psf",
        y=sort_col,
        size="availability",
        color="market_health_score",
        hover_name="sector",
        color_continuous_scale=["#ffd8c7", "#ff4b2b", "#2b2726"],
        title="Where Value Meets Your Goal",
        labels={"avg_psf": "Avg Price/Sqft", sort_col: goal, "market_health_score": "Health"},
        template="plotly_white",
    )
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")

st.markdown('<div class="section-title">Property Shortlist Builder</div>', unsafe_allow_html=True)
shortlist_basis = st.radio(
    "Shortlist Strategy",
    ["Lowest total price", "Lowest price per sqft", "Highest luxury score", "Largest area"],
    horizontal=True,
)
sort_map = {
    "Lowest total price": ("price", True),
    "Lowest price per sqft": ("price_per_sqft", True),
    "Highest luxury score": ("luxury_score", False),
    "Largest area": ("display_area", False),
}
prop_sort_col, ascending = sort_map[shortlist_basis]
shortlist = filtered.sort_values(prop_sort_col, ascending=ascending).head(25)
table_card("Readable Property Shortlist", "Use this as the first practical list for calls, visits, and negotiation checks.")
st.dataframe(readable_property_table(shortlist), width="stretch", hide_index=True, row_height=38)

st.markdown('<div class="section-title">Society Ranking</div>', unsafe_allow_html=True)
if societies.empty:
    st.info("Not enough society-level records are available after your filters.")
else:
    society_view = societies.head(20).rename(
        columns={
            "society": "Society",
            "sector": "Sector",
            "property_type": "Type",
            "listings": "Listings",
            "avg_price": "Avg Price",
            "median_psf": "Median Price/Sqft",
            "avg_luxury": "Luxury",
            "society_score": "Score",
        }
    )
    society_view["Society"] = society_view["Society"].map(title_case)
    society_view["Sector"] = society_view["Sector"].map(title_case)
    society_view["Type"] = society_view["Type"].map(title_case)
    society_view["Avg Price"] = society_view["Avg Price"].map(money_cr)
    society_view["Median Price/Sqft"] = society_view["Median Price/Sqft"].map(psf)
    society_view["Luxury"] = society_view["Luxury"].round(0).astype(int).astype(str)
    society_view["Score"] = society_view["Score"].round(0).astype(int).astype(str) + "/100"
    st.dataframe(
        society_view[["Society", "Sector", "Type", "Listings", "Avg Price", "Median Price/Sqft", "Luxury", "Score"]],
        width="stretch",
        hide_index=True,
        row_height=38,
    )

st.markdown('<div class="section-title">Risk And Negotiation Flags</div>', unsafe_allow_html=True)
low_outliers, high_outliers = outlier_properties(filtered)
r1, r2 = st.columns(2)
with r1:
    table_card("Possible Negotiation Leads", "Very low price-per-sqft records. Check condition, floor, possession, and data quality before treating these as bargains.")
    if low_outliers.empty:
        st.info("No unusually low price-per-sqft records found.")
    else:
        st.dataframe(readable_property_table(low_outliers.head(12)), width="stretch", hide_index=True, row_height=38)
with r2:
    table_card("Premium Or Overpriced Watchlist", "Very high price-per-sqft records. These may be justified by quality, scarcity, or brand, but need stronger evidence.")
    if high_outliers.empty:
        st.info("No unusually high price-per-sqft records found.")
    else:
        st.dataframe(readable_property_table(high_outliers.head(12)), width="stretch", hide_index=True, row_height=38)

st.markdown('<div class="section-title">Compare Two Sectors</div>', unsafe_allow_html=True)
sector_options = sorted(filtered["sector"].dropna().unique().tolist())
if len(sector_options) >= 2 and not scores.empty:
    s1, s2 = st.columns(2)
    with s1:
        left_sector = st.selectbox("First Sector", sector_options, index=0)
    with s2:
        right_sector = st.selectbox("Second Sector", sector_options, index=min(1, len(sector_options) - 1))
    compare = scores[scores["sector"].isin([left_sector, right_sector])]
    st.dataframe(readable_sector_table(compare), width="stretch", hide_index=True, row_height=42)

    if len(compare) == 2:
        left = compare.iloc[0]
        right = compare.iloc[1]
        better_value = left if left["avg_psf"] < right["avg_psf"] else right
        better_health = left if left["market_health_score"] > right["market_health_score"] else right
        st.markdown(
            insight_card(
                "Comparison Takeaway",
                f"{title_case(better_value['sector'])} is cheaper on price per sqft, while {title_case(better_health['sector'])} has the stronger market health score.",
                "Decision",
            ),
            unsafe_allow_html=True,
        )
else:
    st.info("Select a broader filter set to compare sectors.")

st.markdown('<div class="section-title">Next Action Plan</div>', unsafe_allow_html=True)
a1, a2, a3 = st.columns(3)
a1.markdown(
    insight_card(
        "Call List",
        "Start with the readable property shortlist. Remove records with missing society names or unrealistic area-price combinations.",
        "Step 1",
    ),
    unsafe_allow_html=True,
)
a2.markdown(
    insight_card(
        "Visit Plan",
        "Prioritize sectors that appear in both your goal shortlist and society ranking. That overlap is your strongest practical signal.",
        "Step 2",
    ),
    unsafe_allow_html=True,
)
a3.markdown(
    insight_card(
        "Negotiation",
        "Use median price per sqft from your shortlist as the anchor, then adjust for floor, condition, furnishing, and possession.",
        "Step 3",
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
st.download_button(
    "Download Matching Records",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_property_insights.csv",
    mime="text/csv",
)
