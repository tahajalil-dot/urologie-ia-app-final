from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

def stratifier_tvnim(stade, grade, taille, nombre):
    # Classification AFU
    if stade == "pTa" and grade == "Bas grade" and taille < 30 and nombre == "Unique":
        return "faible"
    if stade == "pTa" and grade == "Bas grade":
        return "intermédiaire"
    if stade == "pT1" or grade == "Haut grade" or nombre in ["Multiple", "Papillomatose vésicale"]:
        # critères très haut risque
        if stade == "pT1" and grade == "Haut grade" and (taille > 30 or nombre != "Unique"):
            return "très haut"
        return "haut"
    return "intermédiaire"

def plan_tvnim(risque):
    traitement, suivi = [], []
    if risque == "faible":
        traitement = [
            "RTUV complète de qualité (détrusor présent)",
            "Instillation postopératoire précoce (IPOP) si pas de CI"
        ]
        suivi = [
            "Cystoscopie à 3 et 12 mois puis annuelle ×5 ans",
            "Cytologie : non systématique",
            "Uro-TDM : non systématique"
        ]
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète",
            "Instillations endovésicales de chimiothérapie (MMC, épirubicine, gemcitabine) 6–8 instillations",
            "Alternative : BCG avec entretien 12 mois"
        ]
        suivi = [
            "Cystoscopie à 3 et 6 mois, puis tous les 6 mois ×2 ans, puis annuelle (≥10 ans)",
            "Cytologie systématique",
        ]
    elif risque == "haut":
        traitement = [
            "RTUV complète ± second look si pT1 ou muscle absent",
            "Instillations endovésicales BCG : induction 6 instillations + entretien 3 ans",
            "Si CI ou échec BCG : chimio endovésicale (MMC, gemcitabine ± docétaxel)"
        ]
        suivi = [
            "Cystoscopie tous les 3 mois ×2 ans, puis tous les 6 mois jusqu’à 5 ans, puis annuelle à vie",
            "Cytologie systématique",
            "Uro-TDM annuel recommandé"
        ]
    else:  # très haut
        traitement = [
            "RTUV complète",
            "Instillations endovésicales BCG avec entretien 3 ans",
            "⚠️ Option : cystectomie précoce avec curage ganglionnaire étendu"
        ]
        suivi = [
            "Cystoscopie tous les 3 mois ×2 ans, puis tous les 6 mois jusqu’à 5 ans, puis annuelle à vie",
            "Cytologie systématique",
            "Uro-TDM annuel obligatoire"
        ]
    return traitement, suivi

def render_tvnim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVNIM (tumeur vésicale n’infiltrant pas le muscle)")
    
    with st.form("tvnim_form"):
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1"])
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        taille = st.slider("Taille maximale de la tumeur (mm)", 1, 100, 10)
        nombre = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple", "Papillomatose vésicale"])
        submitted = st.form_submit_button("🔎 Générer la conduite à tenir")
    
    if submitted:
        risque = stratifier_tvnim(stade, grade, taille, nombre)
        traitement, suivi = plan_tvnim(risque)
        
        st.subheader(f"📊 Risque estimé : {risque.upper()}")
        st.markdown("### 💊 Traitement recommandé")
        for t in traitement: st.markdown("- " + t)
        st.markdown("### 📅 Modalités de suivi")
        for s in suivi: st.markdown("- " + s)

        # Export PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        flow = []
        flow.append(Paragraph(f"Conduite à tenir TVNIM ({risque})", styles["Heading1"]))
        flow.append(Spacer(1,12))
        flow.append(Paragraph("Traitement :", styles["Heading2"]))
        for t in traitement: flow.append(Paragraph("• " + t, styles["Normal"]))
        flow.append(Spacer(1,12))
        flow.append(Paragraph("Modalités de suivi :", styles["Heading2"]))
        for s in suivi: flow.append(Paragraph("• " + s, styles["Normal"]))
        doc.build(flow)
        pdf = buffer.getvalue()
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="CAT_TVNIM.pdf">📥 Télécharger en PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
