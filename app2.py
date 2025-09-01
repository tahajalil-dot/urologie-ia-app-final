# app.py — Urology Assistant AI (Accueil + Vessie -> TVNIM/TVIM/Métastatique + HBP refait)
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path
import html as ihtml

# =========================
# CONFIG + THEME CLAIR (VERT)
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

st.markdown("""
<style>
:root, html, body, .stApp, .block-container { background:#ffffff !important; color:#111 !important; }
[data-testid="stHeader"], header { background:#ffffff !important; }

/* Titres & liens */
h1,h2,h3,h4,h5,h6 { color:#0B5D3B !important; }
a, a:visited { color:#0B5D3B !important; }

/* Texte markdown par défaut */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div { color:#111 !important; }

/* Boutons */
.stButton > button {
  background:#0B5D3B !important; color:#fff !important; border-radius:10px; padding:0.6rem 1rem; border:none;
}
.stButton > button:hover { background:#0E744C !important; }

/* Inputs */
div[data-baseweb="select"] > div,
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background:#fff !important; color:#111 !important; border:1px solid #e4efe8 !important;
}

/* En-tête (gradient vert très clair) */
.header-green {
  padding:18px 22px; background:linear-gradient(90deg,#F6FBF7,#EAF6EE);
  border:1px solid #d8eadf; border-radius:12px; margin-bottom:18px;
}

/* Barre décorative sous les catégories */
.cat-bar { height:6px; background:#DFF3E6; border-radius:6px; margin-bottom:12px; }

/* Tableaux (HTML) pour Données & Stratification */
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
.section-block { margin-top: 0.6rem; margin-bottom: 1.2rem; }
</style>
""", unsafe_allow_html=True)

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique aligné AFU 2024–2026"

MODULES = [
    "Tumeur de la vessie",
    "Tumeurs des voies excrétrices",
    "Tumeur de la prostate",
    "Tumeur du rein",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase",
    "Infectiologie",
]
PALETTE = {m: "#DFF3E6" for m in MODULES}

if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

# =========================
# HELPERS UI
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

# ===== Tableaux (HTML 2 colonnes) — pour Données & Stratification =====
def esc(x: str) -> str:
    return ihtml.escape(str(x))

def render_kv_table(title, pairs, col1="Élément", col2="Détail"):
    if not pairs: return
    st.markdown(f"### {esc(title)}")
    html = [f"<div class='section-block'><table class='kv-table'><thead><tr><th>{esc(col1)}</th><th>{esc(col2)}</th></tr></thead><tbody>"]
    for k, v in pairs:
        html.append(f"<tr><td><strong>{esc(k)}</strong></td><td>{esc(v)}</td></tr>")
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ===== Export helpers =====
def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title} (AFU 2024–2026)")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr: continue
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
# IMAGE DES PROTOCOLES (facultatif)
# =========================
PROTO_URL = ""  # ← colle ici l’URL raw d’un schéma si tu veux l’afficher
CANDIDATE_PATHS = [
    Path(__file__).parent / "assets" / "protocoles_tvnim.png",
    Path(__file__).parent / "protocoles_tvnim.png",
]
def show_protocol_image():
    st.markdown("### 🖼️ Schéma visuel (optionnel)")
    if PROTO_URL.strip():
        try:
            st.image(PROTO_URL.strip(), use_container_width=True)
            return
        except Exception:
            st.warning("Échec du chargement via l’URL — on tente les fichiers locaux…")
    for p in CANDIDATE_PATHS:
        if p.exists():
            st.image(str(p), use_container_width=True)
            return
    up = st.file_uploader("📎 Importer une image (png/jpg) — optionnel", type=["png", "jpg", "jpeg"])
    if up is not None:
        st.image(up, use_container_width=True)

# =========================
# LOGIQUE CLINIQUE — VESSIE (TVNIM/TVIM/Métastatique)
# =========================
def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str,
                     cis_associe=False, lvi=False, urethre_prostatique=False, formes_agressives=False) -> str:
    aggravants = (taille_mm > 30) or (nombre != "Unique") or cis_associe or lvi or urethre_prostatique or formes_agressives
    if stade == "pT1" and grade == "Haut grade" and aggravants:
        return "très haut"
    if stade == "pT1" or grade == "Haut grade":
        return "haut"
    if stade == "pTa" and grade == "Bas grade" and taille_mm < 30 and nombre == "Unique":
        return "faible"
    return "intermédiaire"

def plan_tvnim(risque: str):
    notes_second_look = [
        "RTUV de second look → pT1 (réévaluation systématique).",
        "RTUV de second look → tumeur volumineuse et/ou multifocale (résection possiblement incomplète).",
        "RTUV de second look → muscle détrusor absent dans la pièce initiale.",
    ]
    PROTO = {
        "IPOP": [
            "Instillation postopératoire précoce (IPOP) → dans les 2 h si pas d’hématurie/perforation.",
            "→ Mitomycine C 40 mg/40 mL (instillation unique, rétention 1–2 h).",
            "→ ou Épirubicine 50 mg/40–50 mL.",
            "→ ou Gemcitabine 1 g/50 mL.",
        ],
        "CHIMIO_EV": [
            "Chimiothérapie endovésicale (induction hebdomadaire 6–8) →",
            "→ Mitomycine C 40 mg/40 mL, 1×/semaine ×6–8.",
            "→ Épirubicine 50 mg/40–50 mL, 1×/semaine ×6–8.",
            "→ Gemcitabine 1 g/50 mL, 1×/semaine ×6–8.",
            "Entretien (intermédiaire) → 1 instillation mensuelle ×9 (mois 4→12).",
        ],
        "BCG_12M": [
            "BCG (entretien 12 mois) →",
            "→ Induction 6 instillations hebdomadaires (semaines 1–6).",
            "→ Entretien aux mois 3, 6 et 12 (schéma 3×3).",
        ],
        "BCG_36M": [
            "BCG (entretien 36 mois) →",
            "→ Induction 6 instillations hebdomadaires (semaines 1–6).",
            "→ Entretien à M3, M6, M12, puis tous les 6 mois jusqu’à M36.",
        ],
        "RCP_CYSTECTOMIE": [
            "Très haut risque → discussion RCP pour cystectomie précoce + curage étendu.",
        ],
    }

    if risque == "faible":
        traitement = [
            "RTUV complète et profonde (détrusor présent au compte rendu).",
            *PROTO["IPOP"],
            "Pas d’entretien additionnel requis.",
        ]
        suivi = [
            "Cystoscopie → 3e et 12e mois, puis 1×/an pendant 5 ans.",
            "Cytologie urinaire → non systématique.",
            "Imagerie (uro-TDM/uro-IRM) → non systématique; à réaliser si signes d’appel.",
        ]
        protocoles = []
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète (second look si doute d’exérèse).",
            *PROTO["CHIMIO_EV"],
            "Alternative → BCG avec entretien 12 mois (selon profil/ressources).",
        ]
        suivi = [
            "Cystoscopie → 3e et 6e mois, puis /6 mois pendant 2 ans, puis 1×/an (≥10 ans).",
            "Cytologie urinaire → systématique.",
            "Imagerie (uro-TDM/uro-IRM) → à 12–24 mois ou si symptômes.",
        ]
        protocoles = [*PROTO["BCG_12M"]]
    elif risque == "haut":
        traitement = [
            "RTUV complète + second look si pT1 ou muscle absent.",
            "BCG endovésical avec entretien 36 mois.",
        ]
        suivi = [
            "Cystoscopie → /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie urinaire → systématique.",
            "Imagerie (TDM TAP ou uro-TDM) → annuelle recommandée.",
        ]
        protocoles = [*PROTO["BCG_36M"]]
    else:  # très haut
        traitement = [
            "RTUV complète (qualité maximale).",
            "BCG avec entretien 36 mois → OU cystectomie précoce selon RCP.",
            *PROTO["RCP_CYSTECTOMIE"],
        ]
        suivi = [
            "Cystoscopie → /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis 1×/an à vie.",
            "Cytologie urinaire → systématique.",
            "Imagerie (TDM TAP ou uro-TDM) → annuelle systématique.",
        ]
        protocoles = [*PROTO["BCG_36M"]]

    return traitement, suivi, protocoles, notes_second_look

def plan_tvim(t_cat: str, cN_pos: bool, metastases: bool, cis_eligible: bool,
              t2_localise: bool, hydron: bool, bonne_fct_v: bool, cis_diffus: bool,
              pdl1_pos: bool, post_op_high_risk: bool, neo_adjuvant_fait: bool):
    res = {"traitement": [], "surveillance": [], "notes": []}
    if metastases:
        res["traitement"].append("Maladie métastatique → utiliser le module « Vessie: Métastatique » (schémas 1re/2e ligne).")
        return res
    if cis_eligible:
        res["traitement"] += [
            "Chimiothérapie néoadjuvante (NAC) → avant cystectomie (si possible).",
            "→ Gemcitabine + Cisplatine (GC) q21j ×4 cycles.",
            "→ ou dd-MVAC q14j ×4 avec support G-CSF.",
        ]
    else:
        res["traitement"].append("Non éligible cisplatine → NAC non standard.")
    if t2_localise and (not hydron) and bonne_fct_v and (not cis_diffus):
        res["traitement"] += [
            "Option préservation vésicale (TMT) → décision partagée.",
            "→ RTUV maximale + radiothérapie + radiosensibilisation (5-FU + mitomycine C, ou cisplatine hebdomadaire).",
            "→ Cystectomie de rattrapage si échec/progression.",
        ]
        res["notes"] += ["CI relatives TMT → hydronéphrose, CIS diffus, mauvaise capacité vésicale, tumeur non résécable."]
    res["traitement"] += [
        "Cystectomie radicale + curage ganglionnaire étendu (si pas de TMT).",
        "→ Dérivation : conduit iléal / néovessie orthotopique (urètre indemne, bonne fonction rénale/hépatique).",
    ]
    if post_op_high_risk or (not neo_adjuvant_fait):
        res["traitement"].append("Adjuvant à discuter →")
        if cis_eligible and (not neo_adjuvant_fait) and post_op_high_risk:
            res["traitement"].append("→ Chimiothérapie adjuvante (GC q21j ×4 ou dd-MVAC q14j ×4) si pT3–4/pN+.")
        res["traitement"].append("→ Immunothérapie adjuvante (ex : nivolumab) selon AMM/PD-L1, environ 1 an.")
    res["surveillance"] += [
        "Après cystectomie → clinique + biologie à 3–4 mois, puis /6 mois ×2 ans, puis annuel jusqu’à 5 ans.",
        "Après cystectomie → TDM TAP /6 mois ×2–3 ans, puis annuelle jusqu’à 5 ans.",
        "Surveillance urètre → si marge urétrale/CIS trigonal (cytologie ± urétroscopie).",
        "Dérivation → fonction rénale/électrolytes; B12 annuelle si néovessie; soins de stomie si conduit.",
        "Après TMT → cystoscopie + cytologie /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis annuel.",
        "Après TMT → TDM TAP annuelle (ou /6–12 mois selon risque).",
    ]
    res["notes"] += ["Décision partagée en RCP (NAC vs TMT vs cystectomie)."]
    return res

def plan_meta(cis_eligible: bool, carbo_eligible: bool, platinum_naive: bool,
              pdl1_pos: bool, prior_platinum: bool, prior_cpi: bool, bone_mets: bool):
    res = {"traitement": [], "suivi": [], "notes": []}
    if platinum_naive:
        if cis_eligible:
            res["traitement"] += [
                "1re ligne → Gemcitabine + Cisplatine (GC) q21j ×4–6.",
                "→ ou dd-MVAC q14j ×4–6 avec G-CSF.",
                "→ Maintenance par avelumab si réponse/stabilisation après platine.",
            ]
        elif carbo_eligible:
            res["traitement"] += [
                "1re ligne → Gemcitabine + Carboplatine (AUC 4–5) q21j ×4–6.",
                "→ Maintenance par avelumab si réponse/stabilisation après platine.",
            ]
        else:
            if pdl1_pos:
                res["traitement"].append("Inéligible platine → immunothérapie seule (ex : pembrolizumab) si PD-L1 positif.")
            else:
                res["traitement"].append("Inéligible platine → immunothérapie seule à discuter (AMM/ressources).")
    else:
        if prior_platinum and (not prior_cpi):
            res["traitement"].append("Après platine → pembrolizumab.")
        if prior_platinum and prior_cpi:
            res["traitement"] += [
                "Après platine + CPI → enfortumab vedotin.",
                "→ ou sacituzumab govitecan (selon disponibilité).",
            ]
        if (not prior_platinum):
            res["traitement"].append("Jamais exposé au platine → envisager GC ou Gem-Carbo selon éligibilité.")
    if bone_mets:
        res["traitement"] += [
            "Atteinte osseuse → protection osseuse : acide zolédronique IV ou dénosumab SC + Ca/VitD.",
        ]
        res["notes"].append("Prévenir l’ostéonécrose mandibulaire (bilan dentaire).")
    res["suivi"] += [
        "Clinique/biologie/toxicités → avant chaque cycle.",
        "Imagerie de réponse → toutes les 8–12 semaines au début, puis selon évolution.",
        "Soins de support → douleur, nutrition, thrombo-prophylaxie selon risque.",
    ]
    return res

# =========================
# LOGIQUE CLINIQUE — HBP (refait)
# =========================
def classer_ipss(ipss: int) -> str:
    if ipss <= 7: return "légers"
    if ipss <= 19: return "modérés"
    return "sévères"

def eval_suspicion_adk(psa_total: float, psa_libre: float, volume_ml: int, tr_suspect: bool):
    """Retourne (suspect_adk: bool, explications: list[str], psad: float, ratio: float|None)."""
    exp = []
    psad = None
    ratio = None

    # Toucher rectal
    if tr_suspect:
        exp.append("TR suspect → orientation cancer de la prostate.")
        return True, exp, psad, ratio

    # PSA total
    if psa_total >= 10.0:
        exp.append("PSA ≥ 10 ng/mL → orientation cancer de la prostate.")
        return True, exp, psad, ratio

    # PSA < 10 → calculer densité et f/t
    if volume_ml > 0:
        psad = psa_total / float(volume_ml)  # ng/mL / mL
        exp.append(f"Densité PSA (PSAD) = {psad:.2f}.")
    if psa_total > 0 and psa_libre is not None and psa_libre >= 0:
        ratio = psa_libre / psa_total
        exp.append(f"Rapport PSA libre/total (f/t) = {ratio:.2f}.")

    # Cutoffs usuels
    flags = []
    if psad is not None and psad > 0.15:
        flags.append("PSAD > 0,15")
    if ratio is not None and ratio < 0.15:
        flags.append("f/t < 0,15")

    if flags:
        exp.append("Critères suspects → " + " & ".join(flags) + ".")
        return True, exp, psad, ratio

    exp.append("PSAD et/ou f/t dans les normes → on poursuit l’analyse HBP.")
    return False, exp, psad, ratio

def plan_hbp(age: int, volume_ml: int, lobe_median: bool, ipss: int, psa_total: float,
             tr_suspect: bool, anticoag: bool, preservation_ejac: bool,
             ci_chirurgie: bool, refus_chir: bool, infections_recid: bool,
             retention: bool, calculs: bool, hematurie_recid: bool, ir_post_obstacle: bool,
             psa_libre: float | None):
    """Retourne dict {donnees_pairs, traitement_list, notes_list} sans 'suivi' (retiré)."""
    donnees = [
        ("Âge", f"{age} ans"),
        ("Volume prostatique", f"{volume_ml} mL"),
        ("Lobe médian", "Oui" if lobe_median else "Non"),
        ("IPSS", f"{ipss} ({classer_ipss(ipss)})"),
        ("PSA total", f"{psa_total:.2f} ng/mL"),
        ("TR suspect", "Oui" if tr_suspect else "Non"),
        ("Anticoagulants/antiagrégants", "Oui" if anticoag else "Non"),
        ("Préservation éjaculation", "Oui" if preservation_ejac else "Non"),
        ("CI/refus chirurgie", "Oui" if (ci_chirurgie or refus_chir) else "Non"),
        ("Complications", ", ".join([txt for ok, txt in [
            (infections_recid, "IU récidivantes"),
            (retention, "Rétention urinaire"),
            (calculs, "Calculs vésicaux"),
            (hematurie_recid, "Hématurie récidivante"),
            (ir_post_obstacle, "Altération fonction rénale liée à l’obstacle"),
        ] if ok]) or "Aucune"),
    ]

    # 0) Triage cancer (ADK) d’abord
    suspect_adk, exp_adk, psad, ratio = eval_suspicion_adk(psa_total, psa_libre, volume_ml, tr_suspect)
    if psad is not None:
        donnees.append(("Densité PSA (PSAD)", f"{psad:.2f}"))
    if ratio is not None:
        donnees.append(("PSA libre/total (f/t)", f"{ratio:.2f}"))

    if suspect_adk:
        traitement = [
            "Orientation ADK prostatique →",
            "→ IRM prostatique multiparamétrique.",
            "→ Biopsies prostatiques ciblées ± systématiques (selon IRM/PIRADS).",
            "→ Bilan complémentaire selon risque (ex : PSMA PET-CT si disponible).",
            "→ Discussion en RCP uro-oncologie.",
        ]
        notes = exp_adk
        return {"donnees": donnees, "traitement": traitement, "notes": notes}

    # 1) HBP : règles et traitements (sans suivi)
    traitement = []
    notes = []

    # Symptômes légers (et pas de complication)
    if ipss <= 7 and not any([infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, lobe_median]):
        traitement += [
            "Symptômes légers → abstention surveillée + règles hygiéno-diététiques.",
            "→ Réduire caféine/alcool le soir, mictions régulières, gestion hydrique.",
        ]

    # Traitement médical (modérés/sévères ou gène importante)
    if ipss >= 8 and not any([retention, ir_post_obstacle]):
        traitement += [
            "Traitement médical →",
            "→ Alpha-bloquant (ex : tamsulosine/silodosine) si LUTS modérés/sévères (effet rapide).",
        ]
        # 5-ARI selon volume/PSA
        if volume_ml >= 40 or psa_total >= 1.5:
            traitement += [
                "→ ± Inhibiteur 5-α-réductase (finastéride/dutastéride) si prostate ≥ 40 mL ou PSA ≥ 1,5 (réduction volume/risque RA à long terme).",
                "→ ± Association alpha-bloquant + 5-ARI si symptômes importants ET gros volume.",
            ]
        # Options selon profil
        traitement += [
            "→ ± Tadalafil 5 mg/j si LUTS associés à dysfonction érectile.",
            "→ ± Antimuscarinique ou β3-agoniste si symptômes de stockage (si RPM non élevé).",
        ]
        if preservation_ejac:
            notes += ["Préservation éjaculation → attention aux troubles éjaculatoires possibles avec certains alpha-bloquants."]

    # Indications chirurgicales fortes
    indications_chir = any([infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, lobe_median])
    if indications_chir or (ipss >= 8 and not ci_chirurgie and not refus_chir):
        if ci_chirurgie or refus_chir:
            if volume_ml > 80:
                traitement += ["CI/refus de chirurgie avec gros volume → embolisation artères prostatiques (discussion RCP)."]
            else:
                traitement += ["CI/refus de chirurgie → optimisation médicale, sondages intermittents si besoin."]
        else:
            # Choix technique selon volume + lobe médian (ta consigne : lobe médian = indication chirurgicale)
            if volume_ml < 30:
                # Normalement TUIP si pas de lobe médian; mais ici lobe médian → éviter TUIP, préférer RTUP/énucléation
                if lobe_median:
                    traitement += [
                        "Petit volume avec lobe médian → privilégier RTUP bipolaire ou énucléation endoscopique (éviter TUIP).",
                    ]
                else:
                    traitement += [
                        "Volume < 30 mL (sans lobe médian) → TUIP (incision cervico-prostatique).",
                        "→ Avantages : geste court, peu de saignement, meilleure préservation éjaculatoire.",
                        "→ Inconvénients : risque de retraitement supérieur à RTUP.",
                    ]
            elif 30 <= volume_ml <= 80:
                bloc = []
                bloc.append("30–80 mL → RTUP mono/bipolaire (référence).")
                if anticoag:
                    bloc.append("→ Risque hémorragique/anticoagulants → PVP GreenLight (excellente hémostase).")
                bloc.append("→ Alternatives selon plateau/expérience : énucléation endoscopique (HoLEP/ThuLEP/BipolEP).")
                traitement += bloc
            else:  # >80 mL
                traitement += [
                    "> 80–100 mL → énucléation endoscopique (HoLEP/ThuLEP) à privilégier si disponible.",
                    "→ Si non disponible → adénomectomie voie haute (ouverte/robot assistée).",
                ]

            # Préservation éjaculation (fenêtre)
            if (volume_ml < 70) and (not lobe_median) and preservation_ejac:
                traitement += ["Objectif préservation éjaculation (< 70 mL, sans lobe médian) → implants urétraux (UroLift)."]

    # Notes additionnelles
    if anticoag:
        notes += ["Anticoagulants/antiagrégants → préférer GreenLight/HoLEP (hémostase supérieure)."]
    if lobe_median and volume_ml < 30:
        notes += ["Lobe médian présent avec petit volume → RTUP/énucléation préférables à TUIP."]

    return {"donnees": donnees, "traitement": traitement, "notes": notes}

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
        risque = stratifier_tvnim(stade, grade, taille, nombre, cis_associe, lvi, urethre_prostatique, formes_agressives)
        traitement, suivi, protocoles, notes_second_look = plan_tvnim(risque)
        donnees_pairs = [("Stade", stade), ("Grade", grade), ("Taille maximale", f"{taille} mm"), ("Nombre", nombre)]
        if stade == "pT1" and grade == "Haut grade":
            if cis_associe: donnees_pairs.append(("CIS associé", "Oui"))
            if lvi: donnees_pairs.append(("LVI", "Oui"))
            if urethre_prostatique: donnees_pairs.append(("Atteinte urètre prostatique", "Oui"))
            if formes_agressives: donnees_pairs.append(("Formes anatomo-path. agressives", "Oui"))
        render_kv_table("🧾 Données saisies", donnees_pairs)
        render_kv_table("📊 Stratification", [("Risque estimé", risque.upper())], "Élément", "Résultat")
        st.markdown("### 💊 Traitement recommandé")
        for t in traitement: st.markdown("- " + t)
        if protocoles:
            st.markdown("### 📦 Schémas BCG (sans dose)")
            for p in protocoles: st.markdown("- " + p)
        st.markdown("### 📅 Modalités de suivi")
        for s in suivi: st.markdown("- " + s)
        st.markdown("### 📝 RTUV de second look — rappels")
        for n in notes_second_look: st.markdown("- " + n)
        # show_protocol_image()  # optionnel
        sections = {
            "Données": [f"{k}: {v}" for k, v in donnees_pairs],
            "Stratification": [f"Risque estimé : {risque.upper()}"],
            "Traitement recommandé": traitement + (["Schémas BCG :"] + protocoles if protocoles else []),
            "Modalités de suivi": suivi,
            "Rappels second look": notes_second_look,
        }
        report_text = build_report_text("CAT TVNIM", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_TVNIM")

def render_tvim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVIM (tumeur infiltrant le muscle)")
    with st.form("tvim_form"):
        t_cat = st.selectbox("T (clinique)", ["T2", "T3", "T4a"])
        cN_pos = st.radio("Atteinte ganglionnaire clinique (cN+) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        metastases = st.radio("Métastases à distance ?", ["Non", "Oui"], horizontal=True) == "Oui"
        st.markdown("#### Éligibilités & contexte")
        cis_eligible = st.radio("Éligible Cisplatine (PS 0–1, DFG ≥50–60…)?", ["Oui", "Non"], horizontal=True) == "Oui"
        t2_localise = st.radio("Tumeur T2 localisée (unique, mobile) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        hydron = st.radio("Hydronéphrose ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bonne_fct_v = st.radio("Bonne fonction vésicale ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_diffus = st.radio("CIS diffus ?", ["Non", "Oui"], horizontal=True) == "Oui"
        pdl1_pos = st.radio("PD-L1 positif (si dispo) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        post_op_high_risk = st.radio("pT3–4 et/ou pN+ attendu/identifié ?", ["Non", "Oui"], horizontal=True) == "Oui"
        neo_adjuvant_fait = st.radio("Néoadjuvant déjà réalisé ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – TVIM")
    if submitted:
        plan = plan_tvim(t_cat, cN_pos, metastases, cis_eligible, t2_localise, hydron, bonne_fct_v, cis_diffus, pdl1_pos, post_op_high_risk, neo_adjuvant_fait)
        donnees_pairs = [
            ("T", t_cat), ("cN+", "Oui" if cN_pos else "Non"), ("Métastases", "Oui" if metastases else "Non"),
            ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"), ("T2 localisée (TMT possible)", "Oui" if t2_localise else "Non"),
            ("Hydronéphrose", "Oui" if hydron else "Non"), ("Bonne fonction vésicale", "Oui" if bonne_fct_v else "Non"),
            ("CIS diffus", "Oui" if cis_diffus else "Non"), ("PD-L1 positif", "Oui" if pdl1_pos else "Non"),
            ("pT3–4/pN+ attendu/identifié", "Oui" if post_op_high_risk else "Non"), ("NAC déjà faite", "Oui" if neo_adjuvant_fait else "Non"),
        ]
        render_kv_table("🧾 Données saisies", donnees_pairs)
        st.markdown("### 💊 Traitement recommandé");  [st.markdown("- " + x) for x in plan["traitement"]]
        st.markdown("### 📅 Modalités de suivi");      [st.markdown("- " + x) for x in plan["surveillance"]]
        if plan["notes"]:
            st.markdown("### 📝 Notes");              [st.markdown("- " + x) for x in plan["notes"]]
        sections = {"Données":[f"{k}: {v}" for k,v in donnees_pairs],"Traitement recommandé":plan["traitement"],"Modalités de suivi":plan["surveillance"],"Notes":plan["notes"]}
        report_text = build_report_text("CAT TVIM", sections); st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_TVIM")

def render_vessie_meta_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 Tumeur de la vessie métastatique")
    with st.form("meta_form"):
        st.markdown("#### Contexte & éligibilité")
        platinum_naive = st.radio("Jamais traité par platine (1re ligne) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_eligible = st.radio("Éligible Cisplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        carbo_eligible = st.radio("Éligible Carboplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        pdl1_pos = st.radio("PD-L1 positif (si dispo) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_platinum = st.radio("A déjà reçu un platine ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_cpi = st.radio("A déjà reçu une immunothérapie (CPI) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bone_mets = st.radio("Métastases osseuses ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – Métastatique")
    if submitted:
        plan = plan_meta(cis_eligible, carbo_eligible, platinum_naive, pdl1_pos, prior_platinum, prior_cpi, bone_mets)
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
        st.markdown("### 💊 Traitement recommandé"); [st.markdown("- " + x) for x in plan["traitement"]]
        st.markdown("### 📅 Modalités de suivi");     [st.markdown("- " + x) for x in plan["suivi"]]
        if plan["notes"]:
            st.markdown("### 📝 Notes");             [st.markdown("- " + x) for x in plan["notes"]]
        sections = {"Données":[f"{k}: {v}" for k,v in donnees_pairs],"Traitement recommandé":plan["traitement"],"Modalités de suivi":plan["suivi"],"Notes":plan["notes"]}
        report_text = build_report_text("CAT Vessie Métastatique", sections); st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Vessie_Metastatique")

# -------------------------
# HBP (UI)
# -------------------------
def render_hbp_page():
    btn_home_and_back()
    st.header("🔷 Hypertrophie bénigne de la prostate (HBP)")

    with st.form("hbp_form"):
        age = st.number_input("Âge", min_value=40, max_value=100, value=65)
        volume = st.number_input("Volume prostatique (mL)", min_value=10, max_value=250, value=45)
        lobe_median = st.radio("Lobe médian présent ?", ["Non", "Oui"], horizontal=True) == "Oui"
        ipss = st.slider("Score IPSS", 0, 35, 18)
        psa_total = st.number_input("PSA total (ng/mL)", min_value=0.0, step=0.1, value=1.6)
        tr_suspect = st.radio("Toucher rectal suspect ?", ["Non", "Oui"], horizontal=True) == "Oui"
        anticoag = st.radio("Anticoagulants/antiagrégants ?", ["Non", "Oui"], horizontal=True) == "Oui"
        preservation_ejac = st.radio("Souhaite préserver l’éjaculation ?", ["Non", "Oui"], horizontal=True) == "Oui"
        ci_chirurgie = st.radio("Contre-indication à la chirurgie ?", ["Non", "Oui"], horizontal=True) == "Oui"
        refus_chir = st.radio("Refus de chirurgie ?", ["Non", "Oui"], horizontal=True) == "Oui"

        st.markdown("#### Complications (cocher si présentes)")
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: infections_recid = st.checkbox("IU récidivantes")
        with c2: retention = st.checkbox("Rétention urinaire")
        with c3: calculs = st.checkbox("Calculs vésicaux")
        with c4: hematurie_recid = st.checkbox("Hématurie récidivante")
        with c5: ir_post_obstacle = st.checkbox("Altération fonction rénale")

        

        submitted = st.form_submit_button("🔎 Générer la CAT – HBP")

    if submitted:
        plan = plan_hbp(
            age, volume, lobe_median, ipss, psa_total, tr_suspect, anticoag, preservation_ejac,
            ci_chirurgie, refus_chir, infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])

        st.markdown("### 💊 Conduite à tenir / Options thérapeutiques")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Conduite à tenir / Options thérapeutiques": plan["traitement"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT HBP", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_HBP")

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
elif page == "Hypertrophie bénigne de la prostate (HBP)":
    render_hbp_page()
else:
    render_generic(page)
