# 🛒 GROCERY_AI_CHATBOT  
### *Transform Shopping into Effortless Culinary Adventures*

[![Last Commit](https://img.shields.io/github/last-commit/d0t3ncrypt10n/Grocery_AI_Chatbot?style=for-the-badge)](https://github.com/d0t3ncrypt10n/Grocery_AI_Chatbot/commits)  
[![Repo Language](https://img.shields.io/github/languages/top/d0t3ncrypt10n/Grocery_AI_Chatbot?style=for-the-badge)](https://github.com/d0t3ncrypt10n/Grocery_AI_Chatbot)  

---

## 📌 Overview

**Grocery_AI_Chatbot** is a smart, conversational assistant that revolutionizes grocery shopping. Built on a modern **Hybrid Microservices Architecture**, it seamlessly understands natural language queries, fetches recipes, scales ingredients, matches them to real e-commerce products, and synchronizes a fully interactive shopping cart.

---

## 🚀 Features

- 🧠 **Dynamic NLP Pipeline** (Flask AI Service)
  Interactive chat engine fueled by advanced fallback NLP processing and Gemini API. 
- 🛒 **E-commerce Engine** (Node.js + SQLite)
  Intelligently maps raw recipe ingredients (e.g., "Pyaaz") to real database products (e.g., "Onions (1 kg)") through a multi-step fuzzy match pipeline.
- 🎨 **Modern SPA Interface** (React + Vite + Zustand)
  Dark-themed glassmorphic UI offering a frictionless chat and cart sidebar experience.
- 💵 **Budget Modes & Substitutions**
  Automatically adjusts suggestions to fit under specific budgets or offers vegan/healthier substitutes if items are out of stock.

---

## 🏗️ Architecture

```
React Frontend (:5173) ↔ Flask AI Service (:5000) ↔ Node.js Backend (:4000)
```

---

## 🛠️ Getting Started

### 1. Flask AI Service (Port 5000)
Handles NLP and conversational intelligence.
```bash
cd flask-ai
pip install -r requirements.txt
python app.py
```
*(Requires Python 3.9+)*

### 2. Node.js Backend (Port 4000)
Handles product inventory, ingredient mapping, and cart operations.
```bash
cd node-backend
npm install
npm start
```
*(Running `npm start` automatically seeds the SQLite DB with 50+ local products!)*

### 3. React Frontend (Port 5173)
The interactive Chat and Cart UI.
```bash
cd react-frontend
npm install
npm run dev
```

Once all services are up, simply open `http://localhost:5173` in your browser.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

> *Crafted with ❤️ to simplify your culinary journey.*  
> — Team Grocery_AI_Chatbot
