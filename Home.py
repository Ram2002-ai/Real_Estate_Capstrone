import streamlit as st
import pandas as pd
import pickle as pkl
import os

st.set_page_config(
    page_title="Real Estate Analytics - Gurgaon",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #f8f9fa;
        color: #333;
    }
    h1, h2, h3 {
        color: #0f172a; /* Slate 900 */
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Metrics Cards */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid #3b82f6; /* Blue 500 */
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e40af; /* Blue 800 */
    }
    .metric-label {
        color: #64748b; /* Slate 500 */
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
        height: 100%;
        border-top: 5px solid #6366f1; /* Indigo 500 */
        transition: all 0.3s ease;
    }
    .nav-card:hover {
        transform: scale(1.03);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    .icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Headers */
    .hero-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .hero-sub {
        font-size: 1.25rem;
        text-align: center;
        color: #475569;
        margin-bottom: 3rem;
        font-weight: 300;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data for Metrics ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/gurgaon_properties_cleaned_v2.csv")
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/gurgaon_properties_cleaned_v2.csv' exists.")
        return pd.DataFrame() # Return empty if fails

df = load_data()

# --- Hero Section ---
st.markdown('<div class="hero-header">Real Estate Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">The Smartest Way to Buy Property in Gurgaon. <br>Predict Prices, Analyze Trends, and Find Your Dream Home.</div>', unsafe_allow_html=True)

st.divider()

# --- Key Metrics Section ---
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_properties = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_properties:,}</div>
            <div class="metric-label">Properties Listed</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        avg_price = df['price'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹ {avg_price:.2f} Cr</div>
            <div class="metric-label">Average Price</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        top_sector = df['sector'].mode()[0]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{top_sector}</div>
            <div class="metric-label">Most Popular Sector</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Assuming 'property_type' exists, count the most common
        top_type = df['property_type'].mode()[0].title()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{top_type}</div>
            <div class="metric-label">Trending Type</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Navigation / modules Section ---
st.subheader("Explore Our Modules")

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown("""
    <div class="nav-card">
        <div class="icon">💰</div>
        <h3>Price Predictor</h3>
        <p>Get accurate price estimates for properties based on location, amenities, and size.</p>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown("""
    <div class="nav-card">
        <div class="icon">📊</div>
        <h3>Market Analysis</h3>
        <p>Deep dive into real estate trends, price distributions, and sector-wise comparisons.</p>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown("""
    <div class="nav-card">
        <div class="icon">🏠</div>
        <h3>Recommender System</h3>
        <p>Discover properties that match your lifestyle and preferences using advanced AI.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b;'>© 2024 Real Estate Analytics. All Rights Reserved.</div>", unsafe_allow_html=True)
