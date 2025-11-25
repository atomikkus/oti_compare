import streamlit as st
from views import analysis_detail, deep_dive, genomics_deep_dive
from utils.data_loader import load_twin_analyses, load_patient_profiles

st.set_page_config(page_title="Twin Analysis Dashboard", layout="wide")

st.markdown("""
    <style>
        /* Global Settings */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Typography */
        h1, h2, h3 {
            color: #0F172A;
            font-family: 'Inter', sans-serif;
        }
        p, div, span {
            color: #334155;
            font-family: 'Inter', sans-serif;
        }

        /* Card Styling */
        .stCard {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 1rem;
            border: 1px solid #E2E8F0;
        }

        /* Blue Banner */
        .blue-banner {
            background-color: #EFF6FF;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid #DBEAFE;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .blue-banner-text {
            color: #1E40AF;
            font-weight: bold;
            font-size: 0.95rem;
        }
        .blue-banner-label {
            color: #60A5FA;
            font-weight: bold;
            font-size: 0.85rem;
            margin-right: 0.25rem;
        }

        /* Metric Cards */
        .metric-card {
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        /* Green Metric */
        .bg-green-50 { background-color: #F0FDF4; }
        .text-green-600 { color: #16A34A; }
        
        /* Blue Metric */
        .bg-blue-50 { background-color: #EFF6FF; }
        .text-blue-600 { color: #2563EB; }
        
        /* Purple Metric */
        .bg-purple-50 { background-color: #FAF5FF; }
        .text-purple-600 { color: #9333EA; }
        
        /* Orange Metric */
        .bg-orange-50 { background-color: #FFF7ED; }
        .text-orange-600 { color: #EA580C; }

        /* Pills */
        .pill-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        .pill {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .pill-green {
            background-color: #F0FDF4;
            color: #166534;
            border: 1px solid #DCFCE7;
        }
        .pill-purple {
            background-color: #FAF5FF;
            color: #6B21A8;
            border: 1px solid #F3E8FF;
        }

        /* Checklist */
        .checklist-item {
            display: flex;
            align-items: start;
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            color: #475569;
        }
        .check-icon {
            color: #3B82F6;
            margin-right: 0.75rem;
            margin-top: 0.1rem;
        }

        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            font-size: 1.1rem;
            font-weight: 600;
            color: #1E293B;
            margin-bottom: 1rem;
        }
        .section-icon {
            margin-right: 0.5rem;
            font-size: 1.2rem;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
        }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def get_data():
    analyses = load_twin_analyses("final_twin_analysis_2")
    patient_profiles = load_patient_profiles("patient_profiles_2")
    return analyses, patient_profiles

try:
    analyses, patient_profiles = get_data()
except FileNotFoundError as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
if "navigation" not in st.session_state:
    st.session_state.navigation = "Analysis Detail"

# Ensure valid page selection if state was previously Overview
if st.session_state.navigation == "Overview":
    st.session_state.navigation = "Analysis Detail"

page = st.sidebar.radio("Go to", ["Analysis Detail", "Clinical Deep Dive", "Genomics Deep Dive"], key="navigation")

if page == "Analysis Detail":
    analysis_detail.show(analyses)
elif page == "Clinical Deep Dive":
    deep_dive.show(patient_profiles)
elif page == "Genomics Deep Dive":
    genomics_deep_dive.show(patient_profiles)
