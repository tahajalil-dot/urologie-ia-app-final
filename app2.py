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
# LOGIQUE CLINIQUE — HBP (refait, PSAD uniquement)
# =========================
def classer_ipss(ipss: int) -> str:
    if ipss <= 7: return "légers"
    if ipss <= 19: return "modérés"
    return "sévères"

def eval_suspicion_adk(psa_total: float, volume_ml: int, tr_suspect: bool):
    """
    TRIAGE CANCER (ADK) BASÉ SUR PSAD UNIQUEMENT (PSA 4–10) + TR.
    Retourne (suspect_adk: bool, explications: list[str], psad: float|None).
    Règles:
      - TR suspect → ADK
      - PSA ≥ 10 → ADK
      - 4 ≤ PSA < 10 → calcul PSAD = PSA / volume (mL)
          * PSAD > 0,15 → ADK
          * PSAD ≤ 0,15 → OK HBP
      - PSA < 4 → OK HBP (sauf TR suspect)
    """
    exp = []
    psad = None

    # Toucher rectal
    if tr_suspect:
        exp.append("TR suspect → orientation cancer de la prostate.")
        return True, exp, psad

    # PSA total
    if psa_total >= 10.0:
        exp.append("PSA ≥ 10 ng/mL → orientation cancer de la prostate.")
        return True, exp, psad

    if psa_total >= 4.0:  # plage 4–10 : utiliser PSAD
        if volume_ml > 0:
            psad = psa_total / float(volume_ml)  # ng/mL / mL
            exp.append(f"Densité PSA (PSAD) = {psad:.2f}.")
            if psad > 0.15:
                exp.append("PSAD > 0,15 → critère suspect.")
                return True, exp, psad
            else:
                exp.append("PSAD ≤ 0,15 → on poursuit l’analyse HBP.")
        else:
            exp.append("Volume inconnu/0 → PSAD non calculable; prudence clinique.")

    # PSA < 4 et TR non suspect → OK HBP
    return False, exp, psad

def plan_hbp(age: int, volume_ml: int, lobe_median: bool, ipss: int, psa_total: float,
             tr_suspect: bool, anticoag: bool, preservation_ejac: bool,
             ci_chirurgie: bool, refus_chir: bool, infections_recid: bool,
             retention: bool, calculs: bool, hematurie_recid: bool, ir_post_obstacle: bool):
    """
    Retourne dict {donnees, traitement, notes}
    - Pas de 'suivi' (retiré).
    - Lobe médian = INDICATION CHIRURGICALE (comme demandé).
    - Modalités thérapeutiques détaillées (médical/chirurgical) + indications.
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
        ("Complications", ", ".join([txt for ok, txt in [
            (infections_recid, "IU récidivantes"),
            (retention, "Rétention urinaire"),
            (calculs, "Calculs vésicaux"),
            (hematurie_recid, "Hématurie récidivante"),
            (ir_post_obstacle, "Altération fonction rénale liée à l’obstacle"),
        ] if ok]) or "Aucune"),
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

    # 1) HBP : options thérapeutiques (sans suivi)
    traitement = []
    notes = []

    # A) Mesures générales (si symptômes légers et sans complication)
    if ipss <= 7 and not any([infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, lobe_median]):
        traitement += [
            "Symptômes légers → abstention surveillée + règles hygiéno-diététiques.",
            "→ Réduire caféine/alcool le soir; mictions régulières; gestion hydrique; éviter la rétention prolongée.",
        ]

    # B) Traitement médical (LUTS modérés/sévères sans rétention/IR obstructive majeure)
    if ipss >= 8 and not any([retention, ir_post_obstacle]):
        traitement += [
            "Traitement médical →",
            "→ Alpha-bloquant (ex : tamsulosine/silodosine) → LUTS modérés/sévères; effet rapide sur le débit et les symptômes.",
            "→ ± Inhibiteur 5-α-réductase (finastéride/dutastéride) → prostate ≥ 40 mL ou PSA ≥ 1,5; effet lent (6–12 mois) ↓volume/RA.",
            "→ ± Association alpha-bloquant + 5-ARI → symptômes importants ET gros volume (diminuer risque de RA/CHIR).",
            "→ ± Tadalafil 5 mg/j → LUTS avec dysfonction érectile.",
            "→ ± Antimuscarinique ou β3-agoniste → symptômes de stockage (si RPM non élevé).",
        ]
        if preservation_ejac:
            notes += ["Objectif préservation éjaculation → informer des troubles éjaculatoires possibles avec certains alpha-bloquants."]

    # C) Indications chirurgicales (fortes) — inclut LOBE MÉDIAN
    indications_chir = any([
        infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, lobe_median
    ]) or (ipss >= 8 and not ci_chirurgie and not refus_chir)

    if indications_chir:
        if ci_chirurgie or refus_chir:
            # Alternatives non chirurgicales
            if volume_ml > 80:
                traitement += ["CI/refus de chirurgie avec gros volume → embolisation artères prostatiques (discussion RCP)."]
            else:
                traitement += ["CI/refus de chirurgie → optimisation médicale, sondages intermittents si besoin."]
        else:
            # Choix technique selon volume + lobe médian (lobe médian = indication chirurgicale)
            bloc = []

            # 1) TUIP (incision cervico-prostatique)
            if volume_ml < 30 and not lobe_median:
                bloc += [
                    "TUIP (incision cervico-prostatique) → volume < 30 mL et SANS lobe médian.",
                    "→ Avantages → temps opératoire court, saignement limité, meilleure préservation éjaculatoire.",
                    "→ Limites → risque de retraitement > RTUP à long terme.",
                ]

            # 2) RTUP mono/bipolaire (référence 30–80 mL)
            if 30 <= volume_ml <= 80 or lobe_median:
                bloc += [
                    "RTUP (mono/bipolaire) → standard 30–80 mL; aussi privilégiée en présence de lobe médian.",
                    "→ Bipolaire → meilleure hémostase; élimine le risque de syndrome d’absorption (TUR syndrome).",
                ]

            # 3) PVP GreenLight (saignement/anticoagulants)
            if anticoag or (30 <= volume_ml <= 80):
                bloc += [
                    "PVP GreenLight → alternative si risque hémorragique/anticoagulants ou préférence pour hémostase optimale.",
                    "→ Avantages → excellente hémostase, séjour/sondage courts, ambulatoire fréquent.",
                ]

            # 4) Énucléations endoscopiques (HoLEP/ThuLEP/BipolEP)
            if volume_ml >= 60:
                bloc += [
                    "Énucléation endoscopique (HoLEP/ThuLEP/BipolEP) → efficace pour moyens à TRÈS gros volumes (≥ 60–100+ mL).",
                    "→ Avantages → résultats fonctionnels durables, hémostase favorable, ↓durée de sondage/séjour.",
                    "→ Remarque → courbe d’apprentissage; nécessite plateau expérimenté.",
                ]

            # 5) Adénomectomie voie haute (ouverte/robot assistée)
            if volume_ml > 100:
                bloc += [
                    "Adénomectomie voie haute (ouverte/robot) → si très gros volumes et/ou si énucléation non disponible.",
                    "→ Référence historique pour très grosses prostates; morbidité plus élevée que l’endoscopie.",
                ]

            # 6) Implants urétraux (préservation éjaculation)
            if (volume_ml < 70) and (not lobe_median) and preservation_ejac:
                bloc += [
                    "Implants urétraux (UroLift) → < 70 mL, SANS lobe médian, objectif majeur de préserver l’éjaculation.",
                ]

            # Regroupement chirurgie
            traitement += ["Prise en charge chirurgicale →"] + ["→ " + x for x in bloc]

    # Notes additionnelles
    if anticoag:
        notes += ["Anticoagulants/antiagrégants → privilégier PVP GreenLight/HoLEP (hémostase supérieure)."]
    if lobe_median and volume_ml < 30:
        notes += ["Lobe médian présent avec petit volume → préférer RTUP/énucléation plutôt que TUIP."]

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

        submitted = st.form_submit_button("🔎 Générer la CAT – HBP")

    if submitted:
        plan = plan_hbp(
            age, volume, lobe_median, ipss, psa_total, tr_suspect, anticoag,
            preservation_ejac, ci_chirurgie, refus_chir, infections_recid,
            retention, calculs, hematurie_recid, ir_post_obstacle
        )

        # Tableau des données
        render_kv_table("🧾 Données saisies", plan["donnees"])

        # Conduite à tenir (texte à puces)
        st.markdown("### 💊 Conduite à tenir / Options thérapeutiques")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        # Notes
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        # Export
        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Conduite à tenir / Options thérapeutiques": plan["traitement"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT HBP (triage PSAD)", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_HBP")
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
