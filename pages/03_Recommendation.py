import streamlit as st
import pickle as pkl
import pandas as pd
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="Property Recommender", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .header {
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-card {
        background-color: white;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        border-left: 6px solid #2563EB;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .recommendation-card:hover {
        transform: scale(1.01);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    .prop-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F2937;
    }
    .prop-details {
        color: #4B5563;
        margin-top: 0.5rem;
    }
    .score-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">Smart Property Recommender</h1>', unsafe_allow_html=True)

# --- Load Data & Models ---
@st.cache_resource
def load_recommendation_data():
    try:
        with open("files/pkl.files/location_distance.pkl", 'rb') as f:
            location_df = pkl.load(f)
        with open("files/pkl.files/cosine_sim1.pkl", 'rb') as f:
            cosine_sim1 = pkl.load(f)
        with open("files/pkl.files/cosine_sim2.pkl", 'rb') as f:
            cosine_sim2 = pkl.load(f)
        with open("files/pkl.files/cosine_sim3.pkl", 'rb') as f:
            cosine_sim3 = pkl.load(f)
        return location_df, cosine_sim1, cosine_sim2, cosine_sim3
    except FileNotFoundError:
        st.error("Recommendation data files missing.")
        return None, None, None, None

location_df, cosine_sim1, cosine_sim2, cosine_sim3 = load_recommendation_data()

# --- Recommendation Logic ---
def recommend_properties(property_name, top_n=5):
    # Weighted Similarity Matrix
    cosine_sim_matrix = 0.5*cosine_sim1 + 0.8*cosine_sim2 + 1*cosine_sim3
    
    # Get similarity scores
    try:
        idx = location_df.index.get_loc(property_name)
    except KeyError:
        return pd.DataFrame() # Handle case if property name not found

    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    
    # Sort
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Top N (excluding self)
    top_indices = [i[0] for i in sorted_scores[1:top_n+1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n+1]]
    
    top_properties = location_df.index[top_indices].tolist()
    
    return pd.DataFrame({
        'PropertyName': top_properties,
        'SimilarityScore': top_scores
    })

if location_df is not None:
    tab1, tab2 = st.tabs(["📍 Location Search", "🤖 Recommended for You"])

    # --- Tab 1: Location Radius Search ---
    with tab1:
        st.subheader("Find Properties Near a Landmark")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_location = st.selectbox('Select Location/Landmark', sorted(location_df.columns.tolist()))
        with col2:
            radius = st.number_input('Radius (in Km)', min_value=1, max_value=50, value=5)

        if st.button('Search Properties'):
            # Filter properties within radius
            # dist is in meters in the dataframe usually? Check logic from original file: value/1000
            # Original: location_df[location_df[selected_location]<radius*1000]
            
            try:
                result_ser = location_df[location_df[selected_location] < radius*1000][selected_location].sort_values()
                
                if result_ser.empty:
                    st.warning("No properties found within this range.")
                else:
                    st.success(f"Found {len(result_ser)} properties within {radius} km.")
                    for property_name, dist_meters in result_ser.items():
                        st.markdown(f"""
                        <div class="recommendation-card">
                            <div class="prop-name">{property_name}</div>
                            <div class="prop-details">📍 {dist_meters/1000:.2f} km away from {selected_location}</div>
                        </div>
                        """, unsafe_allow_html=True)
            except KeyError:
                 st.error("Selected location data not available.")

    # --- Tab 2: Content-Based Recommendation ---
    with tab2:
        st.subheader("Similar Property Recommendations")
        st.markdown("Select a property you like, and we'll find similar ones based on amenities, price, and location.")
        
        selected_appartment = st.selectbox('Select Reference Property', sorted(location_df.index.to_list()))

        if st.button('Get Recommendations'):
            recommendations = recommend_properties(selected_appartment)
            
            if recommendations.empty:
                st.error("Could not generate recommendations.")
            else:
                st.subheader(f"Properties similar to '{selected_appartment}'")
                for index, row in recommendations.iterrows():
                     st.markdown(f"""
                        <div class="recommendation-card">
                            <div class="prop-name">{row['PropertyName']}</div>
                            <div class="score-badge">Match Score: {row['SimilarityScore']:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
