# app.py — Urology Assistant AI (Accueil + Vessie TVNIM/TVIM/Métastatique + HBP)
# Version: 2025-09-02
# Notes:
# - Ce prototype vise à structurer la décision clinique (AFU/EAU 2024–2026 à vérifier localement).
# - Le module HBP a été modifié pour: (1) ne PAS proposer de médical si indication chirurgicale stricte
#   (échec médical OU complications OU lobe médian) ; (2) présenter toutes les options en "Option 1, 2, ...".

import base64
from datetime import datetime
from pathlib import Path
import html as ihtml
import io
import streamlit as st

# =========================
# CONFIG + THEME CLAIR (VERT)
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

APP_TITLE = "Urology Assistant AI"
APP_SUBTITLE = "Assistant intelligent pour la décision clinique — *démo, ne remplace pas les RBP officielles*"

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
    if not pairs:
        return
    st.markdown(f"### {esc(title)}")
    html = [
        f"<div class='section-block'><table class='kv-table'><thead><tr><th>{esc(col1)}</th><th>{esc(col2)}</th></tr></thead><tbody>",
    ]
    for k, v in pairs:
        html.append(f"<tr><td><strong>{esc(k)}</strong></td><td>{esc(v)}</td></tr>")
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ===== Export helpers (download_button) =====

def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title} (AFU/EAU 2024–2026 — à vérifier)")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr:
            continue
        lines.append(f"== {sec} ==")
        for x in arr:
            lines.append(f"• {x}")
        lines.append("")
    lines.append("Réfs : AFU/EAU — synthèse PROVISOIRE pour prototypage.")
    return "\n".join(lines)


def offer_exports(report_text: str, basename: str):
    bio = io.BytesIO(report_text.encode("utf-8"))
    st.download_button("📝 Télécharger le rapport .txt", data=bio, file_name=f"{basename}.txt")

    html = f"""<!doctype html><html lang='fr'><meta charset='utf-8'><title>{basename}</title><pre>{ihtml.escape(report_text)}</pre></html>"""
    st.download_button(
        "📄 Télécharger le rapport .html",
        data=html.encode("utf-8"),
        file_name=f"{basename}.html",
        mime="text/html",
    )


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
# LOGIQUE CLINIQUE — HBP (PSAD + CAT)
# =========================

def classer_ipss(ipss: int) -> str:
    if ipss <= 7:
        return "légers"
    if ipss <= 19:
        return "modérés"
    return "sévères"


def eval_suspicion_adk(psa_total: float, volume_ml: int, tr_suspect: bool):
    """
    TRIAGE CANCER (ADK) BASÉ SUR PSAD UNIQUEMENT (PSA 4–10) + TR.
    Retourne (suspect_adk: bool, explications: list[str], psad: float|None).
    Règles: 
      - TR suspect → ADK
      - PSA ≥ 10 → ADK
      - 4 ≤ PSA < 10 → PSAD = PSA/volume ; si PSAD > 0,15 → ADK ; sinon HBP
      - PSA < 4 → HBP (si TR non suspect)
    """
    exp = []
    psad = None

    if tr_suspect:
        exp.append("TR suspect → orientation cancer de la prostate.")
        return True, exp, psad

    if psa_total >= 10.0:
        exp.append("PSA ≥ 10 ng/mL → orientation cancer de la prostate.")
        return True, exp, psad

    if psa_total >= 4.0:
        if volume_ml > 0:
            psad = psa_total / float(volume_ml)
            exp.append(f"Densité PSA (PSAD) = {psad:.2f}.")
            if psad > 0.15:
                exp.append("PSAD > 0,15 → critère suspect.")
                return True, exp, psad
            else:
                exp.append("PSAD ≤ 0,15 → on poursuit l’analyse HBP.")
        else:
            exp.append("Volume inconnu/0 → PSAD non calculable; prudence clinique.")

    return False, exp, psad


def plan_hbp(
    age: int,
    volume_ml: int,
    lobe_median: bool,
    ipss: int,
    psa_total: float,
    tr_suspect: bool,
    anticoag: bool,
    preservation_ejac: bool,
    ci_chirurgie: bool,
    refus_chir: bool,
    infections_recid: bool,
    retention: bool,
    calculs: bool,
    hematurie_recid: bool,
    ir_post_obstacle: bool,
    echec_medical: bool,   # ← NOUVEAU
):
    """Retourne dict {donnees, traitement, notes}
    Règles demandées :
      - *Indication chirurgicale stricte* (échec médical OU complications OU lobe médian)
        ⇒ **ne pas proposer** d'options médicales.
      - Présenter toutes les propositions sous forme "Option 1, Option 2, ...",
        avec étiquette "traitement médical" / "traitement chirurgical" / "alternative".
    """
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
        (
            "Complications",
            ", ".join([
                txt
                for ok, txt in [
                    (infections_recid, "IU récidivantes"),
                    (retention, "Rétention urinaire"),
                    (calculs, "Calculs vésicaux"),
                    (hematurie_recid, "Hématurie récidivante"),
                    (ir_post_obstacle, "Altération fonction rénale liée à l’obstacle"),
                ]
                if ok
            ])
            or "Aucune",
        ),
        ("Échec du traitement médical", "Oui" if echec_medical else "Non"),
    ]

    # 0) Triage ADK basé sur PSAD + TR
    suspect_adk, exp_adk, psad = eval_suspicion_adk(psa_total, volume_ml, tr_suspect)
    if psad is not None:
        donnees.append(("Densité PSA (PSAD)", f"{psad:.2f}"))

    if suspect_adk:
        traitement = [
            "Orientation ADK prostatique →",
            "→ IRM prostatique multiparamétrique.",
            "→ Biopsies prostatiques ciblées ± systématiques (selon IRM/PIRADS).",
            "→ Bilan d’extension selon risque (ex : PSMA PET-CT si disponible).",
            "→ Discussion en RCP uro-oncologie.",
        ]
        notes = exp_adk
        return {"donnees": donnees, "traitement": traitement, "notes": notes}

    # 1) Déterminer si indication chirurgicale stricte
    complications_presentes = any([infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle])
    indication_chir_stricte = echec_medical or lobe_median or complications_presentes

    options = []
    opt_idx = 1

    # 2) STRICT CHIR & chirurgie faisable → seulement options chirurgicales
    if indication_chir_stricte and not (ci_chirurgie or refus_chir):
        if 30 <= volume_ml <= 80 or lobe_median or (volume_ml < 30 and lobe_median):
            options.append(f"Option {opt_idx} : traitement chirurgical — RTUP (mono/bipolaire), standard 30–80 mL; privilégiée si lobe médian. → Bipolaire : meilleure hémostase, pas de TUR syndrome."); opt_idx += 1
        if volume_ml >= 60:
            options.append(f"Option {opt_idx} : traitement chirurgical — Énucléation endoscopique (HoLEP/ThuLEP/BipolEP), efficace pour ≥ 60–100+ mL; résultats durables, bonne hémostase."); opt_idx += 1
        if anticoag or (30 <= volume_ml <= 80):
            options.append(f"Option {opt_idx} : traitement chirurgical — PVP GreenLight, utile si risque hémorragique/anticoagulants; séjour/sondage courts."); opt_idx += 1
        if volume_ml < 30 and not lobe_median:
            options.append(f"Option {opt_idx} : traitement chirurgical — TUIP (incision cervico‑prostatique) si < 30 mL et **sans** lobe médian (meilleure préservation éjaculatoire)."); opt_idx += 1
        if volume_ml < 70 and not lobe_median and preservation_ejac:
            options.append(f"Option {opt_idx} : traitement chirurgical — Implants urétraux (UroLift) < 70 mL, **sans** lobe médian, objectif préservation éjaculation."); opt_idx += 1
        if volume_ml > 100:
            options.append(f"Option {opt_idx} : traitement chirurgical — Adénomectomie voie haute (ouverte/robot) pour très gros volumes ou si énucléation indisponible."); opt_idx += 1

    # 3) STRICT CHIR mais chirurgie impossible (CI/refus) → alternatives
    if indication_chir_stricte and (ci_chirurgie or refus_chir):
        if volume_ml > 80:
            options.append(f"Option {opt_idx} : alternative — Embolisation des artères prostatiques (discussion RCP) si CI/refus de chirurgie et gros volume."); opt_idx += 1
        options.append(f"Option {opt_idx} : alternative — Optimisation médicale et/ou sondages intermittents si besoin (dernier recours)."); opt_idx += 1

    # 4) PAS indication stricte → d’abord médical, puis chir (préférence partagée)
    if not indication_chir_stricte:
        options.append(f"Option {opt_idx} : traitement médical — Alpha‑bloquant (tamsulosine/silodosine) pour LUTS modérés/sévères."); opt_idx += 1
        options.append(f"Option {opt_idx} : traitement médical — Inhibiteur de la 5‑α‑réductase (finastéride/dutastéride) si volume ≥ 40 mL ou PSA ≥ 1,5 (effet 6–12 mois)."); opt_idx += 1
        options.append(f"Option {opt_idx} : traitement médical — Association alpha‑bloquant + 5‑ARI si symptômes importants ET gros volume."); opt_idx += 1
        options.append(f"Option {opt_idx} : traitement médical — Tadalafil 5 mg/j si LUTS + dysfonction érectile."); opt_idx += 1
        options.append(f"Option {opt_idx} : traitement médical — Antimuscarinique ou agoniste β3 si symptômes de stockage (si RPM non élevé)."); opt_idx += 1
        if ipss <= 7:
            options.append(f"Option {opt_idx} : mesures générales — Abstention surveillée + conseils hygiéno‑diététiques (symptômes légers)."); opt_idx += 1
        if ipss >= 8 and not (ci_chirurgie or refus_chir):
            if 30 <= volume_ml <= 80 or lobe_median:
                options.append(f"Option {opt_idx} : traitement chirurgical — RTUP (mono/bipolaire), standard 30–80 mL; privilégier si lobe médian."); opt_idx += 1
            if volume_ml >= 60:
                options.append(f"Option {opt_idx} : traitement chirurgical — Énucléation endoscopique (HoLEP/ThuLEP/BipolEP) pour volumes ≥ 60–100+ mL."); opt_idx += 1
            if anticoag or (30 <= volume_ml <= 80):
                options.append(f"Option {opt_idx} : traitement chirurgical — PVP GreenLight si risque hémorragique/anticoagulants."); opt_idx += 1
            if volume_ml < 30 and not lobe_median:
                options.append(f"Option {opt_idx} : traitement chirurgical — TUIP si < 30 mL et sans lobe médian."); opt_idx += 1
            if volume_ml < 70 and not lobe_median and preservation_ejac:
                options.append(f"Option {opt_idx} : traitement chirurgical — Implants urétraux (UroLift) si objectif préservation éjaculation."); opt_idx += 1
            if volume_ml > 100:
                options.append(f"Option {opt_idx} : traitement chirurgical — Adénomectomie voie haute (ouverte/robot) si très gros volumes."); opt_idx += 1

    # Notes
    notes = []
    if anticoag:
        notes.append("Anticoagulants/antiagrégants → privilégier PVP GreenLight/HoLEP (hémostase supérieure).")
    if lobe_median and volume_ml < 30:
        notes.append("Lobe médian + petit volume → préférer RTUP/énucléation plutôt que TUIP.")
    if preservation_ejac:
        notes.append("Préservation éjaculation : discuter risques éjaculatoires des alpha‑bloquants et des techniques chirurgicales.")

    return {"donnees": donnees, "traitement": options, "notes": notes}

# =========================
# LOGIQUE CLINIQUE — REIN (localisé, métastatique, biopsie)
# =========================

def plan_rein_local(
    cT: str,
    cN_pos: bool,
    size_cm: float,
    thrombus: str,  # "Aucun", "Veine rénale", "VCC infra-hépatique", "VCC supra-hépatique/atrium"
    rein_unique_ou_CKD: bool,
    tumeur_hilaire: bool,
    exophytique: bool,
    age: int,
    haut_risque_op: bool,
    biopsie_dispo: bool,
):
    """
    Retourne dict {donnees, traitement, suivi, notes} avec options numérotées.
    """
    donnees = [
        ("cT", cT),
        ("cN+", "Oui" if cN_pos else "Non"),
        ("Taille", f"{size_cm:.1f} cm"),
        ("Thrombus", thrombus),
        ("Rein unique/CKD", "Oui" if rein_unique_ou_CKD else "Non"),
        ("Tumeur hilaire/centrale", "Oui" if tumeur_hilaire else "Non"),
        ("Exophytique", "Oui" if exophytique else "Non"),
        ("Âge", f"{age} ans"),
        ("Haut risque opératoire", "Oui" if haut_risque_op else "Non"),
        ("Biopsie disponible", "Oui" if biopsie_dispo else "Non"),
    ]

    options = []
    idx = 1
    notes = []

    if not biopsie_dispo:
        notes.append("Biopsie à discuter si traitement focal/surveillance prévue, doute diagnostique, ou avant traitement systémique.")

    # Décision par stade (synthèse)
    if cT == "T1a":  # ≤ 4 cm
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle (standard)."); idx += 1
        if size_cm <= 4.0 and exophytique:
            options.append(f"Option {idx} : traitement focal — Cryoablation/RFA percutanée (≤3–4 cm, exophytique/postérieure, fragile)."); idx += 1
        options.append(f"Option {idx} : surveillance active — Imagerie à 3–6 mois puis 6–12 mois; déclencheurs = croissance rapide, symptômes, haut grade confirmé."); idx += 1
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale si NP non faisable (anatomie/hilaire) ou rein non fonctionnel."); idx += 1

    elif cT == "T1b":  # 4–7 cm
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle en centre expert (préserver la fonction rénale)."); idx += 1
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale si NP non faisable."); idx += 1
        else:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle (sélectionné) OU Néphrectomie totale selon complexité (hilaire/endophytique → plutôt NT)."); idx += 1
        options.append(f"Option {idx} : surveillance active — Uniquement si comorbidités majeures/inopérable (RCP)."); idx += 1

    elif cT in ("T2a", "T2b"):
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle *impérative* (centre expert) OU Néphrectomie totale si NP impossible."); idx += 1
        else:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale (standard)."); idx += 1
        options.append(f"Option {idx} : surveillance — seulement si inopérable/fragilité majeure (RCP, soins de support)."); idx += 1

    elif cT == "T3a":
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale avec exérèse graisse péri-rénale ± veine rénale (si envahie)."); idx += 1
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle *impérative* (centre expert) si anatomie favorable."); idx += 1

    elif cT in ("T3b", "T3c"):
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale + thrombectomie (niveau {thrombus}). Équipe vasculaire/cardiothoracique si VCC."); idx += 1
        options.append(f"Option {idx} : stratégie — Discussion RCP spécialisée (opérabilité vs traitement systémique d’emblée)."); idx += 1

    elif cT == "T4":
        options.append(f"Option {idx} : traitement chirurgical — Résection élargie si résécable (RCP de recours)."); idx += 1
        options.append(f"Option {idx} : stratégie — Traitement systémique d’emblée si non résécable."); idx += 1

    # Ganglions
    if cN_pos:
        notes.append("Curage ganglionnaire ciblé si adénopathies cliniquement envahies; curage étendu systématique non recommandé.")

    # Adjuvant
    notes.append("Adjuvant : pembrolizumab 12 mois à discuter chez ccRCC à haut risque (profils type KEYNOTE-564).")

    # Suivi post-traitement (plus complet)
    suivi = []
    if cT == "T1a" and not cN_pos:
        suivi += [
            "Consultation : 3–6 mois post-op, puis 12 mois, puis annuel jusqu’à 5 ans.",
            "Imagerie : TDM/IRM abdo ± TDM thorax à 12 mois puis annuel (adapter histologie/grade).",
            "Biologie : créat/DFG à chaque visite; PA; +/- Hb/Ca selon contexte.",
        ]
    elif cT in ("T1b", "T2a", "T2b") and not cN_pos:
        suivi += [
            "Consultation : tous les 6–12 mois pendant 3 ans, puis annuel jusqu’à 5 ans.",
            "Imagerie : TDM abdo + TDM thorax tous les 6–12 mois (3 ans), puis annuel.",
            "Biologie : créat/DFG, +/- Hb/Ca; adapter si rein unique/CKD.",
        ]
    else:  # T3/T4 ou N+
        suivi += [
            "Consultation : tous les 3–6 mois pendant 3 ans, puis 6–12 mois jusqu’à 5 ans.",
            "Imagerie : TDM TAP tous les 3–6 mois (3 ans), puis 6–12 mois.",
            "Biologie : créat/DFG, Hb, Ca; symptômes ciblés. IRM cérébrale si clinique.",
        ]

    return {"donnees": donnees, "traitement": options, "suivi": suivi, "notes": notes}


def calc_imdc(
    karnofsky_lt80: bool,
    time_to_systemic_le_12mo: bool,
    hb_basse: bool,
    calcium_haut: bool,
    neutro_hauts: bool,
    plaquettes_hautes: bool,
):
    """Heng/IMDC : 6 facteurs (KPS<80, délai<1 an, Hb basse, Ca haut, neutros hautes, plaquettes hautes)."""
    score = sum([karnofsky_lt80, time_to_systemic_le_12mo, hb_basse, calcium_haut, neutro_hauts, plaquettes_hautes])
    if score == 0:
        groupe = "Bon pronostic (0)"
    elif score in (1, 2):
        groupe = "Intermédiaire (1–2)"
    else:
        groupe = "Mauvais (≥3)"
    return score, groupe


def calc_mskcc(
    karnofsky_lt80: bool,
    time_to_systemic_le_12mo: bool,
    hb_basse: bool,
    calcium_haut: bool,
    ldh_haut: bool,
):
    """MSKCC/Motzer : 5 facteurs (KPS<80, délai<1 an, Hb basse, Ca haut, LDH élevé)."""
    score = sum([karnofsky_lt80, time_to_systemic_le_12mo, hb_basse, calcium_haut, ldh_haut])
    if score == 0:
        groupe = "Bon pronostic (0)"
    elif score in (1, 2):
        groupe = "Intermédiaire (1–2)"
    else:
        groupe = "Mauvais (≥3)"
    return score, groupe


def plan_rein_meta(
    histo: str,             # "ccRCC" ou "non-ccRCC"
    score: int,
    group: str,
    score_system_label: str,
    oligo: bool,
    bone: bool,
    brain: bool,
    liver: bool,
    io_contra: bool,
):
    """
    Retourne dict {donnees, stratification, traitement, suivi, notes}.
    Inclut la *néphrectomie de cytoréduction* comme **option** selon IMDC/MSKCC et charge tumorale.
    """
    donnees = [
        ("Histologie", histo),
        (f"{score_system_label} score", str(score)),
        (f"Groupe {score_system_label}", group),
        ("Oligométastatique", "Oui" if oligo else "Non"),
        ("Métastases osseuses", "Oui" if bone else "Non"),
        ("Cérébrales", "Oui" if brain else "Non"),
        ("Hépatiques", "Oui" if liver else "Non"),
        ("CI immunothérapie", "Oui" if io_contra else "Non"),
    ]

    options = []
    idx = 1
    notes = []

    # ——— Cytoréduction (en options, pas seulement "Notes") ———
    if "Bon" in group and oligo:
        options.append(f"Option {idx} : néphrectomie de cytoréduction **immédiate** (bon pronostic, tumeur rénale dominante, charge métastatique faible)."); idx += 1
    elif "Intermédiaire" in group or "Mauvais" in group:
        options.append(f"Option {idx} : néphrectomie de cytoréduction **différée** après réponse au traitement systémique (sélectionnés)."); idx += 1

    # ——— Traitements systémiques de 1re ligne ———
    if histo == "ccRCC":
        if "Bon" in group:
            if not io_contra:
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Axitinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : stratégie — Surveillance rapprochée (maladie indolente, faible charge)."); idx += 1
            options.append(f"Option {idx} : 1re ligne — TKI seul (Axitinib, Pazopanib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
        else:
            if not io_contra:
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Ipilimumab."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Axitinib."); idx += 1
            options.append(f"Option {idx} : 1re ligne — TKI seul (Cabozantinib, Axitinib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
    else:  # non-ccRCC (global)
        options.append(f"Option {idx} : 1re ligne — Cabozantinib (préférence papillaire)."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Sunitinib ou Pazopanib."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Lenvatinib + Everolimus (sélectionné, ex. chromophobe/indéterminé)."); idx += 1
        options.append(f"Option {idx} : chimiothérapie — Gemcitabine + (Cisplatine/Carboplatine) pour sous-types agressifs (collecting-duct/medullaire)."); idx += 1
        options.append(f"Option {idx} : stratégie — Essai clinique si disponible."); idx += 1

    # ——— Après progression (2e ligne+) ———
    if histo == "ccRCC":
        options.append(f"Option {idx} : 2e ligne — Cabozantinib."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Lenvatinib + Everolimus."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Tivozanib."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Belzutifan (si disponible)."); idx += 1
    else:
        options.append(f"Option {idx} : 2e ligne — Cabozantinib / Lenvatinib + Everolimus (selon tolérance/progression)."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Essai clinique fortement recommandé."); idx += 1

    # ——— Soins de support & sites spéciaux ———
    if oligo:
        notes.append("Maladie oligométastatique : à discuter métastasectomie et/ou radiothérapie stéréotaxique.")
    if bone:
        notes.append("Os : acide zolédronique ou denosumab + Ca/Vit D; radiothérapie antalgique si douloureux.")
    if brain:
        notes.append("Cerveau : stéréotaxie/chirurgie + stéroïdes selon symptômes; coordination neuro-oncologie.")

    # ——— Suivi métastatique (complet) ———
    suivi = [
        "Avant et pendant traitement : PA/poids, symptômes; NFS, créat/DFG, transaminases, phosphatases, Ca; TSH (IO/TKI).",
        "Protéinurie et TA à chaque visite sous TKI; ECG/risques CV si nécessaire.",
        "Imagerie de réévaluation : TDM TAP toutes 8–12 semaines les 6–9 premiers mois, puis espacer selon réponse/clinique.",
        "IRM cérébrale si symptômes ou lésions traitées (toutes 8–12 semaines au début).",
    ]

    return {
        "donnees": donnees,
        "stratification": [(score_system_label, f"{group} (score {score})")],
        "traitement": options,
        "suivi": suivi,
        "notes": notes,
    }


def plan_rein_biopsy(
    indication_systemique: bool,
    indication_ablation: bool,
    inoperable_haut_risque: bool,
    lesion_indet: bool,
    suspicion_lymphome_metastase_infection: bool,
    rein_unique_ou_ckd: bool,
    petite_masse_typique_et_chirurgie_prevue: bool,
    bosniak: str,  # "II", "IIF", "III", "IV", "Non applicable"
    troubles_coag_non_corriges: bool,
):
    """
    Retourne dict {donnees, conduite, suivi, notes} pour les indications de biopsie percutanée d'une masse rénale.
    """
    donnees = [
        ("Avant traitement systémique (métastatique)", "Oui" if indication_systemique else "Non"),
        ("Avant traitement focal (cryo/RFA) prévu", "Oui" if indication_ablation else "Non"),
        ("Patient inopérable/haut risque chirurgical", "Oui" if inoperable_haut_risque else "Non"),
        ("Lésion indéterminée en imagerie", "Oui" if lesion_indet else "Non"),
        ("Suspicion lymphome / métastase / infection", "Oui" if suspicion_lymphome_metastase_infection else "Non"),
        ("Rein unique / CKD significative", "Oui" if rein_unique_ou_ckd else "Non"),
        ("Petite masse typique et chirurgie déjà prévue", "Oui" if petite_masse_typique_et_chirurgie_prevue else "Non"),
        ("Bosniak (si kystique)", bosniak),
        ("Troubles de coagulation non corrigés", "Oui" if troubles_coag_non_corriges else "Non"),
    ]

    options = []
    idx = 1
    notes = []

    # Contre-indication immédiate
    if troubles_coag_non_corriges:
        options.append(f"Option {idx} : corriger les troubles de coagulation **avant** toute biopsie; sinon différer."); idx += 1

    # Indications fortes
    indications_fortes = any([
        indication_systemique,
        indication_ablation,
        inoperable_haut_risque,
        lesion_indet,
        suspicion_lymphome_metastase_infection,
        rein_unique_ou_ckd,
    ])

    # Situations où la biopsie est *souvent non nécessaire* d’emblée
    non_necessaire = petite_masse_typique_et_chirurgie_prevue and not indications_fortes

    # Bosniak
    if bosniak in ("III", "IV"):
        # faisabilité variable; informer sur rendement parfois limité en kystique
        notes.append("Kystique Bosniak III/IV : la biopsie peut avoir un rendement limité; décision RCP (biopsie vs chirurgie d’emblée).")

    if indications_fortes:
        options.append(f"Option {idx} : Biopsie rénale percutanée guidée (TDM/écho), 2–3 carottes, histo + IHC si besoin."); idx += 1
    elif not indications_fortes and not non_necessaire:
        options.append(f"Option {idx} : Discussion RCP — Biopsie **ou** surveillance/traitement selon préférences et risque."); idx += 1
    else:
        options.append(f"Option {idx} : Pas d’indication routinière à la biopsie si chirurgie partielle déjà prévue chez patient apte (petite masse solide typique)."); idx += 1

    # Suivi (selon conduite)
    suivi = [
        "Après biopsie : surveillance du point de ponction, contrôle Hb si risque saignement.",
        "Si surveillance active choisie : imagerie à 3–6 mois puis tous les 6–12 mois; re-biopsie si évolution atypique.",
        "Si ablation après biopsie : TDM/IRM à 3 mois, puis 6–12 mois les 2 premières années.",
    ]

    notes += [
        "CI relatives : infection cutanée au point de ponction, impossibilité de coopération/apnée, anticoagulation non interrompue.",
        "Informer sur rendements : meilleurs pour masses solides; plus limité pour kystiques complexes.",
    ]

    return {"donnees": donnees, "conduite": options, "suivi": suivi, "notes": notes}

# =========================
# LOGIQUE CLINIQUE — TVNIM (simplifiée pour prototypage)
# =========================

def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str,
                     cis_associe: bool, lvi: bool, urethre_prostatique: bool, formes_agressives: bool) -> str:
    """Retourne "faible", "intermédiaire" ou "élevé" (simplifié)."""
    if stade == "pT1" or cis_associe or lvi or urethre_prostatique or formes_agressives:
        return "élevé"
    multiple = (nombre != "Unique")
    if grade == "Bas grade" and (taille_mm < 30) and not multiple:
        return "faible"
    return "intermédiaire"


def plan_tvnim(risque: str):
    traitement, suivi, protocoles, notes = [], [], [], []
    if risque == "faible":
        traitement = [
            "RTUV complète.",
            "Instillation postopératoire précoce de chimio intravésicale (ex. MMC) si non contre-indiquée.",
        ]
        suivi = [
            "Cystoscopie à 3 mois, puis rythme allégé si négatif (ex : 9–12 mois, puis annuel).",
            "Cytologie selon contexte.",
        ]
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète.",
            "Induction intravésicale (BCG OU chimio) puis maintenance ~1 an (à adapter).",
        ]
        suivi = ["Cysto + cytologie à 3, 6, 12 mois, puis semestriel/annuel."]
        protocoles = ["BCG : induction (6 instillations) + maintenance (~1 an)."]
    else:  # élevé
        traitement = [
            "RTUV complète avec re‑résection (second look) si T1 haut grade.",
            "BCG : induction + maintenance prolongée (1–3 ans selon dispo/tolérance).",
            "Discuter cystectomie précoce si T1 haut grade avec facteurs défavorables.",
        ]
        suivi = [
            "Cysto + cytologie rapprochées (ex : 3/6/9/12 mois, puis trimestriel/semestre).",
            "Imagerie selon facteurs/symptômes.",
        ]
        protocoles = ["BCG : induction (6) + maintenance prolongée."]
        notes = ["Second look recommandé si T1 haut grade (2–6 semaines)."]

    notes_second_look = notes or [
        "Second look : à envisager si résection incomplète ou doute sur le stade."
    ]
    return traitement, suivi, protocoles, notes_second_look


# =========================
# LOGIQUE CLINIQUE — TVIM (simplifiée pour prototypage)
# =========================

def plan_tvim(t_cat: str, cN_pos: bool, metastases: bool, cis_eligible: bool, t2_localise: bool,
              hydron: bool, bonne_fct_v: bool, cis_diffus: bool, pdl1_pos: bool,
              post_op_high_risk: bool, neo_adjuvant_fait: bool):
    traitement, surveillance, notes = [], [], []

    if metastases:
        traitement = ["Maladie métastatique → voir module dédié."]
        return {"traitement": traitement, "surveillance": surveillance, "notes": notes}

    if cis_eligible and not neo_adjuvant_fait:
        traitement += [
            "Chimiothérapie néoadjuvante à base de cisplatine (MVAC dose-dense ou GemCis).",
            "→ Puis cystectomie radicale + curage ganglionnaire.",
        ]
    else:
        if t2_localise and bonne_fct_v and not cis_diffus and not hydron:
            traitement += [
                "Option tri‑modale (TMT) pour T2 sélectionné : RTUV maximale + chimioradiothérapie + surveillance.",
            ]
        traitement += ["Cystectomie radicale + curage ganglionnaire selon extension."]

    if post_op_high_risk:
        notes += [
            "Risque post‑op élevé (pT3–4/pN+) : discuter traitement adjuvant (p.ex. immunothérapie adjuvante).",
        ]

    surveillance = [
        "Suivi clinique, imagerie et biologie selon protocole (tous les 3–6 mois les 2 premières années).",
    ]

    return {"traitement": traitement, "surveillance": surveillance, "notes": notes}


# =========================
# LOGIQUE CLINIQUE — Vessie métastatique (simplifiée pour prototypage)
# =========================

def plan_meta(cis_eligible: bool, carbo_eligible: bool, platinum_naive: bool, pdl1_pos: bool,
              prior_platinum: bool, prior_cpi: bool, bone_mets: bool):
    traitement, suivi, notes = [], [], []

    if platinum_naive:
        traitement += [
            "1re ligne (naïf platine) : combinaison récente anticorps‑conjugué + immunothérapie (selon accès).",
            "Alternative : Gemcitabine + Cisplatine (ou Carboplatine si non éligible Cisplatine), puis maintenance IO si RC/PR/SD.",
        ]
    else:
        if prior_platinum and not prior_cpi:
            traitement += ["Après platine : immunothérapie (PD‑1/PD‑L1) si non déjà reçue."]
        elif prior_cpi:
            traitement += ["Après immunothérapie : envisager anticorps‑conjugué (Nectin‑4/Trop‑2) selon disponibilité."]

    if bone_mets:
        notes += [
            "Métastases osseuses : envisager traitement osseux (acide zolédronique/denosumab) + Ca/Vit D, prévention SDS.",
        ]

    suivi = ["Réévaluation toutes 6–8 semaines au début (clinique/imagerie/biologie)."]

    return {"traitement": traitement, "suivi": suivi, "notes": notes}


# =========================
# PAGES (UI)
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
    with c1:
        st.button("TVNIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVNIM"))
    with c2:
        st.button("TVIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVIM"))
    with c3:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Vessie: Métastatique"))


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
        donnees_pairs = [
            ("Stade", stade), ("Grade", grade), ("Taille maximale", f"{taille} mm"), ("Nombre", nombre)
        ]
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
def render_kidney_menu():
    btn_home_and_back()
    st.markdown("## Tumeur du rein")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("Non métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Non métastatique"))
    with c2:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Métastatique"))
    with c3:
        st.button("Indications de biopsie", use_container_width=True, on_click=lambda: go_module("Rein: Biopsie"))


def render_kidney_local_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur non métastatique")
    with st.form("kidney_local_form"):
        cT = st.selectbox("Stade cT (TNM 2017)", ["T1a", "T1b", "T2a", "T2b", "T3a", "T3b", "T3c", "T4"])
        cN_pos = st.radio("Adénopathies cliniques (cN+) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        size_cm = st.number_input("Taille max (cm)", min_value=0.5, max_value=25.0, value=3.0, step=0.1)
        thrombus = st.selectbox("Thrombus veineux", ["Aucun", "Veine rénale", "VCC infra-hépatique", "VCC supra-hépatique/atrium"])
        rein_unique_ou_CKD = st.radio("Rein unique ou CKD significative ?", ["Non", "Oui"], horizontal=True) == "Oui"
        tumeur_hilaire = st.radio("Tumeur hilaire/centrale ?", ["Non", "Oui"], horizontal=True) == "Oui"
        exophytique = st.radio("Tumeur exophytique ?", ["Oui", "Non"], horizontal=True) == "Oui"
        age = st.number_input("Âge (ans)", min_value=18, max_value=100, value=62)
        haut_risque_op = st.radio("Haut risque opératoire ?", ["Non", "Oui"], horizontal=True) == "Oui"
        biopsie_dispo = st.radio("Biopsie disponible ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – Rein non métastatique")

    if submitted:
        plan = plan_rein_local(
            cT, cN_pos, size_cm, thrombus, rein_unique_ou_CKD, tumeur_hilaire,
            exophytique, age, haut_risque_op, biopsie_dispo
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        st.markdown("### 💊 Traitement — Options numérotées")
        for x in plan["traitement"]:
            st.markdown("- " + x)
        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)
        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Traitement (options)": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Rein non métastatique", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Rein_Non_Metastatique")


def render_kidney_meta_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur métastatique")
    with st.form("kidney_meta_form"):
        histo = st.selectbox("Histologie présumée/confirmée", ["ccRCC", "non-ccRCC (papillaire/chromophobe/autre)"])
        risk_system = st.radio("Classification pronostique", ["IMDC (Heng)", "MSKCC (Motzer)"], horizontal=True)

        st.markdown("#### Variables communes")
        kps = st.slider("Karnofsky (%)", 50, 100, 90, step=10)
        karnofsky_lt80 = (kps < 80)
        time_le_12 = st.radio("Délai diagnostic → traitement systémique ≤ 12 mois ?", ["Non", "Oui"], horizontal=True) == "Oui"
        hb_basse = st.radio("Hb < LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
        ca_haut = st.radio("Calcium corrigé > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"

        if risk_system.startswith("IMDC"):
            st.markdown("#### Variables spécifiques IMDC (Heng)")
            neutro_hauts = st.radio("Neutrophiles > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            plaquettes_hautes = st.radio("Plaquettes > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            ldh_haut = False
        else:
            st.markdown("#### Variables spécifiques MSKCC (Motzer)")
            ldh_haut = st.radio("LDH > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            neutro_hauts = False
            plaquettes_hautes = False

        st.markdown("#### Charge tumorale & sites")
        oligo = st.radio("Oligométastatique (nombre limité, résécable/irradiable) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bone = st.radio("Métastases osseuses ?", ["Non", "Oui"], horizontal=True) == "Oui"
        brain = st.radio("Métastases cérébrales ?", ["Non", "Oui"], horizontal=True) == "Oui"
        liver = st.radio("Métastases hépatiques ?", ["Non", "Oui"], horizontal=True) == "Oui"
        io_contra = st.radio("Contre-indication à l’immunothérapie ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT – Rein métastatique")

    if submitted:
        if risk_system.startswith("IMDC"):
            score, group = calc_imdc(karnofsky_lt80, time_le_12, hb_basse, ca_haut, neutro_hauts, plaquettes_hautes)
            label = "IMDC (Heng)"
        else:
            score, group = calc_mskcc(karnofsky_lt80, time_le_12, hb_basse, ca_haut, ldh_haut)
            label = "MSKCC (Motzer)"

        plan = plan_rein_meta(
            "ccRCC" if "ccRCC" in histo else "non-ccRCC",
            score, group, label, oligo, bone, brain, liver, io_contra
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["stratification"], "Système", "Résultat")
        st.markdown("### 💊 Traitement — Options numérotées")
        for x in plan["traitement"]:
            st.markdown("- " + x)
        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Stratification": [f"{label}: {group} (score {score})"],
            "Traitement (options)": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Rein métastatique", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Rein_Metastatique")


def render_kidney_biopsy_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — Indications de biopsie percutanée")
    with st.form("kidney_biopsy_form"):
        indication_systemique = st.radio("Projet de traitement systémique (métastatique) nécessitant confirmation histo ?", ["Non", "Oui"], horizontal=True) == "Oui"
        indication_ablation = st.radio("Traitement focal (cryo/RFA) envisagé ?", ["Non", "Oui"], horizontal=True) == "Oui"
        inoperable_haut_risque = st.radio("Patient inopérable/haut risque chirurgical ?", ["Non", "Oui"], horizontal=True) == "Oui"
        lesion_indet = st.radio("Lésion indéterminée en imagerie (diagnostic incertain) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        suspicion_lymphome_metastase_infection = st.radio("Suspicion lymphome / métastase d’un primitif / infection ?", ["Non", "Oui"], horizontal=True) == "Oui"
        rein_unique_ou_ckd = st.radio("Rein unique ou CKD significative ?", ["Non", "Oui"], horizontal=True) == "Oui"
        petite_masse_typique_et_chirurgie_prevue = st.radio("Petite masse solide typique (T1) et chirurgie conservatrice déjà prévue chez patient apte ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bosniak = st.selectbox("Si lésion kystique : classification Bosniak", ["Non applicable", "II", "IIF", "III", "IV"])
        troubles_coag_non_corriges = st.radio("Troubles de coagulation non corrigés ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la conduite — Biopsie")
    if submitted:
        plan = plan_rein_biopsy(
            indication_systemique, indication_ablation, inoperable_haut_risque,
            lesion_indet, suspicion_lymphome_metastase_infection, rein_unique_ou_ckd,
            petite_masse_typique_et_chirurgie_prevue, bosniak, troubles_coag_non_corriges
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        st.markdown("### 🧭 Conduite proposée")
        for x in plan["conduite"]:
            st.markdown("- " + x)
        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Conduite": plan["conduite"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("Conduite — Biopsie rénale", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "Conduite_Biopsie_Renale")

def render_hbp_page():
    btn_home_and_back()
    st.header("🔷 Hypertrophie bénigne de la prostate (HBP) — triage PSAD + CAT détaillée")

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

        echec_medical = st.checkbox("Non amélioration sous traitement médical (échec)")

        submitted = st.form_submit_button("🔎 Générer la CAT – HBP")

    if submitted:
        plan = plan_hbp(
            age, volume, lobe_median, ipss, psa_total, tr_suspect, anticoag,
            preservation_ejac, ci_chirurgie, refus_chir, infections_recid,
            retention, calculs, hematurie_recid, ir_post_obstacle, echec_medical
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])

        st.markdown("### 💊 Conduite à tenir / Options (classées)")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Conduite à tenir / Options": plan["traitement"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT HBP (triage PSAD)", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_HBP")


# =========================
# ROUTING + FALLBACK
# =========================

def render_home_wrapper():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)
    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")


def render_generic(page_label: str):
    btn_home_and_back()
    st.header(page_label)
    st.info("Module en cours de construction.")


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
elif page == "Tumeur du rein":
    render_kidney_menu()
elif page == "Rein: Non métastatique":
    render_kidney_local_page()
elif page == "Rein: Métastatique":
    render_kidney_meta_page()
elif page == "Rein: Biopsie":
    render_kidney_biopsy_page()
elif page == "Hypertrophie bénigne de la prostate (HBP)":
    render_hbp_page()
else:
    render_generic(page)
