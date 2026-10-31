"""
SPORTZA Chart Builders
Interactive Plotly charts for sports analytics.
All chart computation uses real data - never hardcoded values.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.visualization.theme import (
    COLORS,
    SEVERITY_COLORS,
    TEAM_COLORS,
    get_plotly_layout,
)


def _empty_fig(message: str = "No data available") -> go.Figure:
    """Return an empty figure with a message."""
    fig = go.Figure()
    fig.update_layout(
        **get_plotly_layout(),
        annotations=[{
            "text": message,
            "xref": "paper", "yref": "paper",
            "x": 0.5, "y": 0.5, "showarrow": False,
            "font": {"size": 16, "color": COLORS["text_secondary"]},
        }],
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=300,
    )
    return fig


def correlation_heatmap(
    df: pd.DataFrame,
    method: str = "pearson",
    title: str = "Correlation Matrix"
) -> go.Figure:
    """Interactive correlation heatmap with Pearson/Spearman toggle support."""
    if df.empty or df.select_dtypes(include=[np.number]).shape[1] < 2:
        return _empty_fig("Insufficient numeric columns for correlation analysis")
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr(method=method, min_periods=5)
    
    # Compute sample sizes
    n_samples = numeric_df.notna().astype(int)
    sample_sizes = n_samples.T.dot(n_samples)
    
    # Build hover text
    hover_text = []
    for i, row_name in enumerate(corr.index):
        row_text = []
        for j, col_name in enumerate(corr.columns):
            r = corr.iloc[i, j]
            n = sample_sizes.iloc[i, j]
            row_text.append(f"{row_name} vs {col_name}<br>r = {r:.3f}<br>n = {n}")
        hover_text.append(row_text)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale="RdBu_r",
        zmid=0,
        zmin=-1,
        zmax=1,
        text=hover_text,
        hoverinfo="text",
        colorbar={"title": f"{method.title()} r", "tickfont": {"size": 10}},
    ))
    
    fig.update_layout(
        **get_plotly_layout(title=title, height=500),
    )
    fig.update_xaxes(tickangle=45, tickfont={"size": 10})
    fig.update_yaxes(tickfont={"size": 10})
    return fig


def wellness_timeseries(
    df: pd.DataFrame,
    player_id: str,
    metrics: list[str],
    title: str = "Wellness Time Series"
) -> go.Figure:
    """Player wellness metrics over time with missingness markers."""
    player_data = df[df["player_id"] == player_id].sort_values("date")
    if player_data.empty:
        return _empty_fig(f"No wellness data for player {player_id}")
    
    fig = make_subplots(
        rows=len(metrics), cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=metrics,
    )
    
    colors = [COLORS["primary"], COLORS["secondary"], COLORS["warning"],
              COLORS["info"], COLORS["success"], COLORS["danger"], "#FF80AB"]
    
    for i, metric in enumerate(metrics):
        if metric not in player_data.columns:
            continue
        
        row = i + 1
        values = player_data[metric]
        dates = player_data["date"]
        color = colors[i % len(colors)]
        
        # Plot values
        fig.add_trace(
            go.Scatter(
                x=dates, y=values,
                mode="lines+markers",
                name=metric.replace("_", " ").title(),
                line={"color": color, "width": 2},
                marker={"size": 4},
                hovertemplate=f"{metric}: %{{y:.1f}}<br>Date: %{{x}}<extra></extra>",
            ),
            row=row, col=1,
        )
        
        # Mark missing values
        missing_dates = dates[values.isna()]
        if not missing_dates.empty:
            fig.add_trace(
                go.Scatter(
                    x=missing_dates,
                    y=[0] * len(missing_dates),
                    mode="markers",
                    name=f"{metric} (missing)",
                    marker={"symbol": "x", "size": 8, "color": COLORS["text_secondary"]},
                    showlegend=False,
                    hovertemplate=f"{metric}: Missing<br>Date: %{{x}}<extra></extra>",
                ),
                row=row, col=1,
            )
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=200 * len(metrics),
        showlegend=False,
    )
    return fig


def load_trend_chart(
    sessions_df: pd.DataFrame,
    player_id: str | None = None,
    title: str = "Training Load Trend"
) -> go.Figure:
    """Daily, weekly, and 28-day load trends."""
    df = sessions_df.copy()
    if player_id:
        df = df[df["player_id"] == player_id]
    if df.empty:
        return _empty_fig("No training session data available")
    
    # Compute daily load
    daily = df.groupby("session_date")["srpe"].sum().reset_index()
    daily.columns = ["date", "daily_load"]
    daily = daily.sort_values("date")
    daily["weekly_load"] = daily["daily_load"].rolling(7, min_periods=1).sum()
    daily["load_28d"] = daily["daily_load"].rolling(28, min_periods=1).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["daily_load"],
        name="Daily Load (sRPE)",
        marker_color=COLORS["primary"],
        opacity=0.5,
    ))
    
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["weekly_load"],
        name="7-Day Load",
        line={"color": COLORS["secondary"], "width": 2},
        hovertemplate="7-Day Load: %{y:.0f}<extra></extra>",
    ))
    
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["load_28d"],
        name="28-Day Avg",
        line={"color": COLORS["warning"], "width": 2, "dash": "dash"},
        hovertemplate="28-Day Avg: %{y:.0f}<extra></extra>",
    ))
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=400,
        barmode="overlay",
        yaxis_title="Load (sRPE)",
        legend={"orientation": "h", "y": -0.15},
    )
    return fig


def injury_heatmap(
    injury_df: pd.DataFrame,
    title: str = "Injury Reports: Body Location × Severity"
) -> go.Figure:
    """Injury body location vs severity heatmap."""
    if injury_df.empty or "body_location" not in injury_df.columns:
        return _empty_fig("No injury report data available")
    
    pivot = injury_df.groupby(
        ["body_location", "reported_severity"]
    ).size().unstack(fill_value=0)
    
    # Ensure both severity columns exist
    for sev in ["minor", "major"]:
        if sev not in pivot.columns:
            pivot[sev] = 0
    pivot = pivot[["minor", "major"]]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[[0, "#1E1E2E"], [0.5, "#FFB74D"], [1, "#FF5252"]],
        text=pivot.values,
        texttemplate="%{text}",
        hovertemplate="Location: %{y}<br>Severity: %{x}<br>Count: %{z}<extra></extra>",
        colorbar={"title": "Count"},
    ))
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=max(400, len(pivot) * 30),
        xaxis_title="Reported Severity (Self-Reported)",
        yaxis_title="Body Location",
    )
    fig.add_annotation(
        text="Note: All injury reports are self-reported by players, not clinical diagnoses.",
        xref="paper", yref="paper", x=0, y=-0.15,
        showarrow=False, font={"size": 10, "color": COLORS["text_secondary"]},
    )
    return fig


def injury_timeline(
    injury_df: pd.DataFrame,
    title: str = "Injury Report Timeline"
) -> go.Figure:
    """Timeline of injury reports over time."""
    if injury_df.empty:
        return _empty_fig("No injury report data available")
    
    df = injury_df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"])
    
    fig = go.Figure()
    
    for severity in ["minor", "major"]:
        mask = df["reported_severity"] == severity
        sub = df[mask]
        if not sub.empty:
            fig.add_trace(go.Scatter(
                x=sub["event_date"],
                y=sub["player_id"],
                mode="markers",
                name=f"{severity.title()} (self-reported)",
                marker={
                    "size": 10 if severity == "major" else 7,
                    "color": SEVERITY_COLORS[severity],
                    "symbol": "diamond" if severity == "major" else "circle",
                },
                hovertemplate=(
                    f"Player: %{{y}}<br>Date: %{{x}}<br>"
                    f"Location: {sub['body_location'].values[0] if len(sub) == 1 else '%{customdata[0]}'}<br>"
                    f"Severity: {severity}<extra></extra>"
                ),
            ))
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=400,
        xaxis_title="Date",
        yaxis_title="Player",
        legend={"orientation": "h", "y": -0.15},
    )
    fig.add_annotation(
        text="Self-reported pain/injury notifications, not clinical diagnoses",
        xref="paper", yref="paper", x=0, y=-0.2,
        showarrow=False, font={"size": 10, "color": COLORS["text_secondary"]},
    )
    return fig


def team_comparison_boxplot(
    sessions_df: pd.DataFrame,
    metric: str = "session_count",
    title: str = "Training Sessions per Player by Team/Year"
) -> go.Figure:
    """Team A vs Team B comparison boxplot with raw points."""
    if sessions_df.empty:
        return _empty_fig("No training session data available")
    
    df = sessions_df.copy()
    df["session_date"] = pd.to_datetime(df["session_date"])
    df["year"] = df["session_date"].dt.year
    df["team"] = df["player_id"].apply(
        lambda x: "Team A" if "TeamA" in str(x) else "Team B"
    )
    
    # Count sessions per player per year
    counts = df.groupby(["player_id", "team", "year"]).size().reset_index(name="session_count")
    
    fig = go.Figure()
    
    for team in ["Team A", "Team B"]:
        team_data = counts[counts["team"] == team]
        for year in sorted(team_data["year"].unique()):
            year_data = team_data[team_data["year"] == year]
            color = TEAM_COLORS.get(team.replace(" ", ""), COLORS["primary"])
            
            fig.add_trace(go.Box(
                y=year_data["session_count"],
                name=f"{team} {year}",
                marker_color=color,
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.5,
                hovertemplate=f"{team} {year}<br>Sessions: %{{y}}<extra></extra>",
            ))
    
    n_total = len(counts)
    fig.update_layout(
        **get_plotly_layout(title=f"{title} (n={n_total} player-years)"),
        height=450,
        yaxis_title="Number of Training Sessions",
        showlegend=True,
    )
    return fig


def missingness_heatmap(
    df: pd.DataFrame,
    date_col: str = "date",
    player_col: str = "player_id",
    value_cols: list[str] | None = None,
    title: str = "Data Coverage Matrix"
) -> go.Figure:
    """Missingness / data coverage heatmap by player and date."""
    if df.empty:
        return _empty_fig("No data to analyze for coverage")
    
    if value_cols is None:
        value_cols = [c for c in df.columns if c not in [date_col, player_col, "source_dataset", "source_file", "ingested_at"]]
    
    # Compute coverage per player
    coverage = df.groupby(player_col)[value_cols].apply(
        lambda x: x.notna().mean()
    ).reset_index()
    
    if coverage.empty:
        return _empty_fig("Could not compute coverage")
    
    coverage = coverage.set_index(player_col)
    
    fig = go.Figure(data=go.Heatmap(
        z=coverage.values,
        x=coverage.columns,
        y=coverage.index,
        colorscale=[[0, "#FF5252"], [0.5, "#FFB74D"], [1, "#69F0AE"]],
        zmin=0, zmax=1,
        text=np.round(coverage.values * 100, 1),
        texttemplate="%{text}%",
        hovertemplate="Player: %{y}<br>Metric: %{x}<br>Coverage: %{z:.1%}<extra></extra>",
        colorbar={"title": "Coverage", "tickformat": ".0%"},
    ))
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=max(400, len(coverage) * 25),
    )
    fig.update_xaxes(tickangle=45)
    return fig


def actual_vs_predicted(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    dates: np.ndarray | None = None,
    title: str = "Actual vs Predicted Readiness"
) -> go.Figure:
    """Actual vs predicted scatter and time series."""
    if len(y_true) == 0:
        return _empty_fig("No predictions available")
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Scatter", "Residuals"])
    
    # Scatter plot
    fig.add_trace(
        go.Scatter(
            x=y_true, y=y_pred,
            mode="markers",
            name="Predictions",
            marker={"color": COLORS["primary"], "size": 6, "opacity": 0.6},
            hovertemplate="Actual: %{x:.1f}<br>Predicted: %{y:.1f}<extra></extra>",
        ),
        row=1, col=1,
    )
    
    # Perfect prediction line
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines", name="Perfect",
            line={"color": COLORS["text_secondary"], "dash": "dash"},
        ),
        row=1, col=1,
    )
    
    # Residuals
    residuals = np.array(y_pred) - np.array(y_true)
    x_axis = dates if dates is not None else np.arange(len(residuals))
    
    fig.add_trace(
        go.Bar(
            x=x_axis, y=residuals,
            name="Residuals",
            marker_color=[COLORS["primary"] if r >= 0 else COLORS["danger"] for r in residuals],
            opacity=0.7,
        ),
        row=1, col=2,
    )
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=400,
        showlegend=False,
    )
    fig.update_xaxes(title_text="Actual", row=1, col=1)
    fig.update_yaxes(title_text="Predicted", row=1, col=1)
    fig.update_xaxes(title_text="Sample", row=1, col=2)
    fig.update_yaxes(title_text="Residual", row=1, col=2)
    
    return fig


def feature_importance_chart(
    feature_names: list[str],
    importances: np.ndarray,
    title: str = "Feature Importance",
    top_n: int = 15,
) -> go.Figure:
    """Horizontal bar chart of feature importances."""
    if len(feature_names) == 0:
        return _empty_fig("No feature importances available")
    
    # Sort and take top N
    idx = np.argsort(importances)[-top_n:]
    names = [feature_names[i] for i in idx]
    values = importances[idx]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation="h",
        marker_color=COLORS["primary"],
        hovertemplate="Feature: %{y}<br>Importance: %{x:.4f}<extra></extra>",
    ))
    
    fig.update_layout(
        **get_plotly_layout(title=title),
        height=max(300, top_n * 25),
        xaxis_title="Importance",
    )
    return fig


def squad_readiness_distribution(
    wellness_df: pd.DataFrame,
    date: str | None = None,
    title: str = "Squad Readiness Distribution"
) -> go.Figure:
    """Distribution of readiness scores across the squad."""
    if wellness_df.empty or "readiness" not in wellness_df.columns:
        return _empty_fig("No readiness data available")
    
    df = wellness_df.copy()
    if date:
        df = df[df["date"] == date]
    
    if df.empty:
        return _empty_fig(f"No readiness data for {date}")
    
    values = df["readiness"].dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=10,
        marker_color=COLORS["primary"],
        opacity=0.7,
        name="Readiness",
        hovertemplate="Readiness: %{x}<br>Count: %{y}<extra></extra>",
    ))
    
    # Add mean line
    mean_val = values.mean()
    fig.add_vline(
        x=mean_val, line_dash="dash", line_color=COLORS["warning"],
        annotation_text=f"Mean: {mean_val:.1f}",
    )
    
    fig.update_layout(
        **get_plotly_layout(title=f"{title} (n={len(values)})"),
        height=350,
        xaxis_title="Readiness Score (1-10)",
        yaxis_title="Count",
    )
    return fig

