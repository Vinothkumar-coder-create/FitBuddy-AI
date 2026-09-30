import os


os.environ["MOCK_AI"] = "true"

os.environ["ADMIN_TOKEN"] = "test-token"

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_fitbuddy.db"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_workout():

    form_data = {

        "username": "Test User",

        "user_id": "TEST001",

        "age": "25",

        "weight": "70",

        "goal": "general_wellness",

        "intensity": "low",
    }


    response = client.post(

        "/generate-workout",

        data=form_data,
    )


    assert response.status_code == 200

    assert (
        "personalized"
        in response.text.lower()
    )


def test_submit_feedback():

    form_data = {

        "user_id": "TEST001",

        "feedback": (
            "Add more walking and "
            "make Day 5 easier."
        ),
    }


    response = client.post(

        "/submit-feedback",

        data=form_data,
    )


    assert response.status_code == 200

    assert (
        "updated"
        in response.text.lower()
    )