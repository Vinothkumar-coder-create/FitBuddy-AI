 # FitBuddy - AI Fitness Plan Generator

FitBuddy is an AI-powered fitness plan generator built with:

- FastAPI
- Jinja2
- SQLite
- SQLAlchemy
- Pydantic
- Google Gemini
- Pytest

## Features

- Personalized 7-day workout plan
- AI-generated nutrition guidance
- User feedback and plan regeneration
- SQLite database
- Admin dashboard
- API documentation
- Automated tests
- Mock AI mode

---
# Requirements


- Python
- Visual Studio Code
- A Gemini API key
- Internet connection for Gemini API requests

# The basic workflow is:
User
  |
  v
FitBuddy Web Form
  |
  v
FastAPI Backend
  |
  v
User Input Validation
  |
  v
Gemini API
  |
  v
Structured 7-Day Workout Plan
  |
  v
SQLite Database
  |
  v
Result Page


# For Feed back:

User Feedback
     |
     v
FastAPI
     |
     v
Original Workout Plan + Feedback
     |
     v
Gemini API
     |
     v
Updated Workout Plan