# MediCore চালানোর A–Z গাইড

## ১) ZIP খুলুন

`MediCore-complete.zip` Extract করুন। Extract করা `MediCore` ফোল্ডারের ভেতরে `manage.py` আছে কি না দেখুন। PowerShell ওই ফোল্ডারে খুলুন।

## ২) Python ও virtual environment

Python 3.12 বা নতুন সংস্করণ লাগবে। PowerShell-এ যাচাই করুন:

```powershell
py --version
```

তারপর project folder-এ virtual environment তৈরি ও চালু করুন:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PowerShell activation বন্ধ করলে ওই উইন্ডোতে একবার চালান, তারপর activate করুন:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## ৩) Environment তৈরি

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
notepad .env
```

শেষ command-এ `.env` খুললে নতুন secret key-টি `SECRET_KEY=`-এর পরে বসান। লোকাল চালানোর সময় `DEBUG=True` রাখুন। SQLite ডাটাবেস project নিজেই তৈরি করবে; আলাদা database install করতে হবে না। `.env` ব্যক্তিগত রাখুন এবং GitHub-এ দেবেন না।

## ৪) Database ও demo data তৈরি

```powershell
python manage.py migrate
python manage.py seed_demo_data
```

Demo import command একবার ১২ বা তার বেশি অক্ষরের password চাইবে; টাইপ করার সময় দেখা যাবে না। এই password নতুন সব demo account-এর জন্য একই হবে। CSV ফাইল `data/medicore_demo_data.csv`। এতে ২৯০টি fictional, সম্পর্কযুক্ত row আছে; প্রতিটি database feature-এ অন্তত ১০টি record আছে। Import আবার চালালে একই sample record update/reuse হবে।

Demo account username-এর নমুনা:

- `demo_patient_01`
- `demo_doctor_01`
- `demo_nurse_01`
- `demo_lab_01`
- `demo_pharmacist_01`
- `demo_receptionist_01`

প্রতিটি role-এর জন্য `_01` থেকে `_10` পর্যন্ত account আছে। সব নতুন account-এ import-এর সময় দেওয়া একই password ব্যবহার করুন। এগুলো fictional data—বাস্তব রোগীর তথ্য নয়, চিকিৎসার জন্যও নয়।

Admin account বানান:

```powershell
python manage.py createsuperuser
```

## ৫) Project চালান

```powershell
python manage.py runserver
```

Browser-এ খুলুন <http://127.0.0.1:8000/>। Admin panel: <http://127.0.0.1:8000/admin/>। Server বন্ধ করতে PowerShell-এ `Ctrl+C` চাপুন।

## ৬) AI chatbot চালু করা (ঐচ্ছিক)

`.env` ফাইলে server-side-এ `OPENAI_API_KEY=আপনার-ব্যক্তিগত-key` যোগ করে server restart করুন। Key কখনো frontend JavaScript বা GitHub-এ দেবেন না। API key না থাকলেও MediCore-এর doctor search/slot assistant চলবে; সাধারণ AI উত্তর চালু থাকবে না।

## ৭) GitHub-এ upload

GitHub-এ একটি নতুন, খালি repository তৈরি করুন। Project folder-এ PowerShell খুলে `YOUR-USERNAME` ও `YOUR-REPOSITORY` নিজের তথ্য দিয়ে বদলে চালান:

```powershell
git status
git add .
git commit -m "Add MediCore project and demo dataset"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

`.gitignore` অনুযায়ী `.env`, `db.sqlite3` এবং local media Git-এ যাবে না। GitHub-এ `.env`, API key বা বাস্তব রোগীর তথ্য কখনো upload করবেন না।

## ৮) Online deploy

Project-এ Render Blueprint-এর জন্য `render.yaml` এবং `build.sh` আছে। GitHub-এ push করার পরে Render-এ repository-টি Blueprint হিসেবে connect করে `render.yaml`-এর প্রস্তাবিত service ও database review করে deploy করুন। Web service environment-এ secret `OPENAI_API_KEY` দিতে পারেন। Deploy হওয়ার পর Render Shell-এ চালান:

```bash
python manage.py createsuperuser
```

`render.yaml`/`README.md`-এ deployment settings আছে। Live site-এ demo dataset import করবেন না। বাস্তব স্বাস্থ্যতথ্য রাখার আগে access control, backup, hosting security ও প্রযোজ্য privacy নিয়ম যাচাই করুন।

## সমস্যা হলে

- `No module named ...`: `.venv` activate আছে কি না দেখে `pip install -r requirements.txt` আবার চালান।
- `SECRET_KEY` বা `.env` সমস্যা: `.env.example` থেকে `.env` বানিয়ে secret key সেট করুন।
- Demo import command না পেলে: project root-এ (যেখানে `manage.py`) আছেন নিশ্চিত করে `python manage.py migrate` চালান; এরপর command আবার দিন।
- Port ব্যস্ত থাকলে: `python manage.py runserver 8001` চালিয়ে <http://127.0.0.1:8001/> খুলুন।
