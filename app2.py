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

# ---------- routing ----------
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
    render_generic_module(page)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def stratifier_tvnim(stade, grade, taille, nombre):
    # Classification AFU
    if stade == "pTa" and grade == "Bas grade" and taille < 30 and nombre == "Unique":
        return "faible"
    if stade == "pTa" and grade == "Bas grade":
        return "intermédiaire"
    if stade == "pT1" or grade == "Haut grade" or nombre in ["Multiple", "Papillomatose vésicale"]:
        # critères très haut risque
        if stade == "pT1" and grade == "Haut grade" and (taille > 30 or nombre != "Unique"):
            return "très haut"
        return "haut"
    return "intermédiaire"

def plan_tvnim(risque):
    traitement, suivi = [], []
    if risque == "faible":
        traitement = [
            "RTUV complète de qualité (détrusor présent)",
            "Instillation postopératoire précoce (IPOP) si pas de CI"
        ]
        suivi = [
            "Cystoscopie à 3 et 12 mois puis annuelle ×5 ans",
            "Cytologie : non systématique",
            "Uro-TDM : non systématique"
        ]
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète",
            "Instillations endovésicales de chimiothérapie (MMC, épirubicine, gemcitabine) 6–8 instillations",
            "Alternative : BCG avec entretien 12 mois"
        ]
        suivi = [
            "Cystoscopie à 3 et 6 mois, puis tous les 6 mois ×2 ans, puis annuelle (≥10 ans)",
            "Cytologie systématique",
        ]
    elif risque == "haut":
        traitement = [
            "RTUV complète ± second look si pT1 ou muscle absent",
            "Instillations endovésicales BCG : induction 6 instillations + entretien 3 ans",
            "Si CI ou échec BCG : chimio endovésicale (MMC, gemcitabine ± docétaxel)"
        ]
        suivi = [
            "Cystoscopie tous les 3 mois ×2 ans, puis tous les 6 mois jusqu’à 5 ans, puis annuelle à vie",
            "Cytologie systématique",
            "Uro-TDM annuel recommandé"
        ]
    else:  # très haut
        traitement = [
            "RTUV complète",
            "Instillations endovésicales BCG avec entretien 3 ans",
            "⚠️ Option : cystectomie précoce avec curage ganglionnaire étendu"
        ]
        suivi = [
            "Cystoscopie tous les 3 mois ×2 ans, puis tous les 6 mois jusqu’à 5 ans, puis annuelle à vie",
            "Cytologie systématique",
            "Uro-TDM annuel obligatoire"
        ]
    return traitement, suivi

def render_tvnim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVNIM (tumeur vésicale n’infiltrant pas le muscle)")
    
    with st.form("tvnim_form"):
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1"])
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        taille = st.slider("Taille maximale de la tumeur (mm)", 1, 100, 10)
        nombre = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple", "Papillomatose vésicale"])
        submitted = st.form_submit_button("🔎 Générer la conduite à tenir")
    
    if submitted:
        risque = stratifier_tvnim(stade, grade, taille, nombre)
        traitement, suivi = plan_tvnim(risque)
        
        st.subheader(f"📊 Risque estimé : {risque.upper()}")
        st.markdown("### 💊 Traitement recommandé")
        for t in traitement: st.markdown("- " + t)
        st.markdown("### 📅 Modalités de suivi")
        for s in suivi: st.markdown("- " + s)

        # Export PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        flow = []
        flow.append(Paragraph(f"Conduite à tenir TVNIM ({risque})", styles["Heading1"]))
        flow.append(Spacer(1,12))
        flow.append(Paragraph("Traitement :", styles["Heading2"]))
        for t in traitement: flow.append(Paragraph("• " + t, styles["Normal"]))
        flow.append(Spacer(1,12))
        flow.append(Paragraph("Modalités de suivi :", styles["Heading2"]))
        for s in suivi: flow.append(Paragraph("• " + s, styles["Normal"]))
        doc.build(flow)
        pdf = buffer.getvalue()
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="CAT_TVNIM.pdf">📥 Télécharger en PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
