# app.py — version sans sidebar
import streamlit as st
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Modules accessibles
MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétrices",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]

PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",
    "Tumeurs des voies excrétrices": "#E5F3E6",
    "Tumeur de la prostate": "#FFF2C6",
    "Tumeur du rein": "#FFD8CC",
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",
    "Lithiase": "#FFE6CC",
    "Infectiologie": "#DDE8F7",
}

# Initialiser l’état de navigation
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

# ---------- UI helpers ----------
def go_home():
    st.session_state["page"] = "Accueil"
    st.experimental_rerun()

def go_module(label: str):
    st.session_state["page"] = label
    st.experimental_rerun()

def category_button(label: str, color: str, key: str):
    with st.container():
        clicked = st.button(f"{label}  ›", key=key, use_container_width=True)
        st.markdown(
            f"<div style='height:6px;background:{color};border-radius:6px;margin-bottom:10px;'></div>",
            unsafe_allow_html=True,
        )
        if clicked:
            go_module(label)

# ---------- Home page ----------
def render_home():
    st.markdown(f"<h1 style='color:#0E3C6E'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#3a4a60'>{APP_SUBTITLE}</p>", unsafe_allow_html=True)
    st.markdown("### Sélectionnez une rubrique")

    cols = st.columns(2)
    for i, mod in enumerate(MODULES):
        with cols[i % 2]:
            category_button(mod, PALETTE[mod], key=f"btn_{i}")

# ---------- Module page ----------
def render_module(label: str):
    st.button("🏠 Accueil", on_click=go_home)  # bouton retour
    st.header(f"🔷 {label}")
    st.info(f"Contenu du module **{label}** à implémenter…")

# ---------- Routing ----------
if st.session_state["page"] == "Accueil":
    render_home()
else:
    render_module(st.session_state["page"])

