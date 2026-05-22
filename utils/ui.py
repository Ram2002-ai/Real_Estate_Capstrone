from __future__ import annotations

import html
from pathlib import Path

import streamlit as st


ORANGE = "#ff4b2b"
INK = "#2b2726"
MUTED = "#6b625f"
CREAM = "#f7efe6"
PAPER = "#fffaf4"

BUILDING_IMAGES = [
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1000&q=80",
]


def page_config(title: str) -> None:
    st.set_page_config(
        page_title=title,
        page_icon="G",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_css() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {{
    --orange: {ORANGE};
    --ink: {INK};
    --muted: {MUTED};
    --cream: {CREAM};
    --paper: {PAPER};
    --line: rgba(43, 39, 38, 0.12);
}}

html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at 82% 28%, rgba(255, 110, 48, 0.32), transparent 34%),
        linear-gradient(105deg, #fffaf4 0%, #fff2e8 48%, #ff8a4a 100%);
    color: var(--ink);
}}

[data-testid="stSidebar"] {{
    background: rgba(255, 250, 244, 0.92);
    border-right: 1px solid var(--line);
}}

.block-container {{
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--ink);
    letter-spacing: 0;
}}

.app-shell {{
    background: rgba(255, 250, 244, 0.74);
    border: 1px solid rgba(43, 39, 38, 0.10);
    border-radius: 8px;
    box-shadow: 0 24px 80px rgba(43, 39, 38, 0.08);
    overflow: hidden;
}}

.topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1.1rem 1.1rem;
    border-bottom: 1px solid rgba(255, 75, 43, 0.18);
    background: rgba(247, 239, 230, 0.88);
}}

.brand {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 850;
    font-size: 1.35rem;
    color: var(--orange);
}}

.brand-mark {{
    width: 44px;
    height: 44px;
    border: 3px solid var(--orange);
    border-radius: 999px;
    display: grid;
    place-items: center;
    font-weight: 850;
}}

.nav-pill {{
    background: var(--orange);
    color: white;
    border-radius: 8px;
    padding: 0.82rem 1.15rem;
    font-weight: 750;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 150px;
}}

.hero-grid {{
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
    gap: 2rem;
    align-items: center;
    padding: 2.4rem 2.2rem 1.5rem;
}}

.eyebrow {{
    display: inline-flex;
    border: 1px solid rgba(255, 75, 43, 0.24);
    background: rgba(255, 247, 240, 0.8);
    color: var(--orange);
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 750;
    margin-bottom: 1rem;
}}

.hero-title {{
    font-size: clamp(3.2rem, 6vw, 6.4rem);
    line-height: 0.98;
    font-weight: 900;
    margin: 0 0 1.1rem;
}}

.hero-title .accent {{
    color: var(--orange);
}}

.hero-copy {{
    color: #2f3744;
    font-size: 1.08rem;
    line-height: 1.7;
    max-width: 720px;
}}

.hero-photo {{
    min-height: 420px;
    border-radius: 999px 999px 8px 8px;
    border: 18px solid rgba(255, 122, 43, 0.9);
    background-size: cover;
    background-position: center;
    box-shadow: 0 28px 70px rgba(86, 37, 19, 0.22);
}}

.section-title {{
    font-size: 1.4rem;
    font-weight: 850;
    margin: 1.4rem 0 0.8rem;
}}

.metric-card, .glass-card, .module-card, .insight-card {{
    background: rgba(255, 250, 244, 0.92);
    border: 1px solid rgba(43, 39, 38, 0.10);
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 14px 40px rgba(43, 39, 38, 0.07);
}}

.metric-label {{
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.06em;
}}

.metric-value {{
    color: var(--ink);
    font-size: 1.75rem;
    font-weight: 900;
    margin-top: 0.25rem;
}}

.metric-note {{
    color: var(--muted);
    font-size: 0.86rem;
    margin-top: 0.3rem;
}}

.module-card {{
    min-height: 190px;
    border-top: 4px solid var(--orange);
}}

.module-card h3 {{
    margin: 0.35rem 0 0.5rem;
    font-size: 1.15rem;
}}

.module-card p {{
    color: var(--muted);
    line-height: 1.55;
    margin: 0;
}}

.badge {{
    display: inline-flex;
    align-items: center;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    background: rgba(255, 75, 43, 0.12);
    color: var(--orange);
    font-size: 0.78rem;
    font-weight: 800;
    margin: 0.15rem 0.25rem 0.15rem 0;
}}

.property-card {{
    display: grid;
    grid-template-columns: 168px minmax(0, 1fr);
    gap: 1rem;
    background: rgba(255, 250, 244, 0.94);
    border: 1px solid rgba(43, 39, 38, 0.10);
    border-radius: 8px;
    padding: 0.8rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 14px 40px rgba(43, 39, 38, 0.07);
}}

.property-image {{
    min-height: 128px;
    border-radius: 8px;
    background-size: cover;
    background-position: center;
}}

.property-title {{
    font-size: 1.1rem;
    font-weight: 850;
    margin-bottom: 0.35rem;
}}

.property-meta {{
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.55;
}}

.interpretation {{
    color: #4a403d;
    background: rgba(255, 255, 255, 0.62);
    border-left: 4px solid var(--orange);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.35rem 0 1.2rem;
    font-size: 0.92rem;
}}

[data-testid="stDataFrame"] {{
    background: rgba(255, 250, 244, 0.92);
    border: 1px solid rgba(43, 39, 38, 0.10);
    border-radius: 8px;
    padding: 0.35rem;
    box-shadow: 0 14px 40px rgba(43, 39, 38, 0.06);
}}

[data-testid="stDataFrame"] div[role="columnheader"] {{
    background: rgba(255, 75, 43, 0.10);
    color: var(--ink);
    font-weight: 850;
}}

[data-testid="stDataFrame"] div[role="gridcell"] {{
    color: #3c3431;
}}

.stButton>button, .stDownloadButton>button {{
    border-radius: 8px;
    border: 1px solid var(--orange);
    background: var(--orange);
    color: white;
    font-weight: 800;
}}

.stButton>button:hover, .stDownloadButton>button:hover {{
    border-color: #df351a;
    background: #df351a;
    color: white;
}}

@media (max-width: 900px) {{
    .topbar, .hero-grid, .property-card {{
        grid-template-columns: 1fr;
        display: grid;
    }}
    .hero-grid {{
        padding: 1.35rem;
    }}
    .hero-photo {{
        min-height: 300px;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def shell_start(active: str = "Dashboard") -> None:
    st.markdown(
        f"""
<div class="app-shell">
  <div class="topbar">
    <div class="brand"><div class="brand-mark">RI</div><span>Realty Intelligence</span></div>
    <div class="nav-pill">{html.escape(active)}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, accent: str, body: str, image_url: str | None = None, eyebrow: str = "Decision intelligence for property buyers") -> None:
    photo = image_url or BUILDING_IMAGES[0]
    st.markdown(
        f"""
<div class="app-shell" style="margin-top: 1rem;">
  <div class="hero-grid">
    <div>
      <div class="eyebrow">{html.escape(eyebrow)}</div>
      <h1 class="hero-title">{html.escape(title)} <span class="accent">{html.escape(accent)}</span></h1>
      <div class="hero-copy">{html.escape(body)}</div>
    </div>
    <div class="hero-photo" style="background-image: url('{photo}')"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "") -> str:
    return f"""
<div class="metric-card">
  <div class="metric-label">{html.escape(label)}</div>
  <div class="metric-value">{html.escape(value)}</div>
  <div class="metric-note">{html.escape(note)}</div>
</div>
"""


def module_card(title: str, body: str, badge: str) -> str:
    return f"""
<div class="module-card">
  <span class="badge">{html.escape(badge)}</span>
  <h3>{html.escape(title)}</h3>
  <p>{html.escape(body)}</p>
</div>
"""


def insight_card(title: str, body: str, tone: str = "Signal") -> str:
    return f"""
<div class="insight-card">
  <span class="badge">{html.escape(tone)}</span>
  <h3 style="margin: .35rem 0 .45rem;">{html.escape(title)}</h3>
  <p style="color: var(--muted); line-height: 1.55; margin: 0;">{html.escape(body)}</p>
</div>
"""


def local_society_image(society: str) -> str | None:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in society).strip("_")
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "societies"
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = assets_dir / f"{safe}{ext}"
        if candidate.exists():
            return str(candidate)
    return None


def image_for_name(name: str, property_type: str = "flat") -> str:
    local = local_society_image(name)
    if local:
        return local
    idx = abs(hash((name, property_type))) % len(BUILDING_IMAGES)
    return BUILDING_IMAGES[idx]


def property_card(
    title: str,
    meta: list[str],
    tags: list[str],
    image_url: str,
    score: float | None = None,
) -> str:
    badge_html = "".join(f'<span class="badge">{html.escape(tag)}</span>' for tag in tags[:4])
    score_line = f"Match score: {score:.2f}" if score is not None else ""
    meta_html = "<br>".join(html.escape(item) for item in meta if item)
    return f"""
<div class="property-card">
  <div class="property-image" style="background-image: url('{image_url}')"></div>
  <div>
    <div class="property-title">{html.escape(title)}</div>
    <div class="property-meta">{meta_html}</div>
    <div style="margin-top: .45rem;">{badge_html}</div>
    <div class="property-meta" style="font-weight: 800; color: var(--orange); margin-top: .35rem;">{html.escape(score_line)}</div>
  </div>
</div>
"""


def interpretation(text: str) -> None:
    st.markdown(f'<div class="interpretation">{html.escape(text)}</div>', unsafe_allow_html=True)


def table_card(title: str, body: str = "") -> None:
    st.markdown(
        f"""
<div style="margin: 1rem 0 .45rem;">
  <div class="section-title" style="margin-bottom: .25rem;">{html.escape(title)}</div>
  <div style="color: var(--muted); line-height: 1.45;">{html.escape(body)}</div>
</div>
""",
        unsafe_allow_html=True,
    )
