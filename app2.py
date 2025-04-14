# MODULE CANCER VESSIE - Nouvelle version enrichie
if menu == "Cancer de la vessie \(TVNIM / TVIM\)":
    st.header("🔷 Cancer de la vessie")
    age = st.number_input("Âge du patient", min_value=18, max_value=100)
    hematurie = st.radio("Hématurie macroscopique ?", ["Oui", "Non"])
    deja_reseque = st.radio("Patient déjà résequé ?", ["Oui", "Non"])

    if deja_reseque == "Non":
        st.warning("🔄 RTUV initiale recommandée en première intention.")
    else:
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
                reco.append("📆 Surveillance cystoscopie à 3 mois, puis tous les 6 à 12 mois")
            elif risque == "intermédiaire":
                reco.append("💉 BCG 1 an OU mitomycine hebdomadaire x6 + entretien")
                reco.append("📆 Surveillance cystoscopie à 3 mois, 6 mois, puis tous les 6 mois")
            elif risque == "haut":
                reco.append("💉 BCG thérapeutique sur 3 ans (induction + entretien prolongé)")
                if stade == "pT1":
                    reco.append("🔄 Second look à 4-6 semaines obligatoire (pT1 ou incertitude)")
                reco.append("📆 Cystoscopie tous les 3 mois pendant 2 ans, puis tous les 6 mois")
            elif risque == "très haut":
                reco.append("⚠️ Indication de cystectomie totale si envahissement musculaire confirmé")
                reco.append("📊 Bilan d’extension : TDM TAP + scintigraphie osseuse / TEP scan")
                reco.append("📆 RCP indispensable avant toute décision thérapeutique")

            if metastases == "Oui":
                reco.append("🔴 Maladie métastatique → traitement systémique")
                reco.append("💊 Chimiothérapie type MVAC ou Gemcitabine + Cisplatine")
                reco.append("📆 Suivi et décision en RCP d’oncologie urologique spécialisé")

            st.markdown("### 🧠 Recommandation IA - Cancer de la vessie")
            for r in reco:
                st.markdown(r)
            rapport = "\n".join(reco)
            b64 = base64.b64encode(rapport.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_VESSIE_AFU.txt">📥 Télécharger cette recommandation</a>'
            st.markdown(href, unsafe_allow_html=True)
