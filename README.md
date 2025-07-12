# Smart Quiz Backend

# 🧠 Smart Quiz API

The **Smart Quiz API** is a FastAPI-powered backend for generating, managing, and grading AI-powered quizzes. It integrates with OpenAI's GPT-4o, Firebase Authentication, and PostgreSQL, making it suitable for interview prep, UPSC, SSC, cybersecurity learning, and more.

---

## 🚀 Features

- 🔐 Firebase User Authentication
- 🤖 AI-generated quizzes from prompts or URLs (OpenAI GPT-4o)
- 🧠 Multiple question types (MCQ, True/False, Image-based)
- 🗂️ Quiz categorization by topic, difficulty, and tags
- 📊 User tracking, streaks, badges, and analytics
- 🛡️ Rate limiting, API keys, logging & error tracing
- 🧰 Fully modular FastAPI structure with routers, services, and templates

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy ORM**
- **Firebase Auth**
- **OpenAI GPT-4o**
- **Redis (for caching/queues, optional)**

---

## ⚙️ Setup Guide

### 1. Clone the repo

```bash
git clone https://github.com/JatinSharma1923/smart_quiz_api.git
cd smart_quiz_api
```

### 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env file

Update values for:

```bash
cp .env.example .env
```

Add your keys:

- `OPENAI_API_KEY`
- `FIREBASE_PROJECT_ID`
- `DATABASE_URL`

### 5. Run the API

```bash
uvicorn main:app --reload
```

## 📚 Folder Structure

```
smart-quiz-master/
│
├── smart_quiz_api/                          <-- React app (run `npm start` here)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── admin_router.py
│   │   ├── quiz_router.py
│   │   └── user_router.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── firebase/
│   │       ├── __init__.py
│   │       ├── firebase_init.py          ✅ Firebase App Init
│   │       ├── firebase_utils.py         ✅ Token Extraction + Verification
│   │       ├── firebase_user.py          ✅ DB: Get/Create/Update User
│   │       ├── firebase_auth.py          ✅ FastAPI Dependencies
│   │       └── firebase_health.py        ✅ Optional Health Check
│   │   ├── openai_service.py
│   │   └── scraper_service/
│   │       ├── __init__.py
│   │       ├── content_fetcher.py       # For fetching and validating article HTML
│   │       ├── text_cleaner.py          # For extracting clean text using readability/BeautifulSoup
│   │       ├── difficulty_estimator.py  # For Flesch-Kincaid & word count based difficulty scoring
│   │       ├── topic_classifier.py      # For topic classification via OpenAI
│   │       ├── quiz_generator.py        # For generating quiz prompt and calling OpenAI
│   │       ├── cache.py                 # Redis cache logic
│   │       ├── interface.py             # Main public-facing function like scrape_and_generate_quiz()
|   |       └── openai_wrapper.py        # OpenAI call with retry logic.
│   ├── templates/
│   │   ├── image.txt
│   │   ├── mcq.txt
│   │   ├── tf.txt
│   │   └── scraper_prompt.txt
│   ├── utils/
│   │   ├── auth_utils.py
│   │   ├── decorators.py
│   │   ├── retry_utils.py
│   │   └── text_utils.py
│   ├── migrations/                         # 📦 Alembic DB migrations
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── main.py                             # FastAPI entrypoint
│   ├── models/
│   │   ├──__init__.py
│   │   ├──answer.py
│   │   ├──background.py
│   │   ├──badge.py
│   │   ├──base.py
│   │   ├──enum.py
│   │   ├──feedback.py
│   │   ├──log.py
│   │   ├──mixins.py
│   │   ├──prompt.py
│   │   ├──quiz.py
│   │   ├──user.py
│   ├── schema.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env                                # Local API env
│   └── .env.example
│
├── smart_quiz_frontend/                    <-- FastAPI backend (run `uvicorn main:app --reload` here)
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   ├── hero.mp4
│   │   └── lottie/
│   │       ├── loading.json
│   │       └── badge-earned.json
│   ├── src/
│   │   ├── assets/ (images, icons, fonts, videos)
│   │   ├── animations/ (gsap, lottie, framer)
│   │   ├── api/ (quizApi, authApi, axiosInstance...)
│   │   ├── components/ (ui, quiz, layout, dashboard)
│   │   ├── constants/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── interfaces/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── store/
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── .env                                # VITE_API_URL, Firebase keys
│   ├── .env.example
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
│
├── docker/                                 # 🐳 Dockerfiles and config
│   ├── backend.dockerfile
│   ├── frontend.dockerfile
│   └── nginx.conf                          # Optional: For proxy
│
├── .github/                                # 🧪 GitHub Actions CI/CD
│   └── workflows/
│       └── ci.yml
│
├── .env                                     # Top-level env vars if shared
├── .env.example
├── docker-compose.yml                      # Dev + deployment orchestration
├── alembic.ini                             # Alembic config
├── LICENSE
├── README.md                                # 📘 Full monorepo guide
├── .gitignore
├── .prettierrc                              # Format rules (optional)
├── .eslintrc.js                             # Linting config (optional)
├── tsconfig.base.json                       # Base TS config if needed
└── CONTRIBUTING.md                          # 👥 Dev guidelines (optional)

```

## 📫 Contact

**Made by:** Jatin Sharma  
📬 **Email:** [jatinsharma1923@gmail.com](mailto:jatinsharma1923@gmail.com)  
🌐 **GitHub:** [@JatinSharma1923](https://github.com/JatinSharma1923)
