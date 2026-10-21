import re
import streamlit as st
from utils.styling import render_header, render_footer
from utils.api_client import login_user, register_user


def _role_info():
    role = st.session_state.get("portal") or "doctor"

    return (
        role,
        "Doctor" if role == "doctor" else "Patient",
        "🩺" if role == "doctor" else "◉"
    )


def show_login():

    role, label, icon = _role_info()

    render_header(f"{label} portal")

    st.markdown(
        '<div class="rs-auth-wrap">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="rs-section-label" style="text-align:center;">
            {label.upper()} PORTAL
        </div>

        <h1 class="rs-auth-title">
            {icon} Welcome back
        </h1>

        <p class="rs-auth-sub">
            Sign in securely to continue to your
            {label.lower()} workspace.
        </p>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-card">',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    email = st.text_input(
        "Email address",
        placeholder="name@example.com",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    a, b = st.columns(2)

    # FIXED: removed width="stretch"
    with a:
        login = st.button(
            "Sign in  →",
            key="login_btn"
        )

    # FIXED: removed width="stretch"
    with b:
        back = st.button(
            "← Landing",
            key="login_back"
        )

    # --------------------------------------------------------
    # LOGIN ACTION
    # --------------------------------------------------------

    if login:

        if not email.strip() or not password:
            st.warning(
                "Enter your email and password."
            )

        elif not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email.strip()
        ):
            st.warning(
                "Enter a valid email address."
            )

        else:

            with st.spinner(
                "Authenticating securely..."
            ):

                result, status = login_user(
                    email.strip(),
                    password,
                    role=role
                )

            if status == 200 and result.get("success"):

                st.session_state.user = result.get("user")

                st.session_state.history_cache = None

                st.session_state.page = "dashboard"

                st.rerun()

            else:

                st.error(
                    result.get(
                        "message",
                        "Login failed."
                    )
                )

    # --------------------------------------------------------
    # BACK TO LANDING
    # --------------------------------------------------------

    if back:

        st.session_state.page = "landing"

        st.rerun()

    # --------------------------------------------------------
    # REGISTER LINK
    # --------------------------------------------------------

    st.markdown(
        '''
        <div style="
            border-top:1px solid #ECECF4;
            margin:24px 0 17px;
        ">
        </div>

        <div style="
            text-align:center;
            font-size:12px;
            color:#7A8090;
        ">
            New to RetinaScan AI?
        </div>
        ''',
        unsafe_allow_html=True
    )

    # FIXED: removed width="stretch"
    if st.button(
        "Create a new account",
        key="to_register"
    ):

        st.session_state.page = "register"

        st.rerun()

    st.markdown(
        '</div></div>',
        unsafe_allow_html=True
    )

    render_footer()


def show_register():

    role, label, icon = _role_info()

    render_header(
        f"{label} registration"
    )

    st.markdown(
        '<div class="rs-auth-wrap">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="rs-section-label" style="text-align:center;">
            {label.upper()} PORTAL
        </div>

        <h1 class="rs-auth-title">
            Create your account
        </h1>

        <p class="rs-auth-sub">
            Register once, then return to the secure login page.
        </p>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="rs-card">',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # REGISTRATION FORM
    # --------------------------------------------------------

    full_name = st.text_input(
        "Full name",
        placeholder="Your full name",
        key="reg_name"
    )

    email = st.text_input(
        "Email address",
        placeholder="name@example.com",
        key="reg_email"
    )

    phone = st.text_input(
        "Phone number",
        placeholder="+91 XXXXX XXXXX",
        key="reg_phone"
    )

    p1 = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password",
        key="reg_password"
    )

    p2 = st.text_input(
        "Confirm password",
        type="password",
        placeholder="Repeat your password",
        key="reg_confirm"
    )

    # --------------------------------------------------------
    # ROLE-SPECIFIC FIELD
    # --------------------------------------------------------

    if role == "doctor":

        extra = st.text_input(
            "Specialization",
            placeholder="e.g. Ophthalmology",
            key="reg_specialization"
        )

    else:

        extra = st.text_input(
            "Institution / College",
            placeholder="Your institution",
            key="reg_institution"
        )

    # --------------------------------------------------------
    # REGISTRATION BUTTONS
    # --------------------------------------------------------

    a, b = st.columns(2)

    # FIXED: removed width="stretch"
    with a:

        create = st.button(
            "Create account  →",
            key="register_btn"
        )

    # FIXED: removed width="stretch"
    with b:

        back = st.button(
            "← Back to login",
            key="register_back"
        )

    # --------------------------------------------------------
    # CREATE ACCOUNT
    # --------------------------------------------------------

    if create:

        if (
            not full_name.strip()
            or not email.strip()
            or not p1
        ):

            st.warning(
                "Please complete all required fields."
            )

        elif not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email.strip()
        ):

            st.warning(
                "Enter a valid email address."
            )

        elif len(p1) < 6:

            st.warning(
                "Use a password with at least 6 characters."
            )

        elif p1 != p2:

            st.error(
                "Passwords do not match."
            )

        else:

            with st.spinner(
                "Creating your account..."
            ):

                result, status = register_user(
                    full_name.strip(),
                    email.strip(),
                    p1,
                    role,
                    specialization=(
                        extra
                        if role == "doctor"
                        else None
                    ),
                    institution=(
                        extra
                        if role != "doctor"
                        else None
                    )
                )

            if (
                status == 201
                and result.get("success")
            ):

                st.session_state.login_email = (
                    email.strip()
                )

                st.session_state.login_password = ""

                st.session_state.page = "login"

                st.session_state.registration_success = True

                st.rerun()

            elif status == 409:

                st.error(
                    "This email is already registered. "
                    "Please log in or use a different email."
                )

            else:

                st.error(
                    result.get(
                        "message",
                        "Registration failed."
                    )
                )

    # --------------------------------------------------------
    # BACK TO LOGIN
    # --------------------------------------------------------

    if back:

        st.session_state.page = "login"

        st.rerun()

    # --------------------------------------------------------
    # PHONE NOTE
    # --------------------------------------------------------

    st.markdown(
        '''
        <p style="
            font-size:10px;
            color:#7C8190;
            margin-top:18px;
        ">
            Phone number is collected for the registration
            interface. Your current backend/database schema
            does not persist a phone field, so no backend
            contract was changed.
        </p>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '</div></div>',
        unsafe_allow_html=True
    )

    render_footer()