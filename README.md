---

# 🌌 AI Recommender System

> A futuristic AI-powered recommendation system with a *Flask backend* and a *React + MUI frontend*, featuring a galaxy-inspired professional UI.

---

## 🚀 Overview

The *AI Recommender System* intelligently suggests products to users based on collaborative filtering and cosine similarity.  
It combines a *machine learning model* for recommendation with a *modern 3D-inspired frontend* for an immersive user experience.

This project showcases a full-stack architecture — from *model training and Flask APIs* to *React UI integration* — designed for scalability, clean design, and modern usability.

---

## 🧩 Project Architecture

project2/ │ ├── ai_recommender/ │   └── reco_project/ │       └── reco/ │           ├── app.py                # Flask backend API │           ├── train_and_save.py     # Model training and saving │           ├── models/ │           │   └── item_sim.pkl      # Trained recommendation model │           └── data/ │               ├── items.csv         # Item data │               └── ratings.csv       # User ratings │ └── reco_frontend/ ├── src/ │   ├── App.js                   # Main React entry point │   ├── components/              # Reusable UI components │   │   ├── Sidebar.js │   │   └── UniverseBackground.js │   └── pages/                   # Page views (Recommendations, MyRatings) ├── public/ └── package.json

---

## 🧠 Features

✅ *AI-Powered Recommendations* – Uses cosine similarity to recommend similar items  
✅ *User Rating System* – Store and update ratings dynamically  
✅ *Flask REST API* – Backend endpoints for items, recommendations, and ratings  
✅ *React Frontend* – Built with Material UI, Framer Motion, and 3D animations  
✅ *Galaxy-Themed UI* – Modern, immersive design using @react-three/fiber and drei  
✅ *Fully Modular Architecture* – Easy to extend and maintain

---

## ⚙ Tech Stack

*Frontend:*
- ⚛ React (18+)
- 🎨 Material UI (MUI)
- 💫 Framer Motion
- 🌌 Three.js + React Three Fiber
- 📦 Axios (API integration)

*Backend:*
- 🐍 Flask
- 🧮 Scikit-learn
- 🐼 Pandas
- 🔥 Pickle (for model persistence)

---

## 🧰 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | /items/<item_id> | Get item details |
| GET | /recommend/<user_id> | Get recommendations for a user |
| POST | /rate | Submit a user rating (JSON body: { user_id, item_id, rating }) |

---

## 🏃‍♂ How to Run Locally

### 1️⃣ Backend (Flask)

bash
cd ai_recommender/reco_project/reco
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_and_save.py
python app.py

Flask will start on: 👉 http://127.0.0.1:5000


---

2️⃣ Frontend (React)

cd reco_frontend
npm install
npm start

React app will start on: 👉 http://localhost:3000


---

🧮 Example API Test (PowerShell or CMD)

Invoke-RestMethod http://127.0.0.1:5000/recommend/1 | ConvertTo-Json -Depth 5

Output:

{
  "user_id": 1,
  "recommendations": [
    { "item_id": "102", "score": 2.5 },
    { "item_id": "103", "score": 1.9 }
  ]
}


---

🪐 UI Preview

> The UI features a cosmic-inspired layout with 3D galaxy animations, glowing cards, and smooth transitions powered by Framer Motion and Three.js.



Example page: 


---

🧑‍💻 Contributing

Pull requests are welcome!
If you’d like to enhance the UI, improve model accuracy, or add new datasets, feel free to open an issue or fork this repo.


---

📄 License

This project is licensed under the MIT License.
You’re free to use, modify, and distribute this project with attribution.


---

⭐ Show Your Support

If you find this project useful, please star ⭐ the repository on GitHub — it helps others discover this AI project!


---

Author: @sriramchikkala0
Project: 🌌 AI Recommender System
Tech: Flask + React + Machine Learning

---
