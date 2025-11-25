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
        st.markdown("<h1>Twin Comparison Summary</h1>", unsafe_allow_html=True)
        st.markdown("<p>Detailed analysis of molecularly similar patient pairs showing biomarker alignment, treatment comparisons, and clinical decision insights.</p>", unsafe_allow_html=True)
        
    with col_select:
        # Select Analysis
        analysis_options = {f"{a['query_patient_id']} ↔ {a['twin_id']} (Rank #{a['rank']})": a for a in analyses}
        selected_option = st.selectbox("Select Pair:", list(analysis_options.keys()))
    
    if selected_option:
        analysis = analysis_options[selected_option]
        
        # --- Custom Styling for Accordions ---
        st.markdown("""
            <style>
                .stExpander > details > summary > div[data-testid="stExpanderToggleIcon"] + div {
                    font-weight: bold !important;
                    color: #0C4A6E !important; /* Dark Blue */
                    font-size: 1.1rem !important;
                }
                .stExpander > details > summary:hover {
                    color: #0284C7 !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # --- 1. High-Level Summary Banner ---
        match_quality = analysis.get('match_quality', {})
        clinical_pct = analysis.get('clinical_pct', 'N/A')
        genomic_pct = analysis.get('genomic_pct', 'N/A')
        
        # Format Similarity Score
        try:
            raw_score = float(analysis.get('similarity_score', 0))
            display_score = f"{raw_score * 10:.2f}"
        except (ValueError, TypeError):
            display_score = analysis.get('similarity_score', 'N/A')
        
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
                    <div><span class="blue-banner-label">Similarity:</span> <span class="blue-banner-text">{display_score}</span></div>
                    <div><span class="blue-banner-label">Clinical Match:</span> <span class="blue-banner-text" style="font-weight: 800; color: #2563EB;">{clinical_pct}%</span></div>
                    <div><span class="blue-banner-label">Genomic Match:</span> <span class="blue-banner-text" style="font-weight: 800; color: #2563EB;">{genomic_pct}%</span></div>
                    <div><span class="blue-banner-label">Shared Biomarkers:</span> <span class="blue-banner-text">{shared_biomarkers_count}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. Twin Comparison (Table) ---
        with st.expander("**Twin Comparison**", expanded=True):
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
                # Ensure all values are strings to prevent PyArrow inference errors
                comp_data.append({
                    "Feature": str(k).replace('_', ' ').title(), 
                    "Query Patient": str(q_val), 
                    "Twin Patient": str(t_val), 
                    "Match": match_icon
                })
            
            st.dataframe(pd.DataFrame(comp_data).set_index("Feature"), use_container_width=True)

        # --- 3. Summary (Differences & Similarities) ---
        with st.expander("**Summary**", expanded=False):
            # Try to find a dedicated summary section, otherwise construct it
            analysis_summary = analysis.get('summary')
            if analysis_summary:
                if isinstance(analysis_summary, dict):
                     for k, v in analysis_summary.items():
                         st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                else:
                    st.markdown(analysis_summary)
            
            # Fallback/Additional info if no dedicated summary text
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Key Similarities")
                # Phenotypes
                phenotypes = analysis.get('phenotype_comparison', {})
                if phenotypes:
                    for p in phenotypes.get('shared', []):
                        st.markdown(f"- {p}")
                
                # Genomic Shared
                genomic = analysis.get('genomic_comparison', {})
                shared_variants = genomic.get('shared_variants', [])
                if shared_variants:
                    for sv in shared_variants:
                        gene = sv.get('gene', '') if isinstance(sv, dict) else sv
                        st.markdown(f"- Genomic: {gene}")

            with c2:
                st.markdown("#### Key Differences")
                differences = analysis.get('key_differences', [])
                if not differences: differences = analysis.get('differences', [])
                
                if differences:
                    for diff in differences:
                        if isinstance(diff, dict):
                            feature = diff.get('feature', 'Feature')
                            q_val = diff.get('query_value', '-')
                            t_val = diff.get('twin_value', '-')
                            impact = diff.get('clinical_impact', '')
                            
                            st.markdown(f"**{feature}**")
                            st.markdown(f"- **Query:** {q_val}")
                            st.markdown(f"- **Twin:** {t_val}")
                            if impact:
                                st.info(f"_{impact}_")
                        else:
                            st.markdown(f"- {diff}")
                else:
                    st.caption("No major differences highlighted.")

        # --- 4. Detailed Analysis (Phenotype & Genomics) ---
        with st.expander("**Detailed Analysis**", expanded=False):
            st.markdown("### Phenotype Comparison")
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
            
            st.markdown("---")
            st.markdown("### Genomic Comparison")
            genomic = analysis.get('genomic_comparison', {})
            
            # Shared Variants
            st.markdown("**Shared Genomic Features**")
            shared_variants = genomic.get('shared_variants', [])
            if shared_variants:
                for sv in shared_variants:
                    gene = sv.get('gene', '')
                    variant = sv.get('variant', '')
                    sig = sv.get('clinical_significance', '')
                    st.markdown(f"- **{gene} {variant}**: {sig}")
            else:
                st.caption("No specific shared variants listed.")
            
            # Unique Alterations
            c3, c4 = st.columns(2)
            with c3:
                st.markdown(f"**Unique to Query ({analysis['query_patient_id']})**")
                for u in genomic.get('query_unique', []):
                    if isinstance(u, dict):
                        st.markdown(f"- **{u.get('gene')} {u.get('variant')}**: {u.get('clinical_significance')}")
                    else:
                        st.markdown(f"- {u}")
            with c4:
                st.markdown(f"**Unique to Twin ({analysis['twin_id']})**")
                for u in genomic.get('twin_unique', []):
                    if isinstance(u, dict):
                        st.markdown(f"- **{u.get('gene')} {u.get('variant')}**: {u.get('clinical_significance')}")
                    else:
                        st.markdown(f"- {u}")
            
            # Similarity Note
            if 'genomic_similarity_note' in genomic:
                st.info(f"**Note:** {genomic['genomic_similarity_note']}")

        # --- 5. Treatment Comparison ---
        with st.expander("**Treatment Comparison**", expanded=False):
            treatment = analysis.get('treatment_comparison', {})
            
            # Regimens
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Query Treatment ({analysis['query_patient_id']})**")
                for t in treatment.get('query_treatments', []):
                    t_name = t.get('treatment', t) if isinstance(t, dict) else t
                    st.markdown(f"<span class='pill pill-blue'>{t_name}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**Twin Treatment ({analysis['twin_id']})**")
                for t in treatment.get('twin_treatments', []):
                    t_name = t.get('treatment', t) if isinstance(t, dict) else t
                    st.markdown(f"<span class='pill pill-blue'>{t_name}</span>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Analysis Text
            if 'treatment_overlap' in treatment:
                st.markdown(f"**Treatment Overlap:** {treatment['treatment_overlap']}")
            if 'treatment_divergence' in treatment:
                st.markdown(f"**Treatment Divergence:** {treatment['treatment_divergence']}")
            
            # Gaps
            gaps = treatment.get('treatment_gaps', [])
            if gaps:
                st.markdown("**Identified Treatment Gaps:**")
                for gap in gaps:
                    st.warning(gap)

        # --- 6. Actionable Insights ---
        with st.expander("**Actionable Insights**", expanded=False):
            insights = analysis.get('actionable_insights', [])
            if insights:
                st.markdown("""
                <style>
                    .insight-card {
                        background-color: #FDF4FF;
                        border-left: 5px solid #D946EF;
                        padding: 15px;
                        margin-bottom: 10px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    }
                    .insight-header {
                        color: #86198F;
                        font-weight: bold;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        margin-bottom: 5px;
                    }
                    .insight-body {
                        color: #4A044E;
                        font-size: 0.95rem;
                        margin-bottom: 8px;
                    }
                    .insight-evidence {
                        font-size: 0.85rem;
                        color: #701A75;
                        font-style: italic;
                        margin-bottom: 5px;
                    }
                    .insight-action {
                        background-color: #FAE8FF;
                        padding: 5px 10px;
                        border-radius: 4px;
                        font-size: 0.9rem;
                        color: #86198F;
                        font-weight: 600;
                        display: inline-block;
                    }
                </style>
                """, unsafe_allow_html=True)

                for insight in insights:
                    if isinstance(insight, dict):
                        i_text = insight.get('insight', 'Insight')
                        evidence = insight.get('evidence', '')
                        action = insight.get('recommended_action', '')
                        
                        # Flatten HTML to avoid markdown code block issues
                        html_content = f"""<div class="insight-card"><div class="insight-header">💡 Insight</div><div class="insight-body">{i_text}</div>"""
                        if evidence:
                            html_content += f"""<div class="insight-evidence">Evidence: {evidence}</div>"""
                        if action:
                            html_content += f"""<div class="insight-action">Action: {action}</div>"""
                        html_content += "</div>"
                        
                        st.markdown(html_content, unsafe_allow_html=True)
                    else:
                        st.markdown(f"- {insight}")
            else:
                st.info("No specific actionable insights listed.")

        # --- 7. Recommendations ---
        with st.expander("**Recommendations**", expanded=False):
            recs = analysis.get('recommendations', [])
            if recs:
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
            else:
                st.info("No specific recommendations listed.")

        # --- 8. Matching Quality and Rationale ---
        with st.expander("**Matching Quality and Rationale**", expanded=False):
            
            # Create a single row with 3 columns (Cards)
            c1, c2, c3 = st.columns([1, 1, 2])
            
            # --- Card 1: Match Metrics ---
            with c1:
                st.markdown("""
                    <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; height: 100%;">
                        <div style="font-weight: 600; color: #0F172A; margin-bottom: 10px;">📊 Match Metrics</div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #64748B;">Score:</span>
                            <span style="font-weight: 600;">{score}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="color: #64748B;">Clinical:</span>
                            <span style="font-weight: 600;">{clinical}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748B;">Genomic:</span>
                            <span style="font-weight: 600;">{genomic}%</span>
                        </div>
                    </div>
                """.format(
                    score=display_score,
                    clinical=clinical_pct,
                    genomic=genomic_pct
                ), unsafe_allow_html=True)

            # --- Card 2: Treatment Guidance ---
            with c2:
                guidance = analysis.get('use_for_treatment_guidance')
                guidance_text = "Not Specified"
                guidance_color = "#64748B" # Gray
                bg_color = "#F1F5F9"
                
                if guidance is not None:
                    if isinstance(guidance, bool):
                        if guidance:
                            guidance_text = "Recommended"
                            guidance_color = "#166534" # Green
                            bg_color = "#F0FDF4"
                        else:
                            guidance_text = "Not Recommended"
                            guidance_color = "#991B1B" # Red
                            bg_color = "#FEF2F2"
                    else:
                        guidance_text = str(guidance)
                
                st.markdown(f"""
                    <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; border: 1px solid {bg_color}; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                        <div style="font-weight: 600; color: #0F172A; margin-bottom: 5px;">Treatment Guidance</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: {guidance_color};">
                            {guidance_text}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # --- Card 3: Overall Assessment ---
            with c3:
                assessment = match_quality.get('overall_assessment', 'No overall assessment provided.')
                st.markdown(f"""
                    <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; height: 100%;">
                        <div style="font-weight: 600; color: #0F172A; margin-bottom: 5px;">📝 Overall Assessment</div>
                        <div style="font-size: 0.9rem; color: #334155; line-height: 1.4;">
                            {assessment}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 4. Rationale
            st.markdown("#### Rationale")
            if 'rationale' in analysis:
                st.write(analysis['rationale'])
            
            # Strengths & Weaknesses
            st.markdown("**Strengths & Weaknesses**")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-header"><span class="text-green-600 section-icon">●</span> Match Strengths</div>', unsafe_allow_html=True)
                for s in match_quality.get('strengths', []):
                    st.markdown(f"- {s}")
            with c2:
                st.markdown('<div class="section-header"><span class="text-red-600 section-icon">●</span> Match Weaknesses</div>', unsafe_allow_html=True)
                for l in match_quality.get('weaknesses', []):
                    st.markdown(f"- {l}")

        # --- Deep Dive Navigation ---
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
