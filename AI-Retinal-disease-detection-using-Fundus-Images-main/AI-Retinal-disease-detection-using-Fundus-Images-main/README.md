# 👁️ RetinaScan AI

AI-powered multi-class retinal disease screening system.
**Frontend:** Streamlit &nbsp;|&nbsp; **Backend:** Flask &nbsp;|&nbsp; **Database:** Supabase (PostgreSQL) &nbsp;|&nbsp; **Model:** Fine-tuned ResNet50

Classifies fundus images into 6 classes: **AMD, DR, DN, MH, ODC, Normal**

Developed by **Madii**

---

## 📁 Project Structure

```
retinal_disease_app/
├── README.md
├── database/
│   └── supabase_schema.sql        <- Run this in Supabase SQL Editor
├── backend/
│   ├── app.py                     <- Flask API (routes)
│   ├── db.py                      <- Supabase client
│   ├── model_utils.py             <- Loads model + runs predictions
│   ├── requirements.txt
│   ├── .env.example                <- Copy to .env and fill in
│   └── saved_model/
│       └── (put your model.h5 here)
└── frontend/
    ├── streamlit_app.py           <- Main entry point
    ├── requirements.txt
    ├── .env.example                <- Copy to .env
    ├── utils/
    │   ├── api_client.py           <- Calls the Flask backend
    │   └── styling.py               <- Header/footer/CSS theme
    ├── pages_logic/
    │   ├── landing.py               <- Doctor vs Student portal choice
    │   ├── auth.py                  <- Login + Registration
    │   └── dashboard.py             <- Upload, predict, history
    └── assets/
        └── logo.svg
```

---

## ⚡ Quick Setup (do this tonight)

### 1. Create your Supabase project
1. Go to https://supabase.com → New Project (free tier is fine).
2. Once created, go to **SQL Editor** → New Query.
3. Paste the entire contents of `database/supabase_schema.sql` and click **Run**.
   This creates the `users` and `predictions` tables.
4. Go to **Project Settings → API**. Copy:
   - **Project URL** → this is `SUPABASE_URL`
   - **service_role key** (NOT the anon key — backend needs full access) → this is `SUPABASE_KEY`

### 2. Add your trained model
Copy your saved model file into:
```
backend/saved_model/model.h5
```
If your file has a different name, update `MODEL_FILENAME` in `backend/.env` to match.

> If your saved model is a **PyTorch** file (`.pt`/`.pth`) instead of Keras/TensorFlow
> (`.h5`), the loader in `backend/model_utils.py` needs a small swap — message me and
> I'll adjust it. Everything else in the app stays the same either way.

> **Note:** Until a model file is present, the backend automatically runs in **DEMO
> mode** (plausible random predictions) so the entire app — login, upload, history —
> still works end-to-end for rehearsal.

### 3. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# now edit .env and paste your SUPABASE_URL and SUPABASE_KEY

python app.py
```
Backend runs at `http://localhost:5000`. Visit it in a browser — you should see
`{"status": "ok", ...}`.

### 4. Frontend setup (in a NEW terminal, keep backend running)
```bash
cd frontend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# default BACKEND_URL=http://localhost:5000 is fine if running locally

streamlit run streamlit_app.py
```
This opens the app in your browser automatically (usually `http://localhost:8501`).

---

## 🖥️ App Flow (what your demo will show)

1. **Landing page** — choose **Doctor Portal** or **Student Portal**.
2. **Login page** — if no account, click **Create an account** → fills a
   registration form → redirects back to login.
3. **Dashboard** (same layout for both portals):
   - **New Prediction tab** — enter patient name/age/gender → upload a fundus
     image → click **Run Prediction** → see predicted class, confidence badge,
     and a probability bar chart across all 6 classes.
   - **Patient History tab** — see every past scan for the logged-in account,
     pulled live from Supabase.
4. **Logout** button returns to the landing page.

Header, footer, and color theme are consistent across every page (teal/blue
medical theme, 👁️ logo, "RetinaScan AI" branding, "Developed by Madii" in the footer).

---

## 🎤 Suggested Demo Script (for tomorrow)

1. "This is RetinaScan AI — an assistive screening tool built on a fine-tuned
   ResNet50 model that classifies retinal fundus images into 6 categories."
2. Show the **landing page** → explain Doctor vs Student portals.
3. Register a new doctor account live → show it lands back on login → log in.
4. On the dashboard, upload a sample fundus image → run prediction → point out
   the confidence badge and probability chart.
5. Switch to **Patient History tab** → show the scan was saved and is retrievable.
6. Mention the tech stack: Streamlit frontend, Flask REST API backend, Supabase
   Postgres database, ResNet50 model reaching **92.19% accuracy** on the held-out
   test set (cite your paper's Table IV here).

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach backend server" in Streamlit | Make sure `python app.py` is running in another terminal on port 5000 |
| Supabase insert/login errors | Double check you used the **service_role** key, not anon key |
| Model won't load | Confirm the filename in `backend/.env` (`MODEL_FILENAME`) exactly matches the file in `backend/saved_model/` |
| Predictions look random | You're in DEMO mode — your real model file isn't in `saved_model/` yet |
| Port 5000 already in use | Change `PORT` in `backend/.env`, and update `BACKEND_URL` in `frontend/.env` to match |

---

## 🔒 Notes on Security (mention if asked in viva)

- Passwords are hashed with `bcrypt` before being stored — never stored in plain text.
- Supabase Row Level Security is enabled on both tables; all access is routed
  through the Flask backend using the service role key, so the database is
  never exposed directly to the frontend.
- This is a project/demo build — for real clinical deployment you'd add
  session tokens (JWT), HTTPS, file-storage (Supabase Storage) for images
  instead of just filenames, and rate limiting.

---

## 📚 Model Reference

Based on: *"AI-Based Multi-Class Retinal Disease Detection Using Fine-Tuned
ResNet50 and Transfer Learning"* — fine-tuned ResNet50 (ImageNet-pretrained),
92.19% test accuracy, 92.74% weighted precision, 92.20% weighted recall,
92.20% weighted F1-score across AMD, DR, DN, MH, ODC, and Normal classes.
