# app.py — Urology Assistant AI (Accueil + Vessie TVNIM/TVIM/Métastatique + HBP)
# Version: 2025-09-02
# Notes:
# - Ce prototype vise à structurer la décision clinique (AFU/EAU 2024–2026 à vérifier localement).
# - Le module HBP a été modifié pour: (1) ne PAS proposer de médical si indication chirurgicale stricte
#   (échec médical OU complications OU lobe médian) ; (2) présenter toutes les options en "Option 1, 2, ...".

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

st.markdown(
    """
<style>
:root, html, body, .stApp, .block-container { background:#ffffff !important; color:#111 !important; }
[data-testid="stHeader"], header { background:#ffffff !important; }

/* Titres & liens */
h1,h2,h3,h4,h5,h6 { color:#0B5D3B !important; }
a, a:visited { color:#0B5D3B !important; }

/* Texte markdown par défaut */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div { color:#111 !important; }

/* Boutons */
.stButton > button {
  background:#0B5D3B !important; color:#fff !important; border-radius:10px; padding:0.6rem 1rem; border:none;
}
.stButton > button:hover { background:#0E744C !important; }

/* Inputs */
div[data-baseweb="select"] > div,
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background:#fff !important; color:#111 !important; border:1px solid #e4efe8 !important;
}

/* En-tête (gradient vert très clair) */
.header-green {
  padding:18px 22px; background:linear-gradient(90deg,#F6FBF7,#EAF6EE);
  border:1px solid #d8eadf; border-radius:12px; margin-bottom:18px;
}

/* Barre décorative sous les catégories */
.cat-bar { height:6px; background:#DFF3E6; border-radius:6px; margin-bottom:12px; }

/* Tableaux (HTML) pour Données & Stratification */
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
""",
    unsafe_allow_html=True,
)

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
    st.markdown(
        f"<div class='header-green'><h1 style='margin:0;font-weight:800;font-size:28px'>{APP_TITLE}</h1></div>",
        unsafe_allow_html=True,
    )


def btn_home_and_back(show_back: bool = False, back_label: str = "Tumeur de la vessie"):
    cols = st.columns([1, 3])
    with cols[0]:
        st.button("🏠 Accueil", on_click=go_home)
    if show_back:
        with cols[1]:
            st.button(f"⬅️ Retour : {back_label}", on_click=lambda: go_module(back_label))


# ===== Tableaux (HTML 2 colonnes) — pour Données & Stratification =====

def esc(x: str) -> str:
    return ihtml.escape(str(x))


def render_kv_table(title, pairs, col1="Élément", col2="Détail"):
    if not pairs:
        return
    st.markdown(f"### {esc(title)}")
    html = [
        f"<div class='section-block'><table class='kv-table'><thead><tr><th>{esc(col1)}</th><th>{esc(col2)}</th></tr></thead><tbody>",
    ]
    for k, v in pairs:
        html.append(f"<tr><td><strong>{esc(k)}</strong></td><td>{esc(v)}</td></tr>")
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# ===== Export helpers (download_button) =====

def build_report_text(title: str, sections: dict) -> str:
    lines = []
    lines.append(f"Urology Assistant AI — {title} (AFU/EAU 2024–2026 — à vérifier)")
    lines.append(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    for sec, arr in sections.items():
        if not arr:
            continue
        lines.append(f"== {sec} ==")
        for x in arr:
            lines.append(f"• {x}")
        lines.append("")
    lines.append("Réfs : AFU/EAU — synthèse PROVISOIRE pour prototypage.")
    return "\n".join(lines)


def offer_exports(report_text: str, basename: str):
    bio = io.BytesIO(report_text.encode("utf-8"))
    st.download_button("📝 Télécharger le rapport .txt", data=bio, file_name=f"{basename}.txt")

    html = f"""<!doctype html><html lang='fr'><meta charset='utf-8'><title>{basename}</title><pre>{ihtml.escape(report_text)}</pre></html>"""
    st.download_button(
        "📄 Télécharger le rapport .html",
        data=html.encode("utf-8"),
        file_name=f"{basename}.html",
        mime="text/html",
    )


# =========================
# LOGIQUE CLINIQUE — HBP 
# =========================
from typing import Optional, Any, List, Tuple, Dict, Union

# -- helper bool robuste (gère Oui/Non, true/false, 1/0, etc.)
def _to_bool(x: Any) -> bool:
    if isinstance(x, bool): return x
    if isinstance(x, (int, float)): return x != 0
    if isinstance(x, str): return x.strip().lower() in {"1","true","vrai","oui","y","yes"}
    return bool(x)

def classer_ipss(ipss: int) -> str:
    if ipss <= 7: return "légers"
    if ipss <= 19: return "modérés"
    return "sévères"

# =========================
# TRIAGE ADK (TR + PSAD si PSA ≥ 4)
# =========================
def eval_suspicion_adk(psa_total: float, volume_ml: int, tr_suspect: Union[bool,str,int,float]) -> Tuple[bool, List[str], Optional[float]]:
    """
    - TR suspect → ADK (IRM multiparamétrique + biopsies)
    - PSA ≥ 4 → PSAD = PSA/volume ; si PSAD > 0,15 → ADK ; sinon HBP
    - PSA < 4 → HBP
    - Si PSA ≥ 4 mais volume inconnu/0 → mesurer le volume (TRUS/IRM) pour calculer PSAD
    """
    exp: List[str] = []
    psad: Optional[float] = None
    if _to_bool(tr_suspect):
        exp.append("TR suspect → orientation ADK (IRM multiparamétrique puis biopsies).")
        return True, exp, psad

    if psa_total >= 4.0:
        if volume_ml and volume_ml > 0:
            psad = psa_total / float(volume_ml)
            exp.append(f"Densité PSA (PSAD) = {psad:.2f}.")
            if psad > 0.15:
                exp.append("PSAD > 0,15 → critère suspect → IRM + biopsies (orientation ADK).")
                return True, exp, psad
            else:
                exp.append("PSAD ≤ 0,15 → non suspect immédiat → poursuite de la CAT HBP.")
        else:
            exp.append("PSA ≥ 4 mais volume inconnu/0 → mesurer le volume (TRUS/IRM) pour calculer la PSAD.")
    else:
        exp.append("PSA < 4 → profil HBP (pas d’orientation ADK immédiate).")
    return False, exp, psad

# =========================
# Coeur logique : NOUVELLE signature (sans lobe_median / preservation_ejac)
# =========================
def _plan_hbp_core(
    age: int,
    volume_ml: int,
    ipss: int,
    psa_total: float,
    tr_suspect: Union[bool,str,int,float],
    anticoag: Union[bool,str,int,float],
    ci_chirurgie: Union[bool,str,int,float],
    refus_chir: Union[bool,str,int,float],
    infections_recid: Union[bool,str,int,float],
    retention: Union[bool,str,int,float],
    calculs: Union[bool,str,int,float],
    hematurie_recid: Union[bool,str,int,float],
    ir_post_obstacle: Union[bool,str,int,float],
    echec_medical: Union[bool,str,int,float],
    *,
    stockage_predominant: Union[bool,str,int,float] = False,
    rpm_ml: Optional[int] = None,
    dysfonction_erectile: Union[bool,str,int,float] = False,
) -> Dict[str, Any]:
    # normalisation
    tr_suspect        = _to_bool(tr_suspect)
    anticoag          = _to_bool(anticoag)
    ci_chirurgie      = _to_bool(ci_chirurgie)
    refus_chir        = _to_bool(refus_chir)
    infections_recid  = _to_bool(infections_recid)
    retention         = _to_bool(retention)
    calculs           = _to_bool(calculs)
    hematurie_recid   = _to_bool(hematurie_recid)
    ir_post_obstacle  = _to_bool(ir_post_obstacle)
    echec_medical     = _to_bool(echec_medical)
    stockage_predominant = _to_bool(stockage_predominant)
    dysfonction_erectile = _to_bool(dysfonction_erectile)

    # Données
    donnees: List[Tuple[str,str]] = [
        ("Âge", f"{age} ans"),
        ("Volume prostatique", f"{volume_ml} mL"),
        ("IPSS", f"{ipss} ({classer_ipss(ipss)})"),
        ("PSA total", f"{psa_total:.2f} ng/mL"),
        ("TR suspect", "Oui" if tr_suspect else "Non"),
        ("Anticoagulants/antiagrégants", "Oui" if anticoag else "Non"),
        (
            "Complications",
            ", ".join([txt for ok, txt in [
                (infections_recid, "IU récidivantes"),
                (retention, "Rétention compliquée/sevrage impossible"),
                (calculs, "Calcul vésical"),
                (hematurie_recid, "Hématurie récidivante liée à l’HBP"),
                (ir_post_obstacle, "IR obstructive liée à l’obstacle"),
            ] if ok]) or "Aucune"
        ),
        ("Échec du traitement médical", "Oui" if echec_medical else "Non"),
        ("LUTS de remplissage prédominants", "Oui" if stockage_predominant else "Non"),
    ]
    if rpm_ml is not None:
        donnees.append(("Résidu post-mictionnel (RPM)", f"{rpm_ml} mL"))

    # (0) TRIAGE ADK
    suspect_adk, exp_adk, psad = eval_suspicion_adk(psa_total, volume_ml, tr_suspect)
    if psad is not None:
        donnees.append(("Densité PSA (PSAD)", f"{psad:.2f}"))
    if suspect_adk:
        traitement = [
            "Option : IRM prostatique multiparamétrique, Biopsies prostatiques ciblées ± systématiques selon IRM.",
        ]
        return {"donnees": donnees, "traitement": traitement, "notes": exp_adk}

    # (1) Indication chirurgicale stricte
    complications_presentes = any([infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle])
    indication_chir_stricte = echec_medical or complications_presentes

    options: List[str] = []
    n = 1

    # (2) Pas d'indication chirurgicale stricte → médical d'abord
    if not indication_chir_stricte:
        if ipss <= 7:
            # STRICTEMENT 2 options
            options.append(
                f"Option {n} : abstention-surveillance — informer du faible risque évolutif + conseils hygiéno-diététiques "
                "(réduire apports hydriques après 18h, diminuer caféine/alcool, traiter la constipation)."
            ); n += 1
            options.append(
                f"Option {n} : traitement médical — α-bloquant (monothérapie). "
                "Action rapide, améliore SBAU et débit."
            ); n += 1
        else:
            options.append(
                f"Option {n} : α-bloquant en première intention puis réévaluation clinique/IPSS pour vérifier amélioration ou échec sous traitement."
            ); n += 1
            if volume_ml > 40:
                options.append(
                    f"Option {n} : inhibiteur de la 5α-réductase L , ↓risque de RAU car il diminue le volume prostatique; PSA mesuré ≈ 50 % du réel, efficacité sur plus de 3 mois )."
                ); n += 1
                options.append(
                    f"Option {n} : association α-bloquant + I5AR si monothérapie insuffisante ."
                ); n += 1
            if stockage_predominant and (rpm_ml is not None and rpm_ml < 150):
                options.append(
                    f"Option {n} : anticholinergique si SBAU de remplissage prédominants ET RPM < 150 mL "
                    "(plutôt en ajout si persistance sous α-bloquant)."
                ); n += 1
            options.append(
                f"Option {n} : alternative — phytothérapie (Serenoa repens / Pygeum africanum) ."
            ); n += 1
          

    # (3) Indication chirurgicale stricte → chirurgie si possible, sinon alternatives/palliatif
    if indication_chir_stricte and not ci_chirurgie and not refus_chir:
        if 30 <= volume_ml <= 70:
            options.append(f"Option {n} : RTUP (mono/bipolaire) ou vaporisation endoscopique (laser/bipolaire) pour 30–70 mL."); n += 1
        if volume_ml >= 70:
            options.append(f"Option {n} : énucléation endoscopique (HoLEP/ThuLEP/BipolEP) pour ≥ 70–100+ mL."); n += 1
        if volume_ml > 100:
            options.append(f"Option {n} : adénomectomie sus-pubienne (ouverte/robot) si très gros volumes ou si énucléation indisponible."); n += 1
        if anticoag or (30 <= volume_ml <= 70):
            options.append(f"Option {n} : vaporisation laser (GreenLight) en cas de risque hémorragique/anticoagulants."); n += 1
        if volume_ml <= 40:
            options.append(f"Option {n} : incision cervico-prostatique si petit volume (≤ 30–40 mL)."); n += 1
    elif indication_chir_stricte and (ci_chirurgie or refus_chir):
        if volume_ml > 80:
            options.append(f"Option {n} : alternative — embolisation des artères prostatiques (diminution du volume) selon contexte."); n += 1
        options.append(f"Option {n} : palliatif — autosondages intermittents, ou sonde vésicale/cathéter sus-pubien à demeure."); n += 1

    notes: List[str] = [
        "Réévaluation après α-bloquant : une semaine (clinique, IPSS, tolérance).",
        "Avant toute chirurgie : réaliser un ECBU ; information et consentement indispensables.",
        "Complications chirurgicales : perop (saignement; TUR syndrome en monopolaire), précoces (RAU, hématurie/caillots, infection, TVP/EP, irritatifs), tardives (sténose urètre, sclérose du col).",
        "RTUP bipolaire/lasers : sérum physiologique (pas de glycocolle). RTUP monopolaire : glycocolle (risque de TUR syndrome).",
    ]
    return {"donnees": donnees, "traitement": options, "notes": notes}

# =========================
# ADAPTATEUR : accepte ANCIEN appel (avec lobe_median, preservation_ejac) et NOUVEL appel
# =========================
def plan_hbp(*args, **kwargs) -> Dict[str, Any]:
    """
    Adapte les appels positionnels:
      Ancienne signature (≥16 args positionnels):
        age, volume_ml, lobe_median, ipss, psa_total, tr_suspect, anticoag,
        preservation_ejac, ci_chirurgie, refus_chir, infections_recid, retention,
        calculs, hematurie_recid, ir_post_obstacle, echec_medical, [optionnels...]
      Nouvelle signature (≥14 args positionnels, sans lobe_median/preservation_ejac):
        age, volume_ml, ipss, psa_total, tr_suspect, anticoag, ci_chirurgie, refus_chir,
        infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, echec_medical, [optionnels...]
      Ou bien en mots-clés (kwargs) avec la nouvelle signature.
    """
    # 1) Appel 100% kwargs (nouvelle signature)
    if not args:
        return _plan_hbp_core(**kwargs)

    # 2) Ancienne signature positionnelle (avec lobe_median & preservation_ejac)
    if len(args) >= 16:
        age              = args[0]
        volume_ml        = args[1]
        # args[2] = lobe_median (ignoré)
        ipss             = args[3]
        psa_total        = args[4]
        tr_suspect       = args[5]
        anticoag         = args[6]
        # args[7] = preservation_ejac (ignoré)
        ci_chirurgie     = args[8]
        refus_chir       = args[9]
        infections_recid = args[10]
        retention        = args[11]
        calculs          = args[12]
        hematurie_recid  = args[13]
        ir_post_obstacle = args[14]
        echec_medical    = args[15]
        # optionnels positionnels suivants
        opt = list(args[16:])
        # extraction optionnels s'ils sont là en position: stockage_predominant, rpm_ml, dysfonction_erectile
        stockage_predominant = opt[0] if len(opt) >= 1 else kwargs.pop("stockage_predominant", False)
        rpm_ml                = opt[1] if len(opt) >= 2 else kwargs.pop("rpm_ml", None)
        dysfonction_erectile  = opt[2] if len(opt) >= 3 else kwargs.pop("dysfonction_erectile", False)
        return _plan_hbp_core(
            age, volume_ml, ipss, psa_total, tr_suspect, anticoag, ci_chirurgie, refus_chir,
            infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, echec_medical,
            stockage_predominant=_to_bool(stockage_predominant),
            rpm_ml=rpm_ml,
            dysfonction_erectile=_to_bool(dysfonction_erectile),
            **kwargs
        )

    # 3) Nouvelle signature positionnelle (sans lobe_median/preservation_ejac)
    if len(args) >= 14:
        age              = args[0]
        volume_ml        = args[1]
        ipss             = args[2]
        psa_total        = args[3]
        tr_suspect       = args[4]
        anticoag         = args[5]
        ci_chirurgie     = args[6]
        refus_chir       = args[7]
        infections_recid = args[8]
        retention        = args[9]
        calculs          = args[10]
        hematurie_recid  = args[11]
        ir_post_obstacle = args[12]
        echec_medical    = args[13]
        # optionnels positionnels suivants (si présents)
        opt = list(args[14:])
        stockage_predominant = opt[0] if len(opt) >= 1 else kwargs.pop("stockage_predominant", False)
        rpm_ml                = opt[1] if len(opt) >= 2 else kwargs.pop("rpm_ml", None)
        dysfonction_erectile  = opt[2] if len(opt) >= 3 else kwargs.pop("dysfonction_erectile", False)
        return _plan_hbp_core(
            age, volume_ml, ipss, psa_total, tr_suspect, anticoag, ci_chirurgie, refus_chir,
            infections_recid, retention, calculs, hematurie_recid, ir_post_obstacle, echec_medical,
            stockage_predominant=_to_bool(stockage_predominant),
            rpm_ml=rpm_ml,
            dysfonction_erectile=_to_bool(dysfonction_erectile),
            **kwargs
        )

    # 4) Sinon, on tente de compléter depuis kwargs (mots-clés)
    return _plan_hbp_core(**kwargs)

# =========================
# LOGIQUE CLINIQUE — PROSTATE (Localisé / Récidive / Métastatique)
# =========================

# --- 1) Strate de risque (D'Amico adapté AFU) ---
def prostate_risk_damico(psa: float, isup: int, cT: str) -> str:
    """
    Retourne 'faible', 'intermédiaire', 'élevé'.
    D'Amico (adapté AFU localisé) : 
      - FAIBLE   : T1–T2a ET PSA < 10 ET ISUP 1
      - INTER    : PSA 10–20 OU ISUP 2–3 OU T2b–T2c (sans critère 'élevé')
      - ÉLEVÉ    : PSA > 20 OU ISUP 4–5 OU ≥ T3
    # IBJSR6-main.pdf — AFU localisé : les parties 'prise en charge de la maladie localisée' cadrent ces approches (ex. F418 L31-L35 pour PT comme traitement de référence).
    """
    t_high = cT.startswith("T3") or cT.startswith("T4")
    t_inter = cT in ["T2b", "T2c"]
    if (psa > 20) or (isup >= 4) or t_high:
        return "élevé"
    if (10 <= psa <= 20) or (isup in [2, 3]) or t_inter:
        return "intermédiaire"
    if (psa < 10) and (isup == 1) and (cT in ["T1", "T2a"]):
        return "faible"
    # Par défaut, classer intermédiaire si ambigu
    return "intermédiaire"


# --- 2) CAT — Prostate localisée (options + degré) ---
def plan_prostate_localise(psa: float, isup: int, cT: str, esperance_vie_ans: int):
    """
    Retourne dict {donnees, risque, options, notes}
    Chaque option = {label, degre ('fort'/'moyen'/'faible'), details}
    Références (commentaires) :
      - PT = traitement de référence dans le localisé (IBJSR6 F418 L31-L35).
      - Surveillance active pour bas-risque (AFU localisé, section dédiée ‘surveillance active’).
      - RT externe/curiethérapie selon risque; HT courte avec RT si intermédiaire défavorable (AFU localisé).
    """
    risque = prostate_risk_damico(psa, isup, cT)
    options = []
    idx = 1

    if risque == "faible":
        # Surveillance active — fort (standard bas-risque)
        options.append({
            "label": f"Option {idx} : Surveillance active",
            "degre": "fort",
            "details": "Bas-risque (T1–T2a, PSA<10, ISUP1). Éviter sur-traitement ; suivi structuré (PSA/IRM/cysto-biopsies selon protocole local)."
            # AFU localisé : SA recommandée pour bas-risque.
        }); idx += 1

        # Prostatectomie totale — fort si espérance de vie > 10 ans
        deg = "fort" if esperance_vie_ans >= 10 else "moyen"
        options.append({
            "label": f"Option {idx} : Prostatectomie totale (PT)",
            "degre": deg,
            "details": "Traitement de référence chirurgical ; bénéfice attendu si espérance de vie ≥10 ans."
            # IBJSR6 F418 L31-L35 : PT = un des traitements de référence du CaP localisé.
        }); idx += 1

        # Radiothérapie externe / curiethérapie — moyen
        options.append({
            "label": f"Option {idx} : Radiothérapie (RCMI/curiethérapie)",
            "degre": "moyen",
            "details": "Alternative non invasive ; SA préférée si bas-risque pur ; pas d’HT associée en bas-risque."
            # AFU localisé : RT standard dans localisé ; HT pas indiquée en bas-risque.
        }); idx += 1

    elif risque == "intermédiaire":
        # RT +/− hormonothérapie courte — fort si 'intermédiaire défavorable'
        options.append({
            "label": f"Option {idx} : Radiothérapie externe ± hormonothérapie 4–6 mois",
            "degre": "fort",
            "details": "RT standard ; HT courte si facteurs défavorables (ISUP3, ≥50% biopsies positives, PSA proche 20)."
            # AFU localisé : RT + HT courte pour intermédiaire défavorable (durée typique 4–6 mois).
        }); idx += 1

        # Prostatectomie totale ± curage — fort si opérable
        options.append({
            "label": f"Option {idx} : Prostatectomie totale ± curage pelvien",
            "degre": "fort",
            "details": "Option de référence si opérable ; discuter marges/nerve-sparing selon tumeur."
            # IBJSR6 F418 L31-L35 : PT = traitement de référence.
        }); idx += 1

        # Surveillance active — faible (sélection ultra-stricte)
        options.append({
            "label": f"Option {idx} : Surveillance active (sélectionnée)",
            "degre": "faible",
            "details": "À éviter si critères défavorables ; réservée à des cas très sélectionnés."
        }); idx += 1

    else:  # élevé
        # RT + HT longue (18–36 mois) — fort
        options.append({
            "label": f"Option {idx} : Radiothérapie + hormonothérapie prolongée (18–36 mois)",
            "degre": "fort",
            "details": "Standard haut-risque ; bénéfice en survie ; intensifications possibles selon contexte."
            # AFU localisé : haut-risque → RT + ADT longue.
        }); idx += 1

        # Prostatectomie totale ± traitements complémentaires — moyen (sélectionné)
        options.append({
            "label": f"Option {idx} : Prostatectomie totale (sélectionnée) ± RT/HT adjuvantes",
            "degre": "moyen",
            "details": "Discutée en RCP (marges, pT3, pN+). Soins complémentaires selon anatomo-path et facteurs."
        }); idx += 1

    notes = [
        "Toujours décision partagée en RCP et avec le patient.",
        "Hypofractionnements/modulations selon plateau technique (service de RT).",
    ]
    donnees = [("PSA", f"{psa:.2f} ng/mL"), ("ISUP", isup), ("cT", cT), ("Espérance de vie", f"{esperance_vie_ans} ans")]
    return {"donnees": donnees, "risque": risque, "options": options, "notes": notes}


# --- 3) Récidive (définition & CAT simple) ---
def detect_recurrence(type_initial: str, psa_actuel: float, psa_nadir_post_rt: float | None, confirmations: int) -> tuple[bool, str]:
    """
    - Après prostatectomie : récidive biologique si PSA ≥ 0,2 ng/mL confirmé (deux dosages).
    - Après radiothérapie : 'Phoenix' = nadir + 2,0 ng/mL.
    Réfs AFU (récidive) : IBJSR6 — sections 'récidive' (ex. F414 L1-L6 sur diagnostic de récidive locale).
    """
    if type_initial == "Prostatectomie":
        if psa_actuel >= 0.2 and confirmations >= 2:
            return True, "Récidive biologique après prostatectomie (PSA ≥ 0,2 ng/mL confirmé)."
        return False, "Pas de récidive biologique confirmée (après prostatectomie)."
    else:  # Radiothérapie
        if (psa_nadir_post_rt is not None) and (psa_actuel >= psa_nadir_post_rt + 2.0):
            return True, "Récidive biologique après radiothérapie (nadir + 2)."
        return False, "Pas de récidive biologique selon Phoenix (après radiothérapie)."


def plan_prostate_recidive(type_initial: str, psa_actuel: float, psa_nadir_post_rt: float | None, confirmations: int):
    """
    Retourne {resume, options, notes}
    Options avec degré indicatif; à affiner selon imagerie (PSMA-PET/IRM), délai, marge, pT, pN, vitesse PSA.
    """
    est_recidive, resume = detect_recurrence(type_initial, psa_actuel, psa_nadir_post_rt, confirmations)
    options, idx = [], 1

    if est_recidive:
        if type_initial == "Prostatectomie":
            options.append({"label": f"Option {idx} : Radiothérapie de rattrapage du lit prostatique ± bassin",
                            "degre": "fort",
                            "details": "À initier précocement ; ± hormonothérapie courte selon facteurs."}); idx += 1
            options.append({"label": f"Option {idx} : Hormonothérapie seule (si non éligible RT/chir ou progression)",
                            "degre": "moyen",
                            "details": "Approche palliative/d’inhibition androgénique selon cinétique PSA/symptômes."}); idx += 1
        else:
            options.append({"label": f"Option {idx} : Traitement local de rattrapage (salvage) sélectionné",
                            "degre": "moyen",
                            "details": "Prostatectomie de rattrapage/curiethérapie/HIFU/cryothérapie selon localisation et expertise."}); idx += 1
            options.append({"label": f"Option {idx} : Hormonothérapie ± traitements systémiques",
                            "degre": "moyen",
                            "details": "Si échec local/oligo vs polyprogression ; imagerie de re-stadification requise."}); idx += 1
        notes = [
            "Re-stadifier (IRM, TEP-PSMA si dispo) avant rattrapage.",
            "Discuter en RCP radio-onco/uro/nucléo.",
        ]
    else:
        options = [{"label": "Option 1 : Poursuivre la surveillance",
                    "degre": "moyen",
                    "details": "Contrôles PSA et imagerie selon protocole ; pas d’argument de récidive pour l’instant."}]
        notes = []

    return {"resume": resume, "options": options, "notes": notes}


# --- 4) Métastatique (mHSPC vs mCRPC) ---
def plan_prostate_metastatique(testosterone_castration: bool,
                               volume_eleve: bool,
                               symptomes_osseux: bool,
                               deja_docetaxel: bool,
                               deja_arpi: bool,
                               alteration_HRR: bool):
    """
    Retourne {profil, options, adjoints, notes}
    Références (AFU récidive/métastatique — Abup6x-main.pdf) :
      - mHSPC : intensification HTNG (abiratérone/enzalutamide/apalutamide) supérieure au docétaxel ; docétaxel utile surtout en haut volume (F469 L41-L47 ; F470 L50-L52).
      - Support osseux : zoledronate/denosumab pour fractures/symptômes (F471 L28-L36).
      - mCRPC : iPARP si altérations HRR (PROfound, TRITON-3) ; cabazitaxel après docétaxel (NEJM 2019) (F515–F516 ; F533 L29-L32).
    """
    options, idx = [], 1
    adjoints = []
    profil = "mHSPC (sensible à la castration)" if not testosterone_castration else "mCRPC (résistant à la castration)"

    if not testosterone_castration:
        # mHSPC
        options.append({"label": f"Option {idx} : ADT + ARPI (abiratérone OU enzalutamide OU apalutamide)",
                        "degre": "fort",
                        "details": "Intensification standard de 1re ligne mHSPC."}); idx += 1
        if volume_eleve:
            options.append({"label": f"Option {idx} : ADT + docétaxel (haut volume)",
                            "degre": "moyen",
                            "details": "Bénéfice surtout en haut volume ; discuter toxicité et comorbidités."}); idx += 1
        else:
            options.append({"label": f"Option {idx} : ADT seule (si contre-indication à l’intensification)",
                            "degre": "faible",
                            "details": "Moins performant ; réservé si CI/fragilité."}); idx += 1

    else:
        # mCRPC
        if not deja_arpi:
            options.append({"label": f"Option {idx} : ARPI (enzalutamide OU abiratérone)",
                            "degre": "fort",
                            "details": "Standard mCRPC 1re ligne selon exposition antérieure."}); idx += 1
        if not deja_docetaxel:
            options.append({"label": f"Option {idx} : Docétaxel",
                            "degre": "fort",
                            "details": "Chimiothérapie de référence si éligible ; surtout si symptomatique/rapide progression."}); idx += 1
        else:
            options.append({"label": f"Option {idx} : Cabazitaxel (après docétaxel)",
                            "degre": "fort",
                            "details": "Supérieur à switch ARPI/ARPI dans procès comparatifs ; standard après docétaxel."}); idx += 1
        if alteration_HRR:
            options.append({"label": f"Option {idx} : iPARP (olaparib/rucaparib) chez altérations BRCA/HRR",
                            "degre": "fort",
                            "details": "Efficacité démontrée (PROfound/TRITON-3) ; combinaisons ARPI+iPARP possibles selon autorisations/local."}); idx += 1

    # Mesures adjointes
    if symptomes_osseux:
        adjoints.append("Soins osseux : acide zolédronique ou denosumab ; supplémentation Ca/Vit D ; évaluer radiothérapie antalgique ciblée.")

    notes = ["Toujours décision en RCP. Séquençage selon expositions antérieures, comorbidités, préférences patient."]
    return {"profil": profil, "options": options, "adjoints": adjoints, "notes": notes}

# =========================
# LOGIQUE CLINIQUE — REIN (localisé, métastatique, biopsie)
# =========================

from typing import List, Tuple, Dict

def plan_rein_local(
    cT: str,
    cN_pos: bool,
    thrombus: str,  # "Aucun", "Veine rénale", "VCC infra-hépatique", "VCC supra-hépatique/atrium"
    rein_unique_ou_CKD: bool,
    tumeur_hilaire: bool,
    exophytique: bool,
    age: int,
    haut_risque_op: bool,
    biopsie_dispo: bool,
):
    """
    Retourne dict {donnees, traitement, suivi, notes} avec options numérotées.
    NOTE: aucune taille en cm; les décisions se basent sur le stade cT.
    """
    donnees = [
        ("cT", cT),
        ("cN+", "Oui" if cN_pos else "Non"),
        ("Thrombus", thrombus),
        ("Rein unique/CKD", "Oui" if rein_unique_ou_CKD else "Non"),
        ("Tumeur hilaire/centrale", "Oui" if tumeur_hilaire else "Non"),
        ("Exophytique", "Oui" if exophytique else "Non"),
        ("Âge", f"{age} ans"),
        ("Haut risque opératoire", "Oui" if haut_risque_op else "Non"),
        ("Biopsie disponible", "Oui" if biopsie_dispo else "Non"),
    ]

    options: List[str] = []
    idx = 1
    notes: List[str] = []

    if not biopsie_dispo:
        notes.append("Biopsie à discuter si traitement focal/surveillance prévue, doute diagnostique, ou avant traitement systémique.")

    # Décision par stade
    if cT == "T1a":  # ≤ 4 cm (catégorisé par le stade)
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle (standard)."); idx += 1
        if exophytique:
            options.append(f"Option {idx} : traitement focal — Cryoablation/RFA percutanée (lésion exophytique, plateau adapté, patient fragile)."); idx += 1
        options.append(f"Option {idx} : surveillance active — Imagerie à 3–6 mois puis 6–12 mois; déclencheurs = croissance rapide, symptômes, haut grade confirmé."); idx += 1
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale si NP non faisable (anatomie/hilaire) ou rein non fonctionnel."); idx += 1

    elif cT == "T1b":  # >4 à ≤7 cm
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle en centre expert (préservation rénale prioritaire)."); idx += 1
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale si NP non faisable."); idx += 1
        else:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle (sélectionnée) OU Néphrectomie totale selon complexité (hilaire/endophytique → plutôt NT)."); idx += 1
        options.append(f"Option {idx} : surveillance active — Uniquement si comorbidités majeures/inopérable (RCP)."); idx += 1

    elif cT in ("T2a", "T2b"):  # >7 à ≤10 cm ; >10 cm
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle *impérative* (centre expert) OU Néphrectomie totale si NP impossible."); idx += 1
        else:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale (standard)."); idx += 1
        options.append(f"Option {idx} : surveillance — seulement si inopérable/fragilité majeure (RCP, soins de support)."); idx += 1

    elif cT == "T3a":
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale avec exérèse graisse péri-rénale ± veine rénale (si envahie)."); idx += 1
        if rein_unique_ou_CKD:
            options.append(f"Option {idx} : traitement chirurgical — Néphrectomie partielle *impérative* (centre expert) si anatomie favorable."); idx += 1

    elif cT in ("T3b", "T3c"):
        options.append(f"Option {idx} : traitement chirurgical — Néphrectomie totale + thrombectomie (niveau {thrombus}). Équipe vasculaire/cardiothoracique si VCC."); idx += 1
        options.append(f"Option {idx} : stratégie — Discussion RCP spécialisée (opérabilité vs traitement systémique d’emblée)."); idx += 1

    elif cT == "T4":
        options.append(f"Option {idx} : traitement chirurgical — Résection élargie si résécable (RCP de recours)."); idx += 1
        options.append(f"Option {idx} : stratégie — Traitement systémique d’emblée si non résécable."); idx += 1

    # Ganglions
    if cN_pos:
        notes.append("Curage ganglionnaire ciblé si adénopathies cliniquement envahies; curage étendu systématique non recommandé.")

    # Adjuvant
    notes.append("Adjuvant : pembrolizumab 12 mois à discuter chez ccRCC à haut risque (profils type KEYNOTE-564).")

    # Haut risque opératoire — rappel d’orientation
    if haut_risque_op:
        notes.append("Haut risque opératoire : privilégier prise en charge mini-invasive si éligible (TA) ou surveillance selon stade/comorbidités, en RCP.")

    # Suivi post-traitement
    suivi: List[str] = []
    if cT == "T1a" and not cN_pos:
        suivi += [
            "Consultation : 3–6 mois post-op, puis 12 mois, puis annuel jusqu’à 5 ans.",
            "Imagerie : TDM/IRM abdo ± TDM thorax à 12 mois puis annuel.",
            "Biologie : créat/DFG à chaque visite; PA; +/- Hb/Ca selon contexte.",
        ]
    elif cT in ("T1b", "T2a", "T2b") and not cN_pos:
        suivi += [
            "Consultation : tous les 6–12 mois pendant 3 ans, puis annuel jusqu’à 5 ans.",
            "Imagerie : TDM abdo + TDM thorax tous les 6–12 mois (3 ans), puis annuel.",
            "Biologie : créat/DFG, +/- Hb/Ca; adapter si rein unique/CKD.",
        ]
    else:  # T3/T4 ou N+
        suivi += [
            "Consultation : tous les 3–6 mois pendant 3 ans, puis 6–12 mois jusqu’à 5 ans.",
            "Imagerie : TDM TAP tous les 3–6 mois (3 ans), puis 6–12 mois.",
            "Biologie : créat/DFG, Hb, Ca; symptômes ciblés. IRM cérébrale si clinique.",
        ]

    return {"donnees": donnees, "traitement": options, "suivi": suivi, "notes": notes}


# ——— inchangé ci-dessous ———

def calc_imdc(
    karnofsky_lt80: bool,
    time_to_systemic_le_12mo: bool,
    hb_basse: bool,
    calcium_haut: bool,
    neutro_hauts: bool,
    plaquettes_hautes: bool,
):
    """Heng/IMDC : 6 facteurs (KPS<80, délai<1 an, Hb basse, Ca haut, neutros hautes, plaquettes hautes)."""
    score = sum([karnofsky_lt80, time_to_systemic_le_12mo, hb_basse, calcium_haut, neutro_hauts, plaquettes_hautes])
    if score == 0:
        groupe = "Bon pronostic (0)"
    elif score in (1, 2):
        groupe = "Intermédiaire (1–2)"
    else:
        groupe = "Mauvais (≥3)"
    return score, groupe


def calc_mskcc(
    karnofsky_lt80: bool,
    time_to_systemic_le_12mo: bool,
    hb_basse: bool,
    calcium_haut: bool,
    ldh_haut: bool,
):
    """MSKCC/Motzer : 5 facteurs (KPS<80, délai<1 an, Hb basse, Ca haut, LDH élevé)."""
    score = sum([karnofsky_lt80, time_to_systemic_le_12mo, hb_basse, calcium_haut, ldh_haut])
    if score == 0:
        groupe = "Bon pronostic (0)"
    elif score in (1, 2):
        groupe = "Intermédiaire (1–2)"
    else:
        groupe = "Mauvais (≥3)"
    return score, groupe


def plan_rein_meta(
    histo: str,             # "ccRCC" ou "non-ccRCC"
    score: int,
    group: str,
    score_system_label: str,
    oligo: bool,
    bone: bool,
    brain: bool,
    liver: bool,
    io_contra: bool,
):
    """
    Retourne dict {donnees, stratification, traitement, suivi, notes}.
    Inclut la néphrectomie de cytoréduction comme option selon IMDC/MSKCC et charge tumorale.
    """
    donnees = [
        ("Histologie", histo),
        (f"{score_system_label} score", str(score)),
        (f"Groupe {score_system_label}", group),
        ("Oligométastatique", "Oui" if oligo else "Non"),
        ("Métastases osseuses", "Oui" if bone else "Non"),
        ("Cérébrales", "Oui" if brain else "Non"),
        ("Hépatiques", "Oui" if liver else "Non"),
        ("CI immunothérapie", "Oui" if io_contra else "Non"),
    ]

    options: List[str] = []
    idx = 1
    notes: List[str] = []

    # Cytoréduction
    if "Bon" in group and oligo:
        options.append(f"Option {idx} : néphrectomie de cytoréduction **immédiate** (bon pronostic, tumeur rénale dominante, faible charge)."); idx += 1
    elif "Intermédiaire" in group or "Mauvais" in group:
        options.append(f"Option {idx} : néphrectomie de cytoréduction **différée** après réponse au traitement systémique (sélectionnés)."); idx += 1

    # 1re ligne
    if histo == "ccRCC":
        if "Bon" in group:
            if not io_contra:
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Axitinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : stratégie — Surveillance rapprochée (maladie indolente, faible charge)."); idx += 1
            options.append(f"Option {idx} : 1re ligne — TKI seul (Axitinib, Pazopanib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
        else:
            if not io_contra:
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Ipilimumab."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Nivolumab + Cabozantinib."); idx += 1
                options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Axitinib."); idx += 1
            options.append(f"Option {idx} : 1re ligne — TKI seul (Cabozantinib, Axitinib, Sunitinib, Tivozanib) si CI à l’immunothérapie."); idx += 1
    else:
        options.append(f"Option {idx} : 1re ligne — Cabozantinib (préférence papillaire)."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Pembrolizumab + Lenvatinib."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Sunitinib ou Pazopanib."); idx += 1
        options.append(f"Option {idx} : 1re ligne — Lenvatinib + Everolimus (sélectionné)."); idx += 1
        options.append(f"Option {idx} : chimiothérapie — Gemcitabine + (Cisplatine/Carboplatine) pour sous-types agressifs."); idx += 1
        options.append(f"Option {idx} : stratégie — Essai clinique si disponible."); idx += 1

    # 2e ligne
    if histo == "ccRCC":
        options.append(f"Option {idx} : 2e ligne — Cabozantinib."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Lenvatinib + Everolimus."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Tivozanib."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Belzutifan (si disponible)."); idx += 1
    else:
        options.append(f"Option {idx} : 2e ligne — Cabozantinib / Lenvatinib + Everolimus."); idx += 1
        options.append(f"Option {idx} : 2e ligne — Essai clinique fortement recommandé."); idx += 1

    # Sites spéciaux
    if oligo:
        notes.append("Maladie oligométastatique : à discuter métastasectomie et/ou radiothérapie stéréotaxique.")
    if bone:
        notes.append("Os : acide zolédronique ou denosumab + Ca/Vit D; radiothérapie antalgique si douloureux.")
    if brain:
        notes.append("Cerveau : stéréotaxie/chirurgie + stéroïdes selon symptômes; coordination neuro-oncologie.")

    # Suivi métastatique
    suivi = [
        "Avant et pendant traitement : PA/poids, symptômes; NFS, créat/DFG, transaminases, phosphatases, Ca; TSH (IO/TKI).",
        "Protéinurie et TA à chaque visite sous TKI; ECG/risques CV si nécessaire.",
        "Imagerie de réévaluation : TDM TAP toutes 8–12 semaines les 6–9 premiers mois, puis espacer selon réponse/clinique.",
        "IRM cérébrale si symptômes ou lésions traitées (toutes 8–12 semaines au début).",
    ]

    return {
        "donnees": donnees,
        "stratification": [(score_system_label, f"{group} (score {score})")],
        "traitement": options,
        "suivi": suivi,
        "notes": notes,
    }


def plan_rein_biopsy(
    indication_systemique: bool,
    indication_ablation: bool,
    inoperable_haut_risque: bool,
    lesion_indet: bool,
    suspicion_lymphome_metastase_infection: bool,
    rein_unique_ou_ckd: bool,
    petite_masse_typique_et_chirurgie_prevue: bool,
    bosniak: str,  # "II", "IIF", "III", "IV", "Non applicable"
    troubles_coag_non_corriges: bool,
):
    """
    Retourne dict {donnees, conduite, suivi, notes} pour les indications de biopsie percutanée d'une masse rénale.
    """
    donnees = [
        ("Avant traitement systémique (métastatique)", "Oui" if indication_systemique else "Non"),
        ("Avant traitement focal (cryo/RFA) prévu", "Oui" if indication_ablation else "Non"),
        ("Patient inopérable/haut risque chirurgical", "Oui" if inoperable_haut_risque else "Non"),
        ("Lésion indéterminée en imagerie", "Oui" if lesion_indet else "Non"),
        ("Suspicion lymphome / métastase / infection", "Oui" if suspicion_lymphome_metastase_infection else "Non"),
        ("Rein unique / CKD significative", "Oui" if rein_unique_ou_ckd else "Non"),
        ("Petite masse typique et chirurgie déjà prévue", "Oui" if petite_masse_typique_et_chirurgie_prevue else "Non"),
        ("Bosniak (si kystique)", bosniak),
        ("Troubles de coagulation non corrigés", "Oui" if troubles_coag_non_corriges else "Non"),
    ]

    options: List[str] = []
    idx = 1
    notes: List[str] = []

    # CI immédiate
    if troubles_coag_non_corriges:
        options.append(f"Option {idx} : corriger les troubles de coagulation **avant** toute biopsie; sinon différer."); idx += 1

    # Indications fortes
    indications_fortes = any([
        indication_systemique,
        indication_ablation,
        inoperable_haut_risque,
        lesion_indet,
        suspicion_lymphome_metastase_infection,
        rein_unique_ou_ckd,
    ])

    # Non nécessaire d’emblée
    non_necessaire = petite_masse_typique_et_chirurgie_prevue and not indications_fortes

    # Bosniak
    if bosniak in ("III", "IV"):
        notes.append("Kystique Bosniak III/IV : la biopsie peut avoir un rendement limité; décision RCP (biopsie vs chirurgie d’emblée).")

    if indications_fortes:
        options.append(f"Option {idx} : Biopsie rénale percutanée guidée (TDM/écho), 2–3 carottes, histo + IHC si besoin."); idx += 1
    elif not indications_fortes and not non_necessaire:
        options.append(f"Option {idx} : Discussion RCP — Biopsie **ou** surveillance/traitement selon préférences et risque."); idx += 1
    else:
        options.append(f"Option {idx} : Pas d’indication routinière à la biopsie si chirurgie partielle déjà prévue chez patient apte (petite masse solide typique)."); idx += 1

    # Suivi
    suivi = [
        "Après biopsie : surveillance du point de ponction, contrôle Hb si risque saignement.",
        "Si surveillance active choisie : imagerie à 3–6 mois puis tous les 6–12 mois; re-biopsie si évolution atypique.",
        "Si ablation après biopsie : TDM/IRM à 3 mois, puis 6–12 mois les 2 premières années.",
    ]

    notes += [
        "CI relatives : infection cutanée au point de ponction, impossibilité de coopération/apnée, anticoagulation non interrompue.",
        "Informer sur rendements : meilleurs pour masses solides; plus limité pour kystiques complexes.",
    ]

    return {"donnees": donnees, "conduite": options, "suivi": suivi, "notes": notes}

# =========================
# LOGIQUE CLINIQUE — TVNIM (simplifiée pour prototypage)
# =========================

def stratifier_tvnim(stade: str, grade: str, taille_mm: int, nombre: str,
                     cis_associe: bool, lvi: bool, urethre_prostatique: bool, formes_agressives: bool) -> str:
    """Retourne "faible", "intermédiaire" ou "élevé" (simplifié)."""
    if stade == "pT1" or cis_associe or lvi or urethre_prostatique or formes_agressives:
        return "élevé"
    multiple = (nombre != "Unique")
    if grade == "Bas grade" and (taille_mm < 30) and not multiple:
        return "faible"
    return "intermédiaire"


def plan_tvnim(risque: str):
    traitement, suivi, protocoles, notes = [], [], [], []
    if risque == "faible":
        traitement = [
            "RTUV complète.",
            " il est recommandé de réaliser une instillation postopératoire précoce (IPOP) . Aucun autre traitement complémentaire n’est nécessaire. Une surveillance simple selon le schéma proposé  est nécessaire pour une durée totale de 5 ans.",
        ]
        suivi = [
            "3e et 12e mois Puis 1×/an pendant 5 ans .",
            
        ]
    elif risque == "intermédiaire":
        traitement = [
            "RTUV complète.",
            "instillations endovésicales par chimiothérapie (mitomycine, épirubicine, gemcitabine) selon un schéma de 6-8 instillations d’induction+ traitement d’entretien peut être discuté pour les patients les plus à risque de récidive. Une alternative thérapeutique est la BCG-thérapie avec un entretien de 1 an  pour diminuer le risque de récidive.",
        ]
        suivi = ["3e et 6e mois puis tous les 6 mois pendant 2 ans Puis 1×/an , + cytologie urinaire."]
        protocoles = ["BCG : induction (6 instillations) + maintenance (~1 an)."]
    else:  # élevé
        traitement = [
            "RTUV complète avec re‑résection (second look) .",
            "BCG : induction 6 seances  + entretien prolongée (3 ans selon dispo/tolérance).",
            "Discuter cystectomie précoce si T1 haut grade avec facteurs défavorables ( très haut risque).",
        ]
        suivi = [
            "Cysto + cytologie rapprochées (ex3e et 6e mois puis tous les 3 mois pendant 2 ans puis tous les 6 mois jusqu’à 5 ans puis 1×/an a vie ).",
            "Imagerie selon facteurs/symptômes.",
        ]
        protocoles = ["BCG : induction (6) + maintenance prolongée."]
        notes = ["Second look recommandé si T1 haut grade (2–6 semaines)."]

    notes_second_look = notes or [
        "Second look : à envisager si résection incomplète ou doute sur le stade, ou muscle non vue a l'anapath;."
    ]
    return traitement, suivi, protocoles, notes_second_look


# =========================
# LOGIQUE CLINIQUE — TVIM (simplifiée pour prototypage)
# =========================

def plan_tvim(
    t_cat: str,
    cN_pos: bool,
    metastases: bool,
    cis_eligible: bool,
    hydron: bool,
    bonne_fct_v: bool,
    cis_diffus: bool,
    post_op_high_risk: bool,
    neo_adjuvant_fait: bool,
    # critères pour l'alternative TMT
    
):
    """
    Alternative TMT affichée seulement si TOUS les critères sont satisfaits :
      - T2–T3 (ou t2_localise = True)
      - N0 (cN_pos = False)
      - M0 (metastases = False)
      - Pas de CIS diffus
      - Pas d’hydronéphrose
      - Bonne fonction vésicale
    """
    traitement, surveillance, notes = [], [], []

    # Maladie métastatique : pas d'alternative TMT ni de chirurgie curative
    if metastases:
        traitement = ["Maladie métastatique → voir module dédié."]
        return {"traitement": traitement, "surveillance": surveillance, "notes": notes}

    # Standard : chimio néoadjuvante si éligible, puis cystectomie
    if cis_eligible and not neo_adjuvant_fait:
        traitement += [
            "Chimiothérapie néoadjuvante à base de cisplatine (MVAC dose-dense ou GemCis).",
            "→ Puis cystectomie radicale + curage ganglionnaire (10–12 semaines après la dernière cure).",
        ]
    else:
        traitement += [
            "Cystectomie radicale + curage ganglionnaire (< 3 mois après le diagnostic de TVIM)."
        ]

    # Vérification stricte de l'éligibilité à l'ALTERNATIVE TMT
    stade_ok = (t_cat.upper() in {"T2", "T3"}) 
    strict_tmt_ok = all([
        stade_ok,
        not bool(cN_pos),         # N0
        not bool(metastases),     # M0
        not bool(cis_diffus),
        not bool(hydron),
        bool(bonne_fct_v),
    ])

    # Ajouter l'ALTERNATIVE TMT uniquement si tous les critères sont remplis
    if strict_tmt_ok:
        traitement += [
            "Alternative : TMT à base de RTUTV itératives + chimiothérapie et radiothérapie + surveillance, "
            "à condition que les RTUTV soient toujours complètes et que le patient soit informé et compliant."
        ]

    # Notes adjuvant si haut risque post-op
    if post_op_high_risk:
        notes += ["Risque post-op élevé (pT3–4/pN+) : discuter traitement adjuvant (ex. immunothérapie adjuvante)."]

    # Suivi
    surveillance = ["Suivi clinique, imagerie et biologie selon protocole (tous les 3–6 mois les 2 premières années)."]

    return {"traitement": traitement, "surveillance": surveillance, "notes": notes}


# =========================
# LOGIQUE CLINIQUE — Vessie métastatique (simplifiée pour prototypage)
# =========================

def plan_meta(cis_eligible: bool, carbo_eligible: bool, platinum_naive: bool, pdl1_pos: bool,
              prior_platinum: bool, prior_cpi: bool, bone_mets: bool):
    traitement, suivi, notes = [], [], []

    if platinum_naive:
        traitement += [
            "1re ligne (naïf platine) : combinaison récente anticorps‑conjugué + immunothérapie (selon accès).",
            "Alternative : Gemcitabine + Cisplatine (ou Carboplatine si non éligible Cisplatine), puis maintenance IO si RC/PR/SD.",
        ]
    else:
        if prior_platinum and not prior_cpi:
            traitement += ["Après platine : immunothérapie (PD‑1/PD‑L1) si non déjà reçue."]
        elif prior_cpi:
            traitement += ["Après immunothérapie : envisager anticorps‑conjugué (Nectin‑4/Trop‑2) selon disponibilité."]

    if bone_mets:
        notes += [
            "Métastases osseuses : envisager traitement osseux (acide zolédronique/denosumab) + Ca/Vit D, prévention SDS.",
        ]

    suivi = ["Réévaluation toutes 6–8 semaines au début (clinique/imagerie/biologie)."]

    return {"traitement": traitement, "suivi": suivi, "notes": notes}

# =========================
# LOGIQUE CLINIQUE — TVES (localisé & métastatique)
# =========================

def stratifier_tves_risque(
    grade_biopsie: str,          # "Bas grade", "Haut grade", "Indéterminé"
    cytologie_hg_positive: bool,
    taille_cm: float,
    multifocal: bool,
    invasion_imagerie: bool,
    hydron: bool,
    kss_faisable: bool,          # possibilité de traitement conservateur endoscopique/segmentaire complet
    accepte_suivi_strict: bool,
):
    """
    Règles (synthèse) :
      BAS RISQUE si TOUT est réuni :
        - Bas grade à la biopsie URSS
        - Cytologie haut grade négative
        - Lésion non infiltrante à l’imagerie (pas d’invasion) et PAS d’hydronéphrose
        - Taille < 2 cm
        - Unifocale (multifocal = False)
        - Traitement conservateur réalisable (kss_faisable = True)
        - Patient accepte le suivi strict (accepte_suivi_strict = True)
      Sinon = HAUT RISQUE
    """
    conditions_bas = [
        grade_biopsie == "Bas grade",
        not cytologie_hg_positive,
        not invasion_imagerie,
        not hydron,
        taille_cm < 2.0,
        not multifocal,
        kss_faisable,
        accepte_suivi_strict,
    ]
    return "Bas risque" if all(conditions_bas) else "Haut risque"


def _suivi_tves_apres_nut():
    return [
        "Cystoscopie + cytologie : tous les 3 mois pendant 1 an, puis tous les 6 mois pendant 2 ans, puis annuelle (durée prolongée > 5–10 ans).",
        "Imagerie (uro-TDM ± TDM thorax) : tous les 6 mois pendant 4 ans, puis annuelle.",
        "Biologie : créat/DFG à chaque visite; adapter si rein unique/CKD.",
    ]


def _suivi_tves_apres_kss():
    return [
        "URSS (± biopsies) + cytologie *in situ* : à 6–8 semaines (second look), puis à 3 et 6 mois, ensuite annuelle si stable.",
        "Cystoscopie : à 3 et 6 mois, puis annuelle.",
        "Imagerie (uro-TDM) : à 3 et 6 mois, puis annuelle.",
        "Biologie : créat/DFG, selon contexte.",
    ]


def plan_tves_localise(
    grade_biopsie: str,
    cytologie_hg_positive: bool,
    taille_cm: float,
    multifocal: bool,
    invasion_imagerie: bool,
    hydron: bool,
    kss_faisable: bool,
    accepte_suivi_strict: bool,
    localisation: str,  # "Bassinets/caliciel", "Uretère proximal", "Uretère moyen", "Uretère distal"
):
    """
    Renvoie dict {donnees, stratification, traitement, suivi, notes}
    - Options numérotées si plusieurs possibilités ; sinon conduite directe.
    """
    risque = stratifier_tves_risque(
        grade_biopsie, cytologie_hg_positive, taille_cm, multifocal,
        invasion_imagerie, hydron, kss_faisable, accepte_suivi_strict
    )

    donnees = [
        ("Risque estimé", risque),
        ("Grade biopsie URSS", grade_biopsie),
        ("Cytologie haut grade positive", "Oui" if cytologie_hg_positive else "Non"),
        ("Taille lésion", f"{taille_cm:.1f} cm"),
        ("Multifocale", "Oui" if multifocal else "Non"),
        ("Invasion suspecte à l’imagerie", "Oui" if invasion_imagerie else "Non"),
        ("Hydronéphrose", "Oui" if hydron else "Non"),
        ("KSS (conservateur) faisable", "Oui" if kss_faisable else "Non"),
        ("Acceptation suivi strict", "Oui" if accepte_suivi_strict else "Non"),
        ("Localisation", localisation),
    ]

    options = []
    notes = []
    suivi = []
    idx = 1

    if risque == "Bas risque":
        # KSS prioritaire
        options.append(f"Option {idx} : traitement conservateur endoscopique (URSS laser/ablation) avec second look à 6–8 semaines."); idx += 1
        if "Uretère distal" in localisation:
            options.append(f"Option {idx} : chirurgie conservatrice — Urétérectomie segmentaire + réimplantation (sélectionné)."); idx += 1

        # Si KSS impossible malgré critères bas risque → NUT
        options.append(f"Option {idx} : Néphro-urétérectomie totale (NUT) si KSS non réalisable/échec."); idx += 1

        # Adjuvants/préventions
        notes += [
            "Après NUT : instillation intravésicale unique (ex. mitomycine) 2–10 jours post-op pour ↓ récidives vésicales.",
            "Topiques réno-urétéraux (ex. MMC/gel) après KSS selon centres/disponibilité.",
        ]

        suivi = _suivi_tves_apres_kss()

    else:  # Haut risque
        options.append(f"Option {idx} : Néphro-urétérectomie totale (NUT) avec collerette vésicale en bloc ± curage selon topographie."); idx += 1
        # (Néoadjuvant possible selon centre; souvent adjuvant privilégié POUT)
        notes.append("Adjuvant : chimiothérapie sels de platine (schéma basé cisplatine si DFG suffisant) à discuter pour pT2–T4 et/ou pN+ (type POUT).")
        notes.append("Après NUT : instillation intravésicale unique (ex. mitomycine) 2–10 jours post-op pour ↓ récidive vésicale.")
        suivi = _suivi_tves_apres_nut()

    # Conduite directe si une seule option
    if len(options) == 1:
        traitement = options  # 1 seule ligne (conduite)
    else:
        traitement = options  # plusieurs "Option x"

    return {
        "donnees": donnees,
        "stratification": [("Risque", risque)],
        "traitement": traitement,
        "suivi": suivi,
        "notes": notes,
    }


def plan_tves_metastatique(
    ev_pembro_eligible: bool,
    cis_eligible: bool,
    carbo_eligible: bool,
    platinum_naif: bool,
    fgfr_alt: bool,
    prior_platinum: bool,
    prior_io: bool,
    use_cis_gem_nivo: bool,   # ← nouveau paramètre (pour le bras "Cisplatine Gem Nivo")
):
    """
    Aligne la CAT sur l’algorithme fourni pour carcinome urothélial métastatique:

    - Si éligible EV + Pembro → 1L = EV + Pembrolizumab (option préférentielle)
        • Progression → 2L: Platine-Gemcitabine (cis/carbo selon éligibilité)
        • (FGFR alt) → Erdafitinib possible (2L/3L)
        • Progression ultérieure → 3L: EV (si non déjà exploitable en monothérapie) ± Erdafitinib si FGFR alt non utilisé

    - Si NON éligible EV + Pembro:
        • Option A (si cis éligible ET choisi): 1L = Cisplatine + Gemcitabine + Nivolumab
              ↳ Progression → EV  ± Erdafitinib (si FGFR alt)
        • Option B (par défaut): 1L = Platine-Gemcitabine (cis si possible, sinon carbo)
              ↳ TDM TAP après 4–6 cycles:
                    - maladie contrôlée (RC/PR/SD) → maintenance Avelumab
                    - progression → Pembrolizumab
              ↳ Progression après maintenance/IO → EV  ± Erdafitinib (si FGFR alt)

    - Si patient NON naïf de platine: orienter directement vers Pembro (si pas d’IO antérieure),
      sinon EV / Erdafitinib selon FGFR.

    Renvoie: dict {donnees, traitement (options numérotées), suivi (détaillé), notes}
    """
    donnees = [
        ("Éligible EV + Pembrolizumab", "Oui" if ev_pembro_eligible else "Non"),
        ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"),
        ("Éligible Carboplatine", "Oui" if carbo_eligible else "Non"),
        ("Naïf de platine (1re ligne)", "Oui" if platinum_naif else "Non"),
        ("Altérations FGFR2/3", "Oui" if fgfr_alt else "Non"),
        ("Platines déjà reçus", "Oui" if prior_platinum else "Non"),
        ("Immunothérapie déjà reçue", "Oui" if prior_io else "Non"),
        ("Choix 1L Cis-Gem-Nivo", "Oui" if use_cis_gem_nivo else "Non"),
    ]

    options = []
    idx = 1
    notes = []

    # Cas où le patient n'est pas naïf de platine (par ex. rechute post-chimio antérieure)
    if not platinum_naif:
        if not prior_io:
            options.append(f"Option {idx} : Pembrolizumab (si IO non reçue)."); idx += 1
        options.append(f"Option {idx} : Enfortumab védotin (EV)."); idx += 1
        if fgfr_alt:
            options.append(f"Option {idx} : Erdafitinib (si altération FGFR2/3)."); idx += 1
        notes.append("Séquence ultérieure selon réponses et tolérance; envisager essais cliniques.")
    else:
        # Vrai 1re ligne
        if ev_pembro_eligible:
            # 1L préférentielle
            options.append(f"Option {idx} : 1L — Enfortumab védotin + Pembrolizumab (préférentiel)."); idx += 1
            # 2L / 3L selon progression
            options.append(f"Option {idx} : 2L — Platine + Gemcitabine (cis si éligible, sinon carbo)."); idx += 1
            if fgfr_alt:
                options.append(f"Option {idx} : 2L/3L — Erdafitinib (si FGFR2/3 altéré)."); idx += 1
            options.append(f"Option {idx} : 3L — EV (si stratégie monothérapie envisageable) ou autre séquence selon tolérance."); idx += 1

        else:
            # Non éligible EV+Pembro → deux branches possibles
            if use_cis_gem_nivo and cis_eligible:
                # Triplet CheckMate-901
                options.append(f"Option {idx} : 1L — Cisplatine + Gemcitabine + Nivolumab."); idx += 1
                options.append(f"Option {idx} : 2L — Enfortumab védotin (EV)."); idx += 1
                if fgfr_alt:
                    options.append(f"Option {idx} : Ligne dédiée — Erdafitinib (si FGFR2/3 altéré)."); idx += 1
            else:
                # 1L platine-gem conventionnelle avec maintenance avelumab si contrôle
                if cis_eligible:
                    options.append(f"Option {idx} : 1L — Gemcitabine + Cisplatine."); idx += 1
                elif carbo_eligible:
                    options.append(f"Option {idx} : 1L — Gemcitabine + Carboplatine."); idx += 1
                else:
                    options.append(f"Option {idx} : 1L — (si aucun platine) discuter alternatives/essai clinique."); idx += 1

                options.append(f"Option {idx} : Contrôle après 4–6 cycles — TDM TAP."); idx += 1
                options.append(f"Option {idx} : Maintenance — Avelumab si maladie contrôlée (RC/PR/SD) après 4–6 cycles."); idx += 1
                options.append(f"Option {idx} : 2L — Pembrolizumab en cas de progression sous/à l’issue de chimio."); idx += 1
                options.append(f"Option {idx} : 2L/3L — Enfortumab védotin (EV) en cas de progression après IO."); idx += 1
                if fgfr_alt:
                    options.append(f"Option {idx} : Ligne dédiée — Erdafitinib (si FGFR2/3 altéré)."); idx += 1

    # Suivi détaillé (communs aux schémas)
    suivi = [
        "Évaluation d’efficacité: TDM TAP toutes 8–12 semaines (au démarrage), puis adapter selon réponse/clinique.",
        "Si 1L platine-gem: TDM TAP après 4–6 cycles pour décider maintenance Avelumab ou bascule 2L.",
        "Biologie récurrente: NFS, créat/DFG, bilan hépatique; glycémie (EV), phosphatémie et bilan ophtalmo (FGFRi), TSH ± enzymes pancréatiques (IO).",
        "Toxicités à surveiller: EV (éruption cutanée, neuropathie, hyperglycémie); IO (dermatites, colite, pneumonite, endocrinopathies); FGFRi (hyperphosphatémie, toxicité oculaire).",
        "Soins de support: prise en charge douleur, diététique, activité adaptée; évaluation gériatrique si besoin.",
    ]

    return {
        "donnees": donnees,
        "traitement": options,
        "suivi": suivi,
        "notes": notes,
    }
# =========================
# LOGIQUE CLINIQUE — LITHIASE (MAJ: hygiène, antalgie si douleur, options chir précises)
# =========================

def classer_cn_severite(fievre: bool, hyperalgique: bool, oligoanurie: bool, doute_diag: bool) -> str:
    """Retourne 'compliquée' si au moins un critère de gravité, sinon 'simple'."""
    if fievre or hyperalgique or oligoanurie or doute_diag:
        return "compliquée"
    return "simple"


def choix_technique_selon_calcul(localisation: str, taille_mm: int, grossesse: bool, anticoag: bool):
    """
    Propose des options procédurales libellées précisément :
    - LEC/ESWL
    - URS semi-rigide (urétéral)
    - URS souple/flexible (rénal ± urétéral)
    - Mini-perc (mini-PCNL)
    - NLPC / PCNL
    Avec prise en compte de CI usuelles: grossesse, troubles hémostase/anticoagulants non corrigés.
    """
    options = []
    i = 1
    eswl_possible = (not grossesse) and (not anticoag)

    is_ureter = localisation.startswith("Uretère")

    if is_ureter:
        # Urétéral <10 mm : ESWL privilégiée, URS semi-rigide en alternative
        if taille_mm < 10:
            if eswl_possible:
                options.append(f"Option {i} : traitement chirurgical — LEC/ESWL (uretère < 10 mm)."); i += 1
            options.append(f"Option {i} : traitement chirurgical — URS semi-rigide (urétéral < 10 mm)."); i += 1
        else:
            # Urétéral ≥10 mm : URS semi-rigide en 1re intention ; ESWL discutée
            options.append(f"Option {i} : traitement chirurgical — URS semi-rigide (uretère ≥ 10 mm)."); i += 1
            if eswl_possible:
                options.append(f"Option {i} : traitement chirurgical — LEC/ESWL (au cas par cas selon densité/position)."); i += 1
        # URS souple/flexible si besoin d'accès proximal/complexe
        options.append(f"Option {i} : traitement chirurgical — URS souple/flexible (si localisation haute/accès difficile)."); i += 1
    else:
        # Rénal (intracavicitaire)
        if taille_mm < 20:
            if eswl_possible:
                options.append(f"Option {i} : traitement chirurgical — LEC/ESWL (rénal < 20 mm)."); i += 1
            options.append(f"Option {i} : traitement chirurgical — URS souple/flexible (rénal < 20 mm, pôle inférieur inclus)."); i += 1
            # Mini-perc possible pour calcul rénal 10–20 mm denses/anatomie défavorable
            if taille_mm >= 10:
                options.append(f"Option {i} : traitement chirurgical — Mini-perc (mini-PCNL) (rénal 10–20 mm denses ou anatomie défavorable)."); i += 1
        else:
            # ≥20 mm : PCNL/NLPC de référence ; mini-perc si charge modérée et morphologie favorable
            options.append(f"Option {i} : traitement chirurgical — NLPC / PCNL (≥ 20 mm, coralliformes)."); i += 1
            options.append(f"Option {i} : traitement chirurgical — Mini-perc (mini-PCNL) (sélectionné selon charge et morphologie)."); i += 1

    # Contre-indications/notes générales
    if grossesse:
        options.append("Note : Grossesse → ESWL contre-indiquée.")
    if anticoag:
        options.append("Note : Anticoagulants/troubles de l’hémostase non corrigés → corriger avant geste endoscopique/ESWL.")

    return options


def plan_lithiase(
    fievre: bool,
    hyperalgique: bool,
    oligoanurie: bool,
    doute_diag: bool,
    grossesse: bool,
    anticoag: bool,
    localisation: str,      # "Uretère distal/moyen/proximal" ou "Rein (intracavicitaire)"
    taille_mm: int | None,  # None si inconnue
    douleur_actuelle: bool  # ← NOUVEAU: pour décider si on prescrit antalgie
):
    """
    Retourne dict {donnees, traitement, hygiene, notes}
    - Met en avant drainage initial si forme compliquée
    - Antalgie seulement si douleur_actuelle = True
    - Remplace 'suivi' par 'hygiene' (règles hygiéno-diététiques)
    """
    severite = classer_cn_severite(fievre, hyperalgique, oligoanurie, doute_diag)

    donnees = [
        ("Forme", severite),
        ("Fièvre/infection", "Oui" if fievre else "Non"),
        ("Douleur hyperalgique", "Oui" if hyperalgique else "Non"),
        ("Oligo-anurie / IR", "Oui" if oligoanurie else "Non"),
        ("Doute diagnostique", "Oui" if doute_diag else "Non"),
        ("Douleur actuelle", "Oui" if douleur_actuelle else "Non"),
        ("Grossesse", "Oui" if grossesse else "Non"),
        ("Anticoagulants/troubles hémostase non corrigés", "Oui" if anticoag else "Non"),
        ("Localisation du calcul", localisation),
        ("Taille estimée", f"{taille_mm} mm" if isinstance(taille_mm, (int, float)) else "Inconnue"),
    ]

    options = []
    notes = []
    i = 1

    # 1) Urgences / imagerie / drainage
    if severite == "compliquée":
        # Imagerie urgente
        if grossesse:
            options.append(f"Option {i} : imagerie — Échographie ± ASP en première intention (grossesse)."); i += 1
        else:
            options.append(f"Option {i} : imagerie — TDM abdomino-pelvienne sans injection en URGENCE."); i += 1

        # Drainage initial en urgence (mettre bien en évidence)
        options.append(f"Option {i} : drainage initial en urgence — sonde JJ **ou** néphrostomie percutanée (obstacle infecté/anurie/hyperalgie)."); i += 1

        # ATB si fièvre/infection (adaptation secondaire)
        if fievre:
            options.append(f"Option {i} : antibiothérapie probabiliste puis adaptée à l’ECBU (si infection associée)."); i += 1

        # Antalgie seulement si douleur
        if douleur_actuelle:
            options.append(f"Option {i} : antalgie — AINS IV (ex. kétoprofène) ± paliers supérieurs si besoin, antiémétiques."); i += 1

        # Notes de CI
        if grossesse:
            notes.append("Grossesse : ESWL contre-indiquée.")
        if anticoag:
            notes.append("Anticoagulants/troubles de l’hémostase non corrigés : corriger avant tout geste.")
        notes.append("Le traitement lithiasique définitif est différé après contrôle de l’infection et levée de l’obstacle.")
    else:
        # 2) Forme simple — options selon taille/localisation
        if taille_mm is not None:
            options += choix_technique_selon_calcul(localisation, taille_mm, grossesse, anticoag)
        else:
            # Taille inconnue → affiner par imagerie hors grossesse TDM, en grossesse écho/ASP
            if grossesse:
                options.append(f"Option {i} : imagerie — Échographie ± ASP pour préciser taille/localisation."); i += 1
            else:
                options.append(f"Option {i} : imagerie — TDM sans injection pour préciser taille/densité/localisation."); i += 1

        # Antalgie seulement si douleur
        if douleur_actuelle:
            options.append(f"Option {i} : antalgie — AINS ± morphiniques si besoin, antiémétiques."); i += 1

        # Notes CI
        if grossesse:
            notes.append("Grossesse : ESWL contre-indiquée.")
        if anticoag:
            notes.append("Anticoagulants/troubles de l’hémostase non corrigés : prudence et correction avant geste.")

    # 3) Hygiène-diététique (remplace 'suivi')
    hygiene = [
        "Hydratation : viser ≥ 2 litres/j (adapter si insuffisance cardiaque/rénale).",
        "Réduire le sel (≈6–7 g/j) et modérer les protéines animales (<1 g/kg/j).",
        "Limiter sucres rapides et aliments riches en oxalates si lithiase oxalo-calcique suspectée.",
        "Activité physique régulière, éviter l’immobilisation prolongée.",
        "À distance : bilan métabolique et **adaptation des apports** selon le type de lithiase (si identifié).",
    ]

    # 4) Notes générales
    notes.append("Tout calcul extrait doit être adressé pour **étude spectrométrique** (analyse morpho-constitutionnelle).")

    return {"donnees": donnees, "traitement": options, "hygiene": hygiene, "notes": notes}


# =========================
# LOGIQUE CLINIQUE — INFECTIO (Grossesse, Cystite, PNA, Prostatite)
# =========================

def _flags_severite(seps_sbp_lt90: bool, seps_hr_gt120: bool, confusion: bool, vomissements: bool, obstruction_suspecte: bool):
    """Retourne (est_grave: bool, raisons: list[str])"""
    raisons = []
    if seps_sbp_lt90: raisons.append("Hypotension (sepsis/choc)")
    if seps_hr_gt120: raisons.append("Tachycardie >120/min")
    if confusion: raisons.append("Troubles neuro (confusion)")
    if vomissements: raisons.append("Vomissements empêchant la voie orale")
    if obstruction_suspecte: raisons.append("Obstacle/suspicion de colique ou anurie")
    grave = bool(seps_sbp_lt90 or seps_hr_gt120 or confusion or obstruction_suspecte or vomissements)
    return grave, raisons


def _is_risque_complication(
    homme: bool=False, grossesse: bool=False, age_ge65_fragile: bool=False, anomalies_uro: bool=False,
    immunodep: bool=False, irc_significative: bool=False, sonde: bool=False, diabete_non_controle: bool=False
):
    """Facteurs de risque de complication (hors gravité)"""
    return any([homme, grossesse, age_ge65_fragile, anomalies_uro, immunodep, irc_significative, sonde, diabete_non_controle])


# ---------- CYSTITE (plutôt femme, hors grossesse) ----------

def plan_cystite(
    age: int,
    fievre_ge_38_5: bool,
    lombalgies: bool,
    douleurs_intenses: bool,
    hematurie: bool,
    recidivante: bool,
    homme: bool,
    grossesse: bool,
    age_ge65_fragile: bool,
    anomalies_uro: bool,
    immunodep: bool,
    irc_significative: bool,
    sonde: bool,
    diabete_non_controle: bool,
    seps_sbp_lt90: bool,
    seps_hr_gt120: bool,
    confusion: bool,
    vomissements: bool,
):
    """
    Classe: simple / à risque de complication / grave (suspicion pyélo ou sepsis).
    """
    donnees = [
        ("Âge", f"{age} ans"),
        ("Fièvre ≥ 38,5°C", "Oui" if fievre_ge_38_5 else "Non"),
        ("Douleur lombaire", "Oui" if lombalgies else "Non"),
        ("Douleur intense", "Oui" if douleurs_intenses else "Non"),
        ("Hématurie", "Oui" if hematurie else "Non"),
        ("Récidivante", "Oui" if recidivante else "Non"),
        ("Sexe masculin", "Oui" if homme else "Non"),
        ("Grossesse", "Oui" if grossesse else "Non"),
        ("≥65 ans fragile", "Oui" if age_ge65_fragile else "Non"),
        ("Anomalies uro/obstacle", "Oui" if anomalies_uro else "Non"),
        ("Immunodépression", "Oui" if immunodep else "Non"),
        ("IR chronique significative", "Oui" if irc_significative else "Non"),
        ("Sonde urinaire", "Oui" if sonde else "Non"),
        ("Diabète non contrôlé", "Oui" if diabete_non_controle else "Non"),
    ]
    obstruction_suspecte = anomalies_uro
    grave, raisons_grav = _flags_severite(seps_sbp_lt90, seps_hr_gt120, confusion, vomissements, obstruction_suspecte)

    # Pyélo suspectée si fièvre/lombalgies/douleurs importantes → bascule vers prise en charge PNA
    suspicion_pyelo = fievre_ge_38_5 or lombalgies or douleurs_intenses

    risque = "Grave" if grave or suspicion_pyelo else ("À risque de complication" if _is_risque_complication(
        homme, grossesse, age_ge65_fragile, anomalies_uro, immunodep, irc_significative, sonde, diabete_non_controle
    ) else "Simple")

    classification = [("Catégorie", risque)]
    if grave or suspicion_pyelo:
        classification.append(("Arguments de gravité/suspicion PNA", ", ".join(raisons_grav) if raisons_grav else "Fièvre/douleur lombaire"))

    options = []
    idx = 1
    notes = []
    suivi = []

    # Conduites + probabiliste
    if risque == "Simple":
        options.append(f"Option {idx} : Probabiliste — Fosfomycine-trométamol (dose unique)."); idx += 1
        options.append(f"Option {idx} : Probabiliste — Pivmécillinam (5–7 jours)."); idx += 1
        options.append(f"Option {idx} : Probabiliste — Nitrofurantoïne (5 jours)."); idx += 1
        options.append(f"Option {idx} : Alternative — Fluoroquinolone courte (si alternatives inadaptées/locales)."); idx += 1

        suivi = [
            "ECBU non systématique si évolution typique; reconsulter si non amélioration en 48–72 h.",
            "Si non amélioration 48–72 h : réaliser ECBU, réévaluer diagnostic, envisager écho rénale (± uro-TDM si fièvre/douleurs).",
            "Si récidivantes : mesures hygiéno-diététiques; ECBU à chaque épisode pour différencier rechute/reinfection.",
        ]

    elif risque == "À risque de complication":
        options.append(f"Option {idx} : ECBU avant ATB si possible, puis Probabiliste — Nitrofurantoïne (7 jours)."); idx += 1
        options.append(f"Option {idx} : Probabiliste — Céfixime (5–7 jours) selon éco locale."); idx += 1
        options.append(f"Option {idx} : Probabiliste — Fluoroquinolone (≈5 jours) si alternatives inadaptées."); idx += 1

        suivi = [
            "ECBU systématique AVANT antibiothérapie si possible; adapter au résultat sous 48–72 h.",
            "Si non amélioration 48–72 h : contrôle ECBU, vérifier observance et interactions; imagerie si fièvre/douleur (écho ± uro-TDM).",
        ]
        notes.append("Éviter fosfomycine/nitrofurantoïne chez l’homme (préférer prostatite : voir module dédié).")

    else:  # Grave
        options.append(f"Option {idx} : Suspect PNA/sepsis → bascule vers protocole PNA (voir rubrique PNA)."); idx += 1
        options.append(f"Option {idx} : Hospitalisation si signes de sepsis/choc, vomissements, ou obstacle suspect."); idx += 1
        suivi = [
            "ECBU + hémocultures avant ATB; antibiothérapie IV probabiliste; imagerie (uro-TDM ≤24 h) si douleur/fièvre prolongée/obstacle.",
        ]

    # Étapes communes
    if risque != "Simple":
        notes.append("Toujours adapter l’antibiothérapie à l’antibiogramme (48–72 h).")
    return {"donnees": donnees, "classification": classification, "traitement": options, "suivi": suivi, "notes": notes}


# ---------- PYÉLONÉPHRITE AIGUË (PNA) ----------

def plan_pna(
    fievre_ge_38_5: bool,
    douleur_lombaire: bool,
    vomissements: bool,
    homme: bool,
    grossesse: bool,
    age_ge65_fragile: bool,
    anomalies_uro: bool,
    immunodep: bool,
    irc_significative: bool,
    sonde: bool,
    diabete_non_controle: bool,
    seps_sbp_lt90: bool,
    seps_hr_gt120: bool,
    confusion: bool,
):
    donnees = [
        ("Fièvre ≥ 38,5°C", "Oui" if fievre_ge_38_5 else "Non"),
        ("Douleur lombaire", "Oui" if douleur_lombaire else "Non"),
        ("Vomissements", "Oui" if vomissements else "Non"),
        ("Sexe masculin", "Oui" if homme else "Non"),
        ("Grossesse", "Oui" if grossesse else "Non"),
        ("≥65 ans fragile", "Oui" if age_ge65_fragile else "Non"),
        ("Anomalies uro/obstacle", "Oui" if anomalies_uro else "Non"),
        ("Immunodépression", "Oui" if immunodep else "Non"),
        ("IR chronique significative", "Oui" if irc_significative else "Non"),
        ("Sonde urinaire", "Oui" if sonde else "Non"),
        ("Diabète non contrôlé", "Oui" if diabete_non_controle else "Non"),
    ]
    obstruction_suspecte = anomalies_uro
    grave, raisons_grav = _flags_severite(seps_sbp_lt90, seps_hr_gt120, confusion, vomissements, obstruction_suspecte)

    if grave:
        categorie = "Grave"
    else:
        categorie = "À risque de complication" if _is_risque_complication(
            homme, grossesse, age_ge65_fragile, anomalies_uro, immunodep, irc_significative, sonde, diabete_non_controle
        ) else "Simple"

    classification = [("Catégorie", categorie)]
    if raisons_grav:
        classification.append(("Critères de gravité", ", ".join(raisons_grav)))

    options = []
    idx = 1
    notes = []
    suivi = []

    # Probabiliste par catégorie
    if categorie == "Simple":
        options.append(f"Option {idx} : Probabiliste — Fluoroquinolone per os (si épidémiologie locale favorable)."); idx += 1
        options.append(f"Option {idx} : Probabiliste — C3G (ex. ceftriaxone) dose initiale IV/IM puis relais per os."); idx += 1
        options.append(f"Option {idx} : Alternative — Bêta-lactamine parentérale en relais PO (durée totale 7–10 jours)."); idx += 1

        suivi = [
            "ECBU systématique (avant ATB si possible).",
            "Réévaluation clinique/biologique à 48–72 h; adapter à l’antibiogramme.",
            "Imagerie non systématique au départ; réaliser une écho si douleur inhabituelle, calcul connu, ou si non amélioration 48–72 h.",
        ]

    elif categorie == "À risque de complication":
        options.append(f"Option {idx} : Probabiliste — C3G IV (ex. cefotaxime/ceftriaxone) ± amikacine selon gravité locale."); idx += 1
        options.append(f"Option {idx} : Alternative — BLSE suspecté : carbapénème ± amikacine."); idx += 1

        suivi = [
            "ECBU + hémocultures avant ATB; imagerie uro-TDM ≤24 h si douleur sévère, fièvre persistante, ou obstacle suspect.",
            "Réévaluation à 48–72 h : adapter ATB; relais per os dès apyrexie/prise orale possible; durée 10–14 jours (selon molécule).",
        ]

    else:  # Grave
        options.append(f"Option {idx} : Hospitalisation d’emblée."); idx += 1
        options.append(f"Option {idx} : Probabiliste — C3G IV + amikacine; si BLSE suspecté → carbapénème + amikacine."); idx += 1
        options.append(f"Option {idx} : Drainage urgent si obstacle (JJ/néphrostomie) après avis urologique."); idx += 1

        suivi = [
            "ECBU + hémocultures; bilan biologique complet.",
            "Uro-TDM en urgence si obstacle suspecté; sinon ≤24 h si état sévère persistant.",
            "Réévaluation 24–48 h : adapter; surveillance rapprochée (PA/FC/SpO2/diurèse).",
        ]

    notes.append("Adapter systématiquement au résultat de l’antibiogramme (48–72 h).")
    return {"donnees": donnees, "classification": classification, "traitement": options, "suivi": suivi, "notes": notes}


# ---------- GROSSESSE (bactériurie, cystite, PNA) ----------

def plan_grossesse(
    type_tableau: str,  # "Bactériurie asymptomatique", "Cystite", "PNA"
    terme_9e_mois: bool,
    allergies_betalactamines: bool,
    seps_sbp_lt90: bool,
    seps_hr_gt120: bool,
    vomissements: bool,
):
    donnees = [
        ("Tableau", type_tableau),
        ("9e mois (nitrofurantoïne à éviter)", "Oui" if terme_9e_mois else "Non"),
        ("Allergie bêta-lactamines", "Oui" if allergies_betalactamines else "Non"),
    ]
    grave, raisons_grav = _flags_severite(seps_sbp_lt90, seps_hr_gt120, False, vomissements, False)

    options = []
    idx = 1
    suivi = []
    notes = []

    if type_tableau in ("Bactériurie asymptomatique", "Cystite"):
        # Toujours à risque (grossesse) mais hors gravité
        options.append(f"Option {idx} : Probabiliste — Amoxicilline / Pivmécillinam / Fosfomycine (dose unique) / Céfixime (selon contexte local)."); idx += 1
        if not terme_9e_mois:
            options.append(f"Option {idx} : Alternative — Nitrofurantoïne (éviter au 9e mois)."); idx += 1
        options.append(f"Option {idx} : Alternative — Triméthoprime (à partir du 2e trimestre) si autres CI."); idx += 1

        suivi = [
            "ECBU AVANT traitement; contrôle ECBU 48 h après début si symptômes persistants; ECBU de contrôle 8–10 jours après fin du traitement.",
            "Dépistage mensuel ultérieur de la bactériurie pendant la grossesse.",
            "Si non amélioration à 48–72 h : réévaluer, refaire ECBU, envisager écho rénale.",
        ]

    else:  # PNA gravidique
        options.append(f"Option {idx} : Hospitalisation d’emblée."); idx += 1
        options.append(f"Option {idx} : Probabiliste — C3G IV (ex. ceftriaxone) ± amikacine selon gravité."); idx += 1
        options.append(f"Option {idx} : Alternative — Selon allergie BL, discuter aztréonam ± aminoside (avis spécialisé)."); idx += 1

        suivi = [
            "ECBU + hémocultures avant ATB; surveillance obstétricale.",
            "Imagerie en cas de non réponse 48–72 h ou douleur atypique (écho; uro-TDM si indispensable).",
            "Durée minimale 14 jours; relais per os dès que possible; ECBU de contrôle à 8–10 jours après fin.",
        ]

    if grave:
        notes.append("Signes de gravité (ex. sepsis, vomissements) → hospitalisation et traitement IV.")
    notes.append("Adapter systématiquement à l’antibiogramme (48–72 h).")
    return {"donnees": donnees, "classification": [("Gravité", "Oui" if grave else "Non")], "traitement": options, "suivi": suivi, "notes": notes}


# ---------- HOMME — PROSTATITE AIGUË (IU masculine) ----------

def plan_prostatite(
    fievre_ge_38_5: bool,
    douleurs_perineales: bool,
    dysurie: bool,
    retention: bool,
    post_biopsie_prostate: bool,
    immunodep: bool,
    irc_significative: bool,
    seps_sbp_lt90: bool,
    seps_hr_gt120: bool,
    confusion: bool,
):
    donnees = [
        ("Fièvre ≥ 38,5°C", "Oui" if fievre_ge_38_5 else "Non"),
        ("Douleurs périnéales", "Oui" if douleurs_perineales else "Non"),
        ("Dysurie", "Oui" if dysurie else "Non"),
        ("Rétention aiguë", "Oui" if retention else "Non"),
        ("Contexte post-biopsie", "Oui" if post_biopsie_prostate else "Non"),
        ("Immunodépression", "Oui" if immunodep else "Non"),
        ("IR chronique significative", "Oui" if irc_significative else "Non"),
    ]
    obstruction_suspecte = retention
    grave, raisons_grav = _flags_severite(seps_sbp_lt90, seps_hr_gt120, confusion, False, obstruction_suspecte)

    # Toute IU masculine = à risque; grave si sepsis/retention/post-biopsie fébrile
    categorie = "Grave" if grave or post_biopsie_prostate else "À risque de complication"

    classification = [("Catégorie", categorie)]
    if raisons_grav or post_biopsie_prostate:
        r = raisons_grav.copy()
        if post_biopsie_prostate: r.append("Contexte post-biopsie")
        classification.append(("Critères", ", ".join(r)))

    options = []
    idx = 1
    notes = []
    suivi = []

    if categorie == "À risque de complication":
        options.append(f"Option {idx} : Probabiliste — Fluoroquinolone (bonne diffusion prostatique) **ou** TMP-SMX (relais documenté)."); idx += 1
        options.append(f"Option {idx} : Alternative — Dose initiale C3G (ceftriaxone) puis relais per os (FQ/TMP-SMX) selon ATBgramme."); idx += 1

        suivi = [
            "ECBU systématique (avant ATB si possible) ± hémocultures si fièvre.",
            "Réévaluation 48–72 h; adapter à l’antibiogramme; durée totale ≥14 jours (souvent 14–21 jours).",
            "Éviter nitrofurantoïne, fosfomycine, amoxicilline+acide clavulanique, céfixime (diffusion prostatique insuffisante).",
        ]

    else:  # Grave ou post-biopsie
        options.append(f"Option {idx} : Hospitalisation/prise en charge rapprochée."); idx += 1
        options.append(f"Option {idx} : Probabiliste — C3G IV + amikacine; relais per os par FQ/TMP-SMX dès amélioration."); idx += 1
        if post_biopsie_prostate:
            options.append(f"Option {idx} : Contexte post-biopsie — Bi-antibiothérapie IV d’emblée (C3G + aminoside)."); idx += 1
        if retention:
            options.append(f"Option {idx} : Drainage vésical (sondage sus-pubien privilégié) après avis."); idx += 1

        suivi = [
            "ECBU + hémocultures; bilan biologique.",
            "Échographie si rétention/douleur; uro-TDM si évolution défavorable.",
            "Réévaluation 24–48 h; adapter ATB; durée totale 14–21 jours.",
        ]

    notes.append("Adapter systématiquement au résultat de l’antibiogramme (48–72 h).")
    return {"donnees": donnees, "classification": classification, "traitement": options, "suivi": suivi, "notes": notes}

# =========================
# PAGES (UI)
# =========================

def render_home():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)
    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")


def render_vessie_menu():
    btn_home_and_back()
    st.markdown("## Tumeur de la vessie")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("TVNIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVNIM"))
    with c2:
        st.button("TVIM", use_container_width=True, on_click=lambda: go_module("Vessie: TVIM"))
    with c3:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Vessie: Métastatique"))


def render_tvnim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVNIM (tumeur n’infiltrant pas le muscle)")
    with st.form("tvnim_form"):
        stade = st.selectbox("Stade tumoral", ["pTa", "pT1"])
        grade = st.selectbox("Grade tumoral", ["Bas grade", "Haut grade"])
        taille = st.slider("Taille maximale (mm)", 1, 100, 10)
        nombre = st.selectbox("Nombre de tumeurs", ["Unique", "Multiple", "Papillomatose vésicale"])
        cis_associe = lvi = urethre_prostatique = formes_agressives = False
        if stade == "pT1" and grade == "Haut grade":
            st.markdown("#### Facteurs aggravants (pT1 haut grade) — cochez s’ils sont présents")
            c1, c2 = st.columns(2)
            with c1:
                cis_associe = st.checkbox("CIS associé")
                lvi = st.checkbox("Envahissement lymphovasculaire (LVI)")
            with c2:
                urethre_prostatique = st.checkbox("Atteinte de l’urètre prostatique")
                formes_agressives = st.checkbox("Formes anatomo-pathologiques agressives")
        submitted = st.form_submit_button("🔎 Générer la CAT")
    if submitted:
        risque = stratifier_tvnim(stade, grade, taille, nombre, cis_associe, lvi, urethre_prostatique, formes_agressives)
        traitement, suivi, protocoles, notes_second_look = plan_tvnim(risque)
        donnees_pairs = [
            ("Stade", stade), ("Grade", grade), ("Taille maximale", f"{taille} mm"), ("Nombre", nombre)
        ]
        if stade == "pT1" and grade == "Haut grade":
            if cis_associe: donnees_pairs.append(("CIS associé", "Oui"))
            if lvi: donnees_pairs.append(("LVI", "Oui"))
            if urethre_prostatique: donnees_pairs.append(("Atteinte urètre prostatique", "Oui"))
            if formes_agressives: donnees_pairs.append(("Formes anatomo-path. agressives", "Oui"))
        render_kv_table("🧾 Données saisies", donnees_pairs)
        render_kv_table("📊 Stratification", [("Risque estimé", risque.upper())], "Élément", "Résultat")
        st.markdown("### 💊 Traitement recommandé")
        for t in traitement: st.markdown("- " + t)
        if protocoles:
            st.markdown("### 📦 Schémas BCG (sans dose)")
            for p in protocoles: st.markdown("- " + p)
        st.markdown("### 📅 Modalités de suivi")
        for s in suivi: st.markdown("- " + s)
        st.markdown("### 📝 RTUV de second look — rappels")
        for n in notes_second_look: st.markdown("- " + n)
        sections = {
            "Données": [f"{k}: {v}" for k, v in donnees_pairs],
            "Stratification": [f"Risque estimé : {risque.upper()}"],
            "Traitement recommandé": traitement + (["Schémas BCG :"] + protocoles if protocoles else []),
            "Modalités de suivi": suivi,
            "Rappels second look": notes_second_look,
        }
        report_text = build_report_text("CAT TVNIM", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_TVNIM")


def render_tvim_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 TVIM (tumeur infiltrant le muscle)")
    with st.form("tvim_form"):
        t_cat = st.selectbox("T (clinique)", ["T2", "T3", "T4a"])
        cN_pos = st.radio("Atteinte ganglionnaire clinique (cN+) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        metastases = st.radio("Métastases à distance ?", ["Non", "Oui"], horizontal=True) == "Oui"
        st.markdown("#### Éligibilités & contexte")
        cis_eligible = st.radio("Éligible Cisplatine (PS 0–1, DFG ≥50–60…)?", ["Oui", "Non"], horizontal=True) == "Oui"
        hydron = st.radio("Hydronéphrose ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bonne_fct_v = st.radio("Bonne fonction vésicale ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_diffus = st.radio("CIS diffus ?", ["Non", "Oui"], horizontal=True) == "Oui"
        post_op_high_risk = st.radio("pT3–4 et/ou pN+ attendu/identifié ?", ["Non", "Oui"], horizontal=True) == "Oui"
        neo_adjuvant_fait = st.radio("Néoadjuvant déjà réalisé ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – TVIM")
    if submitted:
        plan = plan_tvim(
            t_cat, cN_pos, metastases, cis_eligible, hydron,
            bonne_fct_v, cis_diffus, post_op_high_risk, neo_adjuvant_fait
        )
        donnees_pairs = [
            ("T", t_cat), ("cN+", "Oui" if cN_pos else "Non"), ("Métastases", "Oui" if metastases else "Non"),
            ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"),
            ("Hydronéphrose", "Oui" if hydron else "Non"),
            ("Bonne fonction vésicale", "Oui" if bonne_fct_v else "Non"),
            ("CIS diffus", "Oui" if cis_diffus else "Non"),
            ("pT3–4/pN+ attendu/identifié", "Oui" if post_op_high_risk else "Non"),
            ("NAC déjà faite", "Oui" if neo_adjuvant_fait else "Non"),
        ]
        render_kv_table("🧾 Données saisies", donnees_pairs)

        st.markdown("### 💊 Traitement recommandé")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Modalités de suivi")
        for x in plan["surveillance"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in donnees_pairs],
            "Traitement recommandé": plan["traitement"],
            "Modalités de suivi": plan["surveillance"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT TVIM", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_TVIM")



def render_vessie_meta_page():
    btn_home_and_back(show_back=True)
    st.header("🔷 Tumeur de la vessie métastatique")
    with st.form("meta_form"):
        st.markdown("#### Contexte & éligibilité")
        platinum_naive = st.radio("Jamais traité par platine (1re ligne) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        cis_eligible = st.radio("Éligible Cisplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        carbo_eligible = st.radio("Éligible Carboplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
        pdl1_pos = st.radio("PD-L1 positif (si dispo) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_platinum = st.radio("A déjà reçu un platine ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_cpi = st.radio("A déjà reçu une immunothérapie (CPI) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bone_mets = st.radio("Métastases osseuses ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT – Métastatique")
    if submitted:
        plan = plan_meta(cis_eligible, carbo_eligible, platinum_naive, pdl1_pos, prior_platinum, prior_cpi, bone_mets)
        donnees_pairs = [
            ("1re ligne (naïf platine)", "Oui" if platinum_naive else "Non"),
            ("Éligible Cisplatine", "Oui" if cis_eligible else "Non"),
            ("Éligible Carboplatine", "Oui" if carbo_eligible else "Non"),
            ("PD-L1 positif", "Oui" if pdl1_pos else "Non"),
            ("Platines reçus", "Oui" if prior_platinum else "Non"),
            ("CPI reçu", "Oui" if prior_cpi else "Non"),
            ("Métastases osseuses", "Oui" if bone_mets else "Non"),
        ]
        render_kv_table("🧾 Données saisies", donnees_pairs)

        st.markdown("### 💊 Traitement recommandé")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in donnees_pairs],
            "Traitement recommandé": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Vessie Métastatique", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_Vessie_Metastatique")


def render_tves_menu():
    btn_home_and_back()
    st.markdown("## Tumeurs des voies excrétrices")
    st.caption("Choisissez le sous-module")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Localisé (non métastatique)", use_container_width=True, on_click=lambda: go_module("TVES: Localisé"))
    with c2:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("TVES: Métastatique"))


def render_tves_local_page():
    btn_home_and_back(show_back=True, back_label="Tumeurs des voies excrétrices")
    st.header("🔷 TVES — localisé (UTUC non métastatique)")
    with st.form("tves_local_form"):
        grade_biopsie = st.selectbox("Grade biopsie URSS", ["Bas grade", "Haut grade", "Indéterminé"])
        cytologie_hg_positive = st.radio("Cytologie haut grade positive ?", ["Non", "Oui"], horizontal=True) == "Oui"
        taille_cm = st.number_input("Taille lésion (cm)", min_value=0.2, max_value=10.0, value=1.5, step=0.1)
        multifocal = st.radio("Multifocale ?", ["Non", "Oui"], horizontal=True) == "Oui"
        invasion_imagerie = st.radio("Invasion suspecte à l’imagerie (uro-TDM/IRM) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        hydron = st.radio("Hydronéphrose ?", ["Non", "Oui"], horizontal=True) == "Oui"
        kss_faisable = st.radio("Traitement conservateur complet réalisable ?", ["Oui", "Non"], horizontal=True) == "Oui"
        accepte_suivi_strict = st.radio("Patient accepte le suivi strict endoscopique/imagerie ?", ["Oui", "Non"], horizontal=True) == "Oui"
        localisation = st.selectbox("Localisation", ["Bassinets/caliciel", "Uretère proximal", "Uretère moyen", "Uretère distal"])
        submitted = st.form_submit_button("🔎 Générer la CAT – TVES localisé")

    if submitted:
        plan = plan_tves_localise(
            grade_biopsie, cytologie_hg_positive, taille_cm, multifocal,
            invasion_imagerie, hydron, kss_faisable, accepte_suivi_strict,
            localisation
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["stratification"], "Élément", "Résultat")

        if len(plan["traitement"]) == 1:
            st.markdown("### 🧭 Conduite recommandée")
            for x in plan["traitement"]:
                st.markdown("- " + x)
        else:
            st.markdown("### 💊 Traitement — Options numérotées")
            for x in plan["traitement"]:
                st.markdown("- " + x)

        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Stratification": [f"{k}: {v}" for k, v in plan["stratification"]],
            "Traitement": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT TVES localisé", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_TVES_Localise")

def render_tves_meta_page():
    btn_home_and_back(show_back=True, back_label="Tumeurs des voies excrétrices")
    st.header("🔷 TVES — métastatique (algorithme EV+Pembro / Platine-Gem / Cis-Gem-Nivo)")

    with st.form("tves_meta_form"):
        ev_pembro_eligible = st.radio("Éligible à EV + Pembrolizumab (1L préférentielle) ?", ["Oui", "Non"], horizontal=True) == "Oui"

        if not ev_pembro_eligible:
            st.markdown("#### Si EV+Pembro non éligible :")
            cis_eligible = st.radio("Éligible Cisplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
            carbo_eligible = st.radio("Éligible Carboplatine ?", ["Oui", "Non"], horizontal=True) == "Oui"
            use_cis_gem_nivo = False
            if cis_eligible:
                use_cis_gem_nivo = st.radio("Choisir 1L **Cisplatine + Gemcitabine + Nivolumab** ?", ["Non", "Oui"], horizontal=True) == "Oui"
        else:
            # Valeurs par défaut si EV+Pembro éligible
            cis_eligible = False
            carbo_eligible = False
            use_cis_gem_nivo = False

        st.markdown("#### Historique & biomarqueurs")
        platinum_naif = st.radio("Naïf de platine (vraie 1re ligne) ?", ["Oui", "Non"], horizontal=True) == "Oui"
        prior_platinum = st.radio("A déjà reçu une chimio à base de platine ?", ["Non", "Oui"], horizontal=True) == "Oui"
        prior_io = st.radio("A déjà reçu une immunothérapie (PD-1/PD-L1) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        fgfr_alt = st.radio("Altérations FGFR2/3 connues ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT – TVES métastatique")

    if submitted:
        plan = plan_tves_metastatique(
            ev_pembro_eligible, cis_eligible, carbo_eligible, platinum_naif,
            fgfr_alt, prior_platinum, prior_io, use_cis_gem_nivo
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])
        st.markdown("### 💊 Traitement — Options numérotées")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Traitement (options)": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT TVES métastatique (algorithme actualisé)", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_TVES_Metastatique")


def render_infectio_menu():
    btn_home_and_back()
    st.markdown("## Infectiologie — Infections urinaires")
    st.caption("Choisissez le sous-module")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Grossesse", use_container_width=True, on_click=lambda: go_module("IU: Grossesse"))
        st.button("Cystite", use_container_width=True, on_click=lambda: go_module("IU: Cystite"))
    with c2:
        st.button("Pyélonéphrite aiguë (PNA)", use_container_width=True, on_click=lambda: go_module("IU: PNA"))
        st.button("Infection masculine (Prostatite)", use_container_width=True, on_click=lambda: go_module("IU: Prostatite"))


# ---------- UI — Cystite ----------
def render_infectio_cystite_page():
    btn_home_and_back(show_back=True, back_label="Infectiologie")
    st.header("🔷 Cystite (hors grossesse) — triage simple / à risque / grave")

    with st.form("cystite_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Âge", min_value=12, max_value=100, value=28)
            fievre_ge_38_5 = st.radio("Fièvre ≥ 38,5°C ?", ["Non", "Oui"], horizontal=True) == "Oui"
            lombalgies = st.radio("Douleur lombaire ?", ["Non", "Oui"], horizontal=True) == "Oui"
            douleurs_intenses = st.radio("Douleur intense ?", ["Non", "Oui"], horizontal=True) == "Oui"
            hematurie = st.radio("Hématurie ?", ["Non", "Oui"], horizontal=True) == "Oui"
            recidivante = st.radio("Cystites récidivantes ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with col2:
            age_ge65_fragile = st.radio("≥65 ans fragile ?", ["Non", "Oui"], horizontal=True) == "Oui"
            anomalies_uro = st.radio("Anomalies uro/obstacle connu ?", ["Non", "Oui"], horizontal=True) == "Oui"
            immunodep = st.radio("Immunodépression ?", ["Non", "Oui"], horizontal=True) == "Oui"
            irc_significative = st.radio("IR chronique importante ?", ["Non", "Oui"], horizontal=True) == "Oui"
            sonde = st.radio("Sonde urinaire ?", ["Non", "Oui"], horizontal=True) == "Oui"
            diabete_non_controle = st.radio("Diabète non contrôlé ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with col3:
            homme = st.radio("Sexe masculin ?", ["Non", "Oui"], horizontal=True) == "Oui"
            grossesse = st.radio("Grossesse ?", ["Non", "Oui"], horizontal=True) == "Oui"
            seps_sbp_lt90 = st.radio("TAS < 90 mmHg ?", ["Non", "Oui"], horizontal=True) == "Oui"
            seps_hr_gt120 = st.radio("FC > 120/min ?", ["Non", "Oui"], horizontal=True) == "Oui"
            confusion = st.radio("Confusion ?", ["Non", "Oui"], horizontal=True) == "Oui"
            vomissements = st.radio("Vomissements majeurs ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT — Cystite")

    if submitted:
        plan = plan_cystite(
            age, fievre_ge_38_5, lombalgies, douleurs_intenses, hematurie, recidivante,
            homme, grossesse, age_ge65_fragile, anomalies_uro, immunodep, irc_significative,
            sonde, diabete_non_controle, seps_sbp_lt90, seps_hr_gt120, confusion, vomissements
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["classification"], "Élément", "Résultat")

        st.markdown("### 💊 Options probabilistes / conduite")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Conduite et suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in plan["donnees"]],
            "Stratification":[f"{k}: {v}" for k,v in plan["classification"]],
            "Traitement": plan["traitement"],
            "Conduite/Follow-up": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT — Cystite", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_Cystite")



# ---------- UI — PNA ----------
def render_infectio_pna_page():
    btn_home_and_back(show_back=True, back_label="Infectiologie")
    st.header("🔷 Pyélonéphrite aiguë (PNA) — triage simple / à risque / grave")

    with st.form("pna_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            fievre_ge_38_5 = st.radio("Fièvre ≥ 38,5°C ?", ["Oui", "Non"], horizontal=True) == "Oui"
            douleur_lombaire = st.radio("Douleur lombaire ?", ["Oui", "Non"], horizontal=True) == "Oui"
            vomissements = st.radio("Vomissements majeurs ?", ["Non", "Oui"], horizontal=True) == "Oui"
            homme = st.radio("Sexe masculin ?", ["Non", "Oui"], horizontal=True) == "Oui"
            grossesse = st.radio("Grossesse ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with col2:
            age_ge65_fragile = st.radio("≥65 ans fragile ?", ["Non", "Oui"], horizontal=True) == "Oui"
            anomalies_uro = st.radio("Anomalies uro/obstacle ?", ["Non", "Oui"], horizontal=True) == "Oui"
            immunodep = st.radio("Immunodépression ?", ["Non", "Oui"], horizontal=True) == "Oui"
            irc_significative = st.radio("IR chronique importante ?", ["Non", "Oui"], horizontal=True) == "Oui"
            sonde = st.radio("Sonde urinaire ?", ["Non", "Oui"], horizontal=True) == "Oui"
            diabete_non_controle = st.radio("Diabète non contrôlé ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with col3:
            seps_sbp_lt90 = st.radio("TAS < 90 mmHg ?", ["Non", "Oui"], horizontal=True) == "Oui"
            seps_hr_gt120 = st.radio("FC > 120/min ?", ["Non", "Oui"], horizontal=True) == "Oui"
            confusion = st.radio("Confusion ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT — PNA")

    if submitted:
        plan = plan_pna(
            fievre_ge_38_5, douleur_lombaire, vomissements, homme, grossesse, age_ge65_fragile,
            anomalies_uro, immunodep, irc_significative, sonde, diabete_non_controle,
            seps_sbp_lt90, seps_hr_gt120, confusion
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["classification"], "Élément", "Résultat")

        st.markdown("### 💊 Options probabilistes / conduite")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Conduite et suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in plan["donnees"]],
            "Stratification":[f"{k}: {v}" for k,v in plan["classification"]],
            "Traitement": plan["traitement"],
            "Conduite/Follow-up": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT — PNA", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_PNA")



# ---------- UI — Grossesse ----------
def render_infectio_grossesse_page():
    btn_home_and_back(show_back=True, back_label="Infectiologie")
    st.header("🔷 Infection urinaire au cours de la grossesse")

    with st.form("iu_grossesse_form"):
        type_tableau = st.selectbox("Tableau clinique", ["Bactériurie asymptomatique", "Cystite", "PNA"])
        terme_9e_mois = st.radio("9e mois de grossesse ?", ["Non", "Oui"], horizontal=True) == "Oui"
        allergies_betalactamines = st.radio("Allergie bêta-lactamines ?", ["Non", "Oui"], horizontal=True) == "Oui"
        seps_sbp_lt90 = st.radio("TAS < 90 mmHg ?", ["Non", "Oui"], horizontal=True) == "Oui"
        seps_hr_gt120 = st.radio("FC > 120/min ?", ["Non", "Oui"], horizontal=True) == "Oui"
        vomissements = st.radio("Vomissements majeurs ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT — Grossesse")

    if submitted:
        plan = plan_grossesse(
            type_tableau, terme_9e_mois, allergies_betalactamines,
            seps_sbp_lt90, seps_hr_gt120, vomissements
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Gravité", plan["classification"], "Élément", "Résultat")

        st.markdown("### 💊 Options probabilistes / conduite")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Conduite et suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in plan["donnees"]],
            "Gravité":[f"{k}: {v}" for k,v in plan["classification"]],
            "Traitement": plan["traitement"],
            "Conduite/Follow-up": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT — IU Grossesse", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_IU_Grossesse")


# ---------- UI — Prostatite ----------
def render_infectio_homme_page():
    btn_home_and_back(show_back=True, back_label="Infectiologie")
    st.header("🔷 Infection masculine — Prostatite aiguë")

    with st.form("iu_homme_form"):
        col1, col2 = st.columns(2)
        with col1:
            fievre_ge_38_5 = st.radio("Fièvre ≥ 38,5°C ?", ["Oui", "Non"], horizontal=True) == "Oui"
            douleurs_perineales = st.radio("Douleurs périnéales ?", ["Oui", "Non"], horizontal=True) == "Oui"
            dysurie = st.radio("Dysurie ?", ["Oui", "Non"], horizontal=True) == "Oui"
            retention = st.radio("Rétention aiguë ?", ["Non", "Oui"], horizontal=True) == "Oui"
            post_biopsie_prostate = st.radio("Post-biopsie prostatique récente ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with col2:
            immunodep = st.radio("Immunodépression ?", ["Non", "Oui"], horizontal=True) == "Oui"
            irc_significative = st.radio("IR chronique importante ?", ["Non", "Oui"], horizontal=True) == "Oui"
            seps_sbp_lt90 = st.radio("TAS < 90 mmHg ?", ["Non", "Oui"], horizontal=True) == "Oui"
            seps_hr_gt120 = st.radio("FC > 120/min ?", ["Non", "Oui"], horizontal=True) == "Oui"
            confusion = st.radio("Confusion ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT — Prostatite")

    if submitted:
        plan = plan_prostatite(
            fievre_ge_38_5, douleurs_perineales, dysurie, retention, post_biopsie_prostate,
            immunodep, irc_significative, seps_sbp_lt90, seps_hr_gt120, confusion
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["classification"], "Élément", "Résultat")

        st.markdown("### 💊 Options probabilistes / conduite")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 📅 Conduite et suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données":[f"{k}: {v}" for k,v in plan["donnees"]],
            "Stratification":[f"{k}: {v}" for k,v in plan["classification"]],
            "Traitement": plan["traitement"],
            "Conduite/Follow-up": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT — Prostatite aiguë", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_Prostatite")

# -------------------------
# LITHIASE (UI) — MAJ
# -------------------------
def render_lithiase_page():
    btn_home_and_back()
    st.header("🔷 Lithiase urinaire — Conduite à tenir")

    with st.form("lithiase_form"):
        st.markdown("#### Triage initial")
        c1, c2, c3, c4 = st.columns(4)
        with c1: fievre = st.radio("Fièvre / infection ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with c2: hyperalgique = st.radio("Douleur hyperalgique ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with c3: oligoanurie = st.radio("Oligo-anurie / IR ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with c4: doute_diag = st.radio("Doute diagnostique ?", ["Non", "Oui"], horizontal=True) == "Oui"

        st.markdown("#### Contexte")
        c5, c6, c7 = st.columns(3)
        with c5: grossesse = st.radio("Grossesse ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with c6: anticoag = st.radio("Anticoagulants / troubles hémostase non corrigés ?", ["Non", "Oui"], horizontal=True) == "Oui"
        with c7: douleur_actuelle = st.radio("Douleur actuelle ?", ["Non", "Oui"], horizontal=True) == "Oui"

        st.markdown("#### Calcul (si connu)")
        c8, c9 = st.columns(2)
        with c8:
            localisation = st.selectbox(
                "Localisation",
                ["Uretère distal", "Uretère moyen", "Uretère proximal", "Rein (intracavicitaire)"],
                index=0
            )
        with c9:
            taille_mm = st.number_input("Taille estimée (mm)", min_value=0, max_value=40, value=5, step=1)

        submitted = st.form_submit_button("🔎 Générer la CAT – Lithiase")

    if submitted:
        plan = plan_lithiase(
            fievre=fievre,
            hyperalgique=hyperalgique,
            oligoanurie=oligoanurie,
            doute_diag=doute_diag,
            grossesse=grossesse,
            anticoag=anticoag,
            localisation=localisation,
            taille_mm=taille_mm if taille_mm > 0 else None,
            douleur_actuelle=douleur_actuelle,
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])

        st.markdown("### 💊 Conduite à tenir (options classées)")
        for x in plan["traitement"]:
            st.markdown("- " + x)

        st.markdown("### 🍽️ Règles hygiéno-diététiques")
        for x in plan["hygiene"]:
            st.markdown("- " + x)

        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        # Export
        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Conduite à tenir": plan["traitement"],
            "Hygiène-diététique": plan["hygiene"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Lithiase", sections)
        st.markdown("### 📤 Export")
        offer_exports(report_text, "CAT_Lithiase")


# -------------------------
# cancer du rein  (UI)
# -------------------------
def render_kidney_menu():
    btn_home_and_back()
    st.markdown("## Tumeur du rein")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("Non métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Non métastatique"))
    with c2:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Rein: Métastatique"))
    with c3:
        st.button("Indications de biopsie", use_container_width=True, on_click=lambda: go_module("Rein: Biopsie"))


def render_kidney_local_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur non métastatique")

    # Mapping libellé → cT
    ct_labels = [
        "Localisé — T1a (≤ 4 cm)",
        "Localisé — T1b (> 4 à ≤ 7 cm)",
        "Localisé — T2a (> 7 à ≤ 10 cm)",
        "Localisé — T2b (> 10 cm)",
        "Localement avancé — T3a",
        "Localement avancé — T3b",
        "Localement avancé — T3c",
        "Localement avancé — T4",
    ]
    ct_map = {
        "Localisé — T1a (≤ 4 cm)": "T1a",
        "Localisé — T1b (> 4 à ≤ 7 cm)": "T1b",
        "Localisé — T2a (> 7 à ≤ 10 cm)": "T2a",
        "Localisé — T2b (> 10 cm)": "T2b",
        "Localement avancé — T3a": "T3a",
        "Localement avancé — T3b": "T3b",
        "Localement avancé — T3c": "T3c",
        "Localement avancé — T4": "T4",
    }

    with st.form("kidney_local_form"):
        cT_label = st.selectbox("Catégorie (sans saisie de taille)", ct_labels, index=0)
        cT = ct_map[cT_label]

        cN_pos = st.radio("Adénopathies cliniques (cN+) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        thrombus = st.selectbox("Thrombus veineux", ["Aucun", "Veine rénale", "VCC infra-hépatique", "VCC supra-hépatique/atrium"])
        rein_unique_ou_CKD = st.radio("Rein unique ou CKD significative ?", ["Non", "Oui"], horizontal=True) == "Oui"
        tumeur_hilaire = st.radio("Tumeur hilaire/centrale ?", ["Non", "Oui"], horizontal=True) == "Oui"
        exophytique = st.radio("Tumeur exophytique ?", ["Oui", "Non"], horizontal=True) == "Oui"
        age = st.number_input("Âge (ans)", min_value=18, max_value=100, value=62)
        haut_risque_op = st.radio("Haut risque opératoire ?", ["Non", "Oui"], horizontal=True) == "Oui"
        biopsie_dispo = st.radio("Biopsie disponible ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT – Rein non métastatique")

    if submitted:
        plan = plan_rein_local(
            cT, cN_pos, thrombus, rein_unique_ou_CKD, tumeur_hilaire,
            exophytique, age, haut_risque_op, biopsie_dispo
        )
        render_kv_table("🧾 Données saisies", plan["donnees"])
        st.markdown("### 💊 Traitement — Options numérotées")
        for x in plan["traitement"]:
            st.markdown("- " + x)
        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)
        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Traitement (options)": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Rein non métastatique", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Rein_Non_Metastatique")


def render_kidney_meta_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — tumeur métastatique")
    with st.form("kidney_meta_form"):
        histo = st.selectbox("Histologie présumée/confirmée", ["ccRCC", "non-ccRCC (papillaire/chromophobe/autre)"])
        risk_system = st.radio("Classification pronostique", ["IMDC (Heng)", "MSKCC (Motzer)"], horizontal=True)

        st.markdown("#### Variables communes")
        kps = st.slider("Karnofsky (%)", 50, 100, 90, step=10)
        karnofsky_lt80 = (kps < 80)
        time_le_12 = st.radio("Délai diagnostic → traitement systémique ≤ 12 mois ?", ["Non", "Oui"], horizontal=True) == "Oui"
        hb_basse = st.radio("Hb < LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
        ca_haut = st.radio("Calcium corrigé > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"

        if risk_system.startswith("IMDC"):
            st.markdown("#### Variables spécifiques IMDC (Heng)")
            neutro_hauts = st.radio("Neutrophiles > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            plaquettes_hautes = st.radio("Plaquettes > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            ldh_haut = False
        else:
            st.markdown("#### Variables spécifiques MSKCC (Motzer)")
            ldh_haut = st.radio("LDH > LSN ?", ["Non", "Oui"], horizontal=True) == "Oui"
            neutro_hauts = False
            plaquettes_hautes = False

        st.markdown("#### Charge tumorale & sites")
        oligo = st.radio("Oligométastatique (nombre limité, résécable/irradiable) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        bone = st.radio("Métastases osseuses ?", ["Non", "Oui"], horizontal=True) == "Oui"
        brain = st.radio("Métastases cérébrales ?", ["Non", "Oui"], horizontal=True) == "Oui"
        liver = st.radio("Métastases hépatiques ?", ["Non", "Oui"], horizontal=True) == "Oui"
        io_contra = st.radio("Contre-indication à l’immunothérapie ?", ["Non", "Oui"], horizontal=True) == "Oui"

        submitted = st.form_submit_button("🔎 Générer la CAT – Rein métastatique")

    if submitted:
        if risk_system.startswith("IMDC"):
            score, group = calc_imdc(karnofsky_lt80, time_le_12, hb_basse, ca_haut, neutro_hauts, plaquettes_hautes)
            label = "IMDC (Heng)"
        else:
            score, group = calc_mskcc(karnofsky_lt80, time_le_12, hb_basse, ca_haut, ldh_haut)
            label = "MSKCC (Motzer)"

        plan = plan_rein_meta(
            "ccRCC" if "ccRCC" in histo else "non-ccRCC",
            score, group, label, oligo, bone, brain, liver, io_contra
        )

        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", plan["stratification"], "Système", "Résultat")
        st.markdown("### 💊 Traitement — Options numérotées")
        for x in plan["traitement"]:
            st.markdown("- " + x)
        st.markdown("### 📅 Modalités de suivi")
        for x in plan["suivi"]:
            st.markdown("- " + x)
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for x in plan["notes"]:
                st.markdown("- " + x)

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Stratification": [f"{label}: {group} (score {score})"],
            "Traitement (options)": plan["traitement"],
            "Modalités de suivi": plan["suivi"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Rein métastatique", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Rein_Metastatique")


def render_kidney_biopsy_page():
    btn_home_and_back(show_back=True, back_label="Tumeur du rein")
    st.header("🔷 Rein — Indications de biopsie percutanée")
    st.markdown("Les indications suivantes s’appliquent :")
    st.markdown("- **Avant un traitement médical** en l’absence de diagnostic histologique ;")
    st.markdown("- **Avant un traitement focal** (radiofréquence, curiethérapie ou radiothérapie) ;")
    st.markdown("- **Avant une néphrectomie élargie** pour tumeur localisée si la néphrectomie partielle est jugée non réalisable (**cT1, cT2**) ;")
    st.markdown("- **Avant une néphrectomie partielle** pour tumeur de complexité chirurgicale élevée et risque de totalisation ;")
    st.markdown("- **En cas d’indication impérative**, de rein unique et de tumeurs bilatérales ;")
    st.markdown("- **En cas d’incertitude diagnostique** (lymphome, métastase d’un autre cancer, carcinome urothélial, sarcome).")


# =========================
# PAGES — PROSTATE (UI)
# =========================

def render_prostate_menu():
    btn_home_and_back()
    st.markdown("## Tumeur de la prostate")
    st.caption("Choisissez le sous-module")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("Localisée", use_container_width=True, on_click=lambda: go_module("Prostate: Localisée"))
    with c2:
        st.button("Récidive", use_container_width=True, on_click=lambda: go_module("Prostate: Récidive"))
    with c3:
        st.button("Métastatique", use_container_width=True, on_click=lambda: go_module("Prostate: Métastatique"))


def render_prostate_localise_page():
    btn_home_and_back(show_back=True, back_label="Tumeur de la prostate")
    st.header("🔷 Prostate localisée — stratification & CAT")
    with st.form("prost_loc_form"):
        cT = st.selectbox("Stade clinique (cT)", ["T1", "T2a", "T2b", "T2c", "T3a", "T3b", "T4"])
        psa = st.number_input("PSA (ng/mL)", min_value=0.0, step=0.1, value=7.0)
        isup = st.selectbox("ISUP (1–5)", [1, 2, 3, 4, 5])
        exp = st.number_input("Espérance de vie estimée (ans)", min_value=1, max_value=30, value=12)
        submitted = st.form_submit_button("🔎 Générer la CAT — Localisée")

    if submitted:
        plan = plan_prostate_localise(psa, isup, cT, exp)
        render_kv_table("🧾 Données saisies", plan["donnees"])
        render_kv_table("📊 Stratification", [("Risque", plan["risque"].upper())], "Élément", "Résultat")
        st.markdown("### 💊 Options de traitement")
        for x in plan["options"]:
            st.markdown(f"- **{x['label']}** — *niveau de reco : {x['degre']}*  \n  {x['details']}")
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for n in plan["notes"]:
                st.markdown(f"- {n}")

        sections = {
            "Données": [f"{k}: {v}" for k, v in plan["donnees"]],
            "Stratification": [f"Risque : {plan['risque'].upper()}"],
            "Options": [f"{o['label']} — {o['degre']} : {o['details']}" for o in plan["options"]],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Prostate Localisée", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Prostate_Localisee")


def render_prostate_recidive_page():
    btn_home_and_back(show_back=True, back_label="Tumeur de la prostate")
    st.header("🔷 Prostate — Récidive (biologique)")

    with st.form("prost_rec_form"):
        type_initial = st.selectbox("Traitement initial", ["Prostatectomie", "Radiothérapie"])
        psa_actuel = st.number_input("PSA actuel (ng/mL)", min_value=0.0, step=0.01, value=0.18)
        psa_nadir = None
        conf = st.number_input("Nombre de dosages confirmant (si prostatectomie)", min_value=1, max_value=3, value=1)
        if type_initial == "Radiothérapie":
            psa_nadir = st.number_input("PSA nadir post-RT (si connu)", min_value=0.0, step=0.01, value=0.1)
        submitted = st.form_submit_button("🔎 Évaluer la récidive")

    if submitted:
        plan = plan_prostate_recidive(type_initial, psa_actuel, psa_nadir, conf)
        st.markdown(f"**Résumé :** {plan['resume']}")
        st.markdown("### 💊 Options")
        for x in plan["options"]:
            st.markdown(f"- **{x['label']}** — *{x['degre']}*  \n  {x['details']}")
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for n in plan["notes"]:
                st.markdown(f"- {n}")

        sections = {
            "Résumé": [plan["resume"]],
            "Options": [f"{o['label']} — {o['degre']} : {o['details']}" for o in plan["options"]],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Prostate Récidive", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Prostate_Recidive")


def render_prostate_meta_page():
    btn_home_and_back(show_back=True, back_label="Tumeur de la prostate")
    st.header("🔷 Prostate métastatique — mHSPC / mCRPC")

    with st.form("prost_meta_form"):
        testo_castration = st.radio("Testostérone < 50 ng/dL (castration) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        volume_eleve = st.radio("Volume de la maladie élevé (ex : haut volume) ?", ["Non", "Oui"], horizontal=True) == "Oui"
        sympt_os = st.radio("Symptômes osseux ?", ["Non", "Oui"], horizontal=True) == "Oui"
        deja_doc = st.radio("Docétaxel déjà reçu ?", ["Non", "Oui"], horizontal=True) == "Oui"
        deja_arpi = st.radio("ARPI (abiratérone/enzalutamide/apalutamide) déjà reçu ?", ["Non", "Oui"], horizontal=True) == "Oui"
        alt_HRR = st.radio("Altération gènes HRR (BRCA/ATM) connue ?", ["Non", "Oui"], horizontal=True) == "Oui"
        submitted = st.form_submit_button("🔎 Générer la CAT — Métastatique")

    if submitted:
        plan = plan_prostate_metastatique(testo_castration, volume_eleve, sympt_os, deja_doc, deja_arpi, alt_HRR)
        render_kv_table("🧾 Profil", [("Statut", plan["profil"])])
        st.markdown("### 💊 Options")
        for x in plan["options"]:
            st.markdown(f"- **{x['label']}** — *{x['degre']}*  \n  {x['details']}")
        if plan["adjoints"]:
            st.markdown("### ➕ Mesures adjointes")
            for a in plan["adjoints"]:
                st.markdown(f"- {a}")
        if plan["notes"]:
            st.markdown("### 📝 Notes")
            for n in plan["notes"]:
                st.markdown(f"- {n}")

        sections = {
            "Profil": [plan["profil"]],
            "Options": [f"{o['label']} — {o['degre']} : {o['details']}" for o in plan["options"]],
            "Mesures adjointes": plan["adjoints"],
            "Notes": plan["notes"],
        }
        report_text = build_report_text("CAT Prostate Métastatique", sections)
        st.markdown("### 📤 Export"); offer_exports(report_text, "CAT_Prostate_Metastatique")

# =========================
# ROUTING + FALLBACK
# =========================

def render_home_wrapper():
    top_header()
    st.markdown("### Sélectionnez une rubrique")
    st.caption(APP_SUBTITLE)
    col1, col2 = st.columns(2)
    for i, mod in enumerate(MODULES):
        with (col1 if i % 2 == 0 else col2):
            category_button(mod, PALETTE[mod], key=f"btn_{i}")


def render_generic(page_label: str):
    btn_home_and_back()
    st.header(page_label)
    st.info("Module en cours de construction.")


page = st.session_state["page"]
if page == "Accueil":
    render_home_wrapper()
elif page == "Tumeur de la vessie":
    render_vessie_menu()
elif page == "Vessie: TVNIM":
    render_tvnim_page()
elif page == "Vessie: TVIM":
    render_tvim_page()
elif page == "Vessie: Métastatique":
    render_vessie_meta_page()
elif page == "Tumeur du rein":
    render_kidney_menu()
elif page == "Rein: Non métastatique":
    render_kidney_local_page()
elif page == "Rein: Métastatique":
    render_kidney_meta_page()
elif page == "Rein: Biopsie":
    render_kidney_biopsy_page()
elif page == "Tumeurs des voies excrétrices":
    render_tves_menu()
elif page == "TVES: Localisé":
    render_tves_local_page()
elif page == "TVES: Métastatique":
    render_tves_meta_page()
elif page == "Infectiologie":
    render_infectio_menu()
elif page == "IU: Grossesse":
    render_infectio_grossesse_page()
elif page == "IU: Cystite":
    render_infectio_cystite_page()
elif page == "IU: PNA":
    render_infectio_pna_page()
elif page == "IU: Prostatite":
    render_infectio_homme_page() 
elif page == "Lithiase":
    render_lithiase_page()
elif page == "Hypertrophie bénigne de la prostate (HBP)":
elif page == "Tumeur de la prostate":
    render_prostate_menu()
elif page == "Prostate: Localisée":
    render_prostate_localise_page()
elif page == "Prostate: Récidive":
    render_prostate_recidive_page()
elif page == "Prostate: Métastatique":
    render_prostate_meta_page()
else:
    render_generic(page)
