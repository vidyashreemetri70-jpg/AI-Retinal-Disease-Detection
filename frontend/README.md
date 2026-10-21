# RetinaScan AI — Final Frontend

A redesigned Streamlit frontend for the existing RetinaScan AI backend.

## Backend contract preserved

This frontend intentionally keeps the existing API routes unchanged:

- `POST /api/register`
- `POST /api/login`
- `POST /api/predict`
- `GET /api/history/<user_id>`

The backend/database do not need to be replaced for this frontend.

## Run

```powershell
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run streamlit_app.py
```

Make sure the existing Flask backend is already running on `http://localhost:5000`.

## Important compatibility note

The existing backend uses the role value `student`. The frontend presents this role as **Patient** to match the requested UI, but still sends `student` to the backend so the existing authentication/database contract remains intact.

The current database schema has no phone-number column. The registration screen therefore displays a phone field for the requested UI, but does not pretend that the existing backend persists it. The screening form captures a phone number for the generated report.

## Pages

1. Landing page
2. Doctor / Patient login
3. Doctor / Patient registration
4. Doctor dashboard
5. Patient dashboard
6. Screening history
7. Professional PDF screening report

## Model classes

AMD, DR, DN, MH, ODC, Normal.
