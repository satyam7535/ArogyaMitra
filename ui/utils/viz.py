"""
ArogyaMitra — Interactive Plotly Visualization Module
Renders TreeSHAP feature attributions, calibrated probability distributions,
and epidemiological prevalence graphs.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any


def create_shap_waterfall_or_bar(shap_explanations: List[Dict[str, Any]], primary_disease: str) -> go.Figure:
    """
    Renders an interactive horizontal bar chart showing TreeSHAP feature contributions.
    Positive impacts (supports diagnosis) are displayed in teal/emerald,
    while negative impacts are displayed in coral/amber.
    """
    if not shap_explanations:
        fig = go.Figure()
        fig.add_annotation(
            text="No TreeSHAP feature attributions available for this prediction",
            showarrow=False,
            font=dict(size=14, color="#718096"),
        )
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    # Take top 10 features
    features = shap_explanations[:10]
    # Reverse so top feature appears at the top of horizontal chart
    features = features[::-1]

    names = [f.get("symptom", "").replace("_", " ").title() for f in features]
    impacts = [float(f.get("impact", 0.0)) for f in features]
    directions = [f.get("direction", "Supports Diagnosis") for f in features]

    colors = [
        "#10B981" if "supports" in str(d).lower() or imp > 0 else "#EF4444"
        for d, imp in zip(directions, impacts)
    ]

    fig = go.Figure(
        go.Bar(
            x=impacts,
            y=names,
            orientation="h",
            marker=dict(color=colors, line=dict(color="#1F2937", width=1)),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "SHAP Value: %{x:.4f}<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>TreeSHAP Diagnostic Feature Importance — {primary_disease}</b>",
            font=dict(size=16, color="#0F172A"),
        ),
        xaxis=dict(
            title="Marginal Contribution to Log-Odds (SHAP Value)",
            zeroline=True,
            zerolinecolor="#94A3B8",
            zerolinewidth=1.5,
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(
            title="",
            gridcolor="#F1F5F9",
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=340,
        margin=dict(l=150, r=30, t=50, b=50),
    )

    return fig


def create_top_predictions_chart(top_predictions: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders horizontal probability bar chart for differential diagnoses.
    """
    if not top_predictions:
        return go.Figure()

    diseases = [p.get("disease", "") for p in top_predictions][::-1]
    probs = [round(float(p.get("probability", 0.0)) * 100, 1) for p in top_predictions][::-1]

    fig = go.Figure(
        go.Bar(
            x=probs,
            y=diseases,
            orientation="h",
            marker=dict(
                color=["#93C5FD", "#60A5FA", "#2563EB"][:len(diseases)],
                line=dict(color="#1D4ED8", width=1),
            ),
            text=[f"{p}%" for p in probs],
            textposition="auto",
            hovertemplate="<b>%{y}</b>: %{x:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="<b>Calibrated Differential Diagnoses</b>", font=dict(size=14, color="#0F172A")),
        xaxis=dict(title="Calibrated Probability (%)", range=[0, 105], gridcolor="#E2E8F0"),
        yaxis=dict(title=""),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=220,
        margin=dict(l=160, r=20, t=40, b=40),
    )

    return fig


def create_admin_epidemiology_chart(disease_counts: Dict[str, int]) -> go.Figure:
    """
    Renders epidemiological disease prevalence distribution for Admin Dashboard.
    """
    if not disease_counts:
        return go.Figure()

    labels = list(disease_counts.keys())
    values = list(disease_counts.values())

    fig = px.pie(
        names=labels,
        values=values,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism,
    )

    fig.update_layout(
        title=dict(text="<b>Regional Disease Incidence Breakdown</b>", font=dict(size=16)),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    return fig
