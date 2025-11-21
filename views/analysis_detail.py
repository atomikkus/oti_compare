import streamlit as st
import pandas as pd

def navigate_to_clinical(patient_id):
    st.session_state.deep_dive_patient_id = patient_id
    st.session_state.deep_dive_patient_select = patient_id
    st.session_state.navigation = "Clinical Deep Dive"
    
def navigate_to_genomic(patient_id):
    st.session_state.genomics_patient_id = patient_id
    st.session_state.genomics_patient_select = patient_id
    st.session_state.navigation = "Genomics Deep Dive"

def show(analyses):
    if not analyses:
        st.info("No analyses available.")
        return

    # Top Header Area
    col_header, col_select = st.columns([2, 1])
    
    with col_header:
        st.markdown("<h1>Twin Pair Analysis</h1>", unsafe_allow_html=True)
        st.markdown("<p>Detailed analysis of molecularly similar patient pairs showing biomarker alignment, treatment comparisons, and clinical decision insights.</p>", unsafe_allow_html=True)
        
    with col_select:
        # Select Analysis
        analysis_options = {f"{a['query_patient_id']} ↔ {a['twin_id']} (Rank #{a['rank']})": a for a in analyses}
        selected_option = st.selectbox("Select Pair:", list(analysis_options.keys()))
    
    if selected_option:
        analysis = analysis_options[selected_option]
        
        # --- 1. High-Level Summary Banner ---
        match_quality = analysis.get('match_quality', {})
        grade = match_quality.get('grade', 'N/A')
        
        # Calculate shared biomarkers count
        shared_features = analysis.get('shared_features', {})
        if isinstance(shared_features, dict):
            shared_biomarkers_count = len(shared_features.get('biomarkers', []))
        elif isinstance(shared_features, list):
            shared_biomarkers_count = len(shared_features)
        else:
            shared_biomarkers_count = 0
        
        st.markdown(f"""
            <div class="blue-banner">
                <div style="display: flex; gap: 2rem;">
                    <div><span class="blue-banner-label">Query:</span> <span class="blue-banner-text">{analysis['query_patient_id']}</span></div>
                    <div><span class="blue-banner-label">Twin:</span> <span class="blue-banner-text">{analysis['twin_id']}</span></div>
                </div>
                <div style="display: flex; gap: 2rem;">
                    <div><span class="blue-banner-label">Rank:</span> <span class="blue-banner-text">#{analysis['rank']}</span></div>
                    <div><span class="blue-banner-label">Similarity:</span> <span class="blue-banner-text">{analysis['similarity_score']}</span></div>
                    <div><span class="blue-banner-label">Match Grade:</span> <span class="blue-banner-text" style="font-weight: 800; color: #2563EB;">{grade}</span></div>
                    <div><span class="blue-banner-label">Shared Biomarkers:</span> <span class="blue-banner-text">{shared_biomarkers_count}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. Rationale & Match Quality ---
        with st.expander("Match Rationale & Quality", expanded=True):
            # Rationale
            if 'rationale' in analysis:
                st.markdown(f"**Rationale:** {analysis['rationale']}")
                st.markdown("---")

            # Strengths & Limitations
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-header"><span class="text-green-600 section-icon">●</span> Match Strengths</div>', unsafe_allow_html=True)
                for s in match_quality.get('strengths', []):
                    st.markdown(f"- {s}")
            with c2:
                st.markdown('<div class="section-header"><span class="text-red-600 section-icon">●</span> Match Limitations</div>', unsafe_allow_html=True)
                for l in match_quality.get('limitations', []):
                    st.markdown(f"- {l}")

        # --- 3. Clinical & Phenotype Comparison ---
        with st.expander("Clinical & Phenotype Comparison", expanded=False):
            # Phenotypes
            phenotypes = analysis.get('phenotype_comparison', {})
            if phenotypes:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.caption("Shared Phenotypes")
                    for p in phenotypes.get('shared', []):
                        st.markdown(f"<span class='pill pill-green'>{p}</span>", unsafe_allow_html=True)
                with c2:
                    st.caption(f"Query Only ({analysis['query_patient_id']})")
                    for p in phenotypes.get('query_only', []):
                        st.markdown(f"<span class='pill pill-purple'>{p}</span>", unsafe_allow_html=True)
                with c3:
                    st.caption(f"Twin Only ({analysis['twin_id']})")
                    for p in phenotypes.get('twin_only', []):
                        st.markdown(f"<span class='pill pill-purple'>{p}</span>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Clinical Summary Table
            summary = analysis.get('clinical_summary', {})
            query_summary = summary.get('query', {})
            twin_summary = summary.get('twin', {})
            
            all_keys = sorted(list(set(query_summary.keys()) | set(twin_summary.keys())))
            
            # Create a compact table
            comp_data = []
            for k in all_keys:
                q_val = query_summary.get(k, '-')
                t_val = twin_summary.get(k, '-')
                match_icon = "✅" if str(q_val) == str(t_val) and str(q_val) != '-' else ""
                comp_data.append({"Feature": k.replace('_', ' ').title(), "Query Patient": q_val, "Twin Patient": t_val, "Match": match_icon})
            
            st.dataframe(pd.DataFrame(comp_data).set_index("Feature"), use_container_width=True)

            # Key Differences
            differences = analysis.get('key_differences', []) # JSON key is key_differences
            if not differences: differences = analysis.get('differences', []) # Fallback
            
            if differences:
                st.markdown("**Key Differences & Impact**")
                for diff in differences:
                    d_text = diff.get('difference', diff) if isinstance(diff, dict) else diff
                    impact = diff.get('clinical_impact', '') if isinstance(diff, dict) else ''
                    st.info(f"**{d_text}**\n\n_{impact}_")

        # --- 4. Genomic Landscape ---
        with st.expander("Genomic Landscape", expanded=False):
            genomic = analysis.get('genomic_comparison', {})
            
            # Shared Drivers & Pathways
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Shared Drivers**")
                drivers = genomic.get('shared_drivers', [])
                if drivers:
                    st.markdown(" ".join([f"<span class='pill pill-green'>{d}</span>" for d in drivers]), unsafe_allow_html=True)
                else:
                    st.caption("None")
            with c2:
                st.markdown("**Shared Pathways**")
                pathways = genomic.get('shared_pathways', [])
                if pathways:
                    st.markdown(" ".join([f"<span class='pill pill-purple'>{p}</span>" for p in pathways]), unsafe_allow_html=True)
                else:
                    st.caption("None")
            
            st.markdown("---")
            
            # Unique Alterations
            c3, c4 = st.columns(2)
            with c3:
                st.markdown(f"**Unique to Query ({analysis['query_patient_id']})**")
                for u in genomic.get('query_unique', []):
                    st.markdown(f"- {u}")
            with c4:
                st.markdown(f"**Unique to Twin ({analysis['twin_id']})**")
                for u in genomic.get('twin_unique', []):
                    st.markdown(f"- {u}")
            
            # Actionability
            if 'actionability_alignment' in genomic:
                st.markdown("---")
                st.markdown(f"**Actionability Alignment:** {genomic['actionability_alignment']}")

        # --- 5. Treatment Analysis ---
        with st.expander("Treatment Analysis", expanded=False):
            treatment = analysis.get('treatment_comparison', {})
            
            # Regimens
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Query Treatment ({analysis['query_patient_id']})**")
                for t in treatment.get('query_treatments', []):
                    st.markdown(f"<span class='pill pill-blue'>{t}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**Twin Treatment ({analysis['twin_id']})**")
                for t in treatment.get('twin_treatments', []):
                    st.markdown(f"<span class='pill pill-blue'>{t}</span>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Analysis Text
            if 'sequencing_analysis' in treatment:
                st.markdown(f"**Sequencing Analysis:** {treatment['sequencing_analysis']}")
            if 'outcome_correlation' in treatment:
                st.markdown(f"**Outcome Correlation:** {treatment['outcome_correlation']}")
            
            # Gaps
            gaps = treatment.get('treatment_gaps', [])
            if gaps:
                st.markdown("**Identified Treatment Gaps:**")
                for gap in gaps:
                    st.warning(gap)

        # --- 6. Actionable Insights & Recommendations ---
        with st.expander("Actionable Insights & Recommendations", expanded=False):
            # Insights
            insights = analysis.get('actionable_insights', [])
            if insights:
                st.markdown("### Actionable Insights")
                for insight in insights:
                    st.success(insight)
            
            # Recommendations
            recs = analysis.get('recommendations', [])
            if recs:
                st.markdown("### Clinical Recommendations")
                for rec in recs:
                    r_text = rec.get('recommendation', rec) if isinstance(rec, dict) else rec
                    evidence = rec.get('evidence', '') if isinstance(rec, dict) else ''
                    confidence = rec.get('confidence', '') if isinstance(rec, dict) else ''
                    
                    st.markdown(f"""
                        <div style="background-color: #F0F9FF; padding: 1rem; border-radius: 8px; border-left: 4px solid #0EA5E9; margin-bottom: 0.5rem;">
                            <div style="font-weight: 600; color: #0C4A6E;">{r_text}</div>
                            <div style="font-size: 0.9rem; color: #0369A1; margin-top: 0.25rem;">Evidence: {evidence}</div>
                            <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Confidence: {confidence}</div>
                        </div>
                    """, unsafe_allow_html=True)

        # --- 7. Deep Dive Navigation ---
        st.markdown("""
            <style>
                /* Clinical - Red (Primary) */
                div[data-testid="stButton"] button[kind="primary"] {
                    background-color: #EF4444 !important;
                    color: white !important;
                    border-color: #EF4444 !important;
                }
                div[data-testid="stButton"] button[kind="primary"]:hover {
                    background-color: #DC2626 !important;
                    color: white !important;
                    border-color: #DC2626 !important;
                }
                div[data-testid="stButton"] button[kind="primary"]:focus {
                    background-color: #EF4444 !important;
                    color: white !important;
                    border-color: #EF4444 !important;
                    box-shadow: none !important;
                }
                div[data-testid="stButton"] button[kind="primary"] p {
                    color: white !important;
                }

                /* Genomic - Blue (Secondary) */
                div[data-testid="stButton"] button[kind="secondary"] {
                    background-color: #3B82F6 !important;
                    color: white !important;
                    border-color: #3B82F6 !important;
                }
                div[data-testid="stButton"] button[kind="secondary"]:hover {
                    background-color: #2563EB !important;
                    color: white !important;
                    border-color: #2563EB !important;
                }
                div[data-testid="stButton"] button[kind="secondary"]:focus {
                    background-color: #3B82F6 !important;
                    color: white !important;
                    border-color: #3B82F6 !important;
                    box-shadow: none !important;
                }
                div[data-testid="stButton"] button[kind="secondary"] p {
                    color: white !important;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("### Deep Dive Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; margin-bottom: 8px;'><span style='color: #1E40AF; font-weight: bold; font-size: 1.1rem;'>Query Patient:</span> <span style='font-weight: bold; font-size: 1.1rem;'>{analysis['query_patient_id']}</span></div>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.button("Clinical Profile", 
                            key="btn_clinical_query",
                            type="primary",
                            on_click=navigate_to_clinical,
                            args=(analysis['query_patient_id'],),
                            use_container_width=True)
                with c2:
                    st.button("Genomic Profile", 
                            key="btn_genomic_query",
                            type="secondary",
                            on_click=navigate_to_genomic,
                            args=(analysis['query_patient_id'],),
                            use_container_width=True)
                
        with col2:
            with st.container(border=True):
                st.markdown(f"<div style='text-align: center; margin-bottom: 8px;'><span style='color: #166534; font-weight: bold; font-size: 1.1rem;'>Twin Patient:</span> <span style='font-weight: bold; font-size: 1.1rem;'>{analysis['twin_id']}</span></div>", unsafe_allow_html=True)
                
                c3, c4 = st.columns(2)
                with c3:
                    st.button("Clinical Profile", 
                            key="btn_clinical_twin",
                            type="primary",
                            on_click=navigate_to_clinical,
                            args=(analysis['twin_id'],),
                            use_container_width=True)
                with c4:
                    st.button("Genomic Profile", 
                            key="btn_genomic_twin",
                            type="secondary",
                            on_click=navigate_to_genomic,
                            args=(analysis['twin_id'],),
                            use_container_width=True)
