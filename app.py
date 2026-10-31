"""Streamlit dashboard for the Intelligent Memory Management System."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from algorithms import ALGORITHMS, DEFAULT_WEIGHTS
from algorithms.predictive import predictive
from visualization.graphs import comparison_figures


SAMPLE_STRINGS = {
    "Textbook example (3 frames, mixed locality)": "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1",
    "Repeating loop": "1 2 3 4 1 2 3 4 1 2 3 4",
    "Working-set burst": "1 2 3 1 2 3 4 5 4 5 1 2 3",
    "Short custom starter": "1 2 3 2 4 1 5 2",
}


def parse_reference_string(text: str) -> tuple[list, str | None]:
    """Split a typed reference string into page tokens (integers when possible)."""
    if text is None or not str(text).strip():
        return [], "Reference string is empty. Enter page numbers separated by space or comma."

    raw_tokens = str(text).replace(",", " ").replace(";", " ").split()
    pages = []
    for token in raw_tokens:
        try:
            pages.append(int(token))
        except ValueError:
            return [], f"'{token}' is not a valid page number. Use integers such as 7 0 1 2."
    return pages, None


def run_selected(algorithms: list[str], pages: list, frames: int, weights: dict) -> dict:
    results = {}
    for name in algorithms:
        if name == "Predictive":
            results[name] = predictive(pages, frames, weights)
        else:
            results[name] = ALGORITHMS[name](pages, frames)
    return results


def steps_to_dataframe(result: dict) -> pd.DataFrame:
    rows = []
    for step in result["steps"]:
        row = {
            "Step": step["step"],
            "Page": str(step["page"]),
            "Memory Frames": " | ".join(str(slot) for slot in step["frames"]),
            "Result": step["status"],
            "Replaced": str(step["replaced"]),
        }
        if "prediction" in step:
            row["Predictive Decision"] = str(step["prediction"])
        rows.append(row)
    return pd.DataFrame(rows)


def memory_timeline_html(result: dict) -> str:
    cards = []
    for step in result["steps"]:
        status_class = "is-hit" if step["status"] == "Hit" else "is-fault"
        frames = "".join(
            f'<span class="frame-slot{" is-empty" if frame == "-" else ""}">{frame}</span>'
            for frame in step["frames"]
        )
        cards.append(
            f"""
            <div class="memory-step {status_class}">
              <div class="memory-step-heading">
                <span>STEP {step["step"]:02d}</span>
                <span class="memory-step-status">{step["status"].upper()}</span>
              </div>
              <div class="memory-page">PAGE <strong>{step["page"]}</strong></div>
              <div class="memory-frames">{frames}</div>
              <div class="memory-replaced">REPLACED <strong>{step["replaced"]}</strong></div>
            </div>
            """
        )
    return f'<div class="memory-timeline">{"".join(cards)}</div>'


def metric_table(results: dict) -> pd.DataFrame:
    rows = []
    for name, result in results.items():
        if result.get("error"):
            rows.append(
                {
                    "Algorithm": name,
                    "Page Faults": "-",
                    "Page Hits": "-",
                    "Hit Ratio": result["error"],
                    "Fault Ratio": "-",
                }
            )
            continue
        rows.append(
            {
                "Algorithm": name,
                "Page Faults": result["page_faults"],
                "Page Hits": result["page_hits"],
                "Hit Ratio": f"{result['hit_ratio'] * 100:.2f}%",
                "Fault Ratio": f"{result['fault_ratio'] * 100:.2f}%",
            }
        )
    return pd.DataFrame(rows)


def style_comparison_figure(figure) -> None:
    figure.patch.set_facecolor("#1A211E")
    for axis in figure.axes:
        axis.set_facecolor("#1A211E")
        axis.set_axisbelow(True)
        axis.tick_params(colors="#9CA3AF")
        axis.title.set_color("#F3F4F6")
        axis.xaxis.label.set_color("#9CA3AF")
        axis.yaxis.label.set_color("#9CA3AF")
        axis.grid(axis="y", color="#29332E", alpha=0.8, linewidth=0.7)
        for spine in axis.spines.values():
            spine.set_color("#29332E")
        for label in axis.texts:
            label.set_color("#F3F4F6")
        legend = axis.get_legend()
        if legend:
            legend.get_frame().set_facecolor("#1A211E")
            legend.get_frame().set_edgecolor("#29332E")
            for label in legend.get_texts():
                label.set_color("#9CA3AF")


st.set_page_config(page_title="Intelligent Memory Management", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --text: #edf4ff;
        --muted: #9eacc5;
        --line: rgba(145, 180, 236, 0.16);
        --glass: rgba(15, 25, 44, 0.74);
        --cyan: #6de8ee;
        --purple: #b49bff;
    }
    html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .stApp {
        color: var(--text);
        background-color: #070b16;
        background:
            radial-gradient(ellipse at 12% 0%, rgba(32, 91, 171, 0.22), transparent 38%),
            radial-gradient(ellipse at 88% 12%, rgba(109, 67, 181, 0.16), transparent 34%),
            linear-gradient(145deg, #070b16 0%, #0a1020 52%, #080b17 100%);
    }
    [data-testid="stHeader"] { background: rgba(7, 11, 22, 0.68); }
    [data-testid="stMain"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { max-width: 1480px; padding-top: 1.8rem; }
    [data-testid="stMainBlockContainer"] > div { gap: 1.15rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(14, 23, 41, 0.91), rgba(9, 15, 29, 0.94));
        border-right: 1px solid rgba(126, 166, 232, 0.2);
        box-shadow: 8px 0 36px rgba(0, 0, 0, 0.18);
        backdrop-filter: blur(18px);
    }
    [data-testid="stSidebar"] > div:first-child { background: transparent; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label { color: #dce8fc; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.8rem; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { letter-spacing: 0.02em !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong { color: #b9d8ff; }
    h1, h2, h3 { color: var(--text) !important; letter-spacing: 0 !important; }
    p, li, label, [data-testid="stCaptionContainer"] { color: #c1cde0; }
    h2, h3 { font-weight: 680 !important; }
    [data-testid="stSubheader"] { margin-top: 0.35rem; }
    [data-testid="stMarkdownContainer"] a { color: #8ed8ff; }
    .hero {
        margin: 0.3rem 0 1.5rem;
        padding: clamp(1.5rem, 4vw, 2.8rem);
        border: 1px solid rgba(135, 174, 245, 0.22);
        border-radius: 22px;
        background: linear-gradient(118deg, rgba(17, 35, 65, 0.76), rgba(32, 24, 58, 0.67));
        box-shadow: 0 22px 64px rgba(0, 0, 0, 0.32), 0 0 42px rgba(72, 123, 231, 0.08), inset 0 1px rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    .hero:after { content: ""; position: absolute; width: 260px; height: 260px; right: -85px; top: -145px; border-radius: 50%; background: rgba(113, 91, 255, 0.18); filter: blur(10px); pointer-events: none; }
    .hero-kicker, .hero-badge { color: #9fcaff; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; }
    .hero h1 { margin: 0.65rem 0 0.35rem; font-size: clamp(1.8rem, 4vw, 2.65rem); line-height: 1.12; }
    .hero-subtitle { margin: 0 0 1.2rem; color: #c1d5f4; font-size: 1.02rem; }
    .hero-badge {
        display: inline-block;
        padding: 0.42rem 0.72rem;
        border: 1px solid rgba(112, 174, 255, 0.24);
        border-radius: 999px;
        background: rgba(71, 125, 202, 0.12);
        color: #bedbff;
        letter-spacing: 0.07em;
    }
    .section-eyebrow {
        margin-bottom: 0.75rem;
        color: #91b9e8;
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.13em;
    }
    .algorithm-card, .analytics-panel {
        height: 100%;
        padding: 1rem 1.05rem;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(25, 37, 61, 0.74), rgba(13, 21, 38, 0.8));
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.23), 0 0 24px var(--card-glow, rgba(73, 139, 255, 0.06)), inset 0 1px rgba(255,255,255,0.035);
        backdrop-filter: blur(14px);
    }
    .algorithm-card { border-top: 2px solid var(--card-accent); }
    .algorithm-card { transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease; }
    .algorithm-card:hover { transform: translateY(-3px); box-shadow: 0 18px 38px rgba(0,0,0,0.3), 0 0 30px var(--card-glow), inset 0 1px rgba(255,255,255,0.06); }
    .algorithm-name { color: var(--card-accent); font-size: 1.08rem; font-weight: 750; margin-bottom: 0.9rem; letter-spacing: 0.025em; }
    .algorithm-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem 0.55rem; }
    .algorithm-metric-label { display: block; color: var(--muted); font-size: 0.72rem; }
    .algorithm-metric-value { display: block; margin-top: 0.15rem; color: var(--text); font-size: 1.12rem; font-weight: 650; }
    .analytics-heading { color: #b49bff; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(145, 180, 236, 0.18) !important;
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(25, 37, 61, 0.68), rgba(13, 21, 38, 0.74));
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18), inset 0 1px rgba(255,255,255,0.025);
        backdrop-filter: blur(16px);
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(125, 183, 255, 0.3) !important; }
    [data-testid="stMetric"] {
        padding: 0.9rem 1rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: rgba(18, 29, 50, 0.68);
        box-shadow: inset 0 1px rgba(255,255,255,0.035);
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    [data-testid="stMetricValue"] { color: var(--text) !important; }
    [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input {
        color: var(--text);
        border: 1px solid rgba(135, 174, 245, 0.22);
        border-radius: 10px;
        background: rgba(7, 13, 25, 0.72);
    }
    [data-testid="stTextArea"] textarea:focus, [data-testid="stNumberInput"] input:focus {
        border-color: rgba(109, 200, 255, 0.72);
        box-shadow: 0 0 0 1px rgba(109, 200, 255, 0.28), 0 0 18px rgba(68, 160, 255, 0.12);
    }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { box-shadow: 0 0 12px rgba(88, 170, 255, 0.48); }
    [data-testid="stSlider"] [data-testid="stTickBar"] { color: #8fa4c4; }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        border-color: rgba(135, 174, 245, 0.22);
        border-radius: 10px;
        background: rgba(7, 13, 25, 0.72);
    }
    [data-testid="stButton"] button {
        border: 1px solid rgba(101, 173, 255, 0.42);
        border-radius: 10px;
        background: linear-gradient(105deg, #1766bc, #5142a0);
        color: white;
        box-shadow: 0 6px 22px rgba(46, 115, 215, 0.22);
        font-weight: 700;
        transition: filter 140ms ease, box-shadow 140ms ease;
    }
    [data-testid="stButton"] button:hover { border-color: #9ac9ff; color: white; filter: brightness(1.1); box-shadow: 0 8px 26px rgba(46, 115, 215, 0.32); }
    [data-testid="stButton"] button:active { transform: translateY(1px); }
    [data-testid="stTabs"] button[role="tab"] { color: #9eacc5; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: #9bd0ff; }
    [data-testid="stTabs"] button[aria-selected="true"] p { color: #9bd0ff; }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: rgba(13, 21, 38, 0.78);
    }
    [data-testid="stDataFrame"] { box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18); }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 0.35rem; border-bottom-color: var(--line); }
    [data-testid="stTabs"] button[role="tab"] { border-radius: 9px 9px 0 0; padding: 0.55rem 0.8rem; }
    [data-testid="stAlert"] { border-radius: 13px; background: rgba(19, 31, 52, 0.78); }
    [data-testid="stPlotlyChart"], [data-testid="stImage"] {
        border: 1px solid var(--line);
        border-radius: 13px;
        background: rgba(13, 21, 38, 0.55);
        padding: 0.45rem;
    }
    [data-testid="stCode"] {
        border: 1px solid rgba(119, 164, 230, 0.16);
        border-radius: 11px;
        background: rgba(6, 12, 24, 0.68);
    }
    .memory-timeline {
        display: flex;
        gap: 0.7rem;
        margin: 0.6rem 0 1rem;
        padding: 0.3rem 0.15rem 0.8rem;
        overflow-x: auto;
        scrollbar-color: #405b82 rgba(10, 17, 30, 0.7);
        scrollbar-width: thin;
    }
    .memory-step {
        flex: 0 0 auto;
        min-width: 150px;
        padding: 0.75rem;
        border: 1px solid rgba(130, 165, 211, 0.16);
        border-radius: 14px;
        background: linear-gradient(150deg, rgba(21, 32, 52, 0.86), rgba(10, 17, 31, 0.9));
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22), inset 0 1px rgba(255,255,255,0.035);
    }
    .memory-step.is-hit { border-top: 2px solid rgba(73, 226, 160, 0.82); box-shadow: 0 8px 24px rgba(25, 185, 122, 0.08), inset 0 1px rgba(255,255,255,0.035); }
    .memory-step.is-fault { border-top: 2px solid rgba(255, 104, 145, 0.84); box-shadow: 0 8px 24px rgba(223, 63, 107, 0.08), inset 0 1px rgba(255,255,255,0.035); }
    .memory-step-heading { display: flex; justify-content: space-between; gap: 0.5rem; color: #899dbb; font-size: 0.62rem; font-weight: 750; letter-spacing: 0.08em; }
    .memory-step-status { color: #69e5a5; }
    .is-fault .memory-step-status { color: #ff91a9; }
    .memory-page { margin: 0.55rem 0 0.65rem; color: #8fa4c4; font-size: 0.67rem; letter-spacing: 0.08em; }
    .memory-page strong { margin-left: 0.2rem; color: #e8f2ff; font-size: 0.95rem; letter-spacing: 0; }
    .memory-frames { display: flex; flex-wrap: wrap; gap: 0.32rem; }
    .frame-slot {
        display: inline-flex;
        min-width: 32px;
        height: 31px;
        align-items: center;
        justify-content: center;
        padding: 0 0.42rem;
        border: 1px solid rgba(98, 208, 174, 0.33);
        border-radius: 8px;
        background: linear-gradient(145deg, rgba(27, 105, 85, 0.42), rgba(17, 55, 55, 0.58));
        box-shadow: inset 0 1px rgba(255,255,255,0.06), 0 0 10px rgba(42, 221, 167, 0.08);
        color: #a7f5d2;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .is-fault .frame-slot:not(.is-empty) {
        border-color: rgba(255, 119, 153, 0.4);
        background: linear-gradient(145deg, rgba(133, 43, 74, 0.42), rgba(68, 28, 52, 0.6));
        box-shadow: inset 0 1px rgba(255,255,255,0.06), 0 0 10px rgba(255, 85, 134, 0.1);
        color: #ffc0d0;
    }
    .frame-slot.is-empty {
        border-color: rgba(126, 145, 173, 0.15);
        background: rgba(39, 49, 66, 0.42);
        box-shadow: inset 0 1px rgba(255,255,255,0.025);
        color: #74839b;
    }
    .prediction-tags { display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0.7rem 0 1rem; }
    .prediction-tags span {
        padding: 0.35rem 0.58rem;
        border: 1px solid rgba(165, 139, 255, 0.22);
        border-radius: 999px;
        background: linear-gradient(100deg, rgba(99, 67, 167, 0.18), rgba(34, 111, 139, 0.14));
        box-shadow: 0 0 16px rgba(130, 95, 220, 0.07);
        color: #d3c7ff;
        font-size: 0.68rem;
        font-weight: 650;
    }
    code { color: #a9d8ff !important; }
    @media (max-width: 700px) {
        .hero { border-radius: 14px; }
        .algorithm-card { margin-bottom: 0.65rem; }
    }
    :root {
        --text: #F3F4F6;
        --muted: #9CA3AF;
        --line: #29332E;
        --glass: rgba(26, 33, 30, 0.82);
        --cyan: #10B981;
        --purple: #6EE7B7;
    }
    .stApp {
        color: var(--text);
        background: #101312;
    }
    [data-testid="stHeader"] { background: rgba(16, 19, 18, 0.92); }
    [data-testid="stMain"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { max-width: 1500px; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #171D1A 0%, #131815 100%);
        border-right: 1px solid #29332E;
        box-shadow: 8px 0 30px rgba(0, 0, 0, 0.18);
    }
    [data-testid="stSidebar"] > div:first-child { background: transparent; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label { color: #D1D5DB; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #F3F4F6 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong { color: #6EE7B7; }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 0.2rem 0 1.45rem;
        padding: 0.75rem;
        border: 1px solid #29332E;
        border-radius: 13px;
        background: rgba(26, 33, 30, 0.82);
    }
    .sidebar-mark {
        display: inline-flex;
        width: 2.2rem;
        height: 2.2rem;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        background: rgba(16, 185, 129, 0.14);
        color: #6EE7B7;
        font-weight: 750;
    }
    .sidebar-brand strong, .sidebar-brand small { display: block; }
    .sidebar-brand strong { color: #F3F4F6; font-size: 0.82rem; }
    .sidebar-brand small {
        margin-top: 0.16rem;
        color: #9CA3AF;
        font-size: 0.58rem;
        letter-spacing: 0.09em;
    }
    .sidebar-nav-label, .sidebar-section-label {
        margin: 0.8rem 0 0.45rem;
        color: #6EE7B7;
        font-size: 0.65rem;
        font-weight: 750;
        letter-spacing: 0.12em;
    }
    .sidebar-nav { display: grid; gap: 0.2rem; margin-bottom: 1.15rem; }
    .sidebar-nav a {
        display: block;
        padding: 0.52rem 0.65rem;
        border-left: 2px solid transparent;
        border-radius: 0 8px 8px 0;
        color: #9CA3AF !important;
        font-size: 0.84rem;
        text-decoration: none !important;
        transition: color 140ms ease, background 140ms ease, border-color 140ms ease;
    }
    .sidebar-nav a:hover {
        border-left-color: #10B981;
        background: rgba(16, 185, 129, 0.08);
        color: #F3F4F6 !important;
    }
    h1, h2, h3 { color: #F3F4F6 !important; letter-spacing: -0.02em !important; }
    p, li, label, [data-testid="stCaptionContainer"] { color: #9CA3AF; }
    h2, h3 { font-weight: 650 !important; }
    [data-testid="stMarkdownContainer"] a { color: #34D399; }
    .hero {
        margin: 0.3rem 0 1.5rem;
        padding: clamp(1.5rem, 4vw, 2.6rem);
        border: 1px solid #29332E;
        border-radius: 20px;
        background: linear-gradient(120deg, rgba(26, 33, 30, 0.96), rgba(21, 29, 25, 0.9));
        box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22), inset 0 1px rgba(255, 255, 255, 0.035);
    }
    .hero:after { display: none; }
    .hero-kicker, .hero-badge { color: #6EE7B7; }
    .hero h1 { color: #F3F4F6 !important; }
    .hero-subtitle { color: #9CA3AF; }
    .hero-badge {
        border-color: rgba(16, 185, 129, 0.24);
        background: rgba(16, 185, 129, 0.08);
        color: #A7F3D0;
    }
    .section-eyebrow { color: #6EE7B7; }
    .algorithm-card, .analytics-panel {
        border-color: #29332E;
        background: linear-gradient(145deg, rgba(28, 37, 32, 0.9), rgba(23, 30, 26, 0.94));
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18), inset 0 1px rgba(255, 255, 255, 0.025);
        backdrop-filter: blur(12px);
    }
    .algorithm-card:hover {
        border-color: rgba(16, 185, 129, 0.48);
        box-shadow: 0 16px 34px rgba(0, 0, 0, 0.24), inset 0 1px rgba(255, 255, 255, 0.045);
    }
    .algorithm-name { color: #10B981; }
    .algorithm-description { margin: -0.65rem 0 0.95rem; color: #9CA3AF; font-size: 0.76rem; }
    .algorithm-metric-label { color: #9CA3AF; }
    .analytics-heading { color: #6EE7B7; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #29332E !important;
        background: rgba(26, 33, 30, 0.76);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16), inset 0 1px rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(14px);
        transition: border-color 160ms ease, box-shadow 160ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(16, 185, 129, 0.42) !important; }
    [data-testid="stMetric"] {
        border-color: #29332E;
        border-radius: 13px;
        background: rgba(26, 33, 30, 0.88);
        box-shadow: inset 0 1px rgba(255, 255, 255, 0.025);
    }
    [data-testid="stMetricLabel"] { color: #9CA3AF !important; }
    [data-testid="stMetricValue"] { color: #F3F4F6 !important; }
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        color: #F3F4F6;
        border-color: #29332E;
        background: #101312;
    }
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: #10B981;
        box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.2);
    }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { box-shadow: none; }
    [data-testid="stSlider"] [data-testid="stTickBar"] { color: #9CA3AF; }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        border-color: #29332E;
        border-radius: 10px;
        background: #101312;
    }
    [data-testid="stButton"] button {
        border: 1px solid #10B981;
        border-radius: 10px;
        background: #10B981;
        color: #062D20;
        box-shadow: none;
        font-weight: 700;
        transition: background 150ms ease, border-color 150ms ease, transform 150ms ease;
    }
    [data-testid="stButton"] button:hover {
        border-color: #34D399;
        background: #34D399;
        color: #062D20;
        filter: none;
        box-shadow: 0 5px 16px rgba(16, 185, 129, 0.16);
    }
    [data-testid="stButton"] button:active { transform: translateY(1px); }
    [data-testid="stTabs"] button[role="tab"] { color: #9CA3AF; }
    [data-testid="stTabs"] button[aria-selected="true"],
    [data-testid="stTabs"] button[aria-selected="true"] p { color: #34D399; }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid #29332E;
        border-radius: 12px;
        background: rgba(26, 33, 30, 0.72);
    }
    [data-testid="stDataFrame"] { box-shadow: 0 10px 26px rgba(0, 0, 0, 0.16); }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom-color: #29332E; }
    [data-testid="stAlert"] { border-radius: 13px; background: rgba(26, 33, 30, 0.92); }
    [data-testid="stPlotlyChart"], [data-testid="stImage"] {
        border: 1px solid #29332E;
        border-radius: 13px;
        background: rgba(26, 33, 30, 0.55);
        padding: 0.45rem;
    }
    [data-testid="stCode"] {
        border: 1px solid #29332E;
        border-radius: 11px;
        background: #151A18;
    }
    .memory-timeline {
        scrollbar-color: #52635A #151A18;
        scrollbar-width: thin;
    }
    .memory-step {
        border-color: #29332E;
        background: linear-gradient(150deg, rgba(28, 37, 32, 0.96), rgba(21, 27, 24, 0.98));
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18), inset 0 1px rgba(255, 255, 255, 0.025);
    }
    .memory-step.is-hit { border-top-color: #10B981; box-shadow: 0 7px 18px rgba(16, 185, 129, 0.07); }
    .memory-step.is-fault { border-top-color: #F87171; box-shadow: 0 7px 18px rgba(248, 113, 113, 0.06); }
    .memory-step-heading, .memory-page { color: #9CA3AF; }
    .memory-step-status { color: #34D399; }
    .is-fault .memory-step-status { color: #F87171; }
    .memory-page strong { color: #F3F4F6; }
    .memory-replaced {
        margin-top: 0.65rem;
        color: #9CA3AF;
        font-size: 0.6rem;
        letter-spacing: 0.06em;
    }
    .memory-replaced strong { margin-left: 0.2rem; color: #F3F4F6; font-size: 0.7rem; }
    .frame-slot {
        border-color: rgba(16, 185, 129, 0.32);
        background: rgba(16, 185, 129, 0.12);
        box-shadow: none;
        color: #A7F3D0;
    }
    .is-fault .frame-slot:not(.is-empty) {
        border-color: rgba(248, 113, 113, 0.36);
        background: rgba(248, 113, 113, 0.1);
        box-shadow: none;
        color: #FECACA;
    }
    .frame-slot.is-empty {
        border-color: #29332E;
        background: rgba(16, 19, 18, 0.68);
        box-shadow: none;
        color: #6B7280;
    }
    .prediction-tags span {
        border-color: rgba(16, 185, 129, 0.24);
        background: rgba(16, 185, 129, 0.08);
        box-shadow: none;
        color: #A7F3D0;
    }
    code { color: #6EE7B7 !important; }
    </style>
    <section class="hero">
      <div class="hero-kicker">OPERATING SYSTEMS / MEMORY</div>
      <h1>Intelligent memory<br>management system</h1>
      <p class="hero-subtitle">Page replacement simulator</p>
      <span class="hero-badge">FIFO &bull; LRU &bull; OPTIMAL &bull; PREDICTIVE</span>
    </section>
    """,
    unsafe_allow_html=True,
)
st.write(
    "This dashboard simulates how an operating system chooses which page to remove "
    "from limited main memory. It compares FIFO, LRU, and Optimal with a rule-based "
    "predictive algorithm that uses frequency, recency, and page-to-page transition history."
)

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><span class="sidebar-mark">M</span>'
        '<span><strong>Memory management</strong><small>PAGE REPLACEMENT LAB</small></span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-nav-label">NAVIGATION</div>'
        '<nav class="sidebar-nav">'
        '<a href="#simulation-configuration">Input configuration</a>'
        '<a href="#dashboard-overview">Dashboard</a>'
        '<a href="#performance-comparison">Algorithm comparison</a>'
        '<a href="#step-by-step-simulation">Simulation trace</a>'
        '<a href="#project-guide">Project guide</a>'
        '</nav>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section-label">SIMULATION SETUP</div>', unsafe_allow_html=True)
    st.header("Input settings")
    sample_name = st.selectbox("Sample reference string", list(SAMPLE_STRINGS.keys()))
    reference_text = st.text_area(
        "Reference string",
        value=SAMPLE_STRINGS[sample_name],
        help="Integers separated by spaces or commas. Example: 7 0 1 2 0 3",
    )
    frame_count = st.number_input("Number of memory frames", min_value=0, max_value=20, value=3, step=1)
    selected = st.multiselect(
        "Algorithms",
        options=list(ALGORITHMS.keys()),
        default=list(ALGORITHMS.keys()),
    )

    st.subheader("Predictive weights")
    st.caption("Score = α·Frequency + β·Recency + γ·Transition probability")
    alpha = st.slider("α  Frequency", 0.0, 1.0, DEFAULT_WEIGHTS["alpha"], 0.05)
    beta = st.slider("β  Recency", 0.0, 1.0, DEFAULT_WEIGHTS["beta"], 0.05)
    gamma = st.slider("γ  Transition", 0.0, 1.0, DEFAULT_WEIGHTS["gamma"], 0.05)
    run = st.button("Run simulation", type="primary", width="stretch")

pages, parse_error = parse_reference_string(reference_text)
weights = {"alpha": alpha, "beta": beta, "gamma": gamma}

st.subheader("Simulation configuration")
with st.container(border=True):
    st.markdown('<div class="section-eyebrow">REFERENCE STRING / ACTIVE CONFIGURATION</div>', unsafe_allow_html=True)
    config_columns = st.columns(2)
    config_columns[0].metric("Number of frames", frame_count)
    config_columns[1].metric("Total pages", len(pages) if not parse_error else 0)
    st.caption(f"{len(selected)} algorithms selected")
    st.code(reference_text.strip() or "(empty)", language="text")

if run:
    if parse_error:
        st.error(parse_error)
    elif not selected:
        st.error("Select at least one algorithm.")
    else:
        results = run_selected(selected, pages, int(frame_count), weights)
        first_error = next((item["error"] for item in results.values() if item.get("error")), None)
        if first_error:
            st.error(first_error)
        else:
            st.success("Simulation complete.")

            primary_name, primary_result = next(iter(results.items()))
            st.header("Dashboard overview")
            st.caption(f"Summary metrics for {primary_name}; compare all selected algorithms below.")
            overview_row_one = st.columns(2)
            overview_row_one[0].metric("Total pages", len(pages))
            overview_row_one[1].metric("Number of frames", int(frame_count))
            overview_row_two = st.columns(2)
            overview_row_two[0].metric("Page hits", primary_result["page_hits"])
            overview_row_two[1].metric("Page faults", primary_result["page_faults"])
            overview_row_three = st.columns(2)
            overview_row_three[0].metric("Hit ratio", f"{primary_result['hit_ratio'] * 100:.2f}%")
            overview_row_three[1].metric("Fault ratio", f"{primary_result['fault_ratio'] * 100:.2f}%")

            st.header("Performance comparison")
            algorithm_styles = {
                "FIFO": ("#10B981", "rgba(16, 185, 129, 0.08)"),
                "LRU": ("#34D399", "rgba(16, 185, 129, 0.08)"),
                "Optimal": ("#6EE7B7", "rgba(16, 185, 129, 0.08)"),
                "Predictive": ("#059669", "rgba(16, 185, 129, 0.08)"),
            }
            algorithm_descriptions = {
                "FIFO": "First In, First Out",
                "LRU": "Least Recently Used",
                "Optimal": "Theoretical benchmark",
                "Predictive": "History-based replacement",
            }
            result_items = list(results.items())
            for start in range(0, len(result_items), 2):
                algorithm_columns = st.columns(min(2, len(result_items) - start))
                for column, (name, result) in zip(algorithm_columns, result_items[start : start + 2]):
                    accent, glow = algorithm_styles.get(name, ("#10B981", "rgba(16, 185, 129, 0.08)"))
                    column.markdown(
                        f"""
                        <div class="algorithm-card" style="--card-accent:{accent};--card-glow:{glow};">
                          <div class="algorithm-name">{name}</div>
                          <div class="algorithm-description">{algorithm_descriptions[name]}</div>
                          <div class="algorithm-metrics">
                            <div><span class="algorithm-metric-label">Page Faults</span><span class="algorithm-metric-value">{result['page_faults']}</span></div>
                            <div><span class="algorithm-metric-label">Page Hits</span><span class="algorithm-metric-value">{result['page_hits']}</span></div>
                            <div><span class="algorithm-metric-label">Hit Ratio</span><span class="algorithm-metric-value">{result['hit_ratio'] * 100:.2f}%</span></div>
                            <div><span class="algorithm-metric-label">Fault Ratio</span><span class="algorithm-metric-value">{result['fault_ratio'] * 100:.2f}%</span></div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.dataframe(metric_table(results), hide_index=True, width="stretch")

            valid_results = [item for item in results.values() if not item.get("error")]
            if len(valid_results) >= 1:
                fault_fig, hit_fault_fig, utilization_fig = comparison_figures(valid_results)
                style_comparison_figure(fault_fig)
                style_comparison_figure(hit_fault_fig)
                style_comparison_figure(utilization_fig)
                fault_tab, hit_fault_tab, utilization_tab = st.tabs(
                    ["Page faults", "Page hits vs. faults", "Frame utilization"]
                )
                with fault_tab:
                    st.pyplot(fault_fig, width="stretch")
                with hit_fault_tab:
                    st.pyplot(hit_fault_fig, width="stretch")
                with utilization_tab:
                    st.pyplot(utilization_fig, width="stretch")
                plt.close(fault_fig)
                plt.close(hit_fault_fig)
                plt.close(utilization_fig)

            if "Optimal" in results and not results["Optimal"].get("error"):
                st.info(
                    "Optimal is a theoretical benchmark. It looks at future references, "
                    "so a practical algorithm such as Predictive, LRU, or FIFO should not "
                    "be expected to beat it on every (or even most) inputs."
                )

            st.header("Step-by-step simulation")
            tabs = st.tabs(list(results.keys()))
            for tab, name in zip(tabs, results.keys()):
                with tab:
                    result = results[name]
                    m1, m2 = st.columns(2)
                    m1.metric("Page faults", result["page_faults"])
                    m2.metric("Page hits", result["page_hits"])
                    m3, m4 = st.columns(2)
                    m3.metric("Hit ratio", f"{result['hit_ratio'] * 100:.2f}%")
                    m4.metric("Fault ratio", f"{result['fault_ratio'] * 100:.2f}%")
                    st.markdown('<div class="section-eyebrow">MEMORY FRAME TIMELINE / HIT &amp; FAULT TRACE</div>', unsafe_allow_html=True)
                    st.html(memory_timeline_html(result))
                    step_table = steps_to_dataframe(result).style.apply(
                        lambda cells: [
                            "color: #34D399; background-color: rgba(16, 185, 129, 0.1); font-weight: 700"
                            if status == "HIT"
                            else "color: #F87171; background-color: rgba(248, 113, 113, 0.1); font-weight: 700"
                            for status in cells
                        ],
                        subset=["Result"],
                    ).set_properties(
                        subset=["Memory Frames"],
                        **{
                            "background-color": "rgba(16, 185, 129, 0.06)",
                            "color": "#D1D5DB",
                            "font-weight": "600",
                        },
                    )
                    st.dataframe(step_table, hide_index=True, width="stretch")

            if "Predictive" in results and not results["Predictive"].get("error"):
                st.header("Predictive decision explanation")
                used = results["Predictive"].get("weights", {})
                with st.container(border=True):
                    st.markdown(
                        '<div class="analytics-heading">PREDICTIVE ANALYTICS / DECISION MODEL</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="prediction-tags"><span>Prediction Score</span><span>Frequency</span>'
                        '<span>Recency</span><span>Transition Probability</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.write(
                        "On a fault, every page already in memory gets a prediction score. "
                        "The page with the **lowest** score is replaced, because it is treated "
                        "as the least likely to be needed soon."
                    )
                    st.latex(r"S(p) = \alpha \cdot F(p) + \beta \cdot R(p) + \gamma \cdot T(p)")
                    st.markdown(
                        f"- **F(p)** frequency: how often page *p* appeared in history so far  \n"
                        f"- **R(p)** recency: how recently page *p* was last used  \n"
                        f"- **T(p)** transition: P(*p* | previous page) from observed pairs  \n"
                        f"- Weights used (normalized): α = **{used.get('alpha', 0):.2f}**, "
                        f"β = **{used.get('beta', 0):.2f}**, γ = **{used.get('gamma', 0):.2f}**"
                    )
                    st.caption("History is updated after each decision, so the algorithm never looks into the future.")

st.header("Project guide")
st.divider()
about, how, compare, predict = st.tabs(
    ["1. About the Project", "2. How the algorithms work", "3. Performance comparison", "4. Predictive decision explanation"]
)

with about:
    st.markdown(
        """
**Problem.** Main memory holds only a few pages. When a requested page is missing,
the OS must choose a victim page to replace. A poor choice causes extra page faults.

**What this project does.** It is a local simulation (not a real kernel). You provide
a reference string and a frame count. The program replays that string through four
algorithms and reports faults, hits, ratios, memory snapshots, and comparison charts.

**Who it is for.** A 2nd-year Operating Systems college project that you can explain
in a viva: definitions, traces, and why Optimal is a benchmark rather than a real policy.
        """
    )

with how:
    st.markdown(
        """
**FIFO.** The oldest loaded page is replaced. Easy to implement; can throw out a page
that is still in heavy use (Belady's anomaly is possible on some strings).

**LRU.** The page unused for the longest time is replaced. This follows temporal locality.

**Optimal.** The page whose *next* use is farthest in the future is replaced. This needs
the future reference string, so real operating systems cannot run it. Use it only as
a lower-bound comparison.

**Predictive (this project).** Uses only the past: frequency counts, recency, and
first-order transition probabilities. It is rule-based and deterministic — not neural
networks and not random guesses.
        """
    )

with compare:
    st.markdown(
        """
Run all four algorithms on the same input, then read:

- **Page faults** — missing pages (lower is better)
- **Page hits** — page already in a frame
- **Hit ratio** — hits / total references
- **Fault ratio** — faults / total references

Results depend on the reference string and the number of frames. The predictive
method can look better than FIFO or LRU on some traces and worse on others.
That is expected. Do not claim that it always beats Optimal.
        """
    )

with predict:
    st.markdown(
        """
When memory is full and a new page arrives:

1. Score every resident page from history so far.
2. Use **S(p) = α·F(p) + β·R(p) + γ·T(p)**
3. Replace the page with the smallest S(p).
4. If two pages tie, the left-most frame is chosen so the run is reproducible.

**Frequency** captures pages that belong to the current working set.
**Recency** captures temporal locality.
**Transition probability** captures simple sequences such as page 2 often following page 1.

Weights in the sidebar change the mix. They are normalized internally so they sum to 1.
        """
    )
