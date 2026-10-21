"""
RetinaScan AI - Flask Backend
Handles: registration, login, fundus image prediction, patient history.
"""

import os
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from db import get_supabase
from model_utils import predict_image, CLASS_NAMES, MODEL_LOADED

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow Streamlit frontend to call this API

supabase = get_supabase()


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "RetinaScan AI Backend",
        "model_loaded": MODEL_LOADED
    })


# ---------------------------------------------------------
# AUTH: REGISTER
# ---------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)

    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role")  # 'doctor' or 'student'
    specialization = data.get("specialization")
    institution = data.get("institution")

    if not full_name or not email or not password or role not in ("doctor", "student"):
        return jsonify({"success": False, "message": "Missing or invalid fields."}), 400

    # Check if email already exists
    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data:
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    record = {
        "full_name": full_name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "specialization": specialization,
        "institution": institution,
    }

    result = supabase.table("users").insert(record).execute()

    if not result.data:
        return jsonify({"success": False, "message": "Registration failed. Please try again."}), 500

    user = result.data[0]
    user.pop("password_hash", None)
    return jsonify({"success": True, "message": "Account created successfully.", "user": user}), 201


# ---------------------------------------------------------
# AUTH: LOGIN
# ---------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role")  # optional filter: 'doctor' or 'student'

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    result = supabase.table("users").select("*").eq("email", email).execute()

    if not result.data:
        return jsonify({"success": False, "message": "No account found with this email."}), 404

    user = result.data[0]

    if role and user["role"] != role:
        return jsonify({"success": False, "message": f"This account is not registered as a {role}."}), 403

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"success": False, "message": "Incorrect password."}), 401

    user.pop("password_hash", None)
    return jsonify({"success": True, "message": "Login successful.", "user": user}), 200


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"success": False, "message": "No image file uploaded."}), 400

    image_file = request.files["image"]
    user_id = request.form.get("user_id")
    patient_name = request.form.get("patient_name", "Unknown")
    patient_age = request.form.get("patient_age")
    patient_gender = request.form.get("patient_gender")
    notes = request.form.get("notes", "")

    if not user_id:
        return jsonify({"success": False, "message": "Missing user_id."}), 400

    try:
        image_bytes = image_file.read()
        predicted_class, confidence, probabilities = predict_image(image_bytes)
    except Exception as e:
        return jsonify({"success": False, "message": f"Prediction failed: {str(e)}"}), 500

    record = {
        "user_id": user_id,
        "patient_name": patient_name,
        "patient_age": int(patient_age) if patient_age else None,
        "patient_gender": patient_gender,
        "image_name": image_file.filename,
        "predicted_class": predicted_class,
        "confidence": confidence,
        "class_probabilities": probabilities,
        "notes": notes,
    }

    result = supabase.table("predictions").insert(record).execute()
    saved_record = result.data[0] if result.data else record

    return jsonify({
        "success": True,
        "prediction": predicted_class,
        "confidence": confidence,
        "probabilities": probabilities,
        "class_names": CLASS_NAMES,
        "record": saved_record
    }), 200


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------
@app.route("/api/history/<user_id>", methods=["GET"])
def history(user_id):
    result = (
        supabase.table("predictions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify({"success": True, "history": result.data}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
