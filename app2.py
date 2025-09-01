# app.py — Urology Assistant AI (sans sidebar) + module Vessie avec sous-pages
# 1) TOUJOURS d'abord :
import streamlit as st
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Modules de niveau 1 (page d'accueil)
MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétrices",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]

# Palette pastel
PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",
    "Tumeurs des voies excrétrices": "#E5F3E6",
    "Tumeur de la prostate": "#FFF2C6",
    "Tumeur du rein": "#FFD8CC",
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",
    "Lithiase": "#FFE6CC",
    "Infectiologie": "#DDE8F7",
}

# Init état de navigation
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

# ---------- helpers nav ----------
def go_home():
    st.session_state["page"] = "Accueil"
    st.rerun()  # <- remplacement de st.experimental_rerun()

def go_module(label: str):
    st.session_state["page"] = label
    st.rerun()  # <- remplacement de st.experimental_rerun()

# ---------- UI helpers ----------
def category_button(label: str, color: str, key: str):
    with st.container():
        clicked = st.button(f"{label}  ›", key=key, use_container_width=True)
        st.markdown(
            f"<div style='height:6px;background:{color};border-radius:6px;margin-bottom:12px;'></div>",
            unsafe_allow_html=True,
        )
        if clicked:
            go_module(label)

def top_header():
    st.markdown(
        f"<div style='padding:18px 22px;background:linear-gradient(90deg,#0E3C6E,#154c8a);"
        f"border-radius:12px;margin-bottom:18px;'>"
        f"<h1 style='color:#fff;margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1>"
        f"</div>",
        unsafe_allow_html=True,
    )

def btn_home_and_back(show_back: bool = False, back_label: str = "Tumeur de la vessie"):
    cols = st.columns([1, 3])
    with cols[0]:
        st.button("🏠 Accueil", on_click=go_home)
    if show_back:
        with cols[1]:
            st.button(f"⬅️ Retour : {back_label}", on_click=lambda: go_module(back_label))

# ---------- pages ----------
def render_home():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)

    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")

def render_vessie_menu():
    btn_home_and_back()  # juste bouton Accueil
    st.markdown("## Tumeur de la vessie")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("TVNIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVNIM"))
    with c2:
        st.button("TVIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVIM"))
    with c3:
        st.button("Tumeur de vessie métastatique", use_container_width=True, on_click=lambda: go_module("Vessie: Métastatique"))

def render_tvnim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVNIM (tumeur vésicale n’infiltrant pas le muscle)")
    st.info("Placeholder : ici on branchera la stratification AFU (faible/intermédiaire/haut/très haut), "
            "la CAT détaillée (IPOP, chimio endovésicale, BCG) et les modalités de surveillance.")

def render_tvim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVIM (tumeur vésicale infiltrant le muscle)")
    st.info("Placeholder : ici on branchera néoadjuvant cisplatine, cystectomie/TTM, adjuvant (nivolumab/chemo) "
            "et la surveillance AFU.")

def render_vessie_meta_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 Tumeur de la vessie métastatique")
    st.info("Placeholder : ici on branchera Enfortumab+Pembrolizumab (1re ligne), alternatives (Cis/Gem+Nivo; "
            "Pt-based → Avelumab) et le suivi d’imagerie.")

def render_generic_module(label: str):
    btn_home_and_back()
    st.header(f"🔷 {label}")
    st.info(f"Contenu du module **{label}** à implémenter…")
# =========================
# TVNIM — Formulaire + CAT + Export (sans dépendances externes)
# =========================
import base64
import io
from datetime import datetime

def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str) -> str:
    """
    Stratification AFU (Tableau III) — approximation fidèle avec les champs disponibles.
    - Faible : pTa bas grade, <3 cm, unifocale
    - Intermédiaire : pTa bas grade restant (pas de critères haut/très haut)
    - Haut : pT1 OU haut grade (G3)
    - Très haut : pT1 haut grade + (taille >3 cm OU multifocalité/papillomatose)
    """
    if stade == "pTa" and grade == "Bas grade" and taille_mm < 30 and nombre == "Unique":
        return "faible"

    # Très haut risque (pT1 haut grade + facteur aggravant)
    if stade == "pT1" and grade == "Haut grade" and (taille_mm > 30 or nombre != "Unique"):
        return "très haut"

    # Haut risque (au moins un critère : pT1, haut grade)
    if stade == "pT1" or grade == "Haut grade":
        return "haut"

    # Intermédiaire : le reste des pTa bas grade
    return "intermédiaire"


def plan_tvnim(risque: str) -> tuple[list[str], list[str]]:
    """Retourne (traitement, suivi) selon AFU 2024–2026."""
    if risque == "faible":
        traitement = [
            "RTUV complète et profonde (présence de détrusor au compte rendu).",
            "Instillation postopératoire précoce (IPOP) dans les 2 h si pas de CI (mitomycine/épirubicine/gemcitabine).",
        ]
        suivi = [
            "Cystoscopie : 3e et 12e mois, puis 1×/an pendant 5 ans.",
            "Cytologie : n

