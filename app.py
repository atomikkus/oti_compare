import streamlit as st
from views import overview, analysis_detail, deep_dive, genomics_deep_dive
from utils.data_loader import load_twin_analyses, load_patient_profiles

st.set_page_config(page_title="Twin Analysis Dashboard", layout="wide")

# Load Data
@st.cache_data
def get_data():
    analyses = load_twin_analyses("final_twin_analysis")
    patient_profiles = load_patient_profiles("patient_profiles")
    return analyses, patient_profiles

try:
    analyses, patient_profiles = get_data()
except FileNotFoundError as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
if "navigation" not in st.session_state:
    st.session_state.navigation = "Overview"

page = st.sidebar.radio("Go to", ["Overview", "Analysis Detail", "Clinical Deep Dive", "Genomics Deep Dive"], key="navigation")

if page == "Overview":
    overview.show(analyses)
elif page == "Analysis Detail":
    analysis_detail.show(analyses)
elif page == "Clinical Deep Dive":
    deep_dive.show(patient_profiles)
elif page == "Genomics Deep Dive":
    genomics_deep_dive.show(patient_profiles)
