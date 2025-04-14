import streamlit as st
import base64

# 💡 Thème clair et esthétique modernisé
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #003366;
        }
        .stButton>button {
            background-color: #004d99;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.5em 1em;
        }
        .stRadio>div>label {
            font-weight: 500;
        }
        .css-1v0mbdj p {
            font-size: 15px;
        }
        .block-container {
            padding: 1rem 2rem;
        }
    </style>
""", unsafe_allow_html=True)

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

# 🔽 Les autres modules sont déjà définis dans le script existant. Aucun changement ici sauf l'ajout de thème.
# Le reste du code (modules HBP, Lithiase, Prostate, Rein, etc.) reste inchangé pour cette étape esthétique.

# ⚠️ Les modifications ci-dessus concernent uniquement le style visuel (couleurs, padding, titres, boutons).
