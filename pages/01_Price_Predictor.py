import streamlit as st
import pickle as pkl
import pandas as pd
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="Price Predictor", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .header {
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    .prediction-card {
        background-color: #dbeafe;
        color: #1e3a8a;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .prediction-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .prediction-range {
        font-size: 1.2rem;
        color: #4b5563;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data & Model ---
# --- Class Injection for Pickle Loading ---
import sklearn.compose._column_transformer as _column_transformer
class _RemainderColsList(list):
    pass
setattr(_column_transformer, '_RemainderColsList', _RemainderColsList)

@st.cache_resource
def load_resources():
    try:
        with open("files/pkl.files/df.pkl", 'rb') as f:
            df = pkl.load(f)
        with open("files/pkl.files/pipeline.pkl", 'rb') as f:
            model = pkl.load(f)
        return df, model
    except FileNotFoundError:
        st.error("Model or Data file not found. Please check existing files.")
        return None, None

df, model = load_resources()

if df is not None:
    st.markdown('<h1 class="header">Property Price Predictor</h1>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Property Details")
        property_type = st.selectbox('Property Type', ['flat', 'house'])
        sector = st.selectbox('Sector', sorted(df['sector'].unique().tolist()))
        bedroom = st.selectbox('Number of Bedrooms', sorted(df['bedRoom'].unique().tolist()))
        bathroom = st.selectbox('Number of Bathrooms', sorted(df['bathroom'].unique().tolist()))
        balcony = st.selectbox('Balconies', sorted(df['balcony'].unique().tolist()))

    with col2:
        st.subheader("Additional Features")
        age_possession = st.selectbox('Age of Property', sorted(df['agePossession'].unique().tolist()))
        built_up_area = st.number_input('Built Up Area (sq. ft.)', min_value=100.0, step=10.0)
        servant_room = st.selectbox('Servant Room', ['No', 'Yes'])
        store_room = st.selectbox('Store Room', ['No', 'Yes'])
        furnishing_type = st.selectbox('Furnishing Type', sorted(df['furnishing_type'].unique().tolist()))
        luxury_category = st.selectbox('Luxury Category', sorted(df['luxury_category'].unique().tolist()))
        floor_category = st.selectbox('Floor Category', sorted(df['floor_category'].unique().tolist()))

    # Convert Yes/No to float
    servant_room_val = 1.0 if servant_room == 'Yes' else 0.0
    store_room_val = 1.0 if store_room == 'Yes' else 0.0

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button('Predict Price'):
        # Prepare input dataframe
        input_data = pd.DataFrame([{
            'property_type': property_type,
            'sector': sector,
            'bedRoom': float(bedroom),
            'bathroom': float(bathroom),
            'balcony': balcony,
            'agePossession': age_possession,
            'built_up_area': float(built_up_area),
            'servant room': servant_room_val,
            'store room': store_room_val,
            'furnishing_type': furnishing_type,
            'luxury_category': luxury_category,
            'floor_category': floor_category
        }])
        
        try:
            # Predict
            log_price = model.predict(input_data)[0]
            base_price = np.expm1(log_price)
            
            low_est = base_price - 0.22  # Range logic from original code
            high_est = base_price + 0.22
            
            # Formatting
            low_fmt = f"{low_est:.2f}"
            high_fmt = f"{high_est:.2f}"
            base_fmt = f"{base_price:.2f}"
            
            st.markdown(f"""
            <div class="prediction-card">
                <div>Estimated Price</div>
                <div class="prediction-value">₹ {base_fmt} Cr</div>
                <div class="prediction-range">Price Range: ₹ {low_fmt} Cr - ₹ {high_fmt} Cr</div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
            st.warning("Please ensure all inputs are valid for the model.")
