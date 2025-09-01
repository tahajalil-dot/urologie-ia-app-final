import streamlit as st
import base64
from typing import List, Dict

# --- CONFIG ---
st.set_page_config(page_title="Assistant IA - Urologie (AFU)", layout="wide")

# --- Utils ---
def download_text_button(filename: str, content: str, label: str = "📥 Télécharger la recommandation"):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)


def bullet(lines: List[str]) -> None:
    for x in lines:
        st.markdown(x)

# --- Evidence (texte court, pour traçabilité) ---
AFU = "📚 AFU 2024–2026"

# --- TVNIM: Risk stratification ---
def classify_tvnim_risk(stage: str, grade: str, number: str, size_mm: int, cis: bool, recidive: bool,
                        lvi: bool, urethral_prostatic: bool) -> str:
    """Retourne faible / intermédiaire / haut / très haut.
    Logique alignée AFU (simplifiée pour app)."""
    # Très haut risque
    if stage == "pT1" and grade == "Haut grade" and (
        cis or number == "Multiple" or size_mm > 30 or lvi or urethral_prostatic or recidive
    ):
        return "très haut"
    # Haut risque
    if stage == "pT1" or grade == "Haut grade" or cis:
        return "haut"
    # Intermédiaire
    if stage == "pTa" and grade == "Bas grade" and (number == "Multiple" or recidive or size_mm >= 30):
        return "intermédiaire"
    # Faible
    if stage == "pTa" and grade == "Bas grade" and number == "Unique" and size_mm < 30 and not cis and not recidive:
        return "faible"
    # Par défaut
    return "intermédiaire"


# --- TVNIM: CAT détaillée (traitement + surveillance) ---
def tvnim_plan(risk: str, ipop_ok: bool) -> Dict[str, List[str]]:
    plan: Dict[str, List[str]] = {"traitement": [], "surveillance": [], "notes": []}

    # Traitement
    if risk == "faible":
        plan["traitement"] += [
            "✅ RTUV de qualité (détrusor présent)",
            ("💧 IPOP (MMC/épirubicine/gemcitabine) <2h post-RTUV" if ipop_ok else "⚠️ IPOP non réalisée (CI: hématurie/perforation)"),
            f"{AFU} : IPOP seule, pas d'entretien",
        ]
        plan["surveillance"] += [
            "📅 Cystoscopie à 3 mois, 12 mois, puis annuelle ×5 ans",
            "🧪 Cytologie non systématique",
        ]
    elif risk == "intermédiaire":
        plan["traitement"] += [
            "✅ RTUV de qualité (second look si doute de résection)",
            "💉 Chimiothérapie endovésicale (1ère intention) — 6–8 instillations hebdo",
            "   • Mitomycine C 40 mg/40 mL OU Épirubicine 50 mg OU Gemcitabine 1000 mg",
            f"{AFU} : entretien non systématique (à discuter si récidives)",
            "🔁 Alternative : BCG induction + entretien 1 an (si haut risque de récidive)",
        ]
        plan["surveillance"] += [
            "📅 Cystoscopie à 3 et 6 mois, puis /6 mois ×2 ans, puis annuelle ×10 ans",
            "🧪 Cytologie associée aux cystoscopies",
        ]
    elif risk == "haut":
        plan["traitement"] += [
            "✅ RTUV de qualité + second look si pT1 ou pas de détrusor",
            "🦠 BCG (induction 6 instillations) + entretien 3 ans (schéma 3/6/12 mois puis /6 mois)",
            f"{AFU} : ne pas réduire dose ni durée",
            "🔁 Si CI/échec BCG : chimio endovésicale (MMC/gemcitabine ± docétaxel)",
        ]
        plan["surveillance"] += [
            "📅 Cystoscopie /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis annuelle à vie",
            "🧪 Cytologie systématique",
            "🖥️ Uro-TDM annuel (risque TVES)",
        ]
    elif risk == "très haut":
        plan["traitement"] += [
            "⚠️ pT1 haut grade avec facteurs aggravants",
            "🦠 BCG complet (3 ans) OU cystectomie précoce avec curage",
            "🫱 RCP indispensable pour décision partagée",
        ]
        plan["surveillance"] += [
            "📅 Cystoscopie /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis annuelle à vie",
            "🧪 Cytologie systématique",
            "🖥️ Uro-TDM annuel (haut risque TVES)",
        ]
    return plan


# --- TVIM: CAT détaillée (traitement + surveillance) ---
def tvim_plan(metastases: bool, cis_eligible: bool, t2_localise: bool, cis_diffus: bool,
              hydroureteronephrose: bool, bonne_fonction_v: bool, pdl1_pos: bool,
              post_op_high_risk: bool, neo_adjuvant_fait: bool) -> Dict[str, List[str]]:
    plan: Dict[str, List[str]] = {"traitement": [], "surveillance": [], "notes": []}

    if metastases:
        plan["traitement"] += [
            "🧬 TVIM métastatique",
            "1ʳᵉ ligne : Enfortumab vedotin + Pembrolizumab",
            "Alternatives : Cis/Gem + Nivolumab; ou Pt-based (Cis/Carbo) → maintenance Avelumab",
            f"{AFU} : adapter au statut FGFR (Erdafitinib en 2ᵉ ligne si mut FGFR2/3)",
        ]
        plan["surveillance"] += [
            "📅 Scanner TAP /6–8 semaines en induction puis selon réponse",
        ]
        return plan

    # Non métastatique
    if cis_eligible:
        plan["traitement"] += [
            "💊 Chimiothérapie néoadjuvante cisplatine (dd-MVAC×6 ou Gem/Cis×4)",
            "🔪 Cystectomie radicale + curage ganglionnaire standard",
            "💧 Dérivation : néovessie si urètre négatif sinon Bricker",
            f"{AFU} : gain SG ~8% à 5 ans avec néoadjuvant",
        ]
    else:
        plan["traitement"] += [
            "🔪 Cystectomie radicale + curage ganglionnaire standard (non éligible cisplatine)",
        ]

    # Option préservation vésicale (TTM) si profils favorables
    if t2_localise and not cis_diffus and not hydroureteronephrose and bonne_fonction_v:
        plan["traitement"] += [
            "💡 Option conservatrice (TTM) : RTUV complète + radiothérapie + chimio concomitante",
            "   • Protocoles concomitants : 5-FU/mitomycine, cisplatine ou gemcitabine faible dose",
            "   • Cystectomie de rattrapage en cas d'échec (≈15–20%)",
        ]

    # Post-op adjuvant
    if post_op_high_risk and not neo_adjuvant_fait:
        plan["traitement"] += [
            "➕ Chimiothérapie adjuvante (cisplatine) si pT3–4 et/ou pN+ et pas de néoadjuvant",
        ]
    if pdl1_pos:
        plan["traitement"] += [
            "🛡️ Immunothérapie adjuvante : Nivolumab si PD-L1 positif (CheckMate 274)",
        ]

    # Surveillance
    plan["surveillance"] += [
        "📅 Après cystectomie : Uro-TDM + TDM thorax /6 mois ×2–3 ans puis annuel",
        "🔎 Surveillance urétrale si urètre conservé (rythme selon facteurs de risque)",
        "🧪 Suivi fonction rénale + dépistage TVES",
    ]

    if t2_localise and not cis_diffus and not hydroureteronephrose and bonne_fonction_v:
        plan["surveillance"] += [
            "📅 Après TTM : Cystoscopie + cytologie /3 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis annuel à vie",
            "🖥️ Scanner TAP /3–6 mois ×2 ans, puis /6 mois jusqu’à 5 ans, puis annuel",
        ]

    plan["notes"] += [
        "🏥 RAAC recommandé (optimisation péri-opératoire)",
        "🫱 Décision partagée patient (qualité de vie, dérivation, fertilité)",
        AFU,
    ]

    return plan


# --- UI ---
st.title("🧠 Assistant IA - Urologie (AFU)")
st.markdown(
    """
Bienvenue dans l'assistant d’aide à la décision en urologie aligné **AFU 2024–2026**.
> **Avertissement** : outil d’aide à la décision; la responsabilité finale appartient au clinicien.
"""
)

menu = st.sidebar.selectbox(
    "📂 Choisissez un module :",
    [
        "Page d'accueil",
        "Cancer de la vessie (TVNIM / TVIM)",
        "Hypertrophie bénigne de la prostate (HBP)",
        "Lithiase urinaire",
        "Cancer de la prostate",
        "Cancer du rein",
        "Patient porteur de sonde double J",
        "Tumeurs des voies excrétrices supérieures (TVES)",
    ],
)

if menu == "Page d'accueil":
    st.info("Veuillez sélectionner une pathologie dans le menu pour commencer.")

# === MODULE VESSIE (TVNIM/TVIM) — Version améliorée ===
if menu == "Cancer de la vessie (TVNIM / TVIM)":
    st.header("🔷 Cancer de la vessie – TVNIM / TVIM")

    with st.form("vessie_form"):
        st.subheader("📌 Données anatomopathologiques (de base)")
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1", "pT2 ou plus"])  # pT2+=TVIM
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        cis = st.radio("Présence de CIS ?", ["Non", "Oui"], horizontal=True) == "Oui"
        number_basic = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple"])
        size_basic = st.slider("Taille de la plus grande lésion (mm)", 1, 100, 15)

        # Afficher les blocs avancés UNIQUEMENT si pT2+ OU (pT1 avec indication potentielle à la cystectomie)
        pt1_cysto_suspect = (stade == "pT1" and grade == "Haut grade" and (number_basic == "Multiple" or size_basic >= 30 or cis))
        show_advanced = (stade == "pT2 ou plus") or pt1_cysto_suspect

        if show_advanced:
            st.subheader("🔎 Facteurs avancés (affichés car indication potentielle de cystectomie)")
            recidive = st.radio("Récidive ?", ["Non", "Oui"], horizontal=True) == "Oui"
            lvi = st.radio("Envahissement lymphovasculaire ?", ["Non", "Oui"], horizontal=True) == "Oui"
            urethral = st.radio("Atteinte urètre prostatique ?", ["Non", "Oui"], horizontal=True) == "Oui"
        else:
            # Valeurs par défaut non aggravantes si non affichées
            recidive = False
            lvi = False
            urethral = False

        # Contexte clinique TVNIM seulement (IPOP) – reste masqué pour TVIM ou pT1 cystectomie
        if stade in ["pTa", "pT1"] and not show_advanced:

    if submitted:
        reco_lines: List[str] = []
        if stade in ["pTa", "pT1"]:  # TVNIM
            risque = classify_tvnim_risk(
                stage=stade, grade=grade, number=nombre, size_mm=taille, cis=cis,
                recidive=recidive, lvi=lvi, urethral_prostatic=urethral
            )
            plan = tvnim_plan(risque, ipop_ok)
            st.subheader(f"🧠 Recommandation IA — TVNIM ({risque.upper()})")
            st.markdown("### 💊 Traitement")
            bullet(plan["traitement"])
            st.markdown("### 📅 Surveillance")
            bullet(plan["surveillance"])
            if plan["notes"]:
                st.markdown("### 📝 Notes")
                bullet(plan["notes"])

            reco_lines += [
                f"TVNIM — Risque: {risque}",
                "Traitement:" , *plan["traitement"],
                "Surveillance:", *plan["surveillance"],
                *(["Notes:"] + plan["notes"] if plan["notes"] else []),
            ]

        else:  # pT2 ou plus => TVIM
            plan = tvim_plan(
                metastases=metastases, cis_eligible=cis_eligible,
                t2_localise=t2_localise, cis_diffus=cis_diffus,
                hydroureteronephrose=hydro, bonne_fonction_v=bonne_fct,
                pdl1_pos=pdl1_pos, post_op_high_risk=post_op_high_risk,
                neo_adjuvant_fait=neo_adjuvant_fait,
            )
            st.subheader("🧠 Recommandation IA — TVIM")
            st.markdown("### 💊 Traitement")
            bullet(plan["traitement"])
            st.markdown("### 📅 Surveillance")
            bullet(plan["surveillance"])
            if plan["notes"]:
                st.markdown("### 📝 Notes")
                bullet(plan["notes"])

            reco_lines += [
                "TVIM — Plan:",
                "Traitement:", *plan["traitement"],
                "Surveillance:", *plan["surveillance"],
                *(["Notes:"] + plan["notes"] if plan["notes"] else []),
            ]

        st.divider()
        st.markdown("### 📄 Export")
        download_text_button("recommandation_VESSIE_AFU.txt", "\n".join(reco_lines))

# === Les autres modules restent disponibles (placeholder / v1) ===
if menu == "Hypertrophie bénigne de la prostate (HBP)":
    st.header("🔷 Hypertrophie bénigne de la prostate (HBP)")
    st.info("Module HBP à refactorer comme TVNIM/TVIM avec règles et suivi détaillés (alpha-bloquants, 5-ARI, chirurgie selon volume/complications).")

if menu == "Lithiase urinaire":
    st.header("🔷 Lithiase urinaire")
    st.info("Module lithiase à adapter (taille, UH, localisation, grossesse, rein unique, colique; ESWL/URS/NLPC + prévention récidive).")

if menu == "Cancer de la prostate":
    st.header("🔷 Cancer de la prostate")
    st.info("Module prostate à structurer (stratification D’Amico, HT, RT, chirurgie, métastatique).")

if menu == "Cancer du rein":
    st.header("🔷 Cancer du rein")
    st.info("Module rein à structurer (Bosniak, tailles, MSKCC/IMDC, options chirurgicales/systémiques).")

if menu == "Patient porteur de sonde double J":
    st.header("🔷 Patient porteur de sonde double J")
    st.info("Rappels : durée 6–8 semaines, symptômes d’alerte (fièvre, douleurs), ECBU, changement anticipé si sepsis.")

if menu == "Tumeurs des voies excrétrices supérieures (TVES)":
    st.header("🔷 TVES")
    st.info("Bas/Haut risque, endoscopie vs NUT, suivi (cysto, cytologie, imagerie).")
