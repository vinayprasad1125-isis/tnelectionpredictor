# System Rollback Plan

This document outlines standard operating procedures for recovering from deployment failures, corrupted machine learning pipelines, and database catastrophes in production.

## 1. Failed Frontend Deployment (Vercel)
If a new React build introduces breaking changes, blank screens, or API routing errors:
1. Log into the Vercel dashboard.
2. Select your Project -> **Deployments**.
3. Locate the last known working deployment in the history list.
4. Click the three dots (...) and select **Promote to Production** (or "Redeploy").
5. The frontend will instantaneously rollback via Vercel's Edge CDN.

## 2. Failed Backend Deployment (Render)
If a new Django build causes 500 Internal Server Errors or WSGI boot crashes:
1. Log into the Render dashboard.
2. Select your Web Service -> **Events**.
3. Locate the previous successful deploy.
4. Click **Rollback to this deploy**.
5. *Note: Rolling back the codebase does NOT rollback database migrations. See section 3 if migrations are involved.*

## 3. Bad Database Migration
If an invalid migration was deployed and corrupts API endpoints:
1. SSH into the Render Web Service via the "Shell" tab.
2. Unapply the specific bad migration using Django's reverse migration capability:
   ```bash
   python manage.py migrate [app_name] [previous_migration_number]
   ```
3. Commit a fix to the Git repository removing the bad migration file and redeploy.
4. **Catastrophic Failure**: If the database data is corrupted, use Render's Automated Backups feature in the PostgreSQL dashboard to perform a point-in-time restoration.

## 4. Corrupted ML Model or Bad Predictions
If a newly deployed ML model is throwing prediction errors or generating mathematically invalid probabilities:
> **DO NOT** attempt to edit the `.joblib` files directly.

1. SSH into the Render Web Service.
2. Navigate to the model directory mounted on the persistent disk:
   ```bash
   cd ml/data/processed/models
   ```
3. When the pipeline trains models, it saves versions with timestamps (e.g., `classification_v1.0.json`).
4. Replace the `_latest.json` pointer to point back to the previous known good model filename.
5. Restart the Render Web Service to flush the `joblib` memory cache:
   - Click **Manual Deploy** -> **Restart service** in the Render UI.

## 5. Incorrect Dataset Update
If the raw dataset uploaded to `backend/ml/data/raw/` is discovered to have massive provenancial discrepancies after the `verify_election_data` script was ignored:
1. Immediately delete the bad CSV from the raw directory.
2. Re-upload the last known valid ECI dataset.
3. Run the ML pipeline from scratch to overwrite the poisoned features:
   ```bash
   python manage.py train_model
   ```
4. Restart the web service.
