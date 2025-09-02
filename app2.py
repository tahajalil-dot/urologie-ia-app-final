# app.py — Urology Assistant AI (Accueil + Vessie + Rein + HBP)
# Version intégrée : 2025-09-02
# Modules inclus :
# - Vessie (TVNIM, TVIM, Métastatique)
# - Rein (Non métastatique, Métastatique — IMDC/Heng ou MSKCC/Motzer)
# - HBP (PSAD + Options numérotées)

import base64
from datetime import datetime
from pathlib import Path
import html as ihtml
import io
import streamlit as st

# =========================
# CONFIG + THEME CLAIR (VERT)
# =========================
st.set_page_config(page_title="Urology Assistant AI", layout="wide")

st.markdown("""
<style>
:root, html, body, .stApp, .block-container { background:#ffffff !important; color:#111 !important; }
[data-testid="stHeader"], header { background:#ffffff !important; }

h1,h2,h3,h4,h5,h6 { color:#0B5D3B !important; }
a, a:visited { color:#0B5D3B !important; }

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div { color:#111 !important; }

.stButton > button {
  background:#0B5D3B !important; color:#fff !important; border-radius:10px; padding:0.6rem 1rem; border:none;
}
.stButton > button:hover { background:#0E744C !important; }

.header-green {
  padding:18px 22px; background:linear-gradient(90deg,#F6FBF7,#EAF6EE);
  border:1px solid #d8eadf; border-radius:12px; margin-bottom:18px;
}

.cat-bar { height:6px; background:#DFF3E6; border-radius:6px; margin-bottom:12px; }

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
APP_SUBTITLE = "Assistant intelligent pour la décision clinique — *démo, ne remplace pas les RBP officielles*"

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
    st.markdown(f"<div class='header-green'><h1 style='margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1></div>", unsafe_allow_html=True)

def btn_home_and_back(show_back: bool = False, back_label: str = "Tumeur de la vessie"):
    cols = st.columns([1, 3])
    with cols[0]:
        st.button("🏠 Accueil", on_click=go_home)
    if show_back:
        with cols[1]:
            st.button(f"⬅️ Retour : {back_label}", on_click=lambda: go_module(back_label))

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

def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title}")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr: continue
        lines.append(f"== {sec} ==")
        for x in arr:
            lines.append(f"• {x}")
        lines.append("")
    lines.append("Réfs : AFU/EAU — version simplifiée.")
    return "\n".join(lines)

def offer_exports(report_text: str, basename: str):
    bio = io.BytesIO(report_text.encode("utf-8"))
    st.download_button("📝 Télécharger .txt", data=bio, file_name=f"{basename}.txt")
    html = f"<!doctype html><html lang='fr'><meta charset='utf-8'><title>{basename}</title><pre>{ihtml.escape(report_text)}</pre></html>"
    st.download_button("📄 Télécharger .html", data=html.encode("utf-8"), file_name=f"{basename}.html", mime="text/html")

# =========================
# LOGIQUE CLINIQUE — Rein (localisé + métastatique)
# =========================
def plan_rein_local(cT: str, cN_pos: bool, size_cm: float, thrombus: str,
                    rein_unique_ou_CKD: bool, tumeur_hilaire: bool,
                    exophytique: bool, age: int, haut_risque_op: bool,
                    biopsie_dispo: bool):
    # retourne dict {donnees, traitement, suivi, notes} avec options numérotées
    ...

def calc_imdc(karnofsky_lt80: bool, time_to_systemic_le_12mo: bool,
              hb_basse: bool, calcium_haut: bool,
              neutro_hauts: bool, plaquettes_hautes: bool):
    # classification Heng
    ...

def calc_mskcc(karnofsky_lt80: bool, time_to_systemic_le_12mo: bool,
               hb_basse: bool, calcium_haut: bool, ldh_haut: bool):
    # classification Motzer
    ...

def plan_rein_meta(histo: str, score: int, group: str, score_system_label: str,
                   oligo: bool, bone: bool, brain: bool, liver: bool,
                   io_contra: bool):
    # retourne dict {donnees, stratification, traitement, suivi, notes}
    ...

# Ici tu dois implémenter : plan_rein_local, calc_imdc, calc_mskcc, plan_rein_meta
# + UI : render_kidney_menu, render_kidney_local_page, render_kidney_meta_page

# =========================
# PAGES (UI)
# =========================
def render_kidney_menu():
    btn_home_and_back()
    st.markdown("## Tumeur du rein")
    st.caption("Choisissez le sous-module")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Non métastatique", use_container_width=True,
                  on_click=lambda: go_module("Rein: Non métastatique"))
    with c2:
        st.button("Métastatique", use_container_width=True,
                  on_click=lambda: go_module("Rein: Métastatique"))

def render_kidney_local_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur non métastatique")
    with st.form("kidney_local_form"):
        # champs du formulaire localisé
        ...
    # appel plan_rein_local + affichage résultats/export

def render_kidney_meta_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur métastatique")
    with st.form("kidney_meta_form"):
        # champs du formulaire avec choix IMDC ou MSKCC
        ...
    # appel plan_rein_meta + affichage résultats/export

# ... (toutes les fonctions render_xxx déjà intégrées : rein local, rein meta, hbp, vessie...)

# =========================
# ROUTING
# =========================

page = st.session_state["page"]
if page == "Accueil":
    render_home_wrapper()
elif page == "Tumeur de la vessie":
    render_vessie_menu()
elif page.startswith("Vessie:"):
    if page == "Vessie: TVNIM": render_tvnim_page()
    elif page == "Vessie: TVIM": render_tvim_page()
    elif page == "Vessie: Métastatique": render_vessie_meta_page()
elif page == "Tumeur du rein":
    render_kidney_menu()
elif page == "Rein: Non métastatique":
    render_kidney_local_page()
elif page == "Rein: Métastatique":
    render_kidney_meta_page()
elif page == "Hypertrophie bénigne de la prostate (HBP)":
    render_hbp_page()
else:
    render_generic(page)
