# app.py — Urology Assistant AI (Accueil + Vessie -> TVNIM/TVIM/Métastatique)
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path

# =========================
# CONFIG DE BASE + THEME CLAIR
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

# Force un look "mode jour" (clair) via CSS injecté
st.markdown("""
<style>
:root, .stApp, .block-container { background-color: #ffffff !important; color: #111 !important; }
[data-testid="stHeader"], header { background-color: #ffffff !important; }
section.main > div { background-color: #ffffff !important; }
h1,h2,h3,h4,h5,h6 { color:#0E3C6E; }
.stButton > button { background: #0E3C6E; color: #fff; border-radius: 10px; padding: 0.6rem 1rem; border: none; }
.stButton > button:hover { background: #154c8a; }
div[data-baseweb="select"] > div { background: #fff !important; color:#111 !important; }
.st-emotion-cache-1y4p8pa { color:#111 !important; } /* captions */
table { background:#fff !important; }
thead tr th { background:#F2F6FA !important; color:#0E3C6E !important; }
</style>
""", unsafe_allow_html=True)

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

# Modules (page d’accueil)
MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétries",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]

# Couleurs pastel pour la grille d’accueil (barres décoratives)
PALETTE = {
    "Tumeur de la vessie": "#CDEAF1",
    "Tumeurs des voies excrétries": "#E7F4EA",
    "Tumeur de la prostate": "#FFF1C7",
    "Tumeur du rein": "#FFDAD1",
    "Hypertrophie bénigne de la prostate (HBP)": "#E8E2FF",
    "Lithiase": "#FFE9D2",
    "Infectiologie": "#E3ECFF",
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
        f"""
        <div style='padding:18px 22px;background:linear-gradient(90deg,#F7FBFF,#E8F1FA);
        border:1px solid #dfe8f2;border-radius:12px;margin-bottom:18px;'>
        <h1 style='color:#0E3C6E;margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

def btn_home_and_back(show_back: bool = False, back_label: str = "Tumeur de la vessie"):
    cols = st.columns([1, 3])
    with cols[0]:
        st.button("🏠 Accueil", on_click=go_home)
    if show_back:
        with cols[1]:
            st.button(f"⬅️ Retour : {back_label}", on_click=lambda: go_module(back_label))

# ------ Tableau helper (sans pandas) ------
def render_table(title: str, items: list[str], col_name: str = "Recommandation"):
    """Affiche un bloc-titre + un tableau à une colonne contenant items."""
    if not items:
        return
    st.markdown(f"### {title}")
    rows = [{col_name: it} for it in items]
    st.table(rows)

# ------ Export helpers ------
def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title} (AFU 2024–2026)")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr:
            continue
        lines.append(f"== {sec} ==")
        for x in arr:
            lines.append(f"• {x}")
        lines.append("")
    lines.append("Réfs : AFU/EAU — synthèse actualisée.")
    return "\n".join(lines)

def offer_exports(report_text: str, basename: str):
    html = f"""<!doctype html>
<html lang="fr"><meta charset="utf-8">
<title>{basename}</title>
<pre>{report_text}</pre>
</html>"""
    b64_html = base64.b64encode(html.encode()).decode()
    b64_txt = base64.b64encode(report_text.encode()).decode()
    st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="{basename}.html">📄 Télécharger en HTML</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="data:text/plain;base64,{b64_txt}" download="{basename}.txt">📝 Télécharger en TXT</a>', unsafe_allow_html=True)

# =========================
# IMAGE DES PROTOCOLES (BCG / MMC) — URL / LOCAL / UPLOAD
# =========================
# 👉 COLLE ICI l’URL "Raw" de ton image (format .png/.jpg) :
# Exemple :
#   https://raw.githubusercontent.com/<user>/<repo>/<branch>/assets/protocoles_tvnim.png
PROTO_URL = ""  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< COLLE TON URL ICI ENTRE GUILLEMETS

# Chemins locaux possibles (si tu ajoutes l’image dans le repo)
CANDIDATE_PATHS = [
    Path(__file__).parent / "assets" / "protocoles_tvnim.png",  # assets/protocoles_tvnim.png
    Path(__file__).parent / "protocoles_tvnim.png",             # ./protocoles_tvnim.png
]

def show_protocol_image():
    """
    Ordre :
    A) PROTO_URL si renseignée
    B) Fichiers locaux (assets/… ou racine)
    C) Uploader manuel
    """
    st.markdown("### 🖼️ Schéma visuel des protocoles (BCG / MMC)")
    if PROTO_URL.strip():
        try:
            st.image(PROTO_URL.strip(), use_container_width=True, caption="Schéma des protocoles (chargé via URL)")
            return
        except Exception:
            st.warning("Échec du chargement via l’URL fournie. On tente les fichiers locaux…")

    for p in CANDIDATE_PATHS:
        if p.exists():
            st.image(str(p), use_container_width=True, caption=f"Schéma des protocoles (trouvé : {p.name})")
            return

    up = st.file_uploader("📎 Importer l'image des protocoles (png/jpg)", type=["png", "jpg", "jpeg"])
    if up is not None:
        st.image(up, use_container_width=True, caption="Schéma des protocoles (image téléversée)")
    else:
        st.info(
            "Aucune image trouvée.\n\n"
            "Solutions :\n"
            "• Collez l’URL Raw de l’image dans PROTO_URL (ligne indiquée dans le code),\n"
            "• ou ajoutez le fichier dans le repo (assets/protocoles_tvnim.png ou ./protocoles_tvnim.png),\n"
            "• ou importez l’image via le bouton ci-dessus."
        )

# =========================
# LOGIQUE CLINIQUE — TVNIM (AFU)
# =========================
def stratifier_tvnim(
    stade: str,
    grade: str,
    taille_mm: int,
    nombre: str,
    cis_associe: bool = False,
    lvi: bool = False,
    urethre_prostatique: bool = False,
    formes_agressives: bool = False,
) -> str:
    """
    AFU (Tableau III/IV) via nos champs :
    - Faible : pTa bas grade, <3 cm, unifocale
    - Intermédiaire : pTa bas grade (sans critères haut/très haut)
    - Haut : pT1 OU haut grade
    - Très haut : pT1 haut grade + (≥1 facteur aggravant)
                  Facteurs aggravants : taille >3 cm, multifocalité/papillomatose,
                                      CIS associé, LVI, atteinte urètre prostatique,
                                      formes anatomo-pathologiques agressives
    """
    facteurs_aggravants = (
        (taille_mm > 30)
        or (nombre != "Unique")
        or cis_associe
        or lvi
        or urethre_prostatique
        or formes_agressives
    )
    if stade == "pT1" and grade == "Haut grade" and facteurs_aggravants:
        return "très haut"
    if stade == "pT1" or grade == "Haut grade":
        return "haut"
    if stade == "pTa" and grade == "Bas grade" and taille_mm < 30 and nombre == "Unique":
        return "faible"
    return "intermédiaire"

def plan_tvnim(risque: str):
    """
    Retourne (traitement, suivi, protocoles, notes_second_look)
    Protocoles & doses usuelles (à adapter en RCP et selon disponibilité).
    """
    notes_second_look = [
        "RTUV de second look recommandée si :",
        "• Tumeur pT1 (réévaluation systématique).",
        "• Tumeur volumineuse et/ou multifocale (première résection possiblement incomplète).",
        "• Absence de muscle détrusor dans la pièce initiale (qualité insuffisante).",
    ]

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
        protocoles = []
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
# LOGIQUE CLINIQUE — TVIM (AFU)
# =========================
def plan_tvim(
    t_cat: str,
    cN_pos: bool,
    metastases: bool,
    cis_eligible: bool,
    t2_localise: bool,
    hydron: bool,
    bonne_fct_v: bool,
    cis_diffus: bool,
    pdl1_pos: bool,
    post_op_high_risk: bool,
    neo_adjuvant_fait: bool,
):
    """
    Retourne dict: { 'traitement': [...], 'surveillance': [...], 'notes': [...] }
    Synthèse AFU/EAU: NAC cisplatine si éligible -> cystectomie; alternative conservatrice TMT si sélectionné.
    Adjuvant si pT3–4/pN+ ou pas de NAC; adjuvant nivolumab possible (selon PD-L1/AMM locale).
    """
    res = {"traitement": [], "surveillance": [], "notes": []}

    if metastases:
        res["traitement"].append("⚠️ Maladie métastatique : basculer vers le module « Vessie: Métastatique » pour schémas de 1re/2e ligne.")
        return res

    # Néoadjuvant
    if cis_eligible:
        res["traitement"].extend([
            "🧪 **Chimiothérapie néoadjuvante (NAC) recommandée** avant cystectomie (si possible) :",
            "• Gemcitabine + Cisplatine (GC), q21j × 4 cycles :",
            "  - Gemcitabine 1 000 mg/m² J1 & J8, Cisplatine 70 mg/m² J1.",
            "• OU dd-MVAC (q14j × 4) avec G-CSF :",
            "  - Méthotrexate 30 mg/m² J1, Vinblastine 3 mg/m² J2, Doxorubicine 30 mg/m² J2, Cisplatine 70 mg/m² J2.",
            "  - Support G-CSF (J3–J10) selon protocole local.",
        ])
    else:
        res["traitement"].append("⛔ Non éligible cisplatine : pas de NAC standard.")

    # Option TMT
    if t2_localise and (not hydron) and bonne_fct_v and (not cis_diffus):
        res["traitement"].extend([
            "🟦 **Option conservatrice (Trimodal Therapy - TMT)** possible si patient informé :",
            "• RTUV maximale (résection complète) + radiochimiothérapie concomitante.",
            "• Radiothérapie vésicale 64–66 Gy (ex : 55 Gy/20 fractions ou 64 Gy/32 fractions selon centre).",
            "• Radiosensibilisation :",
            "  - 5-FU 500 mg/m² J1–5 et J16–20 + Mitomycine C 12 mg/m² J1,",
            "    OU Cisplatine hebdo 30–40 mg/m² selon éligibilité.",
        ])
        res["notes"].append("❗ CI relatives TMT : hydronéphrose, CIS diffus, mauvaise capacité vésicale, tumeur non résécable.")
        res["notes"].append("🔁 Cystectomie de rattrapage si échec/progression ou récidive MIBC.")

    # Cystectomie
    res["traitement"].extend([
        "🔴 **Cystectomie radicale avec curage ganglionnaire étendu** (si pas de TMT) :",
        "• Dérivation : conduit iléal / néovessie orthotopique (si urètre indemne & bonne fonction rénale/hépatique).",
    ])

    # Adjuvant
    if post_op_high_risk or (not neo_adjuvant_fait):
        res["traitement"].append("🟠 **Adjuvant à discuter** :")
        if cis_eligible and (not neo_adjuvant_fait) and post_op_high_risk:
            res["traitement"].append("• Chimiothérapie adjuvante (GC q21j × 4 ou dd-MVAC q14j × 4) si pT3–4 et/ou pN+.")
        res["traitement"].append("• Immunothérapie adjuvante (ex : Nivolumab 240 mg q2s ou 480 mg q4s, 1 an) si pT3–4/pN+ (selon AMM/PD-L1).")

    # Suivi cystectomie
    res["surveillance"].extend([
        "📅 **Suivi après cystectomie** :",
        "• Clinique + bio à 3–4 mois, puis /6 mois × 2 ans, puis annuel jusqu’à 5 ans.",
        "• TDM TAP : /6 mois × 2–3 ans, puis annuelle jusqu’à 5 ans.",
        "• Surveillance urétrale si marges urétrales/CIS trigonal (cytologie urétrale ± urétroscopie).",
        "• Dérivation : fonction rénale/électrolytes, B12 annuelle si néovessie; soins de stomie si conduit.",
    ])

    # Suivi TMT
    res["surveillance"].extend([
        "📅 **Suivi après TMT** :",
        "• Cystoscopie + cytologie : /3 mois × 2 ans, puis /6 mois jusqu’à 5 ans, puis annuel.",
        "• TDM TAP : annuelle (ou /6–12 mois selon risque).",
        "• Cystectomie de rattrapage si récidive MIBC/non-répondeur.",
    ])

    res["notes"].append("⚖️ Décision partagée en RCP (NAC vs TMT vs cystectomie directe).")
    res["notes"].append("🔬 Doses indicatives, à valider par oncologie/pharmacie (clairance, comorbidités).")
    return res

# =========================
# LOGIQUE CLINIQUE — Métastatique (AFU)
# =========================
def plan_meta(
    cis_eligible: bool,
    carbo_eligible: bool,
    platinum_naive: bool,
    pdl1_pos: bool,
    prior_platinum: bool,
    prior_cpi: bool,
    bone_mets: bool,
):
    """
    Retourne dict: { 'traitement': [...], 'suivi': [...], 'notes': [...] }
    1re ligne : cis-eligible -> GC / dd-MVAC ± avelumab maintenance;
                cis-ineligible -> Gem-Carbo (si éligible) ± avelumab
    Après platine : CPI (pembrolizumab) ; après platine + CPI : enfortumab / sacituzumab (selon disponibilité).
    """
    res = {"traitement": [], "suivi": [], "notes": []}

    if platinum_naive:
        res["traitement"].append("🧪 **1re ligne** :")
        if cis_eligible:
            res["traitement"].extend([
                "• Gemcitabine + Cisplatine (GC), q21j × 4–6 cycles :",
                "  - Gemcitabine 1 000 mg/m² J1 & J8, Cisplatine 70 mg/m² J1.",
                "• OU dd-MVAC (q14j × 4–6) avec G-CSF.",
                "• **Maintenance par Avelumab** 800 mg IV q2s jusqu’à progression/toxicité si réponse/SD après platine.",
            ])
        elif carbo_eligible:
            res["traitement"].extend([
                "• Gemcitabine + Carboplatine (AUC 4–5) q21j × 4–6 cycles (cisplatine inéligible).",
                "• **Maintenance par Avelumab** 800 mg IV q2s si réponse/SD après platine.",
            ])
        else:
            res["traitement"].append("• Patient inéligible au platine :")
            if pdl1_pos:
                res["traitement"].append("  - Immunothérapie seule (ex : Pembrolizumab 200 mg q3s ou 400 mg q6s) si PD-L1 positif.")
            else:
                res["traitement"].append("  - Immunothérapie seule à discuter en RCP (selon AMM/PD-L1/local).")
    else:
        res["traitement"].append("🧪 **Lignes ultérieures** :")
        if prior_platinum and (not prior_cpi):
            res["traitement"].append("• Immunothérapie : Pembrolizumab 200 mg q3s (ou 400 mg q6s).")
        if prior_platinum and prior_cpi:
            res["traitement"].append("• Enfortumab Vedotin 1,25 mg/kg J1/J8/J15 q28j (si disponible).")
            res["traitement"].append("• OU Sacituzumab Govitecan 10 mg/kg J1/J8 q21j (si disponible).")
        if (not prior_platinum):
            res["traitement"].append("• En cas d’absence de platine antérieur et si éligible : revenir à GC ou Gem-Carbo selon éligibilité.")

    if bone_mets:
        res["traitement"].extend([
            "🦴 **Os-protecteurs** :",
            "• Acide zolédronique 4 mg IV q4s (adapter à la fonction rénale) OU Dénosumab 120 mg SC q4s + Ca/VitD.",
        ])
        res["notes"].append("• Prévenir l’ostéonécrose de la mâchoire (bilan dentaire pré-thérapeutique).")

    res["suivi"].extend([
        "📅 **Suivi métastatique** :",
        "• Évaluation clinico-bio + toxicités avant chaque cycle.",
        "• Imagerie de réponse toutes les 8–12 semaines au début, puis selon évolution.",
        "• Soins de support (douleur, nutrition, thrombo-prophylaxie selon risque).",
    ])

    res["notes"].append("⚠️ Adapter à l’AMM locale/stock/essais cliniques. Décisions en RCP.")
    res["notes"].append("🔬 Doses indicatives, à valider avec l’oncologie médicale/pharmacie.")
    return res

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

        # Champs additionnels visibles seulement si pT1 + Haut grade
        cis_associe = False
        lvi = False
        urethre_prostatique = False
        formes_agressives = False
        if stade == "pT1" and grade == "Haut grade":
            st.markdown("#### Facteurs aggravants (pT1 haut grade) — cochez s’ils sont présents")
            c1, c2 = st.columns(2)
            with c1:
                cis_associe = st.checkbox("CIS associé")
                lvi = st.checkbox("Envahissement lymphovasculaire (LVI)")
            with c2:
                urethre_prostatique = st.checkbox("Atteinte de l’urètre prostatique")
                formes_agressives = st.checkbox("Formes anatomo-pathologiques agressives")

        submitted = st.form_submit_button("🔎 Générer la CAT")

    if submitted:
        risque = stratifier_tvnim(
            stade=stade,
            grade=grade,
            taille_mm=taille,
            nombre=nombre,
            cis_associe=cis_associe,
            lvi=lvi,
            urethre_prostatique=urethre_prostatique,
            formes_agressives=formes_agressives,
        )
        traitement, suivi, protocoles, notes_second_look = plan_tvnim(risque)

        # Tables
        donnees = [
            f"Stade : {stade}",
            f"Grade : {grade}",
            f"Taille max : {taille} mm",
            f"Nombre : {nombre}",
        ]
        if stade == "pT1" and grade == "Haut grade":
            flags = []
            if cis_associe: flags.append("CIS associé : OUI")
            if lvi: flags.append("LVI : OUI")
            if urethre_prostatique: flags.append("Atteinte urètre prostatique : OUI")
            if formes_agressives: flags.append("Formes anatomo-path. agressives : OUI")
            donnees += flags

        render_table("📊 Stratification", [f"Risque estimé : {risque.upper()}"], col_name="Résultat")
        render_table("🧾 Données saisies", donnees, col_name="Détail")
        render_table("💊 Traitement recommandé", traitement)
        if protocoles:
            render_table("📦 Protocoles détaillés", protocoles)
        render_table("📅 Modalités de suivi", suivi)
        render_table("📝 RTUV de second look — rappels", notes_second_look)

        show_protocol_image()

        # Export
        sections = {
            "Données": donnees,
            "Stratification": [f"Risque estimé : {risque.upper()}"],
            "Traitement recommandé": traitement + (["Détails de protocoles :"] + protocoles if protocoles else []),
            "Modalités de suivi": suivi,
            "Rappels second look": notes_second_look,
        }
        report_text = build_report_text("CAT TVNIM", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_TVNIM")

def render_tvim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVIM (tumeur infiltrant le muscle)")

    with st.form("tvim_form"):
        t_cat = st.selectbox("T (clinique)", ["T2", "T3", "T4a"])
        cN_pos = st.radio("Atteinte ganglionnaire clinique (cN+) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        metastases = st.radio("Métastases à distance ?", ["Non", "Oui"], horizontal=True) == "Oui"

        st.markdown("#### Éligibilités & contexte")
        cis_eligible = st.radio("Éligible Cisplatine (PS 0–1, DFG ≥50–60, pas de neuropathie/surdité majeures) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        t2_localise = st.radio("Tumeur T2 localisée (unique, mobile à la RTUV) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        hydron = st.radio("Hydronéphrose ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bonne_fct_v = st.radio("Bonne fonction vésicale ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_diffus = st.radio("CIS diffus ?", ["Non", "Oui"], horizontal=True) == "Oui"
        pdl1_pos = st.radio("PD-L1 positif (si disponible) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        post_op_high_risk = st.radio("pT3–4 et/ou pN+ attendu/après chirurgie ?", ["Non", "Oui"], horizontal=True) == "Oui"
        neo_adjuvant_fait = st.radio("Chimiothérapie néoadjuvante déjà réalisée ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – TVIM")

    if submitted:
        plan = plan_tvim(
            t_cat=t_cat, cN_pos=cN_pos, metastases=metastases, cis_eligible=cis_eligible,
            t2_localise=t2_localise, hydron=hydron, bonne_fct_v=bonne_fct_v,
            cis_diffus=cis_diffus, pdl1_pos=pdl1_pos, post_op_high_risk=post_op_high_risk,
            neo_adjuvant_fait=neo_adjuvant_fait
        )

        # Tables
        donnees = [
            f"T : {t_cat}",
            f"cN+ : {'Oui' if cN_pos else 'Non'}",
            f"Métastases : {'Oui' if metastases else 'Non'}",
            f"Éligible Cisplatine : {'Oui' if cis_eligible else 'Non'}",
            f"T2 localisée (TMT possible) : {'Oui' if t2_localise else 'Non'}",
            f"Hydronéphrose : {'Oui' if hydron else 'Non'}",
            f"Bonne fonction vésicale : {'Oui' if bonne_fct_v else 'Non'}",
            f"CIS diffus : {'Oui' if cis_diffus else 'Non'}",
            f"PD-L1 positif : {'Oui' if pdl1_pos else 'Non'}",
            f"pT3–4/pN+ attendu ou retrouvé : {'Oui' if post_op_high_risk else 'Non'}",
            f"NAC déjà faite : {'Oui' if neo_adjuvant_fait else 'Non'}",
        ]
        render_table("🧾 Données saisies", donnees, col_name="Détail")
        render_table("💊 Traitement recommandé", plan["traitement"])
        render_table("📅 Modalités de suivi", plan["surveillance"])
        if plan["notes"]:
            render_table("📝 Notes", plan["notes"])

        # Export
        sections = {
            "Données": donnees,
            "Traitement recommandé": plan["traitement"],
            "Modalités de suivi": plan["surveillance"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT TVIM", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_TVIM")

def render_vessie_meta_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 Tumeur de la vessie métastatique")

    with st.form("meta_form"):
        st.markdown("#### Contexte & éligibilité")
        platinum_naive = st.radio("Jamais traité par platine (1re ligne) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_eligible = st.radio("Éligible Cisplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        carbo_eligible = st.radio("Éligible Carboplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        pdl1_pos = st.radio("PD-L1 positif (si disponible) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_platinum = st.radio("A déjà reçu un platine ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_cpi = st.radio("A déjà reçu une immunothérapie (CPI) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bone_mets = st.radio("Métastases osseuses ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – Métastatique")

    if submitted:
        plan = plan_meta(
            cis_eligible=cis_eligible, carbo_eligible=carbo_eligible, platinum_naive=platinum_naive,
            pdl1_pos=pdl1_pos, prior_platinum=prior_platinum, prior_cpi=prior_cpi, bone_mets=bone_mets
        )

        # Tables
        donnees = [
            f"1re ligne (naïf platine) : {'Oui' if platinum_naive else 'Non'}",
            f"Éligible Cisplatine : {'Oui' if cis_eligible else 'Non'}",
            f"Éligible Carboplatine : {'Oui' if carbo_eligible else 'Non'}",
            f"PD-L1 positif : {'Oui' if pdl1_pos else 'Non'}",
            f"Platines reçus : {'Oui' if prior_platinum else 'Non'}",
            f"CPI reçu : {'Oui' if prior_cpi else 'Non'}",
            f"Métastases osseuses : {'Oui' if bone_mets else 'Non'}",
        ]
        render_table("🧾 Données saisies", donnees, col_name="Détail")
        render_table("💊 Traitement recommandé", plan["traitement"])
        render_table("📅 Modalités de suivi", plan["suivi"])
        if plan["notes"]:
            render_table("📝 Notes", plan["notes"])

        # Export
        sections = {
            "Données": donnees,
            "Traitement recommandé": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Métastatique", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_Vessie_Metastatique")

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
