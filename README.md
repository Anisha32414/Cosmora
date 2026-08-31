# ✨ Cosmora

Cosmora is an AI-powered skincare and haircare recommendation platform that helps users understand their skin and hair concerns through questionnaires and AI-powered image analysis. It integrates multiple skin-analysis tools with LangChain, RAG, and LLMs to provide personalized problem analysis, solutions, and daily wellness routines.

---

## Features

* Skin Care with two personalized analysis options
* Questionnaire-based skin analysis
* Image-based skin analysis using multiple AI analysis tools
* Questionnaire-based hair care analysis
* LangChain-based RAG pipeline
* Retrieval-Augmented Generation (RAG)
* LLM-powered personalized recommendations
* Detailed problem identification and analysis
* Personalized solutions and skincare/haircare guidance
* Personalized daily habits and routines
* Privacy-focused design with no user data storage
* Detailed analysis results and recommendations
* Simple and responsive user interface

---

## Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### AI & RAG

* LangChain
* Retrieval-Augmented Generation (RAG)
* Large Language Model (LLM)
* Embeddings
* Vector Database / Vector Store
* AI Skin Analysis APIs

### Version Control

* Git
* GitHub

---

## How It Works

### Main Options

Cosmora provides two main options:

* **Skin Care**
* **Hair Care**

---

### Skin Care

The Skin Care section provides two different ways to get personalized analysis.

#### 1. Questionnaire-Based Skin Analysis

* Users fill out a questionnaire containing information about their skin type, concerns, lifestyle, and other relevant details.
* The collected user profile is processed through the RAG + LLM pipeline.
* Relevant skincare knowledge is retrieved from the vector database.
* The LLM uses the retrieved information along with the user's profile to generate personalized results.
* Users receive detailed information about their skin problems, possible factors, recommended solutions, and daily habits.
* This option is also available for users who are not comfortable providing a face image.

#### 2. Image-Based Skin Analysis

* Users upload a clear facial image and provide their main skin concern.
* The image is sent to multiple integrated AI skin-analysis tools.
* The results from the available tools are collected and combined.
* The system identifies detected skin findings and calculates the overall skin score.
* The combined findings and user's concern are passed to the RAG + LLM pipeline.
* Relevant skincare information is retrieved from the knowledge base.
* The LLM generates personalized guidance, including identified concerns, solutions, and daily wellness habits.

---

### Hair Care

The Hair Care section uses a questionnaire-based approach.

* Users fill out a questionnaire containing information about their hair type, concerns, lifestyle, and hair-care habits.
* The collected information is converted into a personalized user profile.
* The profile is processed through the RAG + LLM pipeline.
* Relevant hair-care knowledge is retrieved from the vector database.
* The LLM generates personalized results based on the user's profile.
* Users receive detailed information about their hair problems, recommended solutions, and daily habits and routines.

---

## Privacy

Cosmora is designed with user privacy in mind.

* User information and uploaded images are **not stored by Cosmora**.
* Users who are uncomfortable providing a facial image can use the **Skin Care Questionnaire** instead.
* Users can receive personalized skincare guidance without providing a face image.
* The questionnaire provides an alternative way to receive personalized problems, solutions, and daily wellness recommendations.

---

## RAG + LLM Pipeline

The personalized recommendation system follows a RAG-based approach:

**User Input → User Profile / Analysis Results → Relevant Knowledge Retrieval → LLM → Personalized Results**

The generated results include:

* **Problem Analysis**
* **Recommended Solutions**
* **Daily Habits & Routines**
