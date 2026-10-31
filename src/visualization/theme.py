"""
SPORTZA Visualization Theme
Dark theme with tasteful accent colors for sports analytics dashboard.
"""
from typing import Any

# Color palette
COLORS = {
    "primary": "#00D4AA",       # Teal-green accent
    "secondary": "#7C4DFF",     # Purple accent
    "warning": "#FFB74D",       # Amber warning
    "danger": "#FF5252",        # Red danger
    "success": "#69F0AE",       # Green success
    "info": "#40C4FF",          # Blue info
    "text": "#E0E0E0",          # Light text
    "text_secondary": "#9E9E9E", # Muted text
    "background": "#0E1117",    # Dark background
    "surface": "#1E1E2E",       # Card surface
    "border": "#2D2D3F",        # Border color
}

# Team colors
TEAM_COLORS = {
    "TeamA": "#00D4AA",
    "TeamB": "#7C4DFF",
}

# Severity colors
SEVERITY_COLORS = {
    "minor": "#FFB74D",
    "major": "#FF5252",
}

# Status colors for recommendations
STATUS_COLORS = {
    "Monitor": "#69F0AE",
    "Recovery-focused option": "#FFB74D",
    "Human review needed": "#FF5252",
    "Insufficient data": "#9E9E9E",
}

# Plotly dark theme template
PLOTLY_TEMPLATE: dict[str, Any] = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#E0E0E0", "family": "Inter, sans-serif"},
        "title": {"font": {"size": 16, "color": "#E0E0E0"}},
        "xaxis": {
            "gridcolor": "rgba(255,255,255,0.06)",
            "zerolinecolor": "rgba(255,255,255,0.1)",
            "tickfont": {"size": 11},
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,0.06)",
            "zerolinecolor": "rgba(255,255,255,0.1)",
            "tickfont": {"size": 11},
        },
        "colorway": [
            "#00D4AA", "#7C4DFF", "#FFB74D", "#FF5252",
            "#40C4FF", "#69F0AE", "#FF80AB", "#B388FF",
            "#84FFFF", "#FFFF8D",
        ],
        "margin": {"l": 60, "r": 30, "t": 50, "b": 50},
        "hoverlabel": {
            "bgcolor": "#1E1E2E",
            "font_size": 12,
            "font_color": "#E0E0E0",
        },
    }
}


def get_plotly_layout(**kwargs) -> dict:
    """Return a copy of the base Plotly layout with optional overrides."""
    import copy
    layout = copy.deepcopy(PLOTLY_TEMPLATE["layout"])
    for k, v in kwargs.items():
        if isinstance(v, dict) and k in layout and isinstance(layout[k], dict):
            layout[k].update(v)
        else:
            layout[k] = v
    return layout


def apply_streamlit_theme():
    """Apply custom CSS for SPORTZA dark theme in Streamlit."""
    import streamlit as st
    st.markdown("""
    <style>
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1E1E2E 0%, #252540 100%);
        border: 1px solid #2D2D3F;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00D4AA;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #9E9E9E;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    .kpi-sublabel {
        font-size: 0.75rem;
        color: #757575;
        margin: 0;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-monitor { background: rgba(105,240,174,0.15); color: #69F0AE; }
    .status-recovery { background: rgba(255,183,77,0.15); color: #FFB74D; }
    .status-review { background: rgba(255,82,82,0.15); color: #FF5252; }
    .status-insufficient { background: rgba(158,158,158,0.15); color: #9E9E9E; }
    
    /* Data source banner */
    .data-banner {
        background: rgba(0,212,170,0.08);
        border: 1px solid rgba(0,212,170,0.2);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #9E9E9E;
        margin-bottom: 1rem;
    }
    .data-banner-demo {
        background: rgba(255,183,77,0.08);
        border: 1px solid rgba(255,183,77,0.2);
    }
    
    /* Non-medical disclaimer */
    .disclaimer {
        background: rgba(255,82,82,0.06);
        border-left: 3px solid #FF5252;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: #BDBDBD;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    /* Recommendation card */
    .rec-card {
        background: #1E1E2E;
        border: 1px solid #2D2D3F;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Section headers */
    .section-header {
        font-size: 0.9rem;
        color: #9E9E9E;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #2D2D3F;
        padding-bottom: 0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, sublabel: str = "") -> str:
    """Return HTML for a KPI card."""
    sub = f'<p class="kpi-sublabel">{sublabel}</p>' if sublabel else ""
    return f"""
    <div class="kpi-card">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        {sub}
    </div>
    """


def render_data_banner(is_demo: bool, last_updated: str = "", attribution: str = "") -> str:
    """Render data source status banner."""
    cls = "data-banner data-banner-demo" if is_demo else "data-banner"
    mode = "🧪 SYNTHETIC DEMO DATA" if is_demo else "📊 SoccerMon Real Data"
    parts = [f"<strong>{mode}</strong>"]
    if last_updated:
        parts.append(f" | Last updated: {last_updated}")
    if attribution:
        parts.append(f"<br><small>{attribution}</small>")
    return f'<div class="{cls}">{"".join(parts)}</div>'


def render_disclaimer() -> str:
    """Render non-medical disclaimer."""
    return """
    <div class="disclaimer">
        ⚕️ <strong>Non-Medical Tool:</strong> SPORTZA is a decision-support research tool, not a medical device. 
        All suggestions are based on reported data patterns and should be reviewed by a qualified 
        sports clinician or coach before implementation. This system does not diagnose injuries, 
        prescribe treatment, or clear athletes for participation.
    </div>
    """

