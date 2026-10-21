import html
import os
from datetime import datetime

import streamlit as st

from utils.styling import render_header, render_footer, confidence_badge
from utils.api_client import predict_fundus_image, get_history
from components.report import build_report_pdf


# --------------------------------------------------------------------------
# Config / constants
# --------------------------------------------------------------------------
# Keep the model accuracy in config so it can't drift from the deployed model.
MODEL_TEST_ACCURACY = os.getenv("MODEL_TEST_ACCURACY", "92.19%")

CLASS_INFO = {
    "AMD": (
        "Age-related Macular Degeneration",
        "Macular changes that can affect central vision.",
    ),
    "DR": (
        "Diabetic Retinopathy",
        "Diabetes-related damage involving retinal blood vessels.",
    ),
    "DN": (
        "Diabetic Neuropathy",
        "Subtle diabetes-related retinal changes requiring careful review.",
    ),
    "MH": (
        "Macular Hole",
        "A structural opening or thinning in the macular region.",
    ),
    "ODC": (
        "Optic Disc Cupping",
        "Enlargement of the optic cup, often associated with glaucoma.",
    ),
    "Normal": (
        "Normal Retina",
        "The model classified the submitted image as Normal.",
    ),
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _flatten_html(body):
    """
    Strip leading whitespace from every line and drop blank lines.

    Markdown treats a blank line followed by 4+ spaces of indentation as a
    code block, which made the HTML show up as raw code. Flattening the HTML
    into one contiguous block with no indentation avoids that completely.
    """
    return "\n".join(line.strip() for line in body.splitlines() if line.strip())


def _markdown(body, *args, **kwargs):
    """Render markdown/HTML without indentation turning HTML into a code block."""
    if isinstance(body, str):
        body = _flatten_html(body)
    return st.markdown(body, *args, **kwargs)


def _e(value):
    """HTML-escape any value before interpolating into unsafe HTML."""
    return html.escape(str(value if value is not None else ""))


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def _safe_filename(name, fallback="record"):
    cleaned = "".join(
        ch if ch.isalnum() or ch in ("-", "_") else "_"
        for ch in str(name or fallback).strip().replace(" ", "_")
    )
    return cleaned or fallback


def _report_filename(name):
    return f"RetinaScan_Report_{_safe_filename(name)}.pdf"


@st.cache_data(show_spinner=False, max_entries=64)
def _cached_pdf(report_data):
    """Build the PDF once per unique report payload instead of on every rerun."""
    return build_report_pdf(report_data)


def _init_state():
    defaults = {
        "history_cache": None,
        "last_prediction": None,
        "multi_patients": [0],
        "multi_results": [],
        "multi_failures": [],
        "screening_version": 0,
        "multi_version": 0,
    }
    for key, value in defaults.items():
        if st.session_state.get(key) is None and key not in st.session_state:
            st.session_state[key] = value


def _load_history(user_id, force=False):
    if force or st.session_state.get("history_cache") is None:
        with st.spinner("Loading secure screening records..."):
            result, status = get_history(user_id)

        if status == 200 and result.get("success"):
            st.session_state.history_cache = result.get("history", [])
        else:
            # Do not cache failures, so the next rerun retries automatically.
            st.error(result.get("message", "Unable to load history."))
            return []

    return st.session_state.history_cache or []


def _stats(history):
    names = {r.get("patient_name") for r in history if r.get("patient_name")}
    latest = history[0].get("predicted_class", "—") if history else "—"
    return len(history), len(names), latest


def _clear_current_screening():
    """Reset the single-patient form by bumping the version used in widget keys."""
    st.session_state.last_prediction = None
    st.session_state.screening_version = (
        st.session_state.get("screening_version", 0) + 1
    )


def _reset_multi_queue():
    st.session_state.multi_patients = [0]
    st.session_state.multi_results = []
    st.session_state.multi_failures = []
    st.session_state.multi_version = st.session_state.get("multi_version", 0) + 1


def _build_item(user, name, age, gender, phone, notes, uploaded, result):
    return {
        "result": result,
        "patient_name": name.strip(),
        "patient_age": int(age),
        "patient_gender": gender,
        "patient_phone": phone.strip(),
        "doctor_name": user.get("full_name", ""),
        "image_bytes": uploaded.getvalue(),
        "image_name": uploaded.name,
        "created_at": datetime.now().isoformat(),
        "notes": notes,
    }


# --------------------------------------------------------------------------
# Main dashboard
# --------------------------------------------------------------------------
def show_dashboard():
    _init_state()

    user = st.session_state.get("user")

    if not user:
        st.session_state.page = "landing"
        st.rerun()
        return

    role = user.get("role", "student")
    label = "Doctor" if role == "doctor" else "Patient"

    render_header(f"{label} Dashboard")

    history = _load_history(user.get("id"))
    scans, patients, latest = _stats(history)

    _markdown(
        f"""
<div class="rs-dashboard-hero">

    <div class="rs-section-label light">
        {_e(label.upper())} WORKSPACE
    </div>

    <h1>{_greeting()}, {_e(user.get("full_name", "User"))}.</h1>

    <p>
        Your intelligent retinal screening workspace for organized,
        AI-assisted fundus analysis and secure screening records.
    </p>

    <div class="rs-hero-chip-row">
        <span>● Secure workspace</span>
        <span>✦ AI-assisted analysis</span>
        <span>◌ Six-class model</span>
    </div>

</div>
""",
        unsafe_allow_html=True,
    )

    cards = [
        ("Total screenings", scans, "Saved screening events"),
        ("Patients covered", patients, "Unique patient records"),
        ("Latest result", latest, "Most recent classification"),
        ("Model test accuracy", MODEL_TEST_ACCURACY, "Held-out test result"),
    ]

    cols = st.columns(4)

    for col, (title, value, sub) in zip(cols, cards):
        with col:
            _markdown(
                f"""
<div class="rs-stat">
    <small>{_e(title)}</small>
    <strong>{_e(value)}</strong>
    <span>{_e(sub)}</span>
</div>
""",
                unsafe_allow_html=True,
            )

    if role == "doctor":
        show_doctor_workspace(user, history)
    else:
        show_patient_workspace(user, history)

    render_footer()


# --------------------------------------------------------------------------
# Doctor workspace
# --------------------------------------------------------------------------
def show_doctor_workspace(user, history):
    tab1, tab2, tab3 = st.tabs(
        ["🔬  New Screening", "📋  Patient Records", "👤  Profile"]
    )

    with tab1:
        mode_col, action_col = st.columns([3, 1])

        with mode_col:
            _markdown(
                """
<div class="rs-section-label">
    SCREENING CONTROL CENTER
</div>

<h2 class="rs-big-heading">
    Choose your screening workflow
</h2>

<p class="rs-subtle">
    Run one patient at a time or build a multi-patient queue.
    Every prediction is sent to the existing backend model.
</p>
""",
                unsafe_allow_html=True,
            )

        with action_col:
            if st.button("＋ New screening", key="new_single_screening"):
                _clear_current_screening()
                _reset_multi_queue()
                st.rerun()

        mode = st.radio(
            "Screening mode",
            ["Single Patient", "Multiple Patients"],
            horizontal=True,
            key="doctor_screening_mode",
        )

        if mode == "Single Patient":
            _single_patient_form(user)
        else:
            _multiple_patient_form(user)

    with tab2:
        render_records(history)

    with tab3:
        render_profile(user)


def _patient_fields(prefix, index=0, version=0):
    suffix = f"_{prefix}_{index}_v{version}"

    a, b, c = st.columns(3)

    with a:
        name = st.text_input(
            "Patient name",
            placeholder="Full patient name",
            key=f"name{suffix}",
        )

    with b:
        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=30,
            step=1,
            key=f"age{suffix}",
        )

    with c:
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            key=f"gender{suffix}",
        )

    phone = st.text_input(
        "Phone number",
        placeholder="+91 XXXXX XXXXX",
        key=f"phone{suffix}",
    )

    notes = st.text_area(
        "Clinical notes",
        placeholder="Relevant observations or screening context...",
        height=80,
        key=f"notes{suffix}",
    )

    return name, int(age), gender, phone, notes


def _single_patient_form(user):
    version = st.session_state.get("screening_version", 0)

    # st.container(border=True) actually wraps the widgets; split
    # <div> ... </div> markdown calls do not.
    with st.container(border=True):
        _markdown(
            """
<div class="rs-card-title-row">

    <div>
        <span class="rs-tag blue">
            SINGLE PATIENT
        </span>

        <h3>Patient information</h3>

        <p>
            Complete one patient form, upload one fundus photograph,
            run the real prediction API and generate the report.
        </p>
    </div>

    <div class="rs-step">
        CASE 01
    </div>

</div>
""",
            unsafe_allow_html=True,
        )

        name, age, gender, phone, notes = _patient_fields(
            "single", 0, version
        )

        uploaded = st.file_uploader(
            "Fundus image",
            type=["jpg", "jpeg", "png"],
            help="Use a clear retinal fundus photograph.",
            key=f"screen_image_{version}",
        )

        _render_upload_preview(uploaded)

        run = st.button(
            "Analyze fundus image  →",
            disabled=not uploaded,
            key="single_predict_btn",
        )

        if run and uploaded:
            if not name.strip():
                st.warning("Please enter the patient name before prediction.")
            else:
                _perform_prediction(
                    user, name, age, gender, phone, notes, uploaded
                )

        render_prediction_card()


def _multiple_patient_form(user):
    if "multi_patients" not in st.session_state:
        st.session_state.multi_patients = [0]

    version = st.session_state.get("multi_version", 0)

    with st.container(border=True):
        _markdown(
            """
<div class="rs-card-title-row">

    <div>
        <span class="rs-tag blue">
            MULTI-PATIENT QUEUE
        </span>

        <h3>Batch screening workspace</h3>

        <p>
            Add as many independent patient cases as required.
            Each fundus image is sent individually to the same
            working prediction endpoint.
        </p>
    </div>

    <div class="rs-step">
        QUEUE MODE
    </div>

</div>
""",
            unsafe_allow_html=True,
        )

        top1, top2, top3 = st.columns([1, 1, 2])

        with top1:
            if st.button("＋ Add patient", key="add_multi_patient"):
                next_id = max(st.session_state.multi_patients, default=-1) + 1
                st.session_state.multi_patients.append(next_id)
                st.rerun()

        with top2:
            if st.button("↻ Clear queue", key="clear_multi_patient"):
                _reset_multi_queue()
                st.rerun()

        with top3:
            _markdown(
                f"""
<div class="rs-queue-summary">
    <strong>{len(st.session_state.multi_patients)}</strong>
    <span>patient form(s) ready for screening</span>
</div>
""",
                unsafe_allow_html=True,
            )

        queued = []

        for pos, patient_id in enumerate(
            st.session_state.multi_patients, start=1
        ):
            _markdown(
                f"""
<div class="rs-patient-form-head">
    <strong>Patient {pos}</strong>
    <span>Case {pos:02d}</span>
</div>
""",
                unsafe_allow_html=True,
            )

            name, age, gender, phone, notes = _patient_fields(
                "multi", patient_id, version
            )

            uploaded = st.file_uploader(
                "Fundus image",
                type=["jpg", "jpeg", "png"],
                key=f"multi_image_{patient_id}_v{version}",
            )

            _render_upload_preview(uploaded, compact=True)

            queued.append((name, age, gender, phone, notes, uploaded))

        if st.button("Run screening for all patients  →", key="run_multi_predictions"):
            valid = True

            for pos, (name, _a, _g, _p, _n, uploaded) in enumerate(
                queued, start=1
            ):
                if not name.strip() or not uploaded:
                    st.warning(
                        f"Patient {pos}: enter the patient name "
                        "and upload a fundus image."
                    )
                    valid = False

            if valid:
                progress = st.progress(
                    0, text="Starting patient screening queue..."
                )

                st.session_state.multi_results = []
                st.session_state.multi_failures = []

                total = len(queued)

                for idx, (name, age, gender, phone, notes, uploaded) in enumerate(
                    queued, start=1
                ):
                    result, status = _perform_prediction(
                        user,
                        name,
                        age,
                        gender,
                        phone,
                        notes,
                        uploaded,
                        save_last=False,
                    )

                    if status == 200 and result.get("success"):
                        st.session_state.multi_results.append(
                            _build_item(
                                user, name, age, gender, phone, notes,
                                uploaded, result,
                            )
                        )
                    else:
                        st.session_state.multi_failures.append(
                            f"Patient {idx} ({name.strip()}): "
                            f"{result.get('message', 'Prediction failed.')}"
                        )

                    progress.progress(
                        idx / total,
                        text=f"Completed patient {idx} of {total}",
                    )

                st.session_state.history_cache = None

        done = len(st.session_state.get("multi_results") or [])
        failures = st.session_state.get("multi_failures") or []

        if done:
            st.success(f"Completed {done} patient screening(s).")

        if failures:
            st.error(
                f"{len(failures)} screening(s) failed:\n\n"
                + "\n".join(f"- {f}" for f in failures)
            )

        results = st.session_state.get("multi_results") or []

        if results:
            _markdown(
                """
<div class="rs-section-label" style="margin-top:24px;">
    BATCH RESULTS
</div>

<h3>
    Download reports
</h3>
""",
                unsafe_allow_html=True,
            )

            for idx, item in enumerate(results, start=1):
                result = item["result"]
                pred = result.get("prediction", "N/A")
                conf = _to_float(result.get("confidence", 0))

                c1, c2, c3 = st.columns([3, 2, 2])

                with c1:
                    _markdown(
                        f"""
<div class="rs-mini-result">
    <strong>{idx:02d} · {_e(item["patient_name"])}</strong>
    <span>{_e(pred)} · {conf:.1f}%</span>
</div>
""",
                        unsafe_allow_html=True,
                    )

                with c2:
                    st.download_button(
                        "↓ PDF Report",
                        data=_cached_pdf(item),
                        file_name=_report_filename(item["patient_name"]),
                        mime="application/pdf",
                        key=f"multi_pdf_{idx}",
                    )

                with c3:
                    st.button(
                        "✓ Completed",
                        disabled=True,
                        key=f"multi_done_{idx}",
                    )


def _render_upload_preview(uploaded, compact=False):
    if not uploaded:
        _markdown(
            """
<div class="rs-upload-hint">
    ◉ Upload a clear color fundus photograph
    • JPG / JPEG / PNG
</div>
""",
            unsafe_allow_html=True,
        )
        return

    x, y = st.columns([1, 1])

    with x:
        if compact:
            st.image(uploaded, caption="Fundus image preview", width=320)
        else:
            st.image(uploaded, caption="Fundus image preview")

    with y:
        _markdown(
            f"""
<div class="rs-ready-card">

    <span>✓ IMAGE READY</span>

    <strong>{_e(uploaded.name)}</strong>

    <small>
        {uploaded.size / 1024:.1f} KB ·
        {_e(uploaded.type or "image")}
    </small>

    <p>Ready for ResNet50 analysis.</p>

</div>
""",
            unsafe_allow_html=True,
        )


def _perform_prediction(
    user,
    name,
    age,
    gender,
    phone,
    notes,
    uploaded,
    save_last=True,
):
    with st.spinner(f"Analyzing {name.strip()}'s fundus image with ResNet50..."):
        # NOTE: `phone` is not forwarded here because predict_fundus_image's
        # signature doesn't accept it. If the backend should store it, add a
        # `phone` parameter to utils.api_client.predict_fundus_image and pass it.
        result, status = predict_fundus_image(
            uploaded,
            user.get("id"),
            name.strip(),
            int(age),
            gender,
            notes.strip(),
        )

    if status == 200 and result.get("success"):
        if save_last:
            st.session_state.last_prediction = _build_item(
                user, name, age, gender, phone, notes, uploaded, result
            )
            st.session_state.history_cache = None

            st.success("Screening completed and the patient record was saved.")

        return result, status

    if save_last:
        st.error(result.get("message", "Prediction failed."))

    return result, status


def render_prediction_card():
    p = st.session_state.get("last_prediction")

    if not p:
        return

    result = p["result"]

    pred = result.get("prediction", "N/A")
    conf = _to_float(result.get("confidence", 0))

    title, desc = CLASS_INFO.get(
        pred,
        (pred, "Model prediction returned by the backend."),
    )

    _markdown(
        f"""
<div class="rs-result rs-result-premium">

    <div class="rs-result-title">LATEST AI SCREENING</div>

    <div class="rs-result-value">{_e(pred)}</div>

    <div style="margin-top:9px;">
        {confidence_badge(pred, conf)}
    </div>

    <h4>{_e(title)}</h4>

    <p>{_e(desc)}</p>

</div>
""",
        unsafe_allow_html=True,
    )

    probs = result.get("probabilities") or {}

    if probs:
        _markdown("**Class probability profile**")
        st.bar_chart(probs)

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "↓ Download professional PDF report",
            data=_cached_pdf(p),
            file_name=_report_filename(p["patient_name"]),
            mime="application/pdf",
            key="download_latest_report",
        )

    with c2:
        if st.button("＋ Start another patient", key="next_patient_after_prediction"):
            _clear_current_screening()
            st.rerun()

    _markdown(
        """
<div class="rs-disclaimer">
    AI-assisted screening result. This report does not replace
    examination, clinical history or confirmation by a qualified
    ophthalmologist.
</div>
""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------
def render_records(history):
    with st.container(border=True):
        _markdown(
            """
<div class="rs-section-label">
    HISTORY CENTER
</div>

<h2 class="rs-big-heading">
    Patient screening records
</h2>

<p class="rs-subtle">
    Search previous cases, review prediction probabilities
    and download report-ready records.
</p>
""",
            unsafe_allow_html=True,
        )

        a, b = st.columns([4, 1])

        with a:
            query = st.text_input(
                "Search records",
                placeholder="Search patient name or prediction...",
                key="record_search",
            )

        with b:
            if st.button("↻ Refresh records", key="refresh_history"):
                st.session_state.history_cache = None
                st.rerun()

        if not history:
            _markdown(
                """
<div class="rs-empty">

    <div class="rs-empty-icon">⌁</div>

    <h3>No screening records yet</h3>

    <p>Completed screenings will appear here automatically.</p>

</div>
""",
                unsafe_allow_html=True,
            )
            return

        q = query.strip().lower()

        filtered = [
            r
            for r in history
            if not q
            or q in str(r.get("patient_name", "")).lower()
            or q in str(r.get("predicted_class", "")).lower()
        ]

        if not filtered:
            st.info("No records match your search.")

        for idx, r in enumerate(filtered):
            dt = str(r.get("created_at", "")).replace("T", " ")[:19]
            pred = r.get("predicted_class", "N/A")
            conf = _to_float(r.get("confidence", 0))

            with st.expander(
                f"{r.get('patient_name', 'Unknown')}   ·   "
                f"{pred}   ·   {conf:.1f}%   ·   {dt}"
            ):
                m1, m2, m3, m4 = st.columns(4)

                m1.metric("Patient", r.get("patient_name", "—"))
                m2.metric("Age", r.get("patient_age", "—"))
                m3.metric("Gender", r.get("patient_gender", "—"))
                m4.metric("Prediction", pred)

                probs = r.get("class_probabilities") or {}

                if probs:
                    st.bar_chart(probs)

                if r.get("notes"):
                    st.write(f"**Clinical notes:** {r['notes']}")

                report_data = {
                    "result": {
                        "prediction": pred,
                        "confidence": conf,
                        "probabilities": probs,
                        "record": r,
                    },
                    "patient_name": r.get("patient_name", "Unknown"),
                    "patient_age": r.get("patient_age", "—"),
                    "patient_gender": r.get("patient_gender", "—"),
                    "patient_phone": r.get("patient_phone", ""),
                    "doctor_name": r.get("doctor_name", ""),
                    "created_at": r.get("created_at", ""),
                    "notes": r.get("notes", ""),
                }

                st.download_button(
                    "↓ Download report",
                    data=_cached_pdf(report_data),
                    file_name=_report_filename(r.get("patient_name", "record")),
                    mime="application/pdf",
                    key=f"history_pdf_{idx}",
                )


# --------------------------------------------------------------------------
# Patient workspace
# --------------------------------------------------------------------------
def show_patient_workspace(user, history):
    tab1, tab2, tab3 = st.tabs(
        ["🩺  My Screening", "📋  Past Screenings", "👤  My Profile"]
    )

    with tab1:
        latest = history[0] if history else None

        with st.container(border=True):
            _markdown(
                """
<div class="rs-section-label">
    PERSONAL SCREENING HUB
</div>

<h2 class="rs-big-heading">
    Your retinal screening
</h2>

<p class="rs-subtle">
    Your doctor's completed screening records are shown here.
    Refresh to retrieve a newly completed screening without
    returning to the Home page.
</p>
""",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns([3, 1])

            with c1:
                if latest:
                    pred = latest.get("predicted_class", "N/A")
                    conf = _to_float(latest.get("confidence", 0))

                    title, desc = CLASS_INFO.get(
                        pred, (pred, "Screening result")
                    )

                    _markdown(
                        f"""
<div class="rs-result rs-result-premium">

    <div class="rs-result-title">MOST RECENT SCREENING</div>

    <div class="rs-result-value">{_e(pred)}</div>

    <div style="margin:8px 0;">
        {confidence_badge(pred, conf)}
    </div>

    <h4>{_e(title)}</h4>

    <p>{_e(desc)}</p>

</div>
""",
                        unsafe_allow_html=True,
                    )
                else:
                    _markdown(
                        """
<div class="rs-empty">

    <div class="rs-empty-icon">◎</div>

    <h3>No completed screening yet</h3>

    <p>
        Your screening result will appear here after
        a doctor completes a fundus analysis.
    </p>

</div>
""",
                        unsafe_allow_html=True,
                    )

            with c2:
                if st.button("↻ Refresh screening", key="patient_refresh"):
                    st.session_state.history_cache = None
                    st.session_state.last_prediction = None
                    st.rerun()

                _markdown(
                    """
<div class="rs-side-note">

    <strong>Stay informed</strong>

    <p>
        Refresh loads the latest saved screening records
        while keeping you on the Patient Dashboard.
    </p>

</div>
""",
                    unsafe_allow_html=True,
                )

            if latest and latest.get("class_probabilities"):
                _markdown("**AI class probability profile**")
                st.bar_chart(latest.get("class_probabilities"))

    with tab2:
        render_records(history)

    with tab3:
        render_profile(user)


# --------------------------------------------------------------------------
# Profile
# --------------------------------------------------------------------------
def _profile_field(container, label, value):
    container.markdown(
        _flatten_html(
            f"""
<div class="rs-profile-field">
    <small>{_e(label)}</small>
    <strong>{_e(value)}</strong>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_profile(user):
    with st.container(border=True):
        _markdown(
            """
<div class="rs-section-label">
    ACCOUNT CENTER
</div>

<h2 class="rs-big-heading">
    Profile &amp; security
</h2>
""",
            unsafe_allow_html=True,
        )

        a, b = st.columns(2)
        _profile_field(a, "FULL NAME", user.get("full_name", "—"))
        _profile_field(b, "EMAIL ADDRESS", user.get("email", "—"))

        a, b = st.columns(2)
        _profile_field(
            a,
            "ROLE",
            "Doctor" if user.get("role") == "doctor" else "Patient",
        )
        _profile_field(
            b,
            "ACCOUNT CREATED",
            str(user.get("created_at", "—")).replace("T", " ")[:19],
        )

        if user.get("specialization"):
            _profile_field(st, "SPECIALIZATION", user["specialization"])

        if user.get("institution"):
            _profile_field(st, "INSTITUTION", user["institution"])

        if user.get("address"):
            _profile_field(st, "ADDRESS", user["address"])

    _markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    if st.button("Log out securely", key="logout"):
        # Remove all session data (including widget state) instead of
        # setting keys to None, then send the user back to the landing page.
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.session_state.page = "landing"
        st.rerun()