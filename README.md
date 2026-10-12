# MediCore

MediCore is a Django healthcare coordination portal with role based dashboards for patients, doctors, nurses, laboratory staff, pharmacists, receptionists and administrators.

## Features

- Patient accounts, doctor discovery and appointment requests
- Doctor and nursing schedules, home-care requests and reviews
- Consultations, prescriptions and laboratory orders
- Billing records, notifications and Django administration
- Bilingual chat assistant with clickable questions, free-text queries, date-picker doctor availability, real schedule/slot checks and patient appointment lookups; optional OpenAI replies are reserved for general questions
- Responsive desktop and mobile interface
- Environment-based settings for local development and hosted deployment

## Run locally (Windows PowerShell)

1. Install Python 3.12 or newer and open this project folder in PowerShell.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create your local settings file and set a private development key:

   ```powershell
   Copy-Item .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Paste the generated value into `.env` as `SECRET_KEY=...`. Keep `.env` private; Git ignores it.

4. Create the database tables and administrator account:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Start the site at <http://127.0.0.1:8000>:

   ```powershell
   python manage.py runserver
   ```

Patients can create their own accounts from the landing page. Staff accounts should be created by an administrator at `/admin/` and assigned the correct role and profile.

### Load the complete fictional demo dataset

`data/medicore_demo_data.csv` contains 290 linked demo rows. It has at least 10 records for every database feature/model, including 10 hospitals, departments, doctor and nurse profiles, patient profiles, home-care requests and reviews, consultations, prescriptions, lab catalogue items and orders, bills, payments, medicines, dispensing records and notifications. It also includes 10 users each for patient, doctor, nurse, lab, pharmacist and reception roles. The search feature uses the doctor and schedule records. The chatbot does not store conversations in the database, so it has no separate seed table.

All names, accounts and clinical notes in this file are fictional. The CSV is included for local demos and should not be imported into a live patient database. Dates like `today+3d` and `today-3d` are resolved relative to the day you import the file, so upcoming appointments stay upcoming.

After `python manage.py migrate`, run:

```powershell
python manage.py seed_demo_data
```

The command asks once for a shared demo-account password (at least 12 characters; input is hidden). Alternatively, set it in the current PowerShell session first with `$env:DEMO_PASSWORD = "your-private-demo-password"`, run the command, then clear it with `Remove-Item Env:DEMO_PASSWORD`. The import is safe to repeat: it updates or reuses the same keyed demo records. Existing demo users keep their existing passwords.

Demo usernames use the pattern `demo_<role>_01` through `_10`, such as `demo_patient_01`, `demo_doctor_01`, `demo_nurse_01`, `demo_lab_01`, `demo_pharmacist_01` and `demo_receptionist_01`. All newly created demo accounts share the password entered during import. Create your own administrator separately with `python manage.py createsuperuser`.

## A-to-Z local setup on Windows

1. Extract `MediCore-complete.zip` to a folder, then open PowerShell in that extracted folder. Confirm it contains `manage.py`.
2. Install Python 3.12 or newer. Check with `py --version`.
3. Create and activate a virtual environment, then install project packages:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that window, then activate again.

4. Create the private environment file and generate a Django secret key:

   ```powershell
   Copy-Item .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   notepad .env
   ```

   Paste the generated value after `SECRET_KEY=`. For local development, keep `DEBUG=True`. The database uses SQLite by default, so you do not need to install a separate database.

5. Create the database tables, load the demo data, and create an administrator:

   ```powershell
   python manage.py migrate
   python manage.py seed_demo_data
   python manage.py createsuperuser
   ```

6. Start the website and open the local URL:

   ```powershell
   python manage.py runserver
   ```

   Visit <http://127.0.0.1:8000/>. Sign in with one of the demo usernames and the shared demo password, or open <http://127.0.0.1:8000/admin/> with the administrator account you just created. Stop the server with `Ctrl+C`.

7. To use optional AI replies, add `OPENAI_API_KEY=your-key` to `.env`, save it, and restart the server. The core doctor search and slot assistant can still use MediCore data without an API key.

### Upload the project to GitHub

Create an empty repository on GitHub, then from the extracted project folder run:

```powershell
git status
git add .
git commit -m "Add MediCore project and demo dataset"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the repository URL with your own. Do not add `.env`, `db.sqlite3`, real patient data, or a secret/API key to GitHub; `.gitignore` excludes the local database and environment file.

### Optional AI replies

Without an API key, the assistant still finds doctors and checks appointment slots using MediCore data. To enable general AI replies, add a server-side `OPENAI_API_KEY` to `.env`; `OPENAI_MODEL` can override the default `gpt-4.1-mini`. Never place the API key in browser JavaScript or commit it. Only general questions are sent to the AI provider, one message at a time; doctor searches use MediCore data. The assistant does not send patient records or chat history. Users are asked not to enter identifying or private medical details.

## Deploy on Render

The repository includes `render.yaml` and `build.sh` for a Render Blueprint deployment.

1. Push this repository to GitHub or another Git provider connected to Render.
2. In Render, choose **New → Blueprint**, connect the repository and review the proposed web service and PostgreSQL database before applying it. The blueprint uses Singapore for the service and database.
3. Set `OPENAI_API_KEY` in the web service environment only if you want AI replies. The `SECRET_KEY` is generated by Render; `DATABASE_URL` is connected to the PostgreSQL service by the blueprint.
4. After the first deploy succeeds, open `/admin/` and create an administrator from the Render Shell:

   ```bash
   python manage.py createsuperuser
   ```

5. Add doctor, nurse and other staff accounts/profiles through Django admin. Patients can register from the landing page.

The starter blueprint uses Render's free web service and free Postgres for a low-cost demo. Free web services can sleep when idle, and Render's free Postgres expires after 30 days. Upgrade the database to a paid persistent plan before relying on it for long-term records. Do not store real patient data until hosting, access controls, backups and applicable privacy requirements have been reviewed for your organization.

To deploy manually, create a Render PostgreSQL database and Python web service, then set:

- **Build command:** `bash build.sh`
- **Start command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 60`
- **Environment:** `DATABASE_URL` from the database, `SECRET_KEY` (generated), `DEBUG=False`, and optionally `OPENAI_API_KEY` / `OPENAI_MODEL`.
- **Health check path:** `/health/`

`build.sh` installs the dependencies, collects static files and applies database migrations. Static assets are served by WhiteNoise.

## Useful commands

```bash
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

Before changing or deploying model fields, create and review migrations, then commit them with the code change.
