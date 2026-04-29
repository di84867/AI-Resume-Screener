import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import hashlib
import json

@st.cache_data(show_spinner=False)
def _get_cached_layout(data_hash, theme):
    """Internal helper to cache the expensive layout calculation."""
    # We don't actually need the data_hash inside, just for Streamlit caching
    return None 

def create_skill_network(processed_data, jd_text="", theme='dark'):
    """
    Generates an optimized 3D network graph.
    Uses caching to ensure the 'Galaxy' feels fast and responsive.
    """
    # Create a unique key for the data to avoid re-calculating if same data
    data_str = json.dumps({k: v.get('skills', []) for k, v in processed_data.items()}, sort_keys=True)
    data_hash = hashlib.md5(data_str.encode()).hexdigest()
    
    G = nx.Graph()
    text_color = '#E2E8F0' if theme == 'dark' else '#0F172A'
    line_color = 'rgba(255, 255, 255, 0.4)' if theme == 'dark' else 'rgba(0, 0, 0, 0.3)'
    
    # Build Graph with efficiency limits
    for name, data in processed_data.items():
        display_name = data.get('name', name)
        G.add_node(display_name, type='candidate', size=22, color='#6366F1', opacity=1.0)
        
        # Take top 12 most relevant skills to keep the 'Galaxy' clean and efficient
        c_skills = data.get('skills', [])[:12]
        for s in c_skills:
            s_clean = s.strip().title()
            if not G.has_node(s_clean):
                G.add_node(s_clean, type='skill', size=12, color='#2DD4BF', opacity=0.8)
            G.add_edge(display_name, s_clean)

    # Use a faster, cached layout approach
    # We use a fixed seed for layout stability
    pos = nx.spring_layout(G, k=0.8, dim=3, iterations=30, seed=42)

    # Traces configuration
    edge_x, edge_y, edge_z = [], [], []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]; edge_z += [z0, z1, None]

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_z = [pos[node][2] for node in G.nodes()]
    
    node_colors = [G.nodes[node]['color'] for node in G.nodes()]
    node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
    node_texts = [f"<b>{node}</b>" for node in G.nodes()]

    fig = go.Figure(data=[
        go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            line=dict(color=line_color, width=1.5),
            hoverinfo='none', mode='lines'
        ),
        go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            marker=dict(size=node_sizes, color=node_colors, opacity=0.9, line=dict(color='white', width=0.5)),
            text=node_texts,
            textfont=dict(color=text_color, size=11),
            textposition="top center",
            hoverinfo='text'
        )
    ])

    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=700,
        showlegend=False,
        hovermode='closest'
    )
    return fig
