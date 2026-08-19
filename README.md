# Tamil Nadu Election Prediction & Data Analysis System

A comprehensive Full-Stack Python and React application for analyzing historical election data and forecasting constituency outcomes using Machine Learning.

## Tech Stack
- **Frontend**: React.js, Vite, Tailwind CSS, Axios, Recharts
- **Backend**: Django 5.1, Django REST Framework, PostgreSQL
- **Machine Learning**: Scikit-Learn, XGBoost, Pandas, NumPy
- **Authentication**: JWT (Simple JWT)

---

## 1. Local Development Setup

### Backend (Django API)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *(Edit `.env` to match your local PostgreSQL credentials)*
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the local server:
   ```bash
   python manage.py runserver
   ```

### Frontend (React)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 2. Production Architecture

The system utilizes a modern decoupled deployment topology:
- **Vercel** hosts the compiled static React frontend.
- **Render** runs the Django WSGI backend API via `gunicorn` and hosts the managed PostgreSQL instance.
- **Render Persistent Disk** attached to the Django service safely stores `.joblib` machine learning model artifacts between container restarts.

## 3. Deployment Instructions

Since deploying infrastructure requires cloud credentials, follow these manual steps to connect your GitHub repository to Render and Vercel:

### Step 1: Deploy PostgreSQL (Render)
1. Log into your Render dashboard.
2. Click **New +** -> **PostgreSQL**.
3. Name it `tnelectiondb`.
4. Copy the **Internal Database URL** provided once it spins up.

### Step 2: Deploy Django API (Render)
1. Click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Set the Root Directory to `backend/`.
4. Set the Build Command to: `./build.sh`
5. Set the Start Command to: `gunicorn config.wsgi:application`
6. Add an **Advanced -> Persistent Disk**:
   - Name: `ml_models`
   - Mount Path: `/opt/render/project/src/backend/ml/data/processed/models`
7. Define **Environment Variables**:
   - `DJANGO_ENV`: `production`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `DATABASE_URL`: *(Paste the Internal Database URL from Step 1)*
   - `ALLOWED_HOSTS`: *(The `.onrender.com` URL Render gives you)*
   - `CORS_ALLOWED_ORIGINS`: *(The Vercel URL you will create in Step 3)*
   - `CSRF_TRUSTED_ORIGINS`: *(The Vercel URL you will create in Step 3)*

### Step 3: Deploy React Frontend (Vercel)
1. Log into your Vercel dashboard.
2. Click **Add New Project** and select your GitHub repository.
3. Set the Framework Preset to **Vite**.
4. Set the Root Directory to `frontend/`.
5. Under Environment Variables, add:
   - `VITE_API_BASE_URL`: *(Your deployed Render HTTPS URL from Step 2)* `/api`
6. Click **Deploy**.

---

## 4. Retraining Machine Learning Models

ML model retraining is restricted and completely decoupled from public web requests.

To regenerate models after receiving new authentic ECI data:
1. Place the new dataset in `backend/ml/data/raw/`.
2. Connect to your Render Web Service terminal (via the dashboard).
3. Validate data integrity:
   ```bash
   python manage.py verify_election_data
   ```
4. Train the model:
   ```bash
   python manage.py train_model
   ```
The newly generated `.joblib` files will be saved to your Render Persistent disk and immediately utilized by the live API.
