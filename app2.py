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
    # ============================================================
# EXTENSION — Module "Tumeur de la vessie" avec sous-pages
# À COLLER SOUS TON PREMIER CODE (append-only)
# ============================================================

# --- Helpers de navigation locaux (réutilise ton state "page") ---
def _go(label: str):
    st.session_state["page"] = label
    st.experimental_rerun()

def _btn_home_and_back(back_label: str = None):
    c1, c2 = st.columns([1, 3])
    with c1:
        st.button("🏠 Accueil", on_click=lambda: _go("Accueil"))
    if back_label:
        with c2:
            st.button("⬅️ Retour : Tumeur de la vessie", on_click=lambda: _go("Tumeur de la vessie"))

# --- 2ᵉ page : menu interne du module vessie ---
def render_vessie_menu():
    st.markdown("## Tumeur de la vessie")
    st.caption("Choisissez le sous-module à explorer")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("TVNIM", use_container_width=True, on_click=lambda: _go("Vessie: TVNIM"))
    with col2:
        st.button("TVIM", use_container_width=True, on_click=lambda: _go("Vessie: TVIM"))
    with col3:
        st.button("Tumeur de vessie métastatique", use_container_width=True, on_click=lambda: _go("Vessie: Métastatique"))

# --- Placeholders (tu brancheras tes formulaires/logiciels ici) ---
def render_tvnim_page():
    _btn_home_and_back(back_label="Tumeur de la vessie")
    st.header("🔷 TVNIM (tumeur vésicale n’infiltrant pas le muscle)")
    st.info("Ici on branchera la stratification (faible/intermédiaire/haut/très haut), CAT détaillée (IPOP/chimio/BCG) et calendrier de surveillance AFU.")

def render_tvim_page():
    _btn_home_and_back(back_label="Tumeur de la vessie")
    st.header("🔷 TVIM (tumeur vésicale infiltrant le muscle)")
    st.info("Ici on branchera néoadjuvant (cisplatine), cystectomie/TTM, adjuvant (nivolumab/chemo), et la surveillance AFU.")

def render_vessie_meta_page():
    _btn_home_and_back(back_label="Tumeur de la vessie")
    st.header("🔷 Tumeur de la vessie métastatique")
    st.info("Ici on branchera Enfortumab+Pembrolizumab 1ʳᵉ ligne, alternatives (Cis/Gem+Nivo; Pt-based→Avelumab), et suivi d’imagerie.")

# --- Routing : on REMPLACE la version générique par une version avec sous-pages ---
def render_module(label: str):
    # module "Tumeur de la vessie" -> page intermédiaire avec 3 choix
    if label == "Tumeur de la vessie":
        _btn_home_and_back()  # juste le bouton Accueil en haut
        render_vessie_menu()
        return

    # sous-pages
    if label == "Vessie: TVNIM":
        render_tvnim_page()
        return
    if label == "Vessie: TVIM":
        render_tvim_page()
        return
    if label == "Vessie: Métastatique":
        render_vessie_meta_page()
        return

    # fallback pour les autres modules (inchangé)
    _btn_home_and_back()
    st.header(f"🔷 {label}")
    st.info(f"Contenu du module **{label}** à implémenter…")

# --- forcer


