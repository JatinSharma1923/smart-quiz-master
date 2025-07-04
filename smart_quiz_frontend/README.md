# Smart Quiz Frontend

---

## 🖼️ Frontend: `smart_quiz_frontend/README.md`


# 💻 Smart Quiz Frontend

This is the React-based frontend for **Smart Quiz Master**, a gamified quiz platform powered by AI. Users can attempt quizzes, track their performance, earn badges, and more.

---

## 🎯 Key Features

- 👤 Firebase Authentication (Login/Signup)
- 📱 Responsive UI built with Tailwind CSS
- 🧠 Real-time AI quiz rendering via API
- 📈 User dashboard with streaks, badges, and analytics
- 🗂️ Topic/difficulty-wise filtering of quizzes

---

## ⚙️ Tech Stack

- **React 18+**
- **Vite**
- **Firebase Auth**
- **Axios**
- **Tailwind CSS**
- **React Router**

---

## 🧑‍💻 Setup Guide

### 1. Clone the repo
```bash
git clone https://github.com/JatinSharma1923/smart_quiz_frontend.git
cd smart_quiz_frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment
Create a `.env` file like this:
```env
VITE_FIREBASE_API_KEY=xxx
VITE_FIREBASE_AUTH_DOMAIN=xxx
VITE_BACKEND_API_URL=http://localhost:8000
```
Use `.env.example` as a base.

### 4. Run the app
```bash
npm run dev
```
Visit: http://localhost:5173

## 🗂️ Folder Structure
```
smart_quiz_frontend/
├── src/
│   ├── components/      # UI components (Navbar, Cards, etc.)
│   ├── pages/           # Screens like Home, Dashboard, QuizPage
│   ├── services/        # API service handlers (Axios)
│   └── App.jsx
├── .env.example
├── package.json
└── vite.config.js
```

## 🧑‍🚀 Developer
**Built by:** Jatin Sharma  
📬 **Email:** jatinsharma1923@gmail.com  
🔗 **GitHub:** https://github.com/JatinSharma1923
