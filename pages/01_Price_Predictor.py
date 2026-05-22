import numpy as np
import pandas as pd
import streamlit as st

from utils.data_loader import load_prediction_resources
from utils.ui import hero, inject_global_css, insight_card, metric_card, page_config, shell_start


page_config("Price Predictor")
inject_global_css()
shell_start("Price Prediction")

hero(
    title="Predict Fair",
    accent="Market Value",
    body=(
        "Estimate property prices with the trained ML pipeline while keeping the "
        "model input contract stable and transparent for buyers."
    ),
    image_url="https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1000&q=80",
    eyebrow="ML-powered valuation",
)

input_df, model = load_prediction_resources()
if input_df is None or model is None:
    st.error("Prediction resources are missing. Please ensure df.pkl and pipeline.pkl exist under files/pkl.files.")
    st.stop()

required_columns = [
    "property_type",
    "sector",
    "bedRoom",
    "bathroom",
    "balcony",
    "agePossession",
    "built_up_area",
    "servant room",
    "store room",
    "furnishing_type",
    "luxury_category",
    "floor_category",
]

missing_cols = [col for col in required_columns if col not in input_df.columns]
if missing_cols:
    st.error(f"Prediction schema is missing required columns: {', '.join(missing_cols)}")
    st.stop()


def options(col: str) -> list:
    values = input_df[col].dropna().unique().tolist()
    return sorted(values, key=lambda x: str(x))


st.markdown('<div class="section-title">Property Inputs</div>', unsafe_allow_html=True)
with st.form("prediction_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Location")
        property_type = st.selectbox("Property Type", options("property_type"))
        sector = st.selectbox("Sector", options("sector"))
        built_up_area = st.number_input("Built-up Area (sq ft)", min_value=250.0, max_value=15000.0, value=1250.0, step=25.0)

    with c2:
        st.subheader("Configuration")
        bedroom = st.selectbox("Bedrooms", options("bedRoom"))
        bathroom = st.selectbox("Bathrooms", options("bathroom"))
        balcony = st.selectbox("Balconies", options("balcony"))
        floor_category = st.selectbox("Floor Category", options("floor_category"))

    with c3:
        st.subheader("Condition and Amenities")
        age_possession = st.selectbox("Age / Possession", options("agePossession"))
        furnishing_type = st.selectbox("Furnishing", options("furnishing_type"))
        luxury_category = st.selectbox("Luxury Category", options("luxury_category"))
        servant_room = st.toggle("Servant Room")
        store_room = st.toggle("Store Room")

    submitted = st.form_submit_button("Predict Price")

if submitted:
    validation_errors = []
    if float(built_up_area) < 250:
        validation_errors.append("Built-up area is too small for this model.")
    if float(bedroom) >= 6 and float(built_up_area) < 1200:
        validation_errors.append("A high bedroom count with very low area is likely unrealistic.")
    if float(bathroom) > float(bedroom) + 2:
        validation_errors.append("Bathroom count is unusually high for the selected bedroom count.")

    if validation_errors:
        for error in validation_errors:
            st.warning(error)
        st.stop()

    input_data = pd.DataFrame(
        [
            {
                "property_type": property_type,
                "sector": sector,
                "bedRoom": float(bedroom),
                "bathroom": float(bathroom),
                "balcony": balcony,
                "agePossession": age_possession,
                "built_up_area": float(built_up_area),
                "servant room": 1.0 if servant_room else 0.0,
                "store room": 1.0 if store_room else 0.0,
                "furnishing_type": furnishing_type,
                "luxury_category": luxury_category,
                "floor_category": floor_category,
            }
        ]
    )

    try:
        log_price = model.predict(input_data)[0]
        base_price = float(np.expm1(log_price))
        low_est = max(base_price * 0.90, base_price - 0.22)
        high_est = max(base_price * 1.10, base_price + 0.22)
        price_per_sqft = (base_price * 10_000_000) / float(built_up_area)

        if base_price < 1:
            affordability = "Budget"
        elif base_price < 2.5:
            affordability = "Mid-range"
        elif base_price < 5:
            affordability = "Premium"
        else:
            affordability = "Luxury"

        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(metric_card("Estimated Price", f"Rs {base_price:.2f} Cr", "Model point estimate"), unsafe_allow_html=True)
        r2.markdown(metric_card("Expected Range", f"Rs {low_est:.2f}-{high_est:.2f} Cr", "Practical valuation band"), unsafe_allow_html=True)
        r3.markdown(metric_card("Price / Sqft", f"Rs {price_per_sqft:,.0f}", "Derived from built-up area"), unsafe_allow_html=True)
        r4.markdown(metric_card("Affordability", affordability, "Buyer segment tag"), unsafe_allow_html=True)

        st.markdown('<div class="section-title">What Drove The Estimate</div>', unsafe_allow_html=True)
        e1, e2, e3 = st.columns(3)
        e1.markdown(
            insight_card("Location Premium", f"{sector.title()} anchors the local demand and sector-level price curve.", "Location"),
            unsafe_allow_html=True,
        )
        e2.markdown(
            insight_card("Size and Configuration", f"{int(float(bedroom))} BHK over {built_up_area:,.0f} sq ft sets the usable-space baseline.", "Space"),
            unsafe_allow_html=True,
        )
        e3.markdown(
            insight_card("Amenity Signal", f"{luxury_category} luxury and {furnishing_type} furnishing adjust buyer willingness to pay.", "Quality"),
            unsafe_allow_html=True,
        )
    except Exception:
        st.error("Prediction failed for this input combination. Please adjust the fields and try again.")
else:
    st.info("Fill the property profile and run prediction to get an estimated price range.")
