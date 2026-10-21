import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Flask backend
# Explicitly use 127.0.0.1 because we confirmed Flask is running there.
BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "http://127.0.0.1:5000"
).rstrip("/")


def _json(resp):
    try:
        return resp.json()
    except Exception:
        return {
            "success": False,
            "message": f"Backend returned HTTP {resp.status_code}.",
        }


def register_user(
    full_name,
    email,
    password,
    role,
    specialization=None,
    institution=None,
    phone=None,
    address=None,
):
    payload = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
        "specialization": specialization,
        "institution": institution,
        "phone": phone,
        "address": address,
    }

    try:
        r = requests.post(
            f"{BACKEND_URL}/api/register",
            json=payload,
            timeout=15,
        )

        return _json(r), r.status_code

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": (
                "Cannot reach backend server. "
                "Make sure Flask is running on port 5000."
            ),
        }, 500

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Backend request failed: {e}",
        }, 500


def login_user(email, password, role=None):
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/login",
            json={
                "email": email,
                "password": password,
                "role": role,
            },
            timeout=15,
        )

        return _json(r), r.status_code

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": (
                "Cannot reach backend server. "
                "Make sure Flask is running on port 5000."
            ),
        }, 500

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Backend request failed: {e}",
        }, 500


def predict_fundus_image(
    image_file,
    user_id,
    patient_name,
    patient_age,
    patient_gender,
    notes="",
):
    try:
        files = {
            "image": (
                image_file.name,
                image_file.getvalue(),
                image_file.type or "image/jpeg",
            )
        }

        data = {
            "user_id": user_id,
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "notes": notes,
        }

        r = requests.post(
            f"{BACKEND_URL}/api/predict",
            files=files,
            data=data,
            timeout=90,
        )

        return _json(r), r.status_code

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": (
                "Cannot reach backend server. "
                "Make sure Flask is running on port 5000."
            ),
        }, 500

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Prediction request failed: {e}",
        }, 500


def get_history(user_id):
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/history/{user_id}",
            timeout=20,
        )

        return _json(r), r.status_code

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": (
                "Cannot reach backend server. "
                "Make sure Flask is running on port 5000."
            ),
        }, 500

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"History request failed: {e}",
        }, 500