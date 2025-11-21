import streamlit as st
import pandas as pd

def show(patient_profiles):
    st.title("Clinical Deep Dive")

    # Patient Selection
    patient_ids = sorted(list(patient_profiles.keys()))
    
    # Initialize session state for patient selection if not present
    if "deep_dive_patient_id" not in st.session_state:
        st.session_state.deep_dive_patient_id = None
        
    # Use index to set default value if in session state
    index = 0
    if st.session_state.deep_dive_patient_id in patient_ids:
        index = patient_ids.index(st.session_state.deep_dive_patient_id)
        
    selected_patient_id = st.selectbox("Select Patient ID", patient_ids, index=index, key="deep_dive_patient_select")
    
    # Update session state when selection changes
    if selected_patient_id:
        st.session_state.deep_dive_patient_id = selected_patient_id

    if selected_patient_id:
        profile = patient_profiles[selected_patient_id]
        clinical_data = profile.get('clinical', {})
        
        st.header(f"Patient: {selected_patient_id}")
        
        # Demographics
        st.subheader("Demographics")
        demographics = clinical_data.get('demographics', {})
        if demographics:
            cols = st.columns(4)
            cols[0].metric("Age", demographics.get('age', 'N/A'))
            cols[1].metric("Sex", demographics.get('sex', 'N/A'))
            cols[2].metric("Race", demographics.get('race', 'N/A'))
            cols[3].metric("Vital Status", demographics.get('vital_status', 'N/A'))
        else:
            st.info("No demographics data available.")

        # Diagnosis & Stage
        st.subheader("Diagnosis & Stage")
        col1, col2 = st.columns(2)
        stage = clinical_data.get('stage', {})
        biomarkers = clinical_data.get('biomarkers', {})
        
        with col1:
            st.markdown("**Stage Info**")
            st.write(f"Highest Recorded: {stage.get('highest_recorded', 'N/A')}")
            st.write(f"Category: {stage.get('category', 'N/A')}")
            
        with col2:
            st.markdown("**Cancer Type**")
            st.write(f"Oncotree Code: {biomarkers.get('oncotree_code', 'N/A')}")
            st.write(f"Detailed: {biomarkers.get('cancer_type_detailed', 'N/A')}")

        # Biomarkers
        st.subheader("Biomarkers")
        if biomarkers:
            b_cols = st.columns(3)
            b_cols[0].metric("TMB (Non-synonymous)", f"{biomarkers.get('tmb_nonsynonymous', 0):.2f}" if biomarkers.get('tmb_nonsynonymous') else "N/A")
            b_cols[1].metric("MSI Type", biomarkers.get('msi_type', 'N/A'))
            b_cols[2].metric("PD-L1 Status", biomarkers.get('pdl1_status', 'N/A'))
        
        # Treatments
        st.subheader("Treatments")
        # Try nested structure first (Schema A)
        treatments = profile.get('treatments', {}).get('drug_therapy', {}).get('lines', [])
        # Fallback to flat structure (Schema B)
        if not treatments:
            treatments = profile.get('treatment', [])
            
        if treatments:
            df_treatments = pd.DataFrame(treatments)
            # Select and rename columns for better display
            display_cols = ['start_date_days', 'stop_date_days', 'agent', 'subtype', 'investigative', 'line_number']
            # Filter to only existing columns
            display_cols = [col for col in display_cols if col in df_treatments.columns]
            st.dataframe(df_treatments[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No treatment data available.")

        # Timeline Events (Surgery, Radiation, etc.)
        st.subheader("Timeline Events")
        
        # Helper to get timeline events from either nested or flat structure
        def get_timeline_events(profile, key):
            # Try nested in 'timeline' first (Schema A)
            events = profile.get('timeline', {}).get(key, [])
            # Fallback to top-level (Schema B)
            if not events:
                events = profile.get(key, [])
            return events

        tabs = st.tabs(["Surgery", "Radiation", "Progression", "Tumor Sites"])
        
        with tabs[0]:
            surgeries = get_timeline_events(profile, 'surgery')
            if surgeries:
                st.dataframe(pd.DataFrame(surgeries), use_container_width=True)
            else:
                st.info("No surgery events.")
                
        with tabs[1]:
            radiation = get_timeline_events(profile, 'radiation')
            if radiation:
                st.dataframe(pd.DataFrame(radiation), use_container_width=True)
            else:
                st.info("No radiation events.")
                
        with tabs[2]:
            progression = get_timeline_events(profile, 'progression')
            if progression:
                st.dataframe(pd.DataFrame(progression), use_container_width=True)
            else:
                st.info("No progression events.")
                
        with tabs[3]:
            tumor_sites = get_timeline_events(profile, 'tumor_sites')
            if tumor_sites:
                st.dataframe(pd.DataFrame(tumor_sites), use_container_width=True)
            else:
                st.info("No tumor site records.")
