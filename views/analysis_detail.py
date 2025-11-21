import streamlit as st
import pandas as pd

def show(analyses):
    st.title("Analysis Detail")

    if not analyses:
        st.info("No analyses available.")
        return

    # Select Analysis
    analysis_options = {f"{a['query_patient_id']} vs {a['twin_id']} (Score: {a['similarity_score']})": a for a in analyses}
    selected_option = st.selectbox("Select Analysis", list(analysis_options.keys()))
    
    if selected_option:
        analysis = analysis_options[selected_option]
        
        # Header
        st.header(f"Comparison: {analysis['query_patient_id']} & {analysis['twin_id']}")
        st.caption(f"Similarity Score: {analysis['similarity_score']}")

        # Clinical Summary Comparison
        st.subheader("Clinical Summary")
        summary = analysis.get('clinical_summary', {})
        query_summary = summary.get('query', {})
        twin_summary = summary.get('twin', {})

        # Create a comparison dataframe
        comparison_data = {}
        all_keys = set(query_summary.keys()) | set(twin_summary.keys())
        for key in all_keys:
            comparison_data[key] = [query_summary.get(key, 'N/A'), twin_summary.get(key, 'N/A')]
        
        df_summary = pd.DataFrame(comparison_data, index=['Query Patient', 'Twin Patient']).T
        st.table(df_summary)

        # Navigation Links
        st.subheader("Deep Dive Navigation")
        
        def navigate_to_clinical(patient_id):
            st.session_state.deep_dive_patient_id = patient_id
            st.session_state.navigation = "Clinical Deep Dive"
            
        def navigate_to_genomic(patient_id):
            st.session_state.genomics_patient_id = patient_id
            st.session_state.navigation = "Genomics Deep Dive"

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Query Patient: {analysis['query_patient_id']}**")
            st.button("View Clinical Deep Dive", 
                     key="btn_clinical_query",
                     on_click=navigate_to_clinical,
                     args=(analysis['query_patient_id'],))
            
            st.button("View Genomic Deep Dive", 
                     key="btn_genomic_query",
                     on_click=navigate_to_genomic,
                     args=(analysis['query_patient_id'],))
                
        with col2:
            st.markdown(f"**Twin Patient: {analysis['twin_id']}**")
            st.button("View Clinical Deep Dive", 
                     key="btn_clinical_twin",
                     on_click=navigate_to_clinical,
                     args=(analysis['twin_id'],))
            
            st.button("View Genomic Deep Dive", 
                     key="btn_genomic_twin",
                     on_click=navigate_to_genomic,
                     args=(analysis['twin_id'],))
        
        st.divider()

        # Tabs for details
        tab1, tab2, tab3, tab4 = st.tabs(["Shared Features", "Key Differences", "Genomic Comparison", "Recommendations"])

        with tab1:
            for feature in analysis.get('shared_features', []):
                st.markdown(f"**{feature['feature']}**")
                st.write(feature['clinical_relevance'])
                st.divider()

        with tab2:
            for diff in analysis.get('key_differences', []):
                st.markdown(f"**{diff['difference']}**")
                st.write(diff['clinical_impact'])
                st.divider()
        
        with tab3:
            genomic = analysis.get('genomic_comparison', {})
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Shared Drivers")
                for item in genomic.get('shared_drivers', []):
                    st.write(f"- {item}")
            with col2:
                st.markdown("### Shared Pathways")
                for item in genomic.get('shared_pathways', []):
                    st.write(f"- {item}")
            
            st.markdown("### Actionability Alignment")
            st.info(genomic.get('actionability_alignment', 'N/A'))

        with tab4:
            for rec in analysis.get('recommendations', []):
                st.markdown(f"### {rec['recommendation']}")
                st.write(f"**Evidence:** {rec['evidence']}")
                st.caption(f"Confidence: {rec['confidence']}")
                st.divider()
