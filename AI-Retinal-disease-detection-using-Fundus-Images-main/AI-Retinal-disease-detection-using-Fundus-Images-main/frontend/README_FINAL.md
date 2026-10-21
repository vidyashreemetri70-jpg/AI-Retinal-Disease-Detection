# RetinaScan AI — Complete Frontend

## Included workflows

### Doctor
1. Login / registration
2. Doctor Dashboard
3. Single Patient mode
4. Fundus upload
5. Real `/api/predict` call through `utils/api_client.py`
6. Saved screening record
7. Professional PDF report
8. Multiple Patients mode
9. Add any number of patient forms
10. Run screening for all patients
11. Individual result + PDF for every patient
12. Patient Records / search / refresh / report download
13. Profile / secure logout

### Patient
1. Login / registration
2. Patient Dashboard
3. My Screening
4. Refresh Screening without returning Home
5. Past Screenings
6. Prediction probability profile
7. PDF report download
8. Profile / secure logout

## Backend safety

This frontend keeps the existing backend endpoints:

- POST `/api/register`
- POST `/api/login`
- POST `/api/predict`
- GET `/api/history/<user_id>`

Keep the existing Flask backend, Supabase database and model unchanged.

## Run

Backend:
    python app.py

Frontend:
    python -m streamlit run streamlit_app.py
