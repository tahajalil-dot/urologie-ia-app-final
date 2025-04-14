import streamlit as st
import base64

st.set_page_config(page_title="Assistant IA - Urologie (AFU)", layout="wide")

# 🎨 Thème esthétique clair
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            padding: 1.5rem;
        }
        h1, h2, h3, h4 {
            color: #002b5c;
        }
        .stButton>button {
            background-color: #004d99;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.4em 1em;
        }
        .stRadio>div>label {
            font-weight: 500;
        }
        .block-container {
            padding: 1rem 2rem;
        }
        .stDownloadButton>button {
            background-color: #008080;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

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

# Le reste du code des modules (HBP, Lithiase, etc.) reste inchangé ici pour conserver la logique médicale.
# Tu peux continuer à travailler sur l’esthétique interne de chaque module si tu veux :
# - Encadrer les sections avec st.markdown("---")
# - Ajouter des icônes 🧾 ou 🎯 pour guider l’œil
# - Mettre des titres de sections secondaires (st.subheader(...))
