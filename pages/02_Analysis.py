import streamlit as st
import pandas as pd
import plotly.express as px
import pickle as pkl
import plotly.graph_objects as go

st.set_page_config(page_title="Market Analysis", layout="wide")

st.markdown("""
<style>
    .header {
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chart-container {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1rem;
        background-color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header">Real Estate Market Analysis</h1>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/gurgaon_properties_cleaned_v2.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Could not load data. Please check if 'files/pkl.files/df.pkl' exists.")
else:
    # --- Visualization 1: Sector Price Analysis ---
    st.subheader("Results by Sector")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        prop_type = st.selectbox("Select Property Type", ['All'] + sorted(df['property_type'].unique().tolist()))
        top_n = st.slider("Number of Sectors", 5, 20, 10)

    if prop_type != 'All':
        filtered_df = df[df['property_type'] == prop_type]
    else:
        filtered_df = df

    # Groupby Sector
    sector_price = filtered_df.groupby('sector')['price'].mean().reset_index().sort_values('price', ascending=False).head(top_n)
    
    fig_sector = px.bar(
        sector_price, 
        x='sector', 
        y='price', 
        color='price',
        color_continuous_scale='Blues',
        title=f"Top {top_n} Most Expensive Sectors (Avg Price in Cr)",
        labels={'price': 'Avg Price (Cr)', 'sector': 'Sector'},
        template="plotly_white"
    )
    st.plotly_chart(fig_sector, use_container_width=True)

    st.markdown("---")

    # --- Row 2: Distributions ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Property Type Distribution")
        count_data = df['property_type'].value_counts().reset_index()
        count_data.columns = ['Property Type', 'Count']
        
        fig_pie = px.pie(
            count_data, 
            values='Count', 
            names='Property Type', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu,
            title="Apartments vs Independent Houses"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col4:
        st.subheader("Bedroom Configuration")
        # Ensure bedRoom is treated as category or sorted properly
        if 'bedRoom' in df.columns:
            # Filter unrealistic bedroom counts for cleaner chart if necessary, or just plot
            fig_hist = px.histogram(
                df, 
                x='bedRoom', 
                color='property_type',
                barmode='group',
                title="BHK Availability",
                template="plotly_white",
                color_discrete_sequence=['#1E3A8A', '#93C5FD'] # Custom blue shades
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # --- Row 3: Scatter Plot ---
    st.subheader("Price vs. Built-Up Area")
    st.markdown("Explore how the size of a property affects its pricing.")
    
    if 'built_up_area' in df.columns and 'price' in df.columns:
        fig_scatter = px.scatter(
            df, 
            x='built_up_area', 
            y='price', 
            color='bedRoom',
            size='bedRoom',
            hover_data=['sector'],
            title="Price vs Area Relationship",
            template="plotly_white",
            labels={'built_up_area': 'Area (sq. ft)', 'price': 'Price (Cr)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
