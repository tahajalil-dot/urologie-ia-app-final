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
    psa_libre_val = 0.0
    if 4 <= psa <= 10:
        psa_libre_val = st.number_input("PSA libre (ng/mL)", min_value=0.0)
    residu = st.number_input("Résidu post-mictionnel (mL)", min_value=0.0)
    actif = st.radio("Activité sexuelle ?", ["Oui", "Non"])
    enfant = st.radio("Souhaite avoir des enfants ?", ["Oui", "Non"])
    marie = st.radio("Statut marital", ["Marié", "Célibataire"])

    if st.button("🔎 Générer la conduite à tenir - HBP"):
        reco = []

        if psa < 4:
            diagnostic = "HBP probable"
        elif 4 <= psa <= 10:
            ratio_libre = psa_libre_val / psa if psa > 0 else 0
            densite = psa / volume if volume > 0 else 0
            if densite > 0.15 or ratio_libre < 0.15:
                diagnostic = f"Suspicion d’ADK prostatique → IRM + biopsies"
                reco.append(f"🔍 Justification : Densité = {densite:.2f}, Ratio libre = {ratio_libre:.2f}")
            else:
                diagnostic = f"HBP probable"
                reco.append(f"ℹ️ Densité = {densite:.2f}, Ratio libre = {ratio_libre:.2f}")
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
            elif ipss > 7 and volume < 40:
                if actif == "Oui":
                    reco.append("💊 Traitement médical par alpha-bloquant (ex. tamsulosine)")
                    reco.append("ℹ️ Justification : vie sexuelle active, éviter les inhibiteurs de la 5α-réductase")
                else:
                    reco.append("💊 Inhibiteur de la 5α-réductase (ex. finastéride)")
                    reco.append("ℹ️ Justification : absence de vie sexuelle active")
            elif ipss > 7 and volume >= 40:
                if actif == "Oui":
                    reco.append("💊 Alpha-bloquant seul (ex. tamsulosine)")
                    reco.append("ℹ️ Justification : vie sexuelle active, éviter inhibiteur 5α-réductase")
                else:
                    reco.append("💊 Inhibiteur 5α-réductase ± alpha-bloquant")
                    reco.append("ℹ️ Justification : absence de vie sexuelle active")
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
            if taille <= 10:
                reco.append("💠 ESWL en 1ère intention si densité < 1000 UH et localisation favorable")
            if 10 < taille <= 20:
                reco.append("🔷 URS ou mini-NLPC en fonction de la localisation")
            if taille > 20:
                reco.append("🔴 NLPC ou chirurgie combinée selon la complexité")

        reco.append("📌 Règles hygiéno-diététiques pour prévenir la récidive :")
        reco.append("- Boire au moins 2,5L/j")
        reco.append("- Réduire sel, protéines animales")
        reco.append("- Éviter excès oxalates")

        st.markdown("### 🧠 Recommandation IA - Lithiase urinaire")
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

        # Détermination du risque selon AFU
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

        # Conduite à tenir
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

        if metastases == "Oui":
            reco.append("🚨 Tumeur métastatique → chimiothérapie ou immunothérapie selon statut PD-L1")
            reco.append("📆 Suivi oncologique spécialisé")

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
    psa_libre = st.number_input("PSA libre (ng/mL)", min_value=0.0, step=0.1)
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

        # Détermination du risque (localisé)
        psa_val = psa
        if gleason == "3+3": g = 6
        elif gleason == "3+4": g = 7
        elif gleason == "4+3": g = 7
        elif gleason == "4+4": g = 8
        else: g = 9

        if metastases == "Non":
            if psa < 10 and g == 6 and tnm in ["T1c", "T2a"]:
                risque = "faible"
            elif 10 <= psa <= 20 or g == 7 or tnm == "T2b":
                risque = "intermédiaire"
            else:
                risque = "élevé"

            reco.append(f"📊 Risque estimé : **{risque.upper()}** selon AFU")

            if esperance == "Non":
                reco.append("🛑 Espérance de vie < 10 ans → Surveillance ou hormonothérapie")
            else:
                if risque == "faible":
                    reco.append("✅ Surveillance active OU prostatectomie / radiothérapie selon préférence")
                elif risque == "intermédiaire":
                    reco.append("🔶 Prostatectomie avec curage pelvien ou Radiothérapie + HT courte (6 mois)")
                else:
                    reco.append("🔴 Prostatectomie + curage étendu ou Radiothérapie + HT longue (18-36 mois)")

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

# MODULE CANCER DU REIN
# Inclut recommandations avancées : classification TNM, traitements selon MSKCC, options sujet fragile
if menu == "Cancer du rein":
    st.header("🔷 Cancer du rein")
    age = st.number_input("Âge du patient", min_value=18, max_value=100, step=1)
    hematurie = st.radio("Hématurie présente ?", ["Oui", "Non"])
    douleur = st.radio("Douleur lombaire ?", ["Oui", "Non"])
    masse_palpable = st.radio("Masse palpable ?", ["Oui", "Non"])
    taille = st.slider("Taille de la tumeur (cm)", min_value=1, max_value=20)
    later = st.radio("Côté atteint", ["Droit", "Gauche"])
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

        if metastases == "Non":
            # Stade T selon taille
            if taille <= 4:
                stade_t = "T1a"
            elif 4 < taille <= 7:
                stade_t = "T1b"
            else:
                stade_t = "T2 ou plus"
            reco.append(f"📌 Stade T estimé : {stade_t}")

            # Propositions selon taille
            if taille <= 4:
                reco.append("🟢 Petite tumeur localisée (< 4 cm) : néphrectomie partielle (voie robot-assistée si possible)")
                if age > 80:
                    reco.append("🛑 Sujet fragile : discuter ablation percutanée ou surveillance active si comorbidités majeures")
            elif 4 < taille <= 7:
                reco.append("🟡 Tumeur intermédiaire (4-7 cm) : néphrectomie partielle si faisable, sinon totale selon balance bénéfices/risques (AFU)")
            else:
                reco.append("🔴 Tumeur > 7 cm : néphrectomie totale recommandée + curage si ganglions visibles")

            reco.append("📊 Réaliser un scanner TAP ou IRM pour bilan d'extension")
            if taille <= 4:
                reco.append("🟢 Petite tumeur localisée (< 4 cm) : néphrectomie partielle (voie robot-assistée si possible)")
            elif 4 < taille <= 7:
                reco.append("🟡 Tumeur intermédiaire (4-7 cm) : Néphrectomie partielle si faisable, sinon totale selon balance bénéfices/risques (AFU)")
            else:
                reco.append("🔴 Tumeur > 7 cm : néphrectomie totale recommandée + curage si ganglions visibles")
            reco.append("📊 Réaliser un scanner TAP ou IRM pour bilan d'extension")

        else:
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

            reco.append("📚 Histologie à préciser après chirurgie : cellules claires, papillaire, chromophobe, etc.")
            reco.append("📆 Suivi rapproché en RCP spécialisée")
            reco.append("- Inhibiteurs de tyrosine kinase (TKI)")
            reco.append("- Immunothérapie (anti-PD1/PD-L1) si éligible")
            reco.append("- Combinations selon profil moléculaire (nivolumab + cabozantinib, etc.)")

            reco.append("📆 Suivi rapproché en RCP spécialisée")

        st.markdown("### 🧠 Recommandation IA (AFU) - Cancer du rein")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_REIN_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)
