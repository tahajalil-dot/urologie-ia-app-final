import streamlit as st

# ✅ Cette ligne doit être absolument la toute première commande Streamlit
st.set_page_config(page_title="Assistant IA - Urologie (AFU)", layout="wide")

import base64

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

# MODULE HBP
if menu == "Hypertrophie bénigne de la prostate (HBP)":
    st.header("🔷 Hypertrophie bénigne de la prostate (HBP)")
    age = st.number_input("Âge", min_value=40, max_value=100)
    atcd = st.multiselect("Antécédents urologiques", [
    "Rétention urinaire aiguë",
    "Infections urinaires récidivantes",
    "Calculs vésicaux",
    "Hématurie récidivante",
    "Altération de la fonction rénale liée à l’obstacle",
    "Échec de traitement médical"
])
    ipss = st.slider("Score IPSS", 0, 35)
    volume = st.number_input("Volume prostatique à l’échographie (cc)", min_value=10.0)
    psa = st.number_input("PSA total (ng/mL)", min_value=0.0)
    if 4 <= psa <= 10:
            residu = st.number_input("Résidu post-mictionnel (mL)", min_value=0.0)
    actif = st.radio("Activité sexuelle ?", ["Oui", "Non"])
    enfant = st.radio("Souhaite avoir des enfants ?", ["Oui", "Non"])
    marie = st.radio("Statut marital", ["Marié", "Célibataire"])

    if st.button("🔎 Générer la conduite à tenir - HBP"):
        reco = []

        if psa < 4:
            diagnostic = "HBP probable"
        elif 4 <= psa <= 10:
            densite = psa / volume if volume > 0 else 0
            if densite > 0.15:
                diagnostic = f"Suspicion d’ADK prostatique → IRM + biopsies"
                reco.append(f"🔍 Justification : Densité prostatique élevée > 0.15 (densité = {densite:.2f}) → exploration complémentaire recommandée selon AFU")
            else:
                diagnostic = f"HBP probable"
                reco.append(f"ℹ️ Densité prostatique < 0.15 (densité = {densite:.2f}) → compatible avec HBP selon AFU")
        else:
            diagnostic = "Suspicion forte d’ADK prostatique → IRM + biopsies"

        reco.append(f"🧬 Diagnostic : {diagnostic}")

        if diagnostic.startswith("HBP"):
            if any(x in atcd for x in ["Échec de traitement médical", "Altération de la fonction rénale liée à l’obstacle"]):
                pass
            else:
                if ipss <= 7:
                    reco.append("✅ Abstention thérapeutique + règles hygiéno-diététiques :")
                    reco.append("- Diminuer la caféine et alcool")
                    reco.append("- Éviter la rétention prolongée")
                    reco.append("- Uriner régulièrement")
                elif ipss > 7:
                    if actif == "Oui" or enfant == "Oui":
                        reco.append("💊 Traitement médical par alpha-bloquant (ex. tamsulosine)")
                        reco.append("ℹ️ Justification : vie sexuelle active ou désir d’enfant → éviter inhibiteurs de la 5α-réductase")
                    else:
                        reco.append("💊 Inhibiteur de la 5α-réductase (ex. finastéride)")
                        reco.append("ℹ️ Justification : pas de vie sexuelle active ni désir d’enfant → inhibiteur possible")
                
            if any(x in atcd for x in [
                "Rétention urinaire aiguë",
                "Infections urinaires récidivantes",
                "Calculs vésicaux",
                "Hématurie récidivante",
                "Altération de la fonction rénale liée à l’obstacle",
                "Échec de traitement médical"
            ]):
                if volume < 30:
                    reco.append("🔧 Traitement chirurgical : incision cervico-prostatique")
                    reco.append("ℹ️ Justification : volume < 30 cc et complication présente")
                elif 30 <= volume <= 70:
                    reco.append("🔧 Traitement chirurgical : RTUP")
                    reco.append("ℹ️ Justification : volume entre 30 et 70 cc avec complication")
                else:
                    reco.append("🔧 Traitement chirurgical : adénomectomie voie endoscopique ou ouverte")
                    reco.append("ℹ️ Justification : volume > 70 cc avec complication ou échec médical")

        st.markdown("### 🧠 Recommandation IA - HBP")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_HBP_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# MODULE LITHIASE
if menu == "Lithiase urinaire":
    st.header("🔷 Lithiase urinaire")
    age = st.number_input("Âge", min_value=18, max_value=100)
    localisation = st.selectbox("Localisation du calcul", ["Calice supérieur", "Calice moyen", "Calice inférieur", "Bassinet", "Uretère proximal", "Uretère distal"])
    taille = st.slider("Taille du calcul (mm)", 1, 40)
    densite = st.number_input("Densité au scanner (UH)", min_value=100)
    nombre = st.selectbox("Nombre de calculs", ["Unique", "Multiple"])
    grossesse = st.radio("Patiente enceinte ?", ["Oui", "Non"])
    rein_unique = st.radio("Rein unique ?", ["Oui", "Non"])
    colique = st.radio("Colique néphrétique en cours ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - Lithiase"):
        reco = []

        if colique == "Oui":
            reco.append("🚨 Colique néphrétique → antalgie, hydratation, éventuelle pose de JJ en urgence")
        else:
            # Recommandations AFU selon taille, localisation et densité
            if grossesse == "Oui" or rein_unique == "Oui":
                reco.append("🔶 Patiente enceinte ou rein unique → URS en priorité")

            if taille <= 10:
                if densite < 1000:
                    reco.append("💠 ESWL en 1ère intention si localisation favorable")
                else:
                    reco.append("🔸 URS préférée si densité > 1000 UH")
            elif 10 < taille <= 20:
                if localisation in ["Calice inférieur", "Bassinet"]:
                    reco.append("🔷 Mini-NLPC préférable en cas de localisation peu favorable")
                else:
                    reco.append("🔷 URS en 1ère intention si localisation favorable")
            elif taille > 20:
                if nombre == "Multiple":
                    reco.append("🟥 NLPC combinée à URS en cas de calculs complexes ou multiples")
                else:
                    reco.append("🔴 NLPC seule si volume > 20 mm et accès favorable")

            if taille > 30:
                reco.append("🔴 Calcul > 3 cm → NLPC possible OU chirurgie ouverte/laparoscopique selon anatomie et contexte")
            if taille > 30 or localisation in ["Calice inférieur"]:
                reco.append("⚠️ Chirurgie ouverte ou laparoscopique si échec traitements endo-urologiques ou anatomie défavorable")

        reco.append("📌 Règles hygiéno-diététiques pour prévenir la récidive :")
        reco.append("- Boire au moins 2,5L/j")
        reco.append("- Réduire sel, protéines animales")
        reco.append("- Éviter excès oxalates")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_LITHIASE_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# MODULE CANCER VESSIE - Nouvelle version enrichie
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
            elif stade == "pT1" and grade == "Haut grade" or "pT1" and grade == "Haut grade"and nombre_tumeurs == "Multiple" or "pT1" and grade == "Haut grade" and taille > 30 or "pT1" and grade == "Haut grade" and  cis == "oui":
                risque = "très haut"
            elif stade == "pT2 ou plus" and grade == "Haut grade" or "pT1" and grade == "Haut grade"and nombre_tumeurs == "Multiple" or "pT1" and grade == "Haut grade" and taille > 30 or "pT1" and grade == "Haut grade" and  cis == "oui":
                risque = "Tumeur infiltrante le muscle"

            reco.append(f"📊 Risque estimé : **{risque.upper()}**")

            if risque == "faible":
                reco.append("💧 correspondent aux tumeurs urothéliales pTa de bas grade, unifocales et de moins de 3 cm sans antécédent de TV. Elles ont un risque de récidive et de progression qui est faible. Après la résection de ces tumeurs il est recommandé de réaliser une IPOP. Aucun autre traitement complémentaire n’est nécessaire.")
                reco.append("📆 Surveillance cystoscopie à 3 mois, puis au 12 eme mois et annuel pendant 5 ans")
            elif risque == "intermédiaire":
                reco.append("💉 correspondent à toutes les autres tumeurs urothéliales pTa de bas grade qui ne présentent aucun des critères de risque élevé ou très élevé. Ces tumeurs ont un risque de progression faible mais un risque de récidive élevé. Leur traitement fait appel aux instillations endovésicales par chimiothérapie (mitomycine, epirubicine) selon un schéma de 8 instillations sans traitement d’entretien. Une alternative thérapeutique est la BCG-thérapie avec un entretien de 1 an pour diminuer le risque de récidive. Le BCG est plus efficace sur le risque de récidive, mais son profil de tolérance étant moins bon et le risque de progression étant faible, il est recommandé de proposer une chimiothérapie endovésicale en première intention et le BCG avec un traitement d’entretien d’un an en cas d’échec")
                reco.append("📆 Surveillance cystoscopie à 3 mois, 6 mois, puis tous les 6 mois pendant 2 ans puis annuelement pendant 10 ans + cytologie urinaire")
            elif risque == "haut":
                reco.append("💉 au moins un des facteurs de risque suivant : stade pT1, haut grade, présence de carcinome in situ (CIS). Ces tumeurs ont un risque de récidive et de progression élevé. Leur traitement fait appel aux instillations endovésicales par BCG-thérapie (traitement initial par 6 instillations) suivi systématiquement par un traitement d’entretien de 3 ans (schéma d’entretien)")
                reco.append("🔄 Second look à 4-6 semaines si pT1 ou Absence de muscle identifié sur la résection initiale ou Tumeur volumineuse et/ou multifocale")
                reco.append("📆 Surveillance rapprochée : cystoscopie tous les 3 mois pendant 2 ans puis tous les 6 mois pendant 5 ans et puis anuellement a vie + cytologie urinaire.")
            elif risque == "très haut":
                reco.append("⚠️ ont un risque de progression élevé (environ 20%), soit parce que la probabilité d’éradication complète avant traitement est faible,  parce qu’elles sont très agressives,et présentent un risque d’échec du traitement endovésical élevé. La BCG-thérapie et la cystectomie associée à un curage ganglionnaire sont les deux options thérapeutiques de première intention")
                reco.append("📊 Surveillance rapprochée : cystoscopie tous les 3 mois pendant 2 ans puis tous les 6 mois pendant 5 ans et puis anuellement a vie + cytologie urinaire. en cas de cystectomie , Bilan d’extension : TDM TAP, scintigraphie osseuse / TEP scan")
                reco.append("📆 RCP indispensable avant décision")
            elif risque == "Tumeur infiltrante le muscle":
                reco.append("⚠️ Tumeur infiltrante le muscle pT2 : chimiotherapie neo-adjuvante puis traitement chirurgical : cystectomie")
                reco.append("📊 Bilan d’extension : TDM TAP, scintigraphie osseuse / TEP scan")
                reco.append("📆 RCP indispensable avant décision si tumeur de vessie metastatique")

            st.markdown("### 🧠 Recommandation IA - Cancer de la vessie")
            for r in reco:
                st.markdown(r)
            rapport = "\n".join(reco)
            b64 = base64.b64encode(rapport.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_VESSIE_AFU.txt">📥 Télécharger cette recommandation</a>'
            st.markdown(href, unsafe_allow_html=True)

# MODULE CANCER DE LA PROSTATE
if menu == "Cancer de la prostate":
    st.header("🔷 Cancer de la prostate")
    st.subheader("🧩 Données générales")
    age = st.number_input("Âge du patient", min_value=40, max_value=100)
    psa = st.number_input("PSA total (ng/mL)", min_value=0.0, step=0.1)
    volume = st.number_input("Volume prostatique (cc)", min_value=10.0, step=1.0)
    tr = st.selectbox("Résultat du toucher rectal", ["Normal", "Induré unilatéral", "Induré bilatéral", "Suspect diffus"])
    pirads = st.selectbox("Score PIRADS de l’IRM", ["PIRADS 1", "PIRADS 2", "PIRADS 3", "PIRADS 4", "PIRADS 5"])
    esperance = st.radio("Espérance de vie > 10 ans ?", ["Oui", "Non"])

    st.subheader("🔬 Résultat biopsie")
    gleason = st.selectbox("Score de Gleason", ["3+3", "3+4", "4+3", "4+4", "Autre ≥ 8"])
    tnm = st.selectbox("Stade clinique T", ["T1c", "T2a", "T2b", "T2c", "T3", "T4"])
    vesi = st.radio("Envahissement des vésicules séminales ?", ["Oui", "Non"])

    st.subheader("🧪 Bilan d’extension")
    metastases = st.radio("Présence de métastases ?", ["Non", "Oui - Oligo (<4)", "Oui - Pluri (>4)"])
    site_met = st.multiselect("Localisation des métastases", ["Ganglionnaire", "Osseuse", "Pulmonaire", "Hépatique", "Cérébrale"])

    if st.button("🔎 Générer la conduite à tenir - Prostate"):
        reco = []

        if gleason == "3+3": g = 6
        elif gleason == "3+4": g = 7
        elif gleason == "4+3": g = 7
        elif gleason == "4+4": g = 8
        else: g = 9

        if metastases == "Non":
            if psa < 10 and g == 6 and tnm in ["T1c", "T2a"]:
                risque = "faible"
            elif psa >= 20 or g >= 8 or tnm in ["T2c", "T3", "T4"]:
                risque = "élevé"
            else:
                risque = "intermédiaire"

            reco.append(f"📊 Risque estimé : **{risque.upper()}** selon la classification de D'Amico (AFU)")
            reco.append("🔍 Le score de D’Amico repose sur 3 critères : PSA, Gleason, et stade clinique.")
            reco.append("- 🟢 Faible risque : les 3 critères suivants sont TOUS présents → PSA < 10, Gleason ≤ 6, T1c–T2a")
            reco.append("- 🟠 Risque intermédiaire : au moins un critère → PSA 10–20, Gleason 7, T2b")
            reco.append("- 🔴 Risque élevé : un SEUL critère suffit → PSA > 20, Gleason ≥ 8, T2c ou plus")

            if esperance == "Non":
                reco.append("🛑 Espérance de vie < 10 ans → Surveillance ou hormonothérapie")
            else:
                if risque == "faible":
                    reco.append("✅ Surveillance active OU prostatectomie / radiothérapie")
                    reco.append("ℹ️ Justification : Cancer localisé à faible risque → toutes options possibles selon âge, comorbidités et souhait du patient (AFU)")
                elif risque == "intermédiaire":
                    reco.append("🔶 Prostatectomie avec curage pelvien ou Radiothérapie + HT courte (6 mois)")
                    reco.append("ℹ️ Justification : Risque intermédiaire → stratégie combinée selon recommandations AFU")
                else:
                    reco.append("🔴 Prostatectomie + curage étendu ou Radiothérapie + HT longue (18-36 mois)")
                    reco.append("ℹ️ Justification : Risque élevé → traitement intensif recommandé selon les guidelines AFU")

            if tnm in ["T3", "T4"] or vesi == "Oui":
                reco.append("⚠️ Forme localement avancée : curage + HT prolongée + radiothérapie")

        else:
            reco.append("🚨 Forme métastatique")
            if metastases == "Oui - Oligo (<4)":
                reco.append("🔹 Oligo-métastatique → Traitement local possible + HT ± docétaxel")
            else:
                reco.append("🔻 Pluri-métastatique → HT de castration +")
                reco.append("- Docétaxel si toléré")
                reco.append("- Ou anti-androgène de nouvelle génération (abiratérone, enzalutamide)")

            if "Osseuse" in site_met:
                reco.append("🦴 Considérer ajout d’os-protecteurs (acide zolédronique ou dénosumab)")

        st.markdown("### 🧠 Recommandation IA (AFU) - Cancer de la prostate")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_PROSTATE_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)
        
 # MODULE CANCER DU REIN - Unique et corrigé
if menu == "Cancer du rein":
    st.header("🔷 Cancer du rein")
    age = st.number_input("Âge du patient", min_value=18, max_value=100)
    comorbidites = "Non"
    if age >= 75:
        comorbidites = st.radio("Comorbidités contre-indiquant la chirurgie ?", ["Oui", "Non"])

    taille = st.slider("Taille de la tumeur (cm)", 1, 20)
    tumeur_kystique = st.radio("Aspect kystique au scanner ?", ["Oui", "Non"])
    if tumeur_kystique == "Oui":
        bosniak = st.selectbox("Classification Bosniak", ["I", "II", "IIF", "III", "IV"])

    thrombus = st.radio("Présence de thrombus ?", ["Oui", "Non"])
    fascia = st.radio("Extension au fascia de Gerota ?", ["Oui", "Non"])
    metastases = st.radio("Présence de métastases ?", ["Oui", "Non"])

    if metastases == "Oui":
        st.subheader("Formulaire MSKCC (cancer du rein métastatique)")
        karnofsky = st.radio("Score de Karnofsky < 80% ?", ["Oui", "Non"])
        diag_delai = st.radio("Intervalle < 1 an entre diagnostic et traitement ?", ["Oui", "Non"])
        anemia = st.radio("Anémie présente ?", ["Oui", "Non"])
        hypercalc = st.radio("Hypercalcémie ?", ["Oui", "Non"])
        neutros = st.radio("Polynucléose neutrophile ?", ["Oui", "Non"])
        thrombose = st.radio("Thrombocytose ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - Rein"):
        reco = []

        if tumeur_kystique == "Oui":
            if bosniak in ["I", "II"]:
                reco.append("🟢 Bosniak I/II : kystes bénins, aucune surveillance nécessaire")
            elif bosniak == "IIF":
                reco.append("🟡 Bosniak IIF : surveillance annuelle pendant 5 ans par imagerie à la recherche de rehaussement")
            elif bosniak in ["III", "IV"]:
                reco.append("🔴 Bosniak III/IV : exérèse chirurgicale recommandée selon les règles oncologiques")
        else:
            if metastases == "Oui":
                reco.append("📌 En cas de métastases : une biopsie rénale est indiquée avant tout traitement systémique")
                nb_facteurs = sum([
                    karnofsky == "Oui",
                    diag_delai == "Oui",
                    anemia == "Oui",
                    hypercalc == "Oui",
                    neutros == "Oui",
                    thrombose == "Oui"
                ])
                if nb_facteurs == 0:
                    risque = "bon pronostic"
                elif nb_facteurs <= 2:
                    risque = "intermédiaire"
                else:
                    risque = "mauvais pronostic"
                reco.append(f"🧪 Score MSKCC : {nb_facteurs} facteur(s) → **{risque.upper()}**")
                if risque in ["bon pronostic", "intermédiaire"]:
                    reco.append("🔄 Option de néphrectomie cytoréductrice à discuter en RCP si état général stable")
                if risque == "bon pronostic":
                    reco.append("💊 Traitement recommandé : Double immunothérapie (Nivolumab + Ipilimumab) OU Sunitinib")
                elif risque == "intermédiaire":
                    reco.append("💊 Traitement recommandé : Association TKI + Anti-PD1 (ex. Cabozantinib + Nivolumab)")
                else:
                    reco.append("💊 Traitement recommandé : TKI seul (Pazopanib, Sunitinib) ou combinaison si tolérée")
                reco.append("📆 Suivi rapproché en RCP spécialisée")
            elif age >= 75 and comorbidites == "Oui" and taille <= 4:
                reco.append("🟡 Surveillance active possible pour tumeur < 4cm chez sujet âgé avec comorbidités")
                reco.append("📌 Biopsie rénale recommandée avant surveillance : TDM à 3 mois, puis 6 mois x2, puis annuel")
            elif taille <= 4:
                reco.append("✅ Tumeur solide < 4cm : néphrectomie partielle si possible")
            elif 4 < taille <= 7:
                reco.append("📌 Tumeur solide 4-7cm : traitement conservateur si faisable, sinon néphrectomie totale")
            elif taille > 7:
                reco.append("🔴 Tumeur solide > 7cm : néphrectomie totale recommandée")

        if thrombus == "Oui" or fascia == "Oui":
            reco.append("⚠️ Présence de thrombus ou extension locale → imagerie complémentaire, RCP spécialisée")

        reco.append("🔬 Biopsie à envisager en cas d’incertitude diagnostique (sarcome, lymphome, pseudotumeur)")

        st.markdown("### 🧠 Recommandation IA - Cancer du rein")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_REIN_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# MODULE SONDE DOUBLE J
if menu == "Patient porteur de sonde double J":
    st.header("🔷 Patient porteur de sonde double J")

    age = st.number_input("Âge du patient", min_value=18, max_value=100)
    indication = st.selectbox("Indication de pose", ["Lithiase", "Sténose urétérale", "Post-chirurgie", "Tumeur urétérale", "Colique néphrétique", "Sepsis urinaire"])
    date_pose = st.date_input("Date de pose de la sonde")
    duree_prevue = st.slider("Durée prévue de port (semaines)", min_value=1, max_value=12, value=6)
    atcd_infection = st.radio("Antécédent d'infection urinaire ?", ["Oui", "Non"])

    st.subheader("🔍 Symptômes actuels")
    fievre = st.radio("Fièvre ?", ["Oui", "Non"])
    douleurs = st.radio("Douleurs lombaires / sus-pubiennes ?", ["Oui", "Non"])
    hematurie = st.radio("Hématurie ?", ["Oui", "Non"])
    dysurie = st.radio("Troubles urinaires (brûlures, urgences) ?", ["Oui", "Non"])
    sepsis = st.radio("Tableau de sepsis actuel ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - Sonde double J"):
        reco = []
        reco.append("📅 Durée recommandée maximale : 6 à 8 semaines")

        if fievre == "Oui" or douleurs == "Oui" or sepsis == "Oui":
            reco.append("🚨 Symptômes d'alerte → réévaluation en urgence nécessaire")
            reco.append("🔁 Envisager un changement ou retrait anticipé de la sonde")
            reco.append("💊 Antibiothérapie probabiliste en attendant ECBU")

        reco.append("📌 Conseils hygiéno-diététiques :")
        reco.append("- Boire abondamment pour limiter la stagnation urinaire")
        reco.append("- Éviter les efforts physiques intenses")
        reco.append("- Consulter en cas de douleurs inhabituelles, fièvre ou hématurie persistante")

        reco.append("📆 Suivi : Contrôle avant la date limite de retrait / remplacement de la sonde")

        st.markdown("### 🧠 Recommandation IA - Patient porteur de sonde JJ")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_SONDE_JJ.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# MODULE CANCER TVES
if menu == "Tumeurs des voies excrétrices supérieures (TVES)":
    st.header("🔷 Tumeurs des voies excrétrices supérieures (TVES)")
    age = st.number_input("Âge du patient", min_value=18, max_value=100)
    hematurie = st.radio("Hématurie macroscopique ?", ["Oui", "Non"])
    douleurs = st.radio("Douleurs lombaires ?", ["Oui", "Non"])
    imagerie = st.radio("Aspect suspect à l’imagerie (uroTDM ou uroIRM) ?", ["Oui", "Non"])
    localisation = st.selectbox("Localisation de la lésion", ["Bassinet", "Calices", "Uretère proximal", "Uretère distal"])
    taille = st.slider("Taille de la lésion (mm)", min_value=1, max_value=100)
    multifocal = st.radio("Présence de lésions multifocales ?", ["Oui", "Non"])
    rein_unique = st.radio("Rein unique fonctionnel ou anatomique ?", ["Oui", "Non"])
    biopsie = st.selectbox("Résultat de la biopsie urétérale ou du lavage urinaire", ["Bas grade", "Haut grade", "Non réalisé"])
    metastases = st.radio("Présence de métastases ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - TVES"):
        reco = []

        if metastases == "Oui":
            reco.append("🔴 Tumeur métastatique : traitement systémique recommandé")
            reco.append("💊 Chimiothérapie à base de sels de platine (cisplatine si fonction rénale OK)")
            reco.append("📆 Évaluation en RCP d'oncologie urologique")
        else:
            if biopsie == "Haut grade" or taille > 20 or multifocal == "Oui":
                reco.append("🔺 Haut risque → néphro-urétérectomie totale (NUT) avec ablation du méat urétéral")
            elif biopsie == "Bas grade" and taille <= 20 and multifocal == "Non":
                if rein_unique == "Oui":
                    reco.append("🟡 Préservation nécessaire → traitement conservateur par endoscopie (surveillance rapprochée)")
                else:
                    reco.append("🟢 Tumeur bas grade localisée → ablation endoscopique possible + surveillance")
            else:
                reco.append("⚠️ Cas non classifiable, discussion en RCP indispensable")

            reco.append("📊 Bilan complémentaire : scanner TAP + cystoscopie de contrôle")
            reco.append("🧪 Cytologie urinaire de surveillance tous les 3 à 6 mois selon le grade")

        st.markdown("### 🧠 Recommandation IA (AFU) - Tumeurs des voies excrétrices supérieures")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_TVES_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

