# app.py — Urology Assistant AI (Accueil + Vessie -> TVNIM/TVIM/Métastatique)
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path
import html as ihtml  # pour échapper le HTML dans nos tableaux

# =========================
# CONFIG DE BASE + THEME CLAIR (VERT)
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

st.markdown("""
<style>
/* ----- Thème clair à dominance vert ----- */
:root, html, body, .stApp, .block-container { background:#ffffff !important; color:#111 !important; }
[data-testid="stHeader"], header { background:#ffffff !important; }

/* Titres & liens en vert foncé */
h1,h2,h3,h4,h5,h6 { color:#0B5D3B !important; }
a, a:visited { color:#0B5D3B !important; }

/* Texte markdown par défaut */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div {
  color:#111 !important;
}

/* Boutons */
.stButton > button {
  background:#0B5D3B !important; color:#fff !important; border-radius:10px; padding:0.6rem 1rem; border:none;
}
.stButton > button:hover { background:#0E744C !important; }

/* Sélecteurs & inputs */
div[data-baseweb="select"] > div,
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background:#fff !important; color:#111 !important;
  border:1px solid #e4efe8 !important;
}

/* Bandeau d'en-tête (gradient vert très clair) */
.header-green {
  padding:18px 22px; background:linear-gradient(90deg,#F6FBF7,#EAF6EE);
  border:1px solid #d8eadf; border-radius:12px; margin-bottom:18px;
}

/* Barre décorative sous les boutons de catégories (vert clair) */
.cat-bar {
  height:6px; background:#DFF3E6; border-radius:6px; margin-bottom:12px;
}

/* ====== TABLEAUX 2 COLONNES (HTML) ====== */
.kv-table { width:100%; border-collapse:separate; border-spacing:0; }
.kv-table thead th {
  background:#ECF7F0; color:#0B5D3B; font-weight:700; text-align:left;
  border-bottom:1px solid #dfece5; padding:10px 12px;
}
.kv-table tbody td {
  background:#ffffff; color:#111; padding:10px 12px; border-bottom:1px solid #f0f5f2;
}
.kv-table tbody tr:last-child td { border-bottom:none; }
.kv-table td:first-child { width:38%; }
.kv-table td strong { color:#0B5D3B; }

/* Espacement entre sections */
.section-block { margin-top: 0.6rem; margin-bottom: 1.2rem; }
</style>
""", unsafe_allow_html=True)

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

# Couleur décorative (vert clair) pour les barres sous chaque bouton
PALETTE = {m: "#DFF3E6" for m in MODULES}

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
        st.markdown(f"<div class='cat-bar' style='background:{color}'></div>", unsafe_allow_html=True)
        if clicked:
            go_module(label)

def top_header():
    st.markdown(
        f"<div class='header-green'><h1 style='margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1></div>",
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
# TABLE HELPERS (HTML, 2 colonnes, pas d'index)
# =========================
def esc(x: str) -> str:
    return ihtml.escape(str(x))

def render_kv_table(title: str, pairs: list[tuple[str, str]], col1: str = "Élément", col2: str = "Détail"):
    """Affiche un tableau 2 colonnes (titre en gras, explication)."""
    if not pairs:
        return
    st.markdown(f"### {esc(title)}")
    html = [f"<div class='section-block'><table class='kv-table'><thead><tr><th>{esc(col1)}</th><th>{esc(col2)}</th></tr></thead><tbody>"]
    for k, v in pairs:
        html.append(f"<tr><td><strong>{esc(k)}</strong></td><td>{esc(v)}</td></tr>")
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)

def split_line_to_pair(s: str) -> tuple[str, str]:
    """
    Si la ligne contient “:”, on sépare avant/après pour faire (titre, détail).
    Sinon, on met un point médian en titre et la phrase en détail.
    """
    s = s.strip("• ").strip()
    if ":" in s:
        a, b = s.split(":", 1)
        return a.strip(), b.strip()
    return "•", s

def list_to_pairs(lines: list[str]) -> list[tuple[str, str]]:
    return [split_line_to_pair(x) for x in lines]

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
    - Faible : pTa bas grade, <3 cm, unifocale
    - Intermédiaire : pTa bas grade (sans critères haut/très haut)
    - Haut : pT1 OU haut grade
    - Très haut : pT1 haut grade + (≥1 facteur aggravant)
                  (taille >3 cm, multifocalité/papillomatose, CIS associé, LVI,
                   atteinte urètre prostatique, formes anatomo-path. agressives)
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
            "OU : Épirubicine 50 mg (40–50 mL).",
            "OU : Gemcitabine 1 g (50 mL).",
        ],
        "CHIMIO_EV": [
            "Chimiothérapie endovésicale — Induction hebdomadaire 6–8 :",
            "• MMC 40 mg / 40 mL, 1×/semaine ×6–8.",
            "• Épirubicine 50 mg / 40–50 mL, 1×/semaine ×6–8.",
            "• Gemcitabine 1 g / 50 mL, 1×/semaine ×6–8.",
            "Entretien (option) : 1 instillation mensuelle ×9 (mois 4→12).",
        ],
        "BCG_12M": [
            "BCG — maintien 12 mois (risque intermédiaire) :",
            "Induction : 6 instillations hebdomadaires (semaines 1–6).",
            "Entretien : 3 instillations aux mois 3, 6 et 12 (3×3).",
            "Dose : flacon complet, rétention ~2 h si toléré.",
        ],
        "BCG_36M": [
            "BCG — maintien 36 mois (haut / très haut) :",
            "Induction : 6 instillations hebdomadaires (semaines 1–6).",
            "Entretien : 3 instillations à M3, M6, M12, puis /6 mois jusqu’à M36.",
            "Dose : flacon complet, rétention ~2 h si toléré.",
        ],
        "RCP_CYSTECTOMIE": [
            "Très haut risque :",
            "Discussion RCP pour cystectomie précoce + curage étendu.",
        ],
    }

    if risque == "faible":
        traitement = [
            "RTUV complète et profonde : mention du détrusor au CR.",
            *PROTO["IPOP"],
            "Aucun traitement d’entretien requis.",
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
            "Alternative : BCG (induction 6) + entretien 12 mois selon profil.",
        ]
        suivi = [
            "Cystoscopie : 3e et 6e mois, puis /6 mois pendant 2 ans, puis 1×/an (≥10 ans).",
            "Cytologie : systématique.",
            "Uro-TDM : non systématique.",
        ]
        protocoles = [*PROTO["BCG_12M"]]
    elif risque == "haut":
        traitement = [
            "RTUV complète + second look si pT1 ou muscle absent.",
            *PROTO["BCG_36M"],
            "Si CI/échec BCG : chimio EV (MMC/gemcitabine ± docétaxel).",
        ]
        suivi = [
            "Cystoscopie : /3 mois × 2 ans, puis /6 mois jusqu’à 5 ans, puis 1×/an à vie.",
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
            "Cystoscopie : /3 mois × 2 ans, puis /6 mois jusqu’à 5 ans, puis 1×/an à vie.",
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
    res = {"traitement": [], "surveillance": [], "notes": []}

    if metastases:
        res["traitement"].append("Maladie métastatique : se référer au module « Vessie: Métastatique » (1re/2e ligne).")
        return res

    # Néoadjuvant
    if cis_eligible:
        res["traitement"] += [
            "Chimiothérapie néoadjuvante (NAC) avant cystectomie :",
            "Gemcitabine + Cisplatine (GC), q21j × 4 cycles : Gemcitabine 1 000 mg/m² J1 & J8, Cisplatine 70 mg/m² J1.",
            "OU : dd-MVAC (q14j × 4) avec G-CSF : MTX 30 mg/m² J1, VBL 3 mg/m² J2, DOX 30 mg/m² J2, CDDP 70 mg/m² J2.",
        ]
    else:
        res["traitement"].append("Non éligible cisplatine : NAC non standard.")

    # Option TMT
    if t2_localise and (not hydron) and bonne_fct_v and (not cis_diffus):
        res["traitement"] += [
            "Option conservatrice (TMT) si patient informé :",
            "RTUV maximale (résection complète) + radiochimiothérapie concomitante.",
            "Radiothérapie vésicale 64–66 Gy (ex : 55 Gy/20 fx ou 64 Gy/32 fx).",
            "Radiosensibilisation : 5-FU 500 mg/m² J1–5 & J16–20 + MMC 12 mg/m² J1, OU Cisplatine hebdo 30–40 mg/m².",
        ]
        res["notes"] += [
            "CI relatives TMT : hydronéphrose, CIS diffus, mauvaise capacité vésicale, tumeur non résécable.",
            "Cystectomie de rattrapage si échec/progression.",
        ]

    # Cystectomie
    res["traitement"] += [
        "Cystectomie radicale + curage ganglionnaire étendu (si pas de TMT) :",
        "Dérivation : conduit iléal / néovessie orthotopique (urètre indemne, bonne fonction rénale/hépatique).",
    ]

    # Adjuvant
    if post_op_high_risk or (not neo_adjuvant_fait):
        res["traitement"].append("Adjuvant à discuter :")
        if cis_eligible and (not neo_adjuvant_fait) and post_op_high_risk:
            res["traitement"].append("Chimiothérapie adjuvante (GC q21j × 4 ou dd-MVAC q14j × 4) si pT3–4/pN+.")
        res["traitement"].append("Immunothérapie adjuvante : Nivolumab 240 mg q2s ou 480 mg q4s, 1 an (selon AMM/PD-L1).")

    # Suivi
    res["surveillance"] += [
        "Après cystectomie : Clinique + bio à 3–4 mois, puis /6 mois × 2 ans, puis annuel jusqu’à 5 ans.",
        "Après cystectomie : TDM TAP /6 mois × 2–3 ans, puis annuelle jusqu’à 5 ans.",
        "Surveillance urètre si marges urétrales/CIS trigonal (cytologie ± urétroscopie).",
        "Dérivation : fonction rénale/électrolytes; B12 annuelle si néovessie; soins de stomie si conduit.",
        "Après TMT : Cystoscopie + cytologie /3 mois × 2 ans, puis /6 mois jusqu’à 5 ans, puis annuel.",
        "Après TMT : TDM TAP annuelle (ou /6–12 mois selon risque).",
        "Cystectomie de rattrapage si récidive MIBC/non-répondeur.",
    ]

    res["notes"] += [
        "Décision partagée en RCP (NAC vs TMT vs cystectomie).",
        "Doses indicatives à valider par oncologie/pharmacie (clairance, comorbidités).",
    ]
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
    res = {"traitement": [], "suivi": [], "notes": []}

    if platinum_naive:
        if cis_eligible:
            res["traitement"] += [
                "1re ligne : GC q21j × 4–6 (Gemcitabine 1 000 mg/m² J1 & J8 + Cisplatine 70 mg/m² J1).",
                "OU : dd-MVAC q14j × 4–6 avec G-CSF.",
                "Maintenance Avelumab 800 mg IV q2s si réponse/SD après platine.",
            ]
        elif carbo_eligible:
            res["traitement"] += [
                "1re ligne : Gemcitabine + Carboplatine (AUC 4–5) q21j × 4–6.",
                "Maintenance Avelumab 800 mg IV q2s si réponse/SD après platine.",
            ]
        else:
            if pdl1_pos:
                res["traitement"].append("Inéligible platine : Pembrolizumab 200 mg q3s (ou 400 mg q6s) si PD-L1 positif.")
            else:
                res["traitement"].append("Inéligible platine : immunothérapie seule à discuter (AMM/PD-L1/local).")
    else:
        if prior_platinum and (not prior_cpi):
            res["traitement"].append("Après platine : Pembrolizumab 200 mg q3s (ou 400 mg q6s).")
        if prior_platinum and prior_cpi:
            res["traitement"] += [
                "Après platine + CPI : Enfortumab Vedotin 1,25 mg/kg J1/J8/J15 q28j (si dispo).",
                "OU : Sacituzumab Govitecan 10 mg/kg J1/J8 q21j (si dispo).",
            ]
        if (not prior_platinum):
            res["traitement"].append("Jamais exposé au platine : envisager GC ou Gem-Carbo selon éligibilité.")

    if bone_mets:
        res["traitement"] += [
            "Os-protecteurs : Acide zolédronique 4 mg IV q4s (adapter à DFG) OU Dénosumab 120 mg SC q4s + Ca/VitD.",
        ]
        res["notes"].append("Prévenir l’ostéonécrose mandibulaire (bilan dentaire).")

    res["suivi"] += [
        "Évaluation clinico-bio + toxicités avant chaque cycle.",
        "Imagerie de réponse toutes les 8–12 semaines au début, puis selon évolution.",
        "Soins de support (douleur, nutrition, thrombo-prophylaxie selon risque).",
    ]

    res["notes"] += [
        "Adapter à l’AMM locale/essais/stock. Décisions en RCP.",
        "Doses indicatives à valider avec oncologie/pharmacie.",
    ]
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

        # Facteurs aggravants visibles seulement si pT1 + Haut grade
        cis_associe = lvi = urethre_prostatique = formes_agressives = False
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
            stade=stade, grade=grade, taille_mm=taille, nombre=nombre,
            cis_associe=cis_associe, lvi=lvi, urethre_prostatique=urethre_prostatique,
            formes_agressives=formes_agressives,
        )
        traitement, suivi, protocoles, notes_second_look = plan_tvnim(risque)

        # Données (paires)
        donnees_pairs = [
            ("Stade", stade),
            ("Grade", grade),
            ("Taille maximale", f"{taille} mm"),
            ("Nombre", nombre),
        ]
        if stade == "pT1" and grade == "Haut grade":
            if cis_associe: donnees_pairs.append(("CIS associé", "Oui"))
            if lvi: donnees_pairs.append(("LVI", "Oui"))
            if urethre_prostatique: donnees_pairs.append(("Atteinte urètre prostatique", "Oui"))
            if formes_agressives: donnees_pairs.append(("Formes anatomo-path. agressives", "Oui"))

        # Rendu des tableaux
        render_kv_table("📊 Stratification", [("Risque estimé", risque.upper())], "Élément", "Résultat")
        render_kv_table("🧾 Données saisies", donnees_pairs)
        render_kv_table("💊 Traitement recommandé", list_to_pairs(traitement))
        if protocoles:
            render_kv_table("📦 Protocoles détaillés", list_to_pairs(protocoles))
        render_kv_table("📅 Modalités de suivi", list_to_pairs(suivi))
        render_kv_table("📝 RTUV de second look — rappels", list_to_pairs(notes_second_look))

        show_protocol_image()

        # Export (texte)
        sections = {
            "Données": [f"{k}: {v}" for k, v in donnees_pairs],
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

        donnees_pairs = [
            ("T", t_cat),
            ("cN+", "Oui" if cN_pos else "Non"),
            ("Métastases", "Oui" if metastases else "Non"),
            ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"),
            ("T2 localisée (TMT possible)", "Oui" if t2_localise else "Non"),
            ("Hydronéphrose", "Oui" if hydron else "Non"),
            ("Bonne fonction vésicale", "Oui" if bonne_fct_v else "Non"),
            ("CIS diffus", "Oui" if cis_diffus else "Non"),
            ("PD-L1 positif", "Oui" if pdl1_pos else "Non"),
            ("pT3–4/pN+ attendu/identifié", "Oui" if post_op_high_risk else "Non"),
            ("NAC déjà faite", "Oui" if neo_adjuvant_fait else "Non"),
        ]

        render_kv_table("🧾 Données saisies", donnees_pairs)
        render_kv_table("💊 Traitement recommandé", list_to_pairs(plan["traitement"]))
        render_kv_table("📅 Modalités de suivi", list_to_pairs(plan["surveillance"]))
        if plan["notes"]:
            render_kv_table("📝 Notes", list_to_pairs(plan["notes"]))

        sections = {
            "Données": [f"{k}: {v}" for k, v in donnees_pairs],
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

        donnees_pairs = [
            ("1re ligne (naïf platine)", "Oui" if platinum_naive else "Non"),
            ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"),
            ("Éligible Carboplatine", "Oui" if carbo_eligible else "Non"),
            ("PD-L1 positif", "Oui" if pdl1_pos else "Non"),
            ("Platines reçus", "Oui" if prior_platinum else "Non"),
            ("CPI reçu", "Oui" if prior_cpi else "Non"),
            ("Métastases osseuses", "Oui" if bone_mets else "Non"),
        ]

        render_kv_table("🧾 Données saisies", donnees_pairs)
        render_kv_table("💊 Traitement recommandé", list_to_pairs(plan["traitement"]))
        render_kv_table("📅 Modalités de suivi", list_to_pairs(plan["suivi"]))
        if plan["notes"]:
            render_kv_table("📝 Notes", list_to_pairs(plan["notes"]))

        sections = {
            "Données": [f"{k}: {v}" for k, v in donnees_pairs],
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
def render_home_wrapper():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)
    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")

page = st.session_state["page"]
if page == "Accueil":
    render_home_wrapper()
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
