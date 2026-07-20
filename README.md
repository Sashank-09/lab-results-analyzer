# 🩺 Lab Results Analyzer

<p align="center">

![React](https://img.shields.io/badge/React-18-blue?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Anthropic](https://img.shields.io/badge/Claude-AI-orange)
![License](https://img.shields.io/badge/License-MIT-green)

</p>

An AI-powered web application that analyzes laboratory blood test results and provides patient-friendly explanations, severity classification, and personalized health recommendations using **Anthropic Claude AI**.

---

# 🚀 Live Demo

### 🌐 Frontend

https://lab-results-analyzer.vercel.app/

### ⚙️ Backend API

https://lab-results-analyzer-2.onrender.com

### 📖 API Documentation (Swagger)

https://lab-results-analyzer-2.onrender.com/docs

---

# 📌 Project Overview

Understanding laboratory reports can be difficult for non-medical users because blood test reports contain technical terminology and numerical values.

The Lab Results Analyzer simplifies this process by:

- Validating laboratory values
- Comparing them against medical reference ranges
- Detecting abnormal parameters
- Generating AI-powered explanations
- Suggesting next steps and recommendations

Instead of simply displaying numbers, the application explains **what those numbers mean** in simple language.

---

# ✨ Features

- ✅ Laboratory result analysis
- ✅ AI-powered explanations using Claude AI
- ✅ Reference range validation
- ✅ Critical / Warning / Normal classification
- ✅ Patient-friendly medical explanations
- ✅ Recommended next steps
- ✅ REST API
- ✅ Responsive React UI
- ✅ FastAPI backend
- ✅ Secure API key management using environment variables
- ✅ Cloud deployment using Render & Vercel

---

# 🛠 Tech Stack

## Frontend

- React.js
- JavaScript
- CSS
- Fetch API

## Backend

- FastAPI
- Python
- Pydantic
- Uvicorn

## AI

- Anthropic Claude API

## Deployment

- Vercel
- Render

---

# 🏗 Architecture

```text
                   User
                     │
                     ▼
             React Frontend
                     │
              HTTPS POST Request
                     │
                     ▼
             FastAPI Backend
                     │
      Reference Range Validation
                     │
           Prompt Engineering
                     │
                     ▼
          Anthropic Claude API
                     │
             AI Generated Analysis
                     │
                     ▼
             FastAPI Response
                     │
                     ▼
             React Frontend
                     │
                     ▼
            Results Display
```

---

# 🔄 Application Workflow

## Step 1

The user enters laboratory values in the React frontend.

↓

## Step 2

React validates the input and sends a POST request to the FastAPI backend.

↓

## Step 3

FastAPI validates the request using Pydantic models.

↓

## Step 4

The backend compares laboratory values against predefined reference ranges.

↓

## Step 5

A structured prompt is generated and sent to Anthropic Claude.

↓

## Step 6

Claude analyzes the laboratory results and generates:

- Summary
- Severity
- Medical explanation
- Recommendations
- Next steps

↓

## Step 7

The backend returns the analysis as JSON.

↓

## Step 8

React displays the results in an easy-to-understand format.

---

# 📂 Project Structure

```
lab-results-analyzer/
│
├── backend/
│   ├── agent.py
│   ├── main.py
│   ├── models.py
│   ├── reference_ranges.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── screenshots/
│
├── README.md
└── .gitignore
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Sashank-09/lab-results-analyzer.git
```

```
cd lab-results-analyzer
```

---

## Backend

```
cd backend

python -m venv venv
```

Windows

```
venv\Scripts\activate
```

Install packages

```
pip install -r requirements.txt
```

Run

```
uvicorn main:app --reload
```

---

## Frontend

```
cd frontend

npm install

npm start
```

---

# 🔐 Environment Variables

Create

```
backend/.env
```

Example

```env
ANTHROPIC_API_KEY=your_api_key_here
```

⚠️ Do not commit your `.env` file.

---

# 📡 API Endpoint

POST

```
/analyze_labs
```

Example Request

```json
{
  "labs": [
    {
      "test_name": "Hemoglobin",
      "value": 9.8,
      "unit": "g/dL",
      "patient_id": "P001"
    }
  ]
}
```

---

# Future Enhancements

- PDF Lab Report Upload
- OCR Integration
- Authentication
- Patient History
- PDF Export
- Dashboard
- Multi-language Support
- Email Reports
- Doctor Portal

---

# Security

- API keys are stored securely using environment variables.
- `.env` files are excluded from Git.
- Only `.env.example` is included in the repository.

---

# Learning Outcomes

This project helped me gain practical experience with:

- React Development
- FastAPI
- REST APIs
- AI Integration
- Prompt Engineering
- Pydantic Validation
- Cloud Deployment
- Git & GitHub
- Environment Variables
- Full Stack Development

---

# Author

## Sashank Enukurthi

Artificial Intelligence & Data Science Graduate

GitHub:

https://github.com/Sashank-09

LinkedIn:

(Add your LinkedIn)

---

# License

This project is licensed under the MIT License.
