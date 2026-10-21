import streamlit as st
from utils.styling import render_header, render_footer, asset_data_uri

CLASSES = [
    ("AMD", "Age-related Macular Degeneration", "Macular changes affecting central vision."),
    ("DR", "Diabetic Retinopathy", "Diabetes-related retinal blood-vessel damage."),
    ("DN", "Diabetic Neuropathy", "Subtle diabetes-related retinal changes."),
    ("MH", "Macular Hole", "A gap or structural thinning in the macula."),
    ("ODC", "Optic Disc Cupping", "Enlargement of the optic cup, often linked to glaucoma."),
    ("Normal", "Normal Retina", "No disease class detected by the model."),
]


def portal_button(role, label, key_suffix):
    # FIXED: removed width="stretch"
    if st.button(label, key=f"portal_{role}_{key_suffix}"):
        st.session_state.portal = role
        st.session_state.page = "login"
        st.rerun()


def show_landing():
    render_header("AI retinal screening")
    logo = asset_data_uri("logo.svg")
    retina = asset_data_uri("retina_hero.svg")

    left, right = st.columns([1.25, .75], gap="large")

    with left:
        st.markdown(
            '<div class="rs-hero">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<span class="rs-kicker">Fine-tuned ResNet50 • Transfer Learning</span>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<h1 class="rs-hero-title">'
            'AI-powered '
            '<span class="rs-gradient-text">retinal disease</span> detection.'
            '</h1>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<p class="rs-lead">'
            'A polished screening workspace for analyzing retinal fundus '
            'photographs across six classes. Built to help clinicians '
            'perform a faster, more consistent first-pass review.'
            '</p>',
            unsafe_allow_html=True
        )

        a, b = st.columns(2)

        with a:
            portal_button(
                "doctor",
                "Doctor Portal  →",
                "hero_doctor"
            )

        with b:
            portal_button(
                "student",
                "Patient Portal  →",
                "hero_patient"
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right:
        st.markdown(
            f'<div style="padding:40px 10px 0;">'
            f'<img src="{retina}" '
            f'style="width:100%;max-width:420px;display:block;margin:auto;">'
            f'</div>',
            unsafe_allow_html=True
        )

    # ==========================================================
    # WHY RETINASCAN AI
    # ==========================================================

    st.markdown(
        '<div class="rs-section">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-section-head">'
        '<div class="rs-section-label">Why RetinaScan AI</div>'
        '<h2>Innovation features</h2>'
        '<p>Designed as a complete academic AI screening workflow.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    features = [
        (
            "◉",
            "AI Fundus Analysis",
            "Upload a fundus image and send it directly "
            "to the existing prediction API."
        ),
        (
            "✦",
            "Six-Class Intelligence",
            "AMD, DR, DN, MH, ODC and Normal in one "
            "unified classification workflow."
        ),
        (
            "▣",
            "Clinical Records",
            "Keep screening results organized with patient "
            "details, probabilities and timestamps."
        )
    ]

    for c, (icon, title, desc) in zip(cols, features):
        with c:
            st.markdown(
                f'<div class="rs-card rs-feature">'
                f'<div class="rs-feature-icon">{icon}</div>'
                f'<h3>{title}</h3>'
                f'<p>{desc}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # PORTALS
    # ==========================================================

    st.markdown(
        '<div class="rs-section">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-section-head">'
        '<div class="rs-section-label">Secure access</div>'
        '<h2>Choose your portal</h2>'
        '<p>Two focused experiences sharing one consistent visual system.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(
            '<div class="rs-card rs-portal">'
            '<div>'
            '<span class="rs-tag">CLINICIAN WORKSPACE</span>'
            '<h3>Doctor Portal</h3>'
            '<p>'
            'Run new fundus screenings, review previous patient records '
            'and generate professional reports.'
            '</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        portal_button(
            "doctor",
            "Open Doctor Portal",
            "portal_doctor"
        )

    with c2:
        st.markdown(
            '<div class="rs-card rs-portal">'
            '<div>'
            '<span class="rs-tag">PERSONAL WORKSPACE</span>'
            '<h3>Patient Portal</h3>'
            '<p>'
            'Access screening history, prediction results and '
            'report-ready information in one place.'
            '</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        portal_button(
            "student",
            "Open Patient Portal",
            "portal_patient"
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # DEVELOPER STACK
    # ==========================================================

    st.markdown(
        '<div class="rs-section">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-section-head">'
        '<div class="rs-section-label">Developer stack</div>'
        '<h2>Built as a complete AI product</h2>'
        '</div>',
        unsafe_allow_html=True
    )

    # Keeping your original stack exactly as provided
    stack = [
        ("Frontend", "Streamlit"),
        ("Backend", "Flask REST API"),
        ("Database", "Supabase / PostgreSQL"),
        ("Model", "Fine-tuned ResNet50"),
        ("Deep Learning", "TensorFlow"),
        ("Image Processing", "Pillow + NumPy")
    ]

    cols = st.columns(3)

    for i, (a, b) in enumerate(stack):
        with cols[i % 3]:
            st.markdown(
                f'<div class="rs-tech">'
                f'<strong>{a}</strong>'
                f'<span>{b}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # SIX RETINAL CLASSES
    # ==========================================================

    st.markdown(
        '<div class="rs-section">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-section-head">'
        '<div class="rs-section-label">Model output</div>'
        '<h2>Six retinal classes</h2>'
        '<p>'
        'The model follows the six-class label set documented '
        'in the project paper.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    for i, (code, name, desc) in enumerate(CLASSES):
        with cols[i % 3]:
            st.markdown(
                f'<div class="rs-class">'
                f'<div class="rs-class-code">{code}</div>'
                f'<div class="rs-class-name">{name}</div>'
                f'<div class="rs-class-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # RESEARCH / MODEL INFORMATION
    # ==========================================================

    st.markdown(
        '<div class="rs-band">'
        '<div class="rs-section-label" style="color:#DAD8FF;">'
        'Research-backed prototype'
        '</div>'
        '<h2>From fundus image to an actionable screening result.</h2>'
        '<p style="max-width:760px;">'
        'The project uses an ImageNet-pretrained ResNet50, freezes '
        'early feature stages, fine-tunes the final residual block '
        'and classifier head, then produces a six-class softmax prediction.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # DISCLAIMER
    # ==========================================================

    st.markdown(
        '<div class="rs-section" style="padding-top:35px;">'
        '<div class="rs-card">'
        '<div class="rs-section-label">Important</div>'
        '<h3>Assistive screening, not autonomous diagnosis</h3>'
        '<p>'
        'RetinaScan AI is an academic prototype intended to support '
        'clinical review. A qualified ophthalmologist should confirm '
        'findings before clinical decisions.'
        '</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ==========================================================
    # FOOTER
    # ==========================================================

    render_footer()
 