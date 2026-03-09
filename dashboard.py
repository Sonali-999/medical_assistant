# ─── dashboard.py ─────────────────────────────────────────────────────────────
# Health + Drug Dashboard for MediAssist AI
# Imported by gradio_app.py — does NOT modify any existing functions.
# Data pulled from MongoDB (chats_collection + prescriptions_collection).
# Falls back to mock data gracefully if collections are empty.
# ──────────────────────────────────────────────────────────────────────────────

from collections import Counter
from datetime import datetime

import gradio as gr
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for Gradio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
from PIL import Image

from mongo_db import chats_collection, prescriptions_collection


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════

def _mock_data():
    """Fallback mock dataset when MongoDB has no records."""
    return {
        "consultations": 6,
        "drug_recs":     4,
        "images":        3,
        "conditions":    ["Fever", "Skin Rash", "Allergy", "Fever", "Headache", "Fever"],
        "drug_history": [
            {"date": "Feb 10", "condition": "Fever",    "drug": "Paracetamol"},
            {"date": "Feb 18", "condition": "Allergy",  "drug": "Cetirizine"},
            {"date": "Mar 02", "condition": "Headache", "drug": "Ibuprofen"},
            {"date": "Mar 05", "condition": "Fever",    "drug": "Paracetamol"},
        ],
    }


def get_health_summary(user_id: str) -> dict:
    """Return counts: consultations, images_analyzed."""
    try:
        consultations = chats_collection.count_documents({"user_id": user_id})
        images = chats_collection.count_documents({
            "user_id": user_id,
            "bot_msg":  {"$regex": "With what I see", "$options": "i"}
        })
        if consultations == 0:
            mock = _mock_data()
            return {"consultations": mock["consultations"],
                    "images":        mock["images"],
                    "is_mock":       True}
        return {"consultations": consultations,
                "images":        images,
                "is_mock":       False}
    except Exception as e:
        print(f"[dashboard] get_health_summary error: {e}")
        mock = _mock_data()
        return {"consultations": mock["consultations"],
                "images":        mock["images"],
                "is_mock":       True}


def get_recent_diagnoses(user_id: str, limit: int = 5) -> list[str]:
    """Return the last N diagnosed conditions from prescriptions."""
    try:
        docs = list(
            prescriptions_collection
            .find({"user_id": user_id}, {"condition": 1, "_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        conditions = [d["condition"].strip().title() for d in docs if d.get("condition")]
        if not conditions:
            return _mock_data()["conditions"][:limit]
        return conditions
    except Exception as e:
        print(f"[dashboard] get_recent_diagnoses error: {e}")
        return _mock_data()["conditions"][:limit]


def get_drug_history(user_id: str, limit: int = 8) -> list[dict]:
    """Return last N prescription records with date / condition / drug names."""
    try:
        docs = list(
            prescriptions_collection
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        history = []
        for d in docs:
            date_raw = d.get("created_at")
            date_str = date_raw.strftime("%b %d") if isinstance(date_raw, datetime) else "—"
            condition = d.get("condition", "Unknown").strip().title()
            drugs_list = d.get("drugs", [])
            # drugs is a list of dicts with "name" key (from fixed drug_recommender)
            drug_names = ", ".join(
                dr["name"] for dr in drugs_list if isinstance(dr, dict) and dr.get("name")
            ) if drugs_list else "—"
            history.append({"date": date_str, "condition": condition, "drugs": drug_names})
        if not history:
            return _mock_data()["drug_history"]
        return history
    except Exception as e:
        print(f"[dashboard] get_drug_history error: {e}")
        return _mock_data()["drug_history"]


def get_all_conditions(user_id: str) -> list[str]:
    """Return all condition strings for frequency analysis."""
    try:
        docs = list(
            prescriptions_collection
            .find({"user_id": user_id}, {"condition": 1, "_id": 0})
        )
        raw = [d["condition"].strip().lower() for d in docs if d.get("condition")]
        if not raw:
            return [c.lower() for c in _mock_data()["conditions"]]
        return raw
    except Exception:
        return [c.lower() for c in _mock_data()["conditions"]]


def get_all_drugs(user_id: str) -> list[str]:
    """Return flat list of all drug names ever recommended."""
    try:
        docs = list(
            prescriptions_collection
            .find({"user_id": user_id}, {"drugs": 1, "_id": 0})
        )
        names = []
        for d in docs:
            for drug in d.get("drugs", []):
                if isinstance(drug, dict) and drug.get("name"):
                    names.append(drug["name"])
        if not names:
            return ["Paracetamol", "Paracetamol", "Cetirizine",
                    "Ibuprofen", "Paracetamol", "Cetirizine", "Ibuprofen"]
        return names
    except Exception:
        return ["Paracetamol", "Paracetamol", "Cetirizine", "Ibuprofen"]


def generate_health_insights(user_id: str) -> list[dict]:
    """
    Simple frequency-based insight rules.
    Returns list of {icon, title, message} dicts.
    """
    conditions = get_all_conditions(user_id)
    counter    = Counter(conditions)
    insights   = []

    # Rule: repeated condition (≥2 occurrences)
    for condition, count in counter.most_common(3):
        if count >= 2:
            label = condition.title()
            if "headache" in condition or "migraine" in condition:
                insights.append({
                    "icon":    "",
                    "title":   f"Frequent {label} Detected ({count}×)",
                    "message": "Recurring headaches may indicate tension, dehydration, or eye strain. Consider consulting a neurologist if they persist.",
                    "color":   "#7c3aed",
                })
            elif "fever" in condition or "temperature" in condition:
                insights.append({
                    "icon":    "",
                    "title":   f"Recurring {label} ({count}×)",
                    "message": "Multiple fever episodes could point to an underlying infection. A physician check-up is recommended.",
                    "color":   "#dc2626",
                })
            elif "allergy" in condition or "rash" in condition:
                insights.append({
                    "icon":    "",
                    "title":   f"Repeated {label} ({count}×)",
                    "message": "Frequent allergic reactions may benefit from an allergy panel test and consultation with an allergist.",
                    "color":   "#d97706",
                })
            elif "fungal" in condition or "infection" in condition:
                insights.append({
                    "icon":    "",
                    "title":   f"Recurring {label} ({count}×)",
                    "message": "Repeated infections may require stronger treatment or investigation of immune function.",
                    "color":   "#ea580c",
                })
            else:
                insights.append({
                    "icon":    "",
                    "title":   f"Repeated {label} ({count}×)",
                    "message": f"{label} has appeared {count} times in your history. If it persists, consult a healthcare professional.",
                    "color":   "#0891b2",
                })

    if not insights:
        insights.append({
            "icon":    "",
            "title":   "No Recurring Conditions",
            "message": "Your health history looks varied with no single repeated concern. Keep monitoring and stay hydrated!",
            "color":   "#059669",
        })

    return insights


# ══════════════════════════════════════════════════════════════════════════════
# CHART GENERATORS  (return PIL Image objects for gr.Image)
# ══════════════════════════════════════════════════════════════════════════════

_PALETTE = ["#0891b2", "#06b6d4", "#7c3aed", "#059669", "#d97706", "#dc2626", "#64748b"]


def _fig_to_pil(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=130)
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return img


def create_condition_chart(user_id: str) -> Image.Image:
    """Horizontal bar chart of most-detected conditions."""
    conditions = get_all_conditions(user_id)
    counter    = Counter(conditions)
    top        = counter.most_common(6)

    if not top:
        top = [("fever", 3), ("allergy", 2), ("headache", 1)]

    labels = [c.title() for c, _ in reversed(top)]
    values = [v for _, v in reversed(top)]
    colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(6, max(2.5, len(labels) * 0.55)))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    bars = ax.barh(labels, values, color=colors, height=0.55, zorder=3)

    # Value labels inside bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", ha="left",
            fontsize=9, fontweight="600", color="#0f172a"
        )

    ax.set_xlabel("Number of Occurrences", fontsize=9, color="#64748b")
    ax.set_title("Most Detected Conditions", fontsize=11, fontweight="700",
                 color="#0f172a", pad=12)
    ax.tick_params(colors="#475569", labelsize=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.grid(axis="x", color="#e2e8f0", linewidth=0.8, zorder=0)
    ax.set_xlim(0, max(values) * 1.25)
    fig.tight_layout()

    return _fig_to_pil(fig)


def create_drug_chart(user_id: str) -> Image.Image:
    """Donut chart of drug recommendation frequency."""
    drugs   = get_all_drugs(user_id)
    counter = Counter(drugs)
    top     = counter.most_common(6)

    if not top:
        top = [("Paracetamol", 3), ("Cetirizine", 2), ("Ibuprofen", 1)]

    labels = [name for name, _ in top]
    values = [cnt  for _, cnt  in top]
    colors = _PALETTE[:len(labels)]

    fig, ax = plt.subplots(figsize=(5.5, 4))
    fig.patch.set_facecolor("#ffffff")

    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,
        colors=colors,
        autopct="%1.0f%%",
        startangle=140,
        pctdistance=0.78,
        wedgeprops={"width": 0.52, "edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("700")

    # Legend
    patches = [mpatches.Patch(color=c, label=f"{l} ({v})")
               for l, v, c in zip(labels, values, colors)]
    ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.18),
              ncol=2, fontsize=8, frameon=False)

    ax.set_title("Drug Recommendation Frequency", fontsize=11,
                 fontweight="700", color="#0f172a", pad=10)
    fig.tight_layout()

    return _fig_to_pil(fig)


# ══════════════════════════════════════════════════════════════════════════════
# HTML BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _summary_html(summary: dict) -> str:
    mock_note = (
        '<div style="background:#fef9c3;border:1px solid #fde047;border-radius:7px;'
        'padding:0.5rem 0.9rem;margin-bottom:1rem;font-size:0.76rem;color:#854d0e;">'
        'Showing sample data — complete a consultation to see real stats.'
        '</div>'
    ) if summary.get("is_mock") else ""

    stats = [
        ("Consultations",  summary["consultations"], "#0891b2"),
        ("Images Analysed", summary["images"],        "#7c3aed"),
    ]
    cards = ""
    for label, value, color in stats:
        cards += f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
                    padding:1.25rem 1.5rem;flex:1;min-width:140px;
                    border-top:3px solid {color};box-shadow:0 1px 4px rgba(0,0,0,0.05);">
            <div style="font-size:1.75rem;font-weight:800;color:{color};line-height:1;">{value}</div>
            <div style="font-size:0.75rem;color:#64748b;font-weight:600;margin-top:0.3rem;text-transform:uppercase;letter-spacing:0.06em;">{label}</div>
        </div>"""

    return f"""
    {mock_note}
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
        {cards}
    </div>"""


def _diagnoses_html(conditions: list[str]) -> str:
    if not conditions:
        return '<p style="color:#94a3b8;font-size:0.875rem;">No diagnoses recorded yet.</p>'
    items = "".join(
        f'<div style="display:flex;align-items:center;gap:0.6rem;padding:0.55rem 0;'
        f'border-bottom:1px solid #f1f5f9;">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:#0891b2;flex-shrink:0;"></span>'
        f'<span style="font-size:0.875rem;color:#0f172a;font-weight:500;">{c}</span>'
        f'</div>'
        for c in conditions
    )
    return f'<div style="padding-top:0.25rem;">{items}</div>'


def _drug_history_html(history: list[dict]) -> str:
    if not history:
        return '<p style="color:#94a3b8;font-size:0.875rem;">No drug records yet.</p>'
    rows = ""
    for rec in history:
        rows += f"""
        <div style="display:grid;grid-template-columns:56px 1fr 1fr;gap:0.5rem;
                    align-items:center;padding:0.6rem 0;border-bottom:1px solid #f1f5f9;">
            <span style="font-size:0.72rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">{rec['date']}</span>
            <span style="font-size:0.84rem;color:#475569;font-weight:500;">{rec['condition']}</span>
            <span style="font-size:0.84rem;color:#059669;font-weight:600;">{rec.get('drugs') or rec.get('drug','—')}</span>
        </div>"""
    return f"""
    <div style="padding-top:0.25rem;">
        <div style="display:grid;grid-template-columns:56px 1fr 1fr;gap:0.5rem;
                    padding-bottom:0.5rem;border-bottom:2px solid #e2e8f0;margin-bottom:0.25rem;">
            <span style="font-size:0.68rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">Date</span>
            <span style="font-size:0.68rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">Condition</span>
            <span style="font-size:0.68rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">Drug(s)</span>
        </div>
        {rows}
    </div>"""


def _insights_html(insights: list[dict]) -> str:
    cards = ""
    for ins in insights:
        cards += f"""
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:11px;
                    padding:1rem 1.25rem;border-left:4px solid {ins['color']};
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);margin-bottom:0.75rem;">
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;">
                <span style="font-size:0.9rem;font-weight:700;color:#0f172a;">{ins['title']}</span>
            </div>
            <p style="font-size:0.83rem;color:#475569;line-height:1.65;margin:0;">{ins['message']}</p>
        </div>"""
    return cards


# ══════════════════════════════════════════════════════════════════════════════
# MAIN REFRESH FUNCTION  (called by nav_dashboard.click)
# ══════════════════════════════════════════════════════════════════════════════

def refresh_dashboard(user_id: str):
    """
    Called when the user navigates to the Dashboard page.
    Returns: (summary_html, diagnoses_html, drug_history_html,
               condition_chart_img, drug_chart_img, insights_html)
    """
    if not user_id:
        empty = '<p style="color:#94a3b8;font-size:0.875rem;">Please log in to view your dashboard.</p>'
        return empty, empty, empty, None, None, empty

    summary    = get_health_summary(user_id)
    conditions = get_recent_diagnoses(user_id)
    history    = get_drug_history(user_id)
    insights   = generate_health_insights(user_id)
    cond_chart = create_condition_chart(user_id)
    drug_chart = create_drug_chart(user_id)

    return (
        _summary_html(summary),
        _diagnoses_html(conditions),
        _drug_history_html(history),
        cond_chart,
        drug_chart,
        _insights_html(insights),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRADIO UI  — returns the inner components so gradio_app.py can wire events
# ══════════════════════════════════════════════════════════════════════════════

def build_dashboard_ui():
    """
    Build and return all Gradio components for the dashboard page.
    Must be called INSIDE an existing gr.Blocks() context.

    Returns dict of output components needed for event wiring.
    """
    gr.HTML("""
    <div class="pg-head">
        <div style="display:flex;align-items:center;gap:0.75rem;">
            <div style="width:32px;height:32px;
                        background:linear-gradient(135deg,#7c3aed,#a78bfa);
                        border-radius:8px;display:flex;align-items:center;
                        justify-content:center;flex-shrink:0;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                     stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6"  y1="20" x2="6"  y2="14"/>
                </svg>
            </div>
            <div>
                <div class="pg-head-title">Health Dashboard</div>
                <div class="pg-head-sub">Your personal health analytics and drug insights</div>
            </div>
        </div>
    </div>""")

    with gr.Column(elem_classes="pg-body"):

        # ── Row 1: Health Summary ──────────────────────────────────────────
        with gr.Column(elem_classes="card"):
            gr.HTML("""<div class="card-head">
                <div class="card-head-icon">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                         stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                    </svg>
                </div>
                Health Overview
            </div>""")
            summary_out = gr.HTML("")

        # ── Row 2: Recent Diagnoses + Drug History ─────────────────────────
        with gr.Row():
            with gr.Column(scale=1, elem_classes="card"):
                gr.HTML("""<div class="card-head">
                    <div class="card-head-icon">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                             stroke="#0891b2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="8" x2="12" y2="12"/>
                            <line x1="12" y1="16" x2="12.01" y2="16"/>
                        </svg>
                    </div>
                    Recent Diagnoses
                </div>""")
                diagnoses_out = gr.HTML("")

            with gr.Column(scale=1, elem_classes="card"):
                gr.HTML("""<div class="card-head">
                    <div class="card-head-icon">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                             stroke="#059669" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/>
                        </svg>
                    </div>
                    Drug Recommendation History
                </div>""")
                drug_history_out = gr.HTML("")

        # ── Row 3: Charts ──────────────────────────────────────────────────
        with gr.Row():
            with gr.Column(scale=1, elem_classes="card"):
                gr.HTML('<div class="card-head">Most Detected Conditions</div>')
                condition_chart_out = gr.Image(
                    label="", show_label=False,
                    show_download_button=False, container=False
                )
            with gr.Column(scale=1, elem_classes="card"):
                gr.HTML('<div class="card-head">Drug Frequency</div>')
                drug_chart_out = gr.Image(
                    label="", show_label=False,
                    show_download_button=False, container=False
                )

        # ── Row 4: AI Health Insights ──────────────────────────────────────
        with gr.Column(elem_classes="card"):
            gr.HTML("""<div class="card-head">
                <div class="card-head-icon">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                         stroke="#d97706" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                </div>
                AI Health Insights
            </div>""")
            insights_out = gr.HTML("")

    return {
        "summary":         summary_out,
        "diagnoses":       diagnoses_out,
        "drug_history":    drug_history_out,
        "condition_chart": condition_chart_out,
        "drug_chart":      drug_chart_out,
        "insights":        insights_out,
    }