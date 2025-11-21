import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show(patient_profiles):
    st.title("Genomics Deep Dive")
    
    # Patient Selection
    patient_ids = sorted(list(patient_profiles.keys()))
    
    # Initialize session state for patient selection if not present
    if "genomics_patient_id" not in st.session_state:
        st.session_state.genomics_patient_id = None
        
    # Use index to set default value if in session state
    index = 0
    if st.session_state.genomics_patient_id in patient_ids:
        index = patient_ids.index(st.session_state.genomics_patient_id)
        
    selected_patient_id = st.selectbox("Select Patient ID", patient_ids, index=index, key="genomics_patient_select")
    
    # Update session state when selection changes
    if selected_patient_id:
        st.session_state.genomics_patient_id = selected_patient_id
    
    if selected_patient_id:
        profile = patient_profiles[selected_patient_id]
        genomics = profile.get('genomics', {})
        samples = genomics.get('samples', {})
        
        if not samples:
            st.warning(f"No genomic samples found for patient {selected_patient_id}")
            return

        sample_ids = sorted(list(samples.keys()))
        
        if len(sample_ids) == 1:
            # Single sample - show directly
            st.subheader(f"Genomic Profile: {sample_ids[0]}")
            show_sample_data(sample_ids[0], samples[sample_ids[0]])
        else:
            # Multiple samples - show timeline and allow selection
            st.subheader(f"Found {len(sample_ids)} samples for patient {selected_patient_id}")
            
            # Display timeline view
            st.markdown("### Sample Timeline")
            show_sample_timeline(samples)
            
            st.divider()
            
            # Sample selector
            selected_sample_id = st.selectbox(
                "Select a sample to view detailed genomic data:",
                sample_ids
            )
            
            if selected_sample_id:
                st.subheader(f"Detailed Genomic Profile: {selected_sample_id}")
                show_sample_data(selected_sample_id, samples[selected_sample_id])

def show_sample_timeline(samples):
    """Display samples in a timeline view with genomic alteration counts."""
    
    timeline_data = []
    for i, (sample_id, data) in enumerate(samples.items()):
        sample_info = data.get('sample_info', {})
        mutations = data.get('mutations', [])
        cnas = data.get('copy_number_alterations', [])
        svs = data.get('structural_variants', [])
        
        timeline_data.append({
            'Sample': sample_id,
            'Type': sample_info.get('sample_type', 'Unknown'),
            'Cancer Type': sample_info.get('cancer_type_detailed', 'Unknown'),
            'Mutations': len(mutations),
            'CNAs': len(cnas),
            'SVs': len(svs),
            'Total': len(mutations) + len(cnas) + len(svs)
        })
    
    df_timeline = pd.DataFrame(timeline_data)
    
    # Display as cards
    cols = st.columns(min(len(samples), 3))
    for idx, row in df_timeline.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**{row['Sample']}**")
                st.caption(f"Type: {row['Type']}")
                st.caption(f"Cancer: {row['Cancer Type']}")
                
                # Mini metrics
                metric_cols = st.columns(3)
                metric_cols[0].metric("Mut", row['Mutations'])
                metric_cols[1].metric("CNA", row['CNAs'])
                metric_cols[2].metric("SV", row['SVs'])

    # Alteration comparison chart
    st.markdown("#### Genomic Alterations Across Samples")
    fig = go.Figure()
    
    fig.add_trace(go.Bar(name='Mutations', x=df_timeline['Sample'], y=df_timeline['Mutations'], marker_color='#FF6B6B'))
    fig.add_trace(go.Bar(name='CNAs', x=df_timeline['Sample'], y=df_timeline['CNAs'], marker_color='#4ECDC4'))
    fig.add_trace(go.Bar(name='SVs', x=df_timeline['Sample'], y=df_timeline['SVs'], marker_color='#95E1D3'))
    
    fig.update_layout(barmode='group', xaxis_title='Sample', yaxis_title='Count', height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_sample_data(sample_id, sample_data):
    """Display detailed genomic data for a specific sample."""
    
    # Create tabs for different genomic data types
    tab1, tab2, tab3, tab4 = st.tabs(["Mutations", "Copy Number Alterations", "Structural Variants", "Summary"])
    
    with tab1:
        show_mutations(sample_data.get('mutations', []))
    
    with tab2:
        show_cna(sample_data.get('copy_number_alterations', []))
    
    with tab3:
        show_sv(sample_data.get('structural_variants', []))
    
    with tab4:
        show_summary(sample_id, sample_data)

def show_mutations(mutations_list):
    """Display mutation data."""
    st.markdown("### Mutations")
    
    if not mutations_list:
        st.warning("No mutation data available.")
        return
    
    # Convert to DataFrame and map columns
    df = pd.DataFrame(mutations_list)
    
    # Rename columns to match expected display format
    column_map = {
        'gene': 'hugo_symbol',
        'protein_change': 'HGVSp_Short',
        'variant_classification': 'variant_classification',
        'chromosome': 'chromosome',
        'position': 'start_position',
        'ref_allele': 'reference_allele',
        'alt_allele': 'tumor_seq_allele2'
    }
    df = df.rename(columns=column_map)
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Mutations", len(df))
    
    if 'variant_classification' in df.columns:
        missense_count = len(df[df['variant_classification'] == 'Missense_Mutation'])
        col2.metric("Missense Mutations", missense_count)
    
    if 'hugo_symbol' in df.columns:
        unique_genes = df['hugo_symbol'].nunique()
        col3.metric("Affected Genes", unique_genes)
    
    # Variant Classification Distribution
    if 'variant_classification' in df.columns:
        st.markdown("#### Variant Classification Distribution")
        variant_counts = df['variant_classification'].value_counts()
        fig = px.bar(x=variant_counts.index, y=variant_counts.values,
                     labels={'x': 'Variant Classification', 'y': 'Count'},
                     title='Distribution of Variant Types',
                     color=variant_counts.values,
                     color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    # Top mutated genes
    if 'hugo_symbol' in df.columns:
        st.markdown("#### Top Mutated Genes")
        gene_counts = df['hugo_symbol'].value_counts().head(10)
        fig = px.bar(x=gene_counts.values, y=gene_counts.index, orientation='h',
                     labels={'x': 'Number of Mutations', 'y': 'Gene'},
                     title='Top 10 Mutated Genes',
                     color=gene_counts.values,
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed mutations table
    st.markdown("#### Detailed Mutations")
    display_columns = ['hugo_symbol', 'variant_classification', 'HGVSp_Short', 
                      'chromosome', 'start_position', 'reference_allele', 
                      'tumor_seq_allele2']
    
    # Filter to only existing columns
    display_columns = [col for col in display_columns if col in df.columns]
    
    if display_columns:
        st.dataframe(df[display_columns], use_container_width=True, height=400)
    else:
        st.dataframe(df, use_container_width=True, height=400)

def show_cna(cna_list):
    """Display copy number alteration data."""
    st.markdown("### Copy Number Alterations (CNA)")
    
    if not cna_list:
        st.info("No CNA data available.")
        return
    
    df = pd.DataFrame(cna_list)
    
    # Rename columns
    column_map = {
        'gene': 'Hugo_Symbol',
        'alteration_type': 'Alteration_Type',
        'gistic_value': 'GISTIC_value'
    }
    df = df.rename(columns=column_map)
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total CNAs", len(df))
    
    if 'Alteration_Type' in df.columns:
        amp_count = len(df[df['Alteration_Type'] == 'Amplification'])
        del_count = len(df[df['Alteration_Type'] == 'Deletion'])
        col2.metric("Amplifications", amp_count)
        col3.metric("Deletions", del_count)
    
    # CNA Type Distribution
    if 'Alteration_Type' in df.columns:
        st.markdown("#### CNA Type Distribution")
        cna_counts = df['Alteration_Type'].value_counts()
        fig = px.pie(values=cna_counts.values, names=cna_counts.index,
                     title='Distribution of CNA Types',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed CNA table
    st.markdown("#### Detailed CNAs")
    display_columns = ['Hugo_Symbol', 'Alteration_Type', 'GISTIC_value']
    display_columns = [col for col in display_columns if col in df.columns]
    
    if display_columns:
        st.dataframe(df[display_columns], use_container_width=True, height=400)
    else:
        st.dataframe(df, use_container_width=True, height=400)

def show_sv(sv_list):
    """Display structural variant data."""
    st.markdown("### Structural Variants (SV)")
    
    if not sv_list:
        st.info("No SV data available.")
        return
    
    df = pd.DataFrame(sv_list)
    
    # Rename columns
    column_map = {
        'site1_gene': 'SITE1_HUGO_SYMBOL',
        'site2_gene': 'SITE2_HUGO_SYMBOL',
        'sv_type': 'SV_STATUS',
        'site1_chromosome': 'SITE1_CHROMOSOME',
        'site2_chromosome': 'SITE2_CHROMOSOME'
    }
    df = df.rename(columns=column_map)
    
    # Display key metrics
    col1, col2 = st.columns(2)
    col1.metric("Total SVs", len(df))
    
    if 'SV_STATUS' in df.columns:
        somatic_count = len(df[df['SV_STATUS'] == 'SOMATIC'])
        col2.metric("Somatic SVs", somatic_count)
    
    # Detailed SV table
    st.markdown("#### Detailed Structural Variants")
    display_columns = ['SITE1_HUGO_SYMBOL', 'SITE2_HUGO_SYMBOL', 'SV_STATUS', 
                      'SITE1_CHROMOSOME', 'SITE2_CHROMOSOME']
    display_columns = [col for col in display_columns if col in df.columns]
    
    if display_columns:
        st.dataframe(df[display_columns], use_container_width=True, height=400)
    else:
        st.dataframe(df, use_container_width=True, height=400)

def show_summary(sample_id, sample_data):
    """Display summary of all genomic alterations."""
    st.markdown("### Genomic Summary")
    
    mutations = sample_data.get('mutations', [])
    cnas = sample_data.get('copy_number_alterations', [])
    svs = sample_data.get('structural_variants', [])
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Mutations", len(mutations))
    col2.metric("CNAs", len(cnas))
    col3.metric("SVs", len(svs))
    
    # Create summary visualization
    st.markdown("#### Genomic Alteration Overview")
    summary_data = pd.DataFrame({
        'Type': ['Mutations', 'CNAs', 'SVs'],
        'Count': [len(mutations), len(cnas), len(svs)]
    })
    
    fig = px.bar(summary_data, x='Type', y='Count',
                 title='Genomic Alterations by Type',
                 color='Type',
                 color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#95E1D3'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Display sample info
    sample_info = sample_data.get('sample_info', {})
    if sample_info:
        st.markdown("#### Sample Clinical Information")
        st.dataframe(pd.DataFrame([sample_info]).T, use_container_width=True)
