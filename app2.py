# app.py — Urology Assistant AI (Accueil + Vessie -> TVNIM/TVIM/Métastatique)
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path

# =========================
# CONFIG DE BASE
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Modules (page d’accueil)
MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétrices",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]

# Couleurs pastel pour la grille d’accueil
PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",
    "Tumeurs des voies excrétrices": "#E5F3E6",
    "Tumeur de la prostate": "#FFF2C6",
    "Tumeur du rein": "#FFD8CC",
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",
    "Lithiase": "#FFE6CC",
    "Infectiologie": "#DDE8F7",
}

# Etat initial de navigation
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

# =========================
# HELPERS UI & NAVIGATION
# =========================
def go_home():
    st.session_state["page"] = "Accueil"
    st.rerun()

def go_module(label: str):
    st.session_state["page"] = label
    st.rerun()

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

# =========================
# LOGIQUE CLINIQUE — TVNIM (AFU)
# =========================
def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str) -> str:
    """
    AFU (Tableau III) via nos champs :
    - Faible : pTa bas grade, <3 cm, unifocale
    - Intermédiaire : pTa bas grade (sans critères haut/très haut)
    - Haut : pT1 OU haut grade
    - Très haut : pT1 haut grade + (taille >3 cm OU multifocale/papillomatose)
    """
    if stade == "pTa" and grade == "Bas grade" and taille_mm < 30 and nombre == "Unique":
        return "faible"
    if stade == "pT1" and grade == "Haut grade" and (taille_mm > 30 or nombre != "Unique"):
        return "très haut"
    if stade == "pT1" or grade == "Haut grade":
        return "haut"
    return "intermédiaire"

def plan_tvnim(risque: str):
    """
    Retourne (traitement, suivi, protocoles, notes_second_look)
    Protocoles & doses usuelles (à adapter au contexte local / RCP).
    """
    # Notes RTUV second look — A AFFICHER POUR TOUS les cas si un critère est présent
    notes_second_look = [
        "RTUV de second look recommandée si :",
        "• Tumeur pT1 (réévaluation systématique).",
        "• Tumeur volumineuse et/ou multifocale (première résection possiblement incomplète).",
        "• Absence de muscle détrusor dans la pièce initiale (qualité insuffisante).",
    ]

    # Protocoles / Doses — textes prêts à afficher
    PROTO = {
        "IPOP": [
            "IPOP dans les 2 h (≤24 h) si pas d’hématurie/perforation :",
            "• Mitomycine C 40 mg dans 40 mL (instillation unique, rétention 1–2 h).",
            "  OU Épirubicine 50 mg (40–50 mL).",
            "  OU Gemcitabine 1 g (50 mL).",
        ],
        "CHIMIO_EV": [
            "Chimiothérapie endovésicale — Induction 6–8 hebdomadaires :",
            "• Mitomycine C 40 mg / 40 mL, 1×/semaine ×6–8.",
            "• Épirubicine 50 mg / 40–50 mL, 1×/semaine ×6–8.",
            "• Gemcitabine 1 g / 50 mL, 1×/semaine ×6–8.",
            "Entretien optionnel (intermédiaire) : 1 instillation mensuelle ×9 (mois 4→12).",
        ],
        "BCG_12M": [
            "BCG — maintien 12 mois (risque intermédiaire) :",
            "• Induction : 6 instillations hebdomadaires (semaines 1–6).",
            "• Entretien 12 mois : 3 instillations aux mois 3, 6 et 12 (3×3).",
            "Dose : flacon standard (dose complète), rétention ~2 h si toléré.",
        ],
        "BCG_36M": [
            "BCG — maintien 36 mois (haut / très haut) :",
            "• Induction : 6 instillations hebdomadaires (semaines 1–6).",
            "• Entretien : 3 instillations à M3, M6, M12, puis tous les 6 mois jusqu’à M36.",
            "Dose : flacon standard (dose complète), rétention ~2 h si toléré.",
        ],
        "RCP_CYSTECTOMIE": [
            "Très haut risque :",
            "• Discussion RCP pour cystectomie précoce avec curage ganglionnaire étendu.",
        ],
    }

    if risque == "faible":
        traitement = [
            "RTUV complète et profonde (mention du détrusor au CR opératoire).",
            *PROTO["IPOP"],
            "Aucun traitement complémentaire d’entretien requis.",
        ]
        suivi = [
            "Cystoscopie : 3e et 12e mois, puis 1×/an pendant 5 ans.",
            "Cytologie : non systématique.",
            "Uro-TDM : non systématique.",
        ]
        protocoles = []  # on n’impose pas BCG/MMC d’entretien
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète (second look si doute d’exérèse).",
            *PROTO["CHIMIO_EV"],
            "Alternative possible : BCG (induction 6) + entretien 12 mois selon profil.",
        ]
        suivi = [
            "Cystoscopie : 3e et 6e mois, puis tous les 6 mois pendant 2 ans, puis 1×/an (≥10 ans).",
            "Cytologie : systématique.",
            "Uro-TDM : non systématique.",
        ]
        protocoles = [*PROTO["BCG_12M"]]
    elif risque == "haut":
        traitement = [
            "RTUV complète + second look si pT1 ou muscle absent.",
            *PROTO["BCG_36M"],
            "Si CI/échec BCG : chimio endovésicale (MMC/gemcitabine ± docétaxel) selon tolérance.",
        ]
        suivi = [
            "Cystoscopie : tous les 3 mois pendant 2 ans, puis tous les 6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie : systématique.",
            "Uro-TDM : annuel recommandé.",
        ]
        protocoles = []
    else:  # très haut
        traitement = [
            "RTUV complète (qualité maximale).",
            *PROTO["BCG_36M"],
            *PROTO["RCP_CYSTECTOMIE"],
        ]
        suivi = [
            "Cystoscopie : tous les 3 mois pendant 2 ans, puis tous les 6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie : systématique.",
            "Uro-TDM : annuel obligatoire.",
        ]
        protocoles = []

    return traitement, suivi, protocoles, notes_second_look

# =========================
# EXPORTS (HTML / TXT)
# =========================
def build_report_text(stade, grade, taille, nombre, risque, traitement, suivi, protocoles, notes_second_look) -> str:
    lines = []
    lines.append("Urology Assistant AI — CAT TVNIM (AFU 2024–2026)")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("== Données saisies ==")
    lines.append(f"- Stade : {stade}")
    lines.append(f"- Grade : {grade}")
    lines.append(f"- Taille max : {taille} mm")
    lines.append(f"- Nombre : {nombre}")
    lines.append("")
    lines.append(f"== Stratification du risque : {risque.upper()} ==")
    lines.append("")
    lines.append("== Traitement recommandé ==")
    for t in traitement: lines.append(f"• {t}")
    if protocoles:
        lines.append("")
        lines.append("== Détails de protocoles ==")
        for p in protocoles: lines.append(f"• {p}")
    lines.append("")
    lines.append("== Modalités de suivi ==")
    for s in suivi: lines.append(f"• {s}")
    lines.append("")
    lines.append("== RTUV de second look : rappels ==")
    for n in notes_second_look: lines.append(f"• {n}")
    lines.append("")
    lines.append("Réfs : AFU 2024–2026 — Tableau III (stratification/traitement), Tableau IV (suivi), reco RTUV de qualité.")
    return "\n".join(lines)

def offer_exports(report_text: str):
    html = f"""<!doctype html>
<html lang="fr"><meta charset="utf-8">
<title>CAT TVNIM</title>
<pre>{report_text}</pre>
</html>"""
    b64_html = base64.b64encode(html.encode()).decode()
    b64_txt = base64.b64encode(report_text.encode()).decode()
    st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="CAT_TVNIM.html">📄 Télécharger en HTML</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="data:text/plain;base64,{b64_txt}" download="CAT_TVNIM.txt">📝 Télécharger en TXT</a>', unsafe_allow_html=True)

# =========================
# IMAGE DES PROTOCOLES (BCG / MMC)
# =========================
DEFAULT_PROTO_IMG = Path(__file__).parent / "assets" / "protocoles_tvnim.png"

def show_protocol_image():
    """
    1) Si 'assets/protocoles_tvnim.png' existe -> affiche.
    2) Sinon -> propose un uploader pour téléverser l’image (png/jpg).
    3) Si rien -> warning.
    """
    if DEFAULT_PROTO_IMG.exists():
        st.image(str(DEFAULT_PROTO_IMG), use_container_width=True,
                 caption="Schéma des protocoles (depuis assets/protocoles_tvnim.png)")
        return

    uploaded = st.file_uploader("📎 Importer l'image des protocoles (png/jpg)", type=["png", "jpg", "jpeg"])
    if uploaded is not None:
        st.image(uploaded, use_container_width=True, caption="Schéma des protocoles (image téléversée)")
    else:
        st.warning("Image des protocoles introuvable. Ajoute le fichier **assets/protocoles_tvnim.png** au repo "
                   "ou téléverse une image via le sélecteur ci-dessus.")

# =========================
# PAGES
# =========================
def render_home():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)
    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")

def render_vessie_menu():
    btn_home_and_back()
    st.markdown("## Tumeur de la vessie")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1: st.button("TVNIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVNIM"))
    with c2: st.button("TVIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVIM"))
    with c3: st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Vessie: Métastatique"))

def render_tvnim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVNIM (tumeur n’infiltrant pas le muscle)")

    with st.form("tvnim_form"):
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1"])
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        taille = st.slider("Taille maximale (mm)", 1, 100, 10)
        nombre = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple", "Papillomatose vésicale"])
        submitted = st.form_submit_button("🔎 Générer la CAT")

    if submitted:
        risque = stratifier_tvnim(stade, grade, taille, nombre)
        traitement, suivi, protocoles, notes_second_look = plan_tvnim(risque)

        st.subheader(f"📊 Risque estimé : {risque.upper()}")
        st.markdown("### 💊 Traitement")
        for t in traitement: st.markdown("- " + t)

        if protocoles:
            st.markdown("### 📦 Protocoles détaillés")
            for p in protocoles: st.markdown("- " + p)

        st.markdown("### 📅 Suivi")
        for s in suivi: st.markdown("- " + s)

        st.markdown("### 📝 RTUV de second look — rappels (quel que soit le risque)")
        for n in notes_second_look: st.markdown("- " + n)

        st.markdown("### 🖼️ Schéma visuel des protocoles (BCG / MMC)")
        show_protocol_image()

        # Export
        report_text = build_report_text(stade, grade, taille, nombre, risque, traitement, suivi, protocoles, notes_second_look)
        st.markdown("### 📤 Export")
        offer_exports(report_text)

def render_tvim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVIM (tumeur infiltrant le muscle)")
    st.info("Placeholder — à implémenter")

def render_vessie_meta_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 Tumeur de la vessie métastatique")
    st.info("Placeholder — à implémenter")

def render_generic(label: str):
    btn_home_and_back()
    st.header(f"🔷 {label}")
    st.info("Module en cours de construction")

# =========================
# ROUTING
# =========================
page = st.session_state["page"]
if page == "Accueil":
    render_home()
elif page == "Tumeur de la vessie":
    render_vessie_menu()
elif page == "Vessie: TVNIM":
    render_tvnim_page()
elif page == "Vessie: TVIM":
    render_tvim_page()
elif page == "Vessie: Métastatique":
    render_vessie_meta_page()
else:
    render_generic(page)
