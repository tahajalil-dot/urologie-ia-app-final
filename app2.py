# app.py — Urology Assistant AI (Accueil + Vessie + Rein + HBP)
# Version intégrée : 2025-09-02
# Modules inclus :
# - Vessie (TVNIM, TVIM, Métastatique)
# - Rein (Non métastatique, Métastatique — IMDC/Heng ou MSKCC/Motzer)
# - HBP (PSAD + Options numérotées)

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

st.markdown("""
<style>
:root, html, body, .stApp, .block-container { background:#ffffff !important; color:#111 !important; }
[data-testid="stHeader"], header { background:#ffffff !important; }

h1,h2,h3,h4,h5,h6 { color:#0B5D3B !important; }
a, a:visited { color:#0B5D3B !important; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div { color:#111 !important; }

.stButton > button {
  background:#0B5D3B !important; color:#fff !important; border-radius:10px; padding:0.6rem 1rem; border:none;
}
.stButton > button:hover { background:#0E744C !important; }

.header-green {
  padding:18px 22px; background:linear-gradient(90deg,#F6FBF7,#EAF6EE);
  border:1px solid #d8eadf; border-radius:12px; margin-bottom:18px;
}

.cat-bar { height:6px; background:#DFF3E6; border-radius:6px; margin-bottom:12px; }

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
    st.markdown(f"<div class='header-green'><h1 style='margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1></div>", unsafe_allow_html=True)

def btn_home_and_back(show_back: bool = False, back_label: str = "Tumeur de la vessie"):
    cols = st.columns([1, 3])
    with cols[0]:
        st.button("🏠 Accueil", on_click=go_home)
    if show_back:
        with cols[1]:
            st.button(f"⬅️ Retour : {back_label}", on_click=lambda: go_module(back_label))

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

def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title}")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr: continue
        lines.append(f"== {sec} ==")
        for x in arr:
            lines.append(f"• {x}")
        lines.append("")
    lines.append("Réfs : AFU/EAU — version simplifiée.")
    return "\n".join(lines)

def offer_exports(report_text: str, basename: str):
    bio = io.BytesIO(report_text.encode("utf-8"))
    st.download_button("📝 Télécharger .txt", data=bio, file_name=f"{basename}.txt")
    html = f"<!doctype html><html lang='fr'><meta charset='utf-8'><title>{basename}</title><pre>{ihtml.escape(report_text)}</pre></html>"
    st.download_button("📄 Télécharger .html", data=html.encode("utf-8"), file_name=f"{basename}.html", mime="text/html")

# =========================
# LOGIQUE CLINIQUE — Rein (localisé + métastatique)
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
    Renvoie dict {donnees, traitement (list), suivi (list), notes (list)} avec options numérotées.
    Logique synthétique (à adapter aux RBP locales).
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
        notes.append("Biopsie à discuter si traitement focal/surveillance prévue, doute diagnostique, ou avant systémique.")

    # Décision par stade clinique (TNM 2017)
    if cT == "T1a":  # ≤ 4 cm
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle (standard). Approche robot/LP/ouverte selon plateau."); idx += 1
        if size_cm <= 4.0 and exophytique:
            options.append(f"Option {idx} : traitement focal — Cryoablation ou RFA percutanée (≤3–4 cm, exophytique/postérieure, fragilité)."); idx += 1
        options.append(f"Option {idx} : surveillance active — Imagerie à 3–6 mois puis 6–12 mois; déclencheurs = croissance rapide/symptômes/haut grade confirmé."); idx += 1
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
        options.append(f"Option {idx} : surveillance — Seulement si inopérable/fragilité majeure (RCP, soins de support)."); idx += 1

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

    # Adénopathies
    if cN_pos:
        notes.append("Curage ganglionnaire ciblé si adénopathies cliniquement envahies; curage étendu systématique non recommandé.")

    # Adjuvant (info générale)
    notes.append("Adjuvant : pembrolizumab 12 mois à discuter chez ccRCC à haut risque (profils type KEYNOTE-564).")

    # Suivi post-traitement (simplifié par risque)
    suivi = []
    if cT == "T1a" and not cN_pos:
        suivi += [
            "Imagerie abdo ± thorax : à 12 mois, puis annuelle jusqu’à 5 ans (adapter selon histologie/grade).",
            "Fonction rénale : créat/DFG à chaque visite; PA, bilan métabolique."
        ]
    elif cT in ("T1b", "T2a", "T2b") and not cN_pos:
        suivi += [
            "Imagerie : tous les 6–12 mois pendant 3 ans, puis annuelle jusqu’à 5 ans.",
            "Biologie : créat/DFG, ± Hb/Ca selon contexte."
        ]
    else:  # T3/T4 ou N+
        suivi += [
            "Imagerie : tous les 3–6 mois pendant 3 ans, puis tous les 6–12 mois jusqu’à 5 ans.",
            "Biologie : créat/DFG, Hb, Ca; évaluer symptômes ciblés."
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
    """Heng/IMDC : 6 facteurs (KPS<80, délai<1 an, Hb basse, Ca haut, neutros hauts, plaquettes hautes)."""
    score = sum([
        karnofsky_lt80,
        time_to_systemic_le_12mo,
        hb_basse,
        calcium_haut,
        neutro_hauts,
        plaquettes_hautes,
    ])
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
    score = sum([
        karnofsky_lt80,
        time_to_systemic_le_12mo,
        hb_basse,
        calcium_haut,
        ldh_haut,
    ])
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
    Renvoie dict {donnees, stratification, traitement (list), suivi (list), notes (list)}.
    Enumère les options 1, 2, 3... selon pronostic et histologie (molécules sans doses).
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

    # Maladie oligométastatique
    if oligo:
        notes.append("Oligométastatique : envisager métastasectomie et/ou radiothérapie stéréotaxique sur sites sélectionnés.")

    # ccRCC vs non-ccRCC
    if histo == "ccRCC":
        if "Bon" in group:  # IMDC/MSKCC bon pronostic
            if not io_contra:
                options.append(f"Option {idx} : systémique — Pembrolizumab + Axitinib."); idx += 1
                options.append(f"Option {idx} : systémique — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : systémique — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : stratégie — Surveillance rapprochée (indolent, charge tumorale faible)."); idx += 1
            options.append(f"Option {idx} : systémique — TKI seul (Axitinib, Pazopanib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
        else:  # intermédiaire/mauvais
            if not io_contra:
                options.append(f"Option {idx} : systémique — Nivolumab + Ipilimumab."); idx += 1
                options.append(f"Option {idx} : systémique — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : systémique — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : systémique — Pembrolizumab + Axitinib."); idx += 1
            options.append(f"Option {idx} : systémique — TKI seul (Cabozantinib, Axitinib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
    else:
        # non-ccRCC (global)
        options.append(f"Option {idx} : systémique — Cabozantinib (préférence pour papillaire)."); idx += 1
        options.append(f"Option {idx} : systémique — Pembrolizumab + Lenvatinib."); idx += 1
        options.append(f"Option {idx} : systémique — Sunitinib ou Pazopanib."); idx += 1
        options.append(f"Option {idx} : systémique — Lenvatinib + Everolimus (sélectionné, ex. chromophobe/indéterminé)."); idx += 1
        options.append(f"Option {idx} : chimiothérapie — Gemcitabine + (Cisplatine/Carboplatine) pour sous-types agressifs (collecting-duct/medullaire)."); idx += 1
        options.append(f"Option {idx} : stratégie — Essai clinique si disponible."); idx += 1

    # Néphrectomie de cytoréduction (principes)
    notes.append("Néphrectomie de cytoréduction : immédiate (bon pronostic et tumeur rénale dominante), différée (intermédiaire/mauvais après réponse au systémique), ou de clôture si RC/PR majeure.")

    # Sites particuliers
    if bone:
        notes.append("Os : acide zolédronique ou denosumab + Ca/Vit D; radiothérapie antalgique si douloureux.")
    if brain:
        notes.append("Cerveau : stéréotaxie/chirurgie + stéroïdes selon symptômes; coordination neuro-oncologie.")

    # Suivi (métastatique)
    suivi = [
        "Bilan initial : TDM TAP ± cérébrale selon symptômes; biologie (fonction rénale/hépatique, Hb, Ca; TSH si IO/TKI).",
        "Réévaluation : imagerie toutes 8–12 semaines au début, puis adapter selon réponse/clinique.",
        "Toxicités : PA/protéinurie (TKI), TSH/lipase/transaminases (IO/TKI), et symptômes immuno (dermato, colite, pneumonite).",
    ]

    return {
        "donnees": donnees,
        "stratification": [(score_system_label, f"{group} (score {score})")],
        "traitement": options,
        "suivi": suivi,
        "notes": notes,
    }


# =========================
# PAGES (UI)
# =========================

def render_kidney_menu():
    btn_home_and_back()
    st.markdown("## Tumeur du rein")
    st.caption("Choisissez le sous-module")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Non métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Non métastatique"))
    with c2:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Métastatique"))


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

        # Variables communes
        st.markdown("#### Variables communes")
        kps = st.slider("Karnofsky (%)", 50, 100, 90, step=10)
        karnofsky_lt80 = (kps < 80)
        time_le_12 = st.radio("Délai diagnostic → traitement systémique ≤ 12 mois ?", ["Non", "Oui"], horizontal=True) == "Oui"
        hb_basse = st.radio("Hb < LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
        ca_haut = st.radio("Calcium corrigé > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"

        # Variables spécifiques
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

        # Sites et CI IO
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


# ... (toutes les fonctions render_xxx déjà intégrées : rein local, rein meta, hbp, vessie...)

# =========================
# ROUTING
# =========================

page = st.session_state["page"]
if page == "Accueil":
    render_home_wrapper()
elif page == "Tumeur de la vessie":
    render_vessie_menu()
elif page.startswith("Vessie:"):
    if page == "Vessie: TVNIM": render_tvnim_page()
    elif page == "Vessie: TVIM": render_tvim_page()
    elif page == "Vessie: Métastatique": render_vessie_meta_page()
elif page == "Tumeur du rein":
    render_kidney_menu()
elif page == "Rein: Non métastatique":
    render_kidney_local_page()
elif page == "Rein: Métastatique":
    render_kidney_meta_page()
elif page == "Hypertrophie bénigne de la prostate (HBP)":
    render_hbp_page()
else:
    render_generic(page)
