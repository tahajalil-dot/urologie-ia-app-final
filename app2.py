# =========================
# Home (PC) – Urology Assistant AI
# =========================
import streamlit as st

APP_TITLE = "Urologie Assistant IA"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Mappings vers tes modules existants
ROUTE_MAP = {
    "Tumeur de la vessie": "Cancer de la vessie (TVNIM / TVIM)",
    "Tumeurs des voies excrétrices": "Tumeurs des voies excrétrices supérieures (TVES)",
    "Tumeur de la prostate": "Cancer de la prostate",
    "Tumeur du rein": "Cancer du rein",
    "Hypertrophie bénigne de la prostate (HBP)": "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase": "Lithiase urinaire",
    "Infectiologie": "Infectiologie",  # (placeholder si module pas encore branché)
}

# Palette (pastels propres PC)
PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",              # bleu-menthe pastel
    "Tumeurs des voies excrétrices": "#E5F3E6",    # vert clair
    "Tumeur de la prostate": "#FFF2C6",            # jaune doux
    "Tumeur du rein": "#FFD8CC",                   # pêche
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",  # mauve clair
    "Lithiase": "#FFE6CC",                         # abricot clair
    "Infectiologie": "#DDE8F7",                    # bleu gris clair
}

def _go(target: str):
    st.session_state["menu"] = ROUTE_MAP[target]

def _topbar():
    st.markdown(
        """
        <style>
          .ua-header { 
              position: sticky; top: 0; z-index: 10;
              padding: 18px 0; background: linear-gradient(90deg,#0E3C6E,#154c8a);
              border-radius: 12px; margin-bottom: 18px;
          }
          .ua-title { color: #fff; font-size: 28px; font-weight: 800; margin: 0 18px; }
          .ua-nav { color: #cfe3ff; font-weight: 600; margin-right: 18px; }
          .ua-nav a { color: #cfe3ff; text-decoration: none; margin-left: 16px; }
          .ua-hero h2 { margin-top: 6px; font-size: 22px; color: #163657; font-weight: 700; }
          .ua-hero p { color: #3a4a60; margin-top: 6px; }
          .ua-card {
              border: 1px solid #e9eef5; border-radius: 16px; padding: 16px 22px;
              font-weight: 700; text-transform: none; font-size: 16px;
              display: flex; align-items: center; justify-content: space-between;
              box-shadow: 0 1px 0 rgba(16,24,40,.02);
          }
          .ua-card:hover { filter: brightness(.98); transform: translateY(-1px); }
          .ua-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
          @media (max-width: 900px) { .ua-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<div class="ua-header"><div class="ua-title">{APP_TITLE}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="ua-header" style="background:transparent;box-shadow:none;padding:18px 0;">'
            f'<div class="ua-nav" style="text-align:right"><a href="#">Accueil</a><a href="#">Informations</a></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

def _hero():
    st.markdown('<div class="ua-hero">', unsafe_allow_html=True)
    st.markdown(f"### Sélectionnez une rubrique")
    st.markdown(APP_SUBTITLE)
    st.markdown("</div>", unsafe_allow_html=True)

def _category_button(label: str, color: str):
    # Un bouton pleine largeur qui garde la couleur (on utilise st.markdown + form pour capter le clic)
    key = f"btn_{label}"
    with st.form(key):
        st.markdown(
            f'<div class="ua-card" style="background:{color}">'
            f'<span>{label}</span>'
            f'<span>›</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        submitted = st.form_submit_button("", use_container_width=True)
        if submitted:
            _go(label)

def render_home():
    _topbar()
    _hero()

    # grille 2 colonnes sur desktop
    st.markdown('<div class="ua-grid">', unsafe_allow_html=True)

    _category_button("Tumeur de la vessie", PALETTE["Tumeur de la vessie"])
    _category_button("Tumeurs des voies excrétrices", PALETTE["Tumeurs des voies excrétrices"])
    _category_button("Tumeur de la prostate", PALETTE["Tumeur de la prostate"])
    _category_button("Tumeur du rein", PALETTE["Tumeur du rein"])
    _category_button("Hypertrophie bénigne de la prostate (HBP)", PALETTE["Hypertrophie bénigne de la prostate (HBP)"])
    _category_button("Lithiase", PALETTE["Lithiase"])
    _category_button("Infectiologie", PALETTE["Infectiologie"])

    st.markdown("</div>", unsafe_allow_html=True)
