import base64
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PRIMARY = "#5865F2"
PURPLE = "#7C4DFF"
INK = "#101116"
MUTED = "#687083"
BG = "#F4F5FF"
BORDER = "#E4E6F2"


def asset_data_uri(name: str) -> str:
    path = ASSETS / name
    if not path.exists():
        return ""
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#101116; --muted:#687083; --bg:#F4F5FF; --purple:#7C4DFF; --blue:#5865F2; --border:#E4E6F2; }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
    .stApp { background:var(--bg); color:var(--ink); }
    #MainMenu, footer { visibility:hidden; }
    header[data-testid="stHeader"] { background:transparent; }
    .block-container { max-width:1220px; padding:0 28px 48px; }
    h1,h2,h3,h4 { font-family:'Space Grotesk', sans-serif !important; letter-spacing:-.035em; color:var(--ink); }
    p, li { color:var(--muted); }
    .rs-nav { position:relative; margin:0 -28px 28px; padding:12px 28px; background:#08090C; color:white; display:flex; align-items:center; justify-content:space-between; gap:20px; }
    .rs-brand { display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:-.02em; color:white; }
    .rs-brand img { width:34px; height:34px; }
    .rs-navlinks { display:flex; gap:24px; align-items:center; font-size:12px; color:#D7D8DF; }
    .rs-pill { display:inline-flex; align-items:center; gap:7px; border:1px solid #2A2C35; border-radius:999px; padding:8px 12px; color:white; font-size:11px; }
    .rs-hero { padding:46px 0 38px; }
    .rs-kicker { display:inline-flex; padding:7px 11px; border:1px solid #D8DAFF; background:#FFFFFF; border-radius:999px; font-size:11px; color:#5962C8; font-weight:700; }
    .rs-hero-title { font-size:clamp(42px,6vw,76px); line-height:.93; margin:14px 0 18px; max-width:720px; }
    .rs-gradient-text { background:linear-gradient(90deg,#4F46E5,#8B5CF6,#5865F2); -webkit-background-clip:text; color:transparent; }
    .rs-lead { font-size:16px; line-height:1.75; max-width:650px; }
    .rs-card { background:#fff; border:1px solid var(--border); border-radius:24px; padding:25px; box-shadow:0 12px 34px rgba(30,35,80,.07); }
    .rs-card-tight { padding:18px; }
    .rs-section { padding:62px 0; }
    .rs-section-head { text-align:center; margin-bottom:28px; }
    .rs-section-head h2 { font-size:42px; margin:7px 0 8px; }
    .rs-section-label { text-transform:uppercase; letter-spacing:.14em; font-size:10px; font-weight:800; color:#6670DB; margin-bottom:8px; }
    .rs-feature-icon { width:40px;height:40px;border-radius:13px;background:#F0F1FF;display:flex;align-items:center;justify-content:center;font-size:19px;margin-bottom:14px; }
    .rs-feature h3 { font-size:20px; margin:0 0 7px; }
    .rs-feature p { font-size:12px; line-height:1.6; }
    .rs-portal { min-height:250px; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; position:relative; }
    .rs-portal:after { content:''; position:absolute; width:170px;height:170px;border-radius:50%;right:-55px;bottom:-75px;background:#ECECFF; }
    .rs-portal h3 { font-size:28px; margin:3px 0 8px; }
    .rs-tag { display:inline-block; padding:6px 9px; border-radius:999px; background:#F1F2FF; color:#5962C8; font-size:10px; font-weight:700; }
    .rs-stack { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
    .rs-tech { background:#fff; border:1px solid var(--border); border-radius:18px; padding:18px; }
    .rs-tech strong { display:block; margin-bottom:5px; }
    .rs-tech span { font-size:11px; color:var(--muted); }
    .rs-class { background:#fff; border:1px solid var(--border); border-radius:18px; padding:18px; min-height:130px; }
    .rs-class-code { font-family:'Space Grotesk'; font-size:25px; font-weight:700; color:#5865F2; }
    .rs-class-name { font-weight:700; font-size:13px; margin-top:4px; }
    .rs-class-desc { font-size:11px; line-height:1.5; margin-top:6px; }
    .rs-band { background:linear-gradient(135deg,#5865F2,#7C4DFF); border-radius:28px; color:#fff; padding:42px; margin:20px 0; }
    .rs-band h2,.rs-band p { color:white; }
    .rs-band h2 { font-size:38px; margin:0 0 7px; }
    .rs-footer { margin:54px -28px -48px; padding:46px 28px 28px; background:#08090C; color:white; }
    .rs-footer p,.rs-footer span { color:#A7A9B3; font-size:11px; line-height:1.6; }
    .rs-footer h4 { color:white; font-size:12px; margin:0 0 10px; }
    .rs-footer-brand { color:white; font-family:'Space Grotesk'; font-weight:700; }
    .rs-auth-wrap { max-width:520px; margin:35px auto 50px; }
    .rs-auth-title { text-align:center; font-size:42px; margin:7px 0; }
    .rs-auth-sub { text-align:center; font-size:13px; margin-bottom:25px; }
    .rs-dashboard-hero { background:linear-gradient(135deg,#17182A,#25295C); border-radius:26px; padding:30px; color:white; margin:20px 0 25px; position:relative; overflow:hidden; }
    .rs-dashboard-hero:after { content:''; position:absolute; width:260px;height:260px;border-radius:50%;right:-80px;top:-100px;background:rgba(124,77,255,.35); }
    .rs-dashboard-hero h1,.rs-dashboard-hero p,.rs-dashboard-hero span { color:white; position:relative; z-index:1; }
    .rs-dashboard-hero h1 { margin:4px 0 6px; font-size:38px; }
    .rs-stat { background:white; border:1px solid var(--border); border-radius:18px; padding:18px; }
    .rs-stat small { color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
    .rs-stat strong { display:block; font-family:'Space Grotesk'; font-size:29px; margin-top:5px; }
    .rs-result { background:#F7F7FF; border:1px solid #DDE0FF; border-radius:20px; padding:20px; margin:14px 0; }
    .rs-result-title { font-size:10px; text-transform:uppercase; letter-spacing:.12em; color:#6870D0; font-weight:800; }
    .rs-result-value { font-family:'Space Grotesk'; font-size:32px; font-weight:700; margin-top:3px; }
    .rs-confidence { display:inline-flex; padding:6px 10px; border-radius:999px; background:#E8F7ED; color:#1F7A43; font-size:11px; font-weight:700; }
    .rs-empty { text-align:center; padding:42px 20px; border:1px dashed #D6D9E7; border-radius:20px; background:#FAFAFF; }
    .rs-disclaimer { background:#FFF9EA; border:1px solid #F1DFAB; color:#735B16; border-radius:15px; padding:12px 14px; font-size:11px; line-height:1.55; }
    .rs-report { background:#fff; border:1px solid var(--border); border-radius:20px; padding:24px; }
    div[data-testid="stFileUploader"] { border-radius:18px; }
    .stButton > button { border-radius:999px !important; border:1px solid #DADCE8 !important; font-weight:700 !important; min-height:42px; transition:.2s; }
    .stButton > button:hover { transform:translateY(-1px); border-color:#5865F2 !important; box-shadow:0 8px 22px rgba(88,101,242,.16); }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] div { border-radius:12px !important; }
    div[data-testid="stTabs"] button { font-weight:700; }
    @media(max-width:800px){ .rs-navlinks{display:none}.rs-stack{grid-template-columns:1fr}.rs-hero-title{font-size:48px}.rs-band{padding:28px}.rs-section-head h2{font-size:34px} }
    </style>
    """, unsafe_allow_html=True)


def render_header(active_title=""):
    logo = asset_data_uri("logo.svg")
    st.markdown(f"""
    <div class="rs-nav">
      <div class="rs-brand"><img src="{logo}"><span>RetinaScan AI</span></div>
      <div class="rs-navlinks"><span>AI Screening</span><span>Six-Class Detection</span><span>Secure Workflow</span></div>
      <div class="rs-pill">{active_title or 'Clinical AI Platform'}</div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="rs-footer">
      <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:28px;">
        <div><div class="rs-footer-brand">◉ RetinaScan AI</div><p style="max-width:340px;margin-top:10px;">AI-assisted multi-class retinal fundus screening using a fine-tuned ResNet50 model. Designed as a final-year academic project and clinical decision-support prototype.</p></div>
        <div><h4>Platform</h4><span>AI Screening</span><br><span>Doctor Portal</span><br><span>Patient Portal</span></div>
        <div><h4>Technology</h4><span>Streamlit</span><br><span>Flask API</span><br><span>Supabase</span></div>
        <div><h4>Safety</h4><span>AI-assisted screening</span><br><span>Clinical review required</span><br><span>Not a diagnosis</span></div>
      </div>
      <div style="border-top:1px solid #24252D;margin-top:30px;padding-top:18px;font-size:10px;color:#777A85;">RetinaScan AI • Fine-tuned ResNet50 • Six-class retinal disease screening</div>
    </div>
    """, unsafe_allow_html=True)


def confidence_badge(prediction, confidence):
    return f'<span class="rs-confidence">● {prediction} • {float(confidence):.1f}% confidence</span>'
