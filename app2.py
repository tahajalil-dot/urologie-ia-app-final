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

# 🔷 MODULE HBP
# (Module HBP ici inchangé)

# 🔴 MODULE CANCER DE LA PROSTATE

# 🟣 MODULE CANCER DU REIN
if menu == "Cancer du rein":
    st.header("🟣 Cancer du Rein")
    tnm = st.selectbox("Stade clinique (TNM)", ["T1a", "T1b", "T2", "T3", "T4"])
    taille = st.number_input("Taille tumorale (cm)", min_value=0.0, step=0.1)
    laterale = st.selectbox("Localisation", ["Unilatéral", "Bilatéral"])
    metas = st.radio("Présence de métastases ?", ["Non", "Oui"])
    type_metas = st.selectbox("Type de métastases", ["Aucune", "Oligométastatique", "Plurimétastatique"])
    sites_metas = st.multiselect("Sites métastatiques", ["Poumon", "Foie", "Os", "Cerveau", "Ganglions", "Autre"])
    mskcc_risques = st.multiselect("Critères MSKCC présents", [
        "PS > 1",
        "Temps < 1 an entre diagnostic et traitement",
        "Anémie",
        "Hypercalcémie",
        "LDH élevé",
        "Nombre de métastases > 2"
    ])

    if st.button("🔎 Générer la conduite à tenir - Rein"):
        reco = []

        if metas == "Non":
            if tnm == "T1a":
                reco.append("✅ Petite tumeur localisée (T1a) → Néphrectomie partielle recommandée si faisable techniquement")
            elif tnm in ["T1b", "T2"]:
                reco.append("💡 Tumeur localisée > 4 cm → Néphrectomie totale ou partielle selon faisabilité, fonction rénale et bilatéralité")
            elif tnm in ["T3", "T4"]:
                reco.append("📌 Tumeur localement avancée (T3-T4) → Néphrectomie élargie avec analyse du thrombus cave ± curage ganglionnaire")
        else:
            reco.append("⚠️ Forme métastatique → Traitement systémique")
            if len(mskcc_risques) <= 1:
                groupe = "bon pronostic"
            elif len(mskcc_risques) <= 2:
                groupe = "intermédiaire"
            else:
                groupe = "mauvais pronostic"

            reco.append(f"📊 Score MSKCC → {groupe.upper()}")

            if groupe in ["bon pronostic", "intermédiaire"]:
                reco.append("💊 Traitement de 1ère ligne : Double immunothérapie (nivolumab + ipilimumab) ou combinaison ITK + IO selon profil")
                reco.append("🔄 Discuter néphrectomie cytoréductrice après bonne réponse initiale si patient opérable")
            else:
                reco.append("🩺 Mauvais pronostic : prise en charge symptomatique + traitement palliatif adapté")

            if laterale == "Bilatéral":
                reco.append("⚠️ Présence de tumeurs bilatérales → Évaluation personnalisée en RCP avec stratégie conservatrice si possible")

            if "T3" in tnm or "T4" in tnm:
                reco.append("🧠 Important : discuter en RCP la gestion des thrombus cave (IRM/angio-scanner requis)")

        reco.append("📅 Suivi post-thérapeutique : imagerie tous les 3-6 mois la 1ère année, surveillance de la fonction rénale, bilan biologique complet")

        st.markdown("### 🧠 Recommandation IA (AFU) - Cancer du Rein")
        for r in reco:
            st.markdown(r)
        full_report = "\n".join(reco)
        b64 = base64.b64encode(full_report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_REIN_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)
if menu == "Cancer de la prostate":
    st.header("🔴 Cancer de la Prostate")
    age = st.number_input("Âge du patient", min_value=40, max_value=100, step=1)
    psa = st.number_input("PSA total (ng/mL)", min_value=0.0, step=0.1)
    stade_clinique = st.selectbox("Stade clinique (T)", ["T1c", "T2a", "T2b", "T2c", "T3a", "T3b", "T4"])
    gleason = st.selectbox("Score ISUP (Gleason)", ["1", "2", "3", "4", "5"])
    imagerie = st.selectbox("IRM prostatique - PIRADS", ["1", "2", "3", "4", "5"])
    metas = st.radio("Métastases présentes ?", ["Non", "Oui"])
    sites = st.multiselect("Sites de métastases", ["Os", "Poumon", "Foie", "Ganglions", "Cerveau"])
    oligo = st.radio("Maladie oligométastatique ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - Prostate"):
        reco = []

        if metas == "Non":
            if stade_clinique in ["T1c", "T2a"] and gleason in ["1", "2"] and psa < 10:
                reco.append("🟢 Cancer localisé à faible risque → Surveillance active ou prostatectomie radicale")
            elif stade_clinique in ["T2b", "T2c"] or gleason == "3" or 10 <= psa <= 20:
                reco.append("🟡 Risque intermédiaire → Radiothérapie + hormonothérapie courte ou chirurgie")
            elif stade_clinique in ["T3a", "T3b", "T4"] or gleason in ["4", "5"] or psa > 20:
                reco.append("🔴 Haut risque localisé ou localement avancé → Radiothérapie + hormonothérapie longue ou chirurgie + rattrapage")
        else:
            reco.append("⚠️ Maladie métastatique")
            if oligo == "Oui":
                reco.append("🔶 Forme oligométastatique → traitement local possible (chirurgie ou radiothérapie) + hormonothérapie")
            else:
                reco.append("💊 Forme pluri-métastatique → hormonothérapie + chimiothérapie ± agents ciblés")

        reco.append("📋 Suivi selon protocole AFU : PSA trimestriel, IRM ou TEP si suspicion de récidive")

        st.markdown("### 🧠 Recommandation IA (AFU) - Cancer de la Prostate")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_PROSTATE_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# 🟡 MODULE CANCER DE LA VESSIE (TVNIM / TVIM)
if menu == "Cancer de la vessie (TVNIM / TVIM)":
    st.header("🟡 Tumeur de la Vessie (TVNIM / TVIM)")
    stade = st.selectbox("Stade tumoral", ["TVNIM", "TVIM"])
    taille = st.selectbox("Taille de la tumeur", ["< 3 cm", ">= 3 cm"])
    multifocale = st.radio("Tumeur multifocale ?", ["Oui", "Non"])
    haut_grade = st.radio("Tumeur de haut grade ?", ["Oui", "Non"])
    cis = st.radio("CIS associé ?", ["Oui", "Non"])
    envahissement_muscle = st.radio("Envahissement du muscle détrusor confirmé ?", ["Oui", "Non"])
    metastase = st.radio("Métastases à distance ?", ["Non", "Oui"])
    score_efu = st.radio("Score EORTC élevé ? (si TVNIM)", ["Oui", "Non"])

    if st.button("🔎 Recommandation IA - Vessie"):
        reco = []

        if stade == "TVNIM":
            reco.append("🔵 Tumeur NON infiltrant le muscle")
            if haut_grade == "Non" and taille == "< 3 cm" and multifocale == "Non" and cis == "Non" and score_efu == "Non":
                reco.append("🟢 Risque faible → Résection complète + instillation unique de mitomycine dans les 6 heures post-TURB")
                reco.append("📅 Suivi : cystoscopie à 3 mois, puis à 9 mois, puis annuelle si normal")
            elif haut_grade == "Oui" and (cis == "Oui" or multifocale == "Oui" or taille == ">= 3 cm"):
                reco.append("🔴 Risque élevé → Résection complète + BCG selon protocole intensif (6 sem. induction + maintenance 1 an ou 3 ans selon récidive)")
                reco.append("📋 Protocole BCG : 1 instillation/semaine x6 → puis 3 instillations à M3, M6, M12, M18, M24, M30, M36")
                reco.append("📅 Suivi rapproché : cystoscopie à 3 mois, puis tous les 3 mois la 1ère année")
            else:
                reco.append("🟡 Risque intermédiaire → TURB + mitomycine répétée ou BCG court (6 semaines)")
                reco.append("📋 BCG possible selon profil si récidive ou progression → évaluation régulière nécessaire")
                reco.append("📅 Suivi : cystoscopie à 3, 6, 9, 12 mois")

        elif stade == "TVIM":
            reco.append("🔴 Tumeur infiltrant le muscle (TVIM)")

            if envahissement_muscle == "Oui" and metastase == "Non":
                reco.append("🧠 Muscle invasif confirmé sans métastase → Indication de cystectomie totale + curage ganglionnaire")
                reco.append("💉 Chimiothérapie néoadjuvante recommandée (MVAC dose dense ou Gemcitabine/Cisplatine)")
            elif metastase == "Oui":
                reco.append("⚠️ Maladie métastatique → Chimiothérapie systémique ± immunothérapie (anti-PD1/PDL1 selon profil)")
            else:
                reco.append("❗ Confirmation de l'infiltration musculaire nécessaire avant décision thérapeutique définitive")

            reco.append("📅 Suivi post-cystectomie : bilan biologique + scanner TAP tous les 6 mois pendant 2 ans")

        st.markdown("### 🧠 Recommandation IA (AFU) - Tumeur de Vessie")
        for r in reco:
            st.markdown(r)
        full_report = "\n".join(reco)
        b64 = base64.b64encode(full_report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_VESSIE_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)


# 🔵 MODULE PATIENT PORTEUR DE SONDE DOUBLE J
if menu == "Patient porteur de sonde double J":
    st.header("🔵 Patient porteur de sonde double J (DJ)")
    duree = st.selectbox("Depuis combien de temps la sonde DJ est-elle en place ?", ["< 2 semaines", "2–6 semaines", "> 6 semaines"])
    indication = st.selectbox("Indication initiale de la sonde DJ", [
        "Lithiase urétérale",
        "Sténose urétérale",
        "Post-opératoire (chirurgie endo-urologique)",
        "Prévention de complication",
        "Autre"
    ])
    symptomes = st.multiselect("Symptômes actuels", [
        "Douleur lombaire",
        "Hématurie",
        "Fièvre",
        "Brûlures mictionnelles",
        "Pollakiurie",
        "Aucun"
    ])
    terrain = st.multiselect("Terrain du patient", [
        "Diabétique",
        "Immunodéprimé",
        "Antécédents de pyélonéphrite",
        "Aucun terrain particulier"
    ])

    if st.button("🔎 Recommandation IA - Sonde DJ"):
        reco = []

        if "Fièvre" in symptomes:
            reco.append("⚠️ Fièvre → Urgence : suspicion de pyélonéphrite obstructive → hospitalisation et drainage urgent si nécessaire")
        if duree == "> 6 semaines":
            reco.append("⚠️ DJ en place > 6 semaines → retrait ou changement impératif pour éviter infection/encrassement")
        if "Douleur lombaire" in symptomes:
            reco.append("🔶 Douleur lombaire → vérifier position et perméabilité de la sonde (imagerie)")
        if "Brûlures mictionnelles" in symptomes or "Pollakiurie" in symptomes:
            reco.append("💊 Symptômes irritatifs → alpha-bloquant ou anticholinergique selon tolérance")

        reco.append("📋 Conseils hygiéno-diététiques :")
        reco.append("- Boire ≥ 2 L/jour sauf contre-indication")
        reco.append("- Éviter les efforts violents, vigilance lors d’activités physiques")
        reco.append("- Consulter en cas de douleurs importantes, fièvre ou urines troubles")

        reco.append("📅 Suivi recommandé : consultation prévue avant 6 semaines, retrait ou remplacement selon contexte clinique")

        st.markdown("### 🧠 Recommandation IA (AFU) - Sonde double J")
        for r in reco:
            st.markdown(r)
        full_report = "\n".join(reco)
        b64 = base64.b64encode(full_report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_SONDE_DJ_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# 🟠 MODULE TVES (Tumeurs des voies excrétrices supérieures)
if menu == "Tumeurs des voies excrétrices supérieures (TVES)":
    st.header("🟠 Tumeurs des voies excrétrices supérieures (TVES)")
    haut_grade = st.radio("Tumeur de haut grade ?", ["Oui", "Non"])
    multifocale = st.radio("Tumeur multifocale ?", ["Oui", "Non"])
    taille = st.selectbox("Taille de la tumeur", ["< 2 cm", ">= 2 cm"])
    aspect_endoscopique = st.radio("Aspect endoscopique favorable ?", ["Oui", "Non"])
    rein_unique = st.radio("Rein unique fonctionnel ?", ["Oui", "Non"])
    metastase = st.radio("Présence de métastases ?", ["Non", "Oui"])

    if st.button("🔎 Recommandation IA - TVES"):
        reco = []

        if metastase == "Oui":
            reco.append("⚠️ Maladie métastatique → Chimiothérapie à base de sels de platine ± immunothérapie (selon profil moléculaire)")
        else:
            risque = "élevé" if haut_grade == "Oui" or multifocale == "Oui" or taille == ">= 2 cm" or aspect_endoscopique == "Non" else "faible"
            reco.append(f"📊 Risque évalué : {risque.upper()}")

            if risque == "faible":
                reco.append("✅ Risque faible → Traitement conservateur : urétéroscopie + résection + surveillance stricte")
                reco.append("📋 Possibilité d’instillations endocavitaire par mitomycine C (off-label mais utilisée dans certains centres)")
                reco.append("📅 Suivi : endoscopie + cytologie urinaire + TDM annuel")
            else:
                reco.append("🔴 Risque élevé → Néphro-urétérectomie totale (NUT) avec curage ganglionnaire")
                reco.append("💉 Chimiothérapie adjuvante recommandée si fonction rénale conservée (Gemcitabine + Cisplatine)")
                if rein_unique == "Oui":
                    reco.append("⚠️ Rein unique → Discussion RCP pour stratégie conservatrice personnalisée")
                reco.append("📅 Surveillance post-opératoire : cystoscopie régulière + scanner TAP tous les 6 mois pendant 2 ans")

        st.markdown("### 🧠 Recommandation IA (AFU) - Tumeurs des VES")
        for r in reco:
            st.markdown(r)
        full_report = "\n".join(reco)
        b64 = base64.b64encode(full_report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_TVES_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

# 🟢 MODULE LITHIASE URINAIRE
if menu == "Lithiase urinaire":
    st.header("🟢 Lithiase Urinaire")
    taille = st.number_input("Taille du calcul (en mm)", min_value=1, max_value=50, step=1)
    localisation = st.selectbox("Localisation du calcul", ["Calice", "Bassinet", "Jonction pyélo-urétérale", "Uretère proximal", "Uretère moyen", "Uretère distal", "Vessie"])
    radio_opaque = st.radio("Calcul radio-opaque ?", ["Oui", "Non"])
    nombre = st.radio("Calcul unique ?", ["Oui", "Non"])
    infection = st.radio("Signes d'infection associée ?", ["Oui", "Non"])
    rein_unique = st.radio("Patient avec rein unique ?", ["Oui", "Non"])
    douleurs = st.radio("Douleurs invalidantes persistantes ?", ["Oui", "Non"])

    if st.button("🔎 Générer la conduite à tenir - Lithiase"):
        reco = []

        if infection == "Oui":
            reco.append("⚠️ Infection urinaire → drainage en urgence (sonde JJ ou néphrostomie) avant tout traitement lithiasique")

        if taille <= 6 and localisation == "Uretère distal":
            reco.append("✅ Essai de traitement médical expulsif (alpha-bloquant) pendant 2-4 semaines")
        else:
            if taille <= 20:
                if localisation in ["Uretère proximal", "Jonction pyélo-urétérale"]:
                    reco.append("🔧 URS rigide ou souple selon accès et matériel disponible")
                elif localisation in ["Calice", "Bassinet"]:
                    if radio_opaque == "Oui":
                        reco.append("💥 ESWL possible (lithotripsie extracorporelle à onde de choc)")
                    else:
                        reco.append("🔧 URS souple ou mini-NLPC selon expertise")
                else:
                    reco.append("🔧 URS classique en 1re intention")
            else:
                reco.append("🩺 Calcul > 2 cm → mini-NLPC ou NLPC classique")

        if rein_unique == "Oui":
            reco.append("⚠️ Rein unique → privilégier URS ou NLPC selon l'emplacement, éviter ESWL seule")

        reco.append("📋 Règles hygiéno-diététiques :")
        reco.append("- Boire 2 à 2,5 L d'eau par jour")
        reco.append("- Réduire sel, protéines animales, et éviter les sodas")
        reco.append("- Surveillance annuelle si récidive ou terrain à risque")

        st.markdown("### 🧠 Recommandation IA (AFU) - Lithiase Urinaire")
        for r in reco:
            st.markdown(r)
        rapport = "\n".join(reco)
        b64 = base64.b64encode(rapport.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="recommandation_LITHIASE_AFU.txt">📥 Télécharger cette recommandation</a>'
        st.markdown(href, unsafe_allow_html=True)

