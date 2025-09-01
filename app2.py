# app.py — Urology Assistant AI (Accueil PC complet)
# 1) La toute première commande Streamlit :
import streamlit as st
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

# =========================
# Config & State
# =========================
APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Noms EXACTS utilisés par le sélecteur de menu
MENU_OPTIONS = [
    "Page d'accueil",
    "Cancer de la vessie (TVNIM / TVIM)",
    "Tumeurs des voies excrétrices supérieures (TVES)",
    "Cancer de la prostate",
    "Cancer du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase urinaire",
    "Infectiologie",
]

# Boutons d'accueil -> modules
ROUTE_MAP = {
    "Tumeur de la vessie": "Cancer de la vessie (TVNIM / TVIM)",
    "Tumeurs des voies excrétrices": "Tumeurs des voies excrétrices supérieures (TVES)",
    "Tumeur de la prostate": "Cancer de la prostate",
    "Tumeur du rein": "Cancer du rein",
    "Hypertrophie bénigne de la prostate (HBP)": "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase": "Lithiase urinaire",
    "Infectiologie": "Infectiologie",
}

# Palette pastel (sobre et différente du modèle AFU)
PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",
    "Tumeurs des voies excrétrices": "#E5F3E6",
    "Tumeur de la prostate": "#FFF2C6",
    "Tumeur du rein": "#FFD8CC",
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",
    "Lithiase": "#FFE6CC",
    "Infectiologie": "#DDE8F7",
}

# État initial du menu
if "menu" not in st.session_state:
    st.session_state["menu"] = "Page d'accueil"

# =========================
# Styles
# =========================
st.markdown(
    """
    <style>
      .ua-header { padding: 18px 22px; background: linear-gradient(90deg,#0E3C6E,#154c8a);
                   border-radius: 12px; margin-bottom: 18px; }
      .ua-title  { color:#fff; font-size:28px; font-weight:800; margin:0; }
      .ua-hero h2 { margin-top: 6px; font-size: 22px; color: #163657; font-weight: 700; }
      .ua-hero p  { color:#3a4a60; margin-top:6px; }
      .ua-card { border: 1px solid #e9eef5; border-radius: 16px; padding: 16px 22px;
                 font-weight: 700; font-size: 16px; display:flex; align-items:center;
                 justify-content: space-between; box-shadow: 0 1px 0 rgba(16,24,40,.02); }
      .ua-card:hover { filter: brightness(.98); transform: translateY(-1px); }
      .ua-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
      @media (max-width: 900px) { .ua-grid { grid-template-columns: 1fr; } }
      /* Boutons Streamlit uniformisés (texte noir discret) */
      .stButton>button { border-radius: 14px; font-weight: 700; font-size: 16px; padding: 10px 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================
def _go(category_label: str):
    """Changer de module via session_state + rerun."""
    st.session_state["menu"] = ROUTE_MAP[category_label]
    st.experimental_rerun()

def _category_button(label: str, color: str, key: str):
    """Bouton pleine largeur stylé (couleur par catégorie)."""
    # On colore le container autour du bouton pour un rendu homogène
    with st.container():
        st.markdown(f'<div class="ua-card" style="background:{color}">', unsafe_allow_html=True)
        clicked = st.button(f"{label}  ›", key=key, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if clicked:
            _go(label)

def render_home():
    # Header
    st.markdown(f'<div class="ua-header"><div class="ua-title">{APP_TITLE}</div></div>', unsafe_allow_html=True)
    # Hero
    st.markdown('<div class="ua-hero">', unsafe_allow_html=True)
    st.markdown("### Sélectionnez une rubrique")
    st.markdown(APP_SUBTITLE)
    st.markdown("</div>", unsafe_allow_html=True)
    # Grid
    st.markdown('<div class="ua-grid">', unsafe_allow_html=True)
    _category_button("Tumeur de la vessie", PALETTE["Tumeur de la vessie"], "btn_vessie")
    _category_button("Tumeurs des voies excrétrices", PALETTE["Tumeurs des voies excrétrices"], "btn_tves")
    _category_button("Tumeur de la prostate", PALETTE["Tumeur de la prostate"], "btn_prostate")
    _category_button("Tumeur du rein", PALETTE["Tumeur du rein"], "btn_rein")
    _category_button("Hypertrophie bénigne de la prostate (HBP)", PALETTE["Hypertrophie bénigne de la prostate (HBP)"], "btn_hbp")
    _category_button("Lithiase", PALETTE["Lithiase"], "btn_lithiase")
    _category_button("Infectiologie", PALETTE["Infectiologie"], "btn_infectio")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Sidebar (menu maître)
# =========================
# On synchronise la valeur affichée avec session_state["menu"]
menu = st.sidebar.selectbox(
    "📂 Choisissez un module :",
    MENU_OPTIONS,
    index=MENU_OPTIONS.index(st.session_state["menu"]),
)
# Mise à jour de l'état avec le choix utilisateur
st.session_state["menu"] = menu

# =========================
# Routing
# =========================
if menu == "Page d'accueil":
    # 👉 render_home() est bien APPELÉ ici
    render_home()

elif menu == "Cancer de la vessie (TVNIM / TVIM)":
    st.header("🔷 Cancer de la vessie (TVNIM / TVIM)")
    st.info("Page module Vessie — à brancher avec tes formulaires TVNIM/TVIM.")

elif menu == "Tumeurs des voies excrétrices supérieures (TVES)":
    st.header("🔷 Tumeurs des voies excrétrices supérieures (TVES)")
    st.info("Page module TVES — contenu à ajouter.")

elif menu == "Cancer de la prostate":
    st.header("🔷 Cancer de la prostate")
    st.info("Page module Prostate — contenu à ajouter.")

elif menu == "Cancer du rein":
    st.header("🔷 Cancer du rein")
    st.info("Page module Rein — contenu à ajouter.")

elif menu == "Hypertrophie bénigne de la prostate (HBP)":
    st.header("🔷 Hypertrophie bénigne de la prostate (HBP)")
    st.info("Page module HBP — contenu à ajouter.")

elif menu == "Lithiase urinaire":
    st.header("🔷 Lithiase urinaire")
    st.info("Page module Lithiase — contenu à ajouter.")

elif menu == "Infectiologie":
    st.header("🔷 Infectiologie")
    st.info("Page module Infectiologie — contenu à ajouter.")
