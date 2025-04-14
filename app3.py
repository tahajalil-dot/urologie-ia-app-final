
import streamlit as st
import base64

st.set_page_config(page_title="Assistant IA - Urologie (AFU)", layout="wide")

st.title("🧠 Assistant IA - Urologie (AFU)")
st.markdown("""
Bienvenue dans l'assistant intelligent pour la décision clinique en urologie. 
Sélectionnez une pathologie dans le menu de gauche pour générer une recommandation selon les guidelines **AFU**.
""")

menu = st.sidebar.selectbox("📂 Choisissez une pathologie :", [
    "Page d'accueil",
    "Hypertrophie bénigne de la prostate (HBP)",
    "Lithiase urinaire",
    "Cancer de la prostate",
    "Cancer du rein",
    "Cancer de la vessie (TVNIM / TVIM)",
    "Patient porteur de sonde double J",
    "Tumeurs des voies excrétrices supérieures (TVES)"
])

if menu == "Page d'accueil":
    st.info("Veuillez sélectionner une pathologie dans le menu pour commencer.")

# MODULE CANCER VESSIE
if menu == "Cancer de la vessie (TVNIM / TVIM)":
    st.header("🔷 Cancer de la vessie")
    age = st.number_input("Âge du patient", min_value=18, max_value=100)
    deja_reseque = st.radio("Patient déjà résequé ?", ["Oui", "Non"])

    if deja_reseque == "Non":
        st.warning("🔔 Le patient n’a jamais été résequé : RTUV initiale recommandée avant toute autre décision thérapeutique.")
    else:
        hematurie = st.radio("Hématurie macroscopique ?", ["Oui", "Non"])
        nombre_tumeurs = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple"])
        taille = st.slider("Taille de la plus grande tumeur (mm)", 1, 100)
        cis = st.radio("Présence de CIS ?", ["Oui", "Non"])
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1", "pT2 ou plus"])
        recidive = st.radio("Récidive ?", ["Oui", "Non"])
        metastases = st.radio("Métastases à distance ?", ["Oui", "Non"])

        if st.button("🔎 Générer la conduite à tenir - Vessie"):
            reco = []
            if stade == "pTa" and grade == "Bas grade" and nombre_tumeurs == "Unique" and taille < 30 and cis == "Non" and recidive == "Non":
                risque = "faible"
            elif stade == "pTa" and grade == "Bas grade" and (nombre_tumeurs == "Multiple" or recidive == "Oui"):
                risque = "intermédiaire"
            elif stade == "pT1" or grade == "Haut grade" or cis == "Oui":
                risque = "haut"
            elif stade == "pT2 ou plus":
                risque = "très haut"
            else:
                risque = "non classé"

            reco.append(f"📊 Risque estimé : **{risque.upper()}**")

            if risque == "faible":
                reco.append("💧 Instillation unique de mitomycine dans les 6h post RTUV")
                reco.append("📆 Surveillance cystoscopie à 3 mois, puis tous les 6 mois")
            elif risque == "intermédiaire":
                reco.append("💉 BCG 1 an OU mitomycine hebdomadaire x6 + entretien")
                reco.append("📆 Surveillance cystoscopie à 3 mois, 6 mois, puis tous les 6 mois")
            elif risque == "haut":
                reco.append("💉 BCG thérapeutique sur 3 ans (induction + entretien)")
                reco.append("🔄 Second look à 4-6 semaines si pT1 ou incertitude")
                reco.append("📆 Surveillance rapprochée : cystoscopie tous les 3 mois la 1ère année")
            elif risque == "très haut":
                reco.append("⚠️ Indication de cystectomie totale si envahissement musculaire confirmé")
                reco.append("📊 Bilan d’extension : TDM TAP, scintigraphie osseuse / TEP scan")
                reco.append("📆 RCP indispensable avant décision")

            st.markdown("### 🧠 Recommandation IA - Cancer de la vessie")
            for r in reco:
                st.markdown(r)
            rapport = "\n".join(reco)
            b64 = base64.b64encode(rapport.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_VESSIE_AFU.txt">📥 Télécharger cette recommandation</a>'
            st.markdown(href, unsafe_allow_html=True)
