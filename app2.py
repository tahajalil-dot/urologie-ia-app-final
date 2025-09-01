# app.py — Urology Assistant AI
import streamlit as st
import base64
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Modules principaux
MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétrices",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]

# Couleurs pastel
PALETTE = {
    "Tumeur de la vessie": "#D8EEF0",
    "Tumeurs des voies excrétrices": "#E5F3E6",
    "Tumeur de la prostate": "#FFF2C6",
    "Tumeur du rein": "#FFD8CC",
    "Hypertrophie bénigne de la prostate (HBP)": "#E7E0FF",
    "Lithiase": "#FFE6CC",
    "Infectiologie": "#DDE8F7",
}

# Etat initial
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

# --- Helpers navigation ---
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

# --- Stratification TVNIM ---
def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str) -> str:
    if stade == "pTa" and grade == "Bas grade" and taille_mm < 30 and nombre == "Unique":
        return "faible"
    if stade == "pT1" and grade == "Haut grade" and (taille_mm > 30 or nombre != "Unique"):
        return "très haut"
    if stade == "pT1" or grade == "Haut grade":
        return "haut"
    return "intermédiaire"

def plan_tvnim(risque: str):
    if risque == "faible":
        traitement = [
            "RTUV complète et profonde (présence de détrusor au compte rendu anathomopathologique).",
            "Après la résection de ces tumeurs, il est recom-
mandé de réaliser une Instillation postopératoire précoce (IPOP) dans les 2 h si pas de CI (mitomycine/épirubicine/gemcitabine). Aucun autre traitement
complémentaire n'est nécessaire..",
        ]
        suivi = [
            "Cystoscopie : 3e et 12e mois, puis 1×/an pendant 5 ans.",
            "Cytologie : non systématique.",
            "Uro-TDM : non systématique.",
        ]
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète (second-look si doute de résection).",
            "Instillations endovésicales de chimiothérapie (MMC/épirubicine/gemcitabine) : 6–8 instillations hebdomadaires.",
            "Alternative si besoin : BCG avec entretien 12 mois.",
        ]
        suivi = [
            "Cystoscopie : 3e et 6e mois, puis tous les 6 mois pendant 2 ans, puis 1×/an (≥10 ans).",
            "Cytologie : systématique.",
            "Uro-TDM : non systématique.",
        ]
    elif risque == "haut":
        traitement = [
            "RTUV complète + second-look si pT1 ou muscle absent.",
            "BCG endovésical : induction (6 instillations) + entretien 3 ans (schéma 3/6/12 mois puis /6 mois).",
            "Si CI/échec BCG : chimio endovésicale (MMC/gemcitabine ± docétaxel).",
        ]
        suivi = [
            "Cystoscopie : tous les 3 mois pendant 2 ans, puis tous les 6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie : systématique.",
            "Uro-TDM : annuel recommandé.",
        ]
    else:  # très haut
        traitement = [
            "RTUV complète (qualité maximale).",
            "BCG avec entretien 3 ans OU cystectomie précoce avec curage ganglionnaire étendu (selon RCP).",
        ]
        suivi = [
            "Cystoscopie : tous les 3 mois pendant 2 ans, puis tous les 6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie : systématique.",
            "Uro-TDM : annuel obligatoire.",
        ]
    return traitement, suivi

def build_report_text(stade, grade, taille, nombre, risque, traitement, suivi) -> str:
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
    lines.append("")
    lines.append("== Modalités de suivi ==")
    for s in suivi: lines.append(f"• {s}")
    lines.append("")
    lines.append("Références : AFU 2024–2026 (Tableau III & IV, reco RTUV).")
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

# --- Pages ---
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
        traitement, suivi = plan_tvnim(risque)
        st.subheader(f"📊 Risque estimé : {risque.upper()}")
        st.markdown("### 💊 Traitement")
        for t in traitement: st.markdown("- " + t)
        st.markdown("### 📅 Suivi")
        for s in suivi: st.markdown("- " + s)
        report_text = build_report_text(stade, grade, taille, nombre, risque, traitement, suivi)
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

# --- Routing ---
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
