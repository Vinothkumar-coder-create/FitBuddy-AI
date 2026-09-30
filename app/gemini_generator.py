from google import genai

from app.config import get_settings
from app.schemas import (
    WorkoutDay,
    WorkoutPlan,
)


# =========================================================
# GEMINI CLIENT
# =========================================================

def _client():

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


# =========================================================
# MOCK WORKOUT PLAN
# =========================================================

def _mock_plan(user):

    days_data = [

        (
            "Full Body",
            [
                "Bodyweight squat - 3 x 10",
                "Push-up - 3 x 8",
                "Glute bridge - 3 x 12",
            ],
        ),

        (
            "Cardio",
            [
                "Brisk walk or cycling - 25 minutes",
                "Easy intervals - 5 x 1 minute",
            ],
        ),

        (
            "Upper Body",
            [
                "Incline push-up - 3 x 10",
                "Backpack row - 3 x 12",
                "Shoulder press - 3 x 10",
            ],
        ),

        (
            "Mobility",
            [
                "Cat-cow - 2 x 8",
                "Hip mobility - 2 x 8 per side",
                "Easy walk - 15 minutes",
            ],
        ),

        (
            "Lower Body",
            [
                "Squat - 3 x 10",
                "Reverse lunge - 3 x 8 per side",
                "Calf raise - 3 x 15",
            ],
        ),

        (
            "Core + Cardio",
            [
                "Dead bug - 3 x 8 per side",
                "Plank - 3 x 20 seconds",
                "Walk - 20 minutes",
            ],
        ),

        (
            "Active Recovery",
            [
                "Easy walk - 20 minutes",
                "Full body mobility - 10 minutes",
            ],
        ),
    ]

    days = []

    for index, (focus, exercises) in enumerate(
        days_data,
        start=1,
    ):

        days.append(
            WorkoutDay(

                day=f"Day {index}",

                focus=focus,

                warm_up=(
                    "5-8 minutes of easy movement "
                    "and dynamic mobility."
                ),

                exercises=exercises,

                cooldown=(
                    "5 minutes of easy movement "
                    "and gentle stretching."
                ),

                recovery_tip=(
                    "Hydrate, sleep well, and reduce "
                    "volume if recovery is poor."
                ),

            )
        )

    plan = WorkoutPlan(

        title=(
            f"7-Day "
            f"{user.goal.replace('_', ' ').title()} "
            "Plan"
        ),

        safety_note=(
            "Start gradually. Use controlled technique. "
            "Stop if you experience sharp pain, dizziness, "
            "or unusual shortness of breath."
        ),

        days=days,

    )

    return plan


# =========================================================
# GENERATE WORKOUT WITH GEMINI
# =========================================================

def generate_workout_gemini(user):

    settings = get_settings()

    # -----------------------------------------------------
    # MOCK MODE
    # -----------------------------------------------------

    if settings.mock_ai:

        return _mock_plan(user).model_dump_json(
            indent=2
        )

    # -----------------------------------------------------
    # GEMINI CLIENT
    # -----------------------------------------------------

    client = _client()

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
Create a safe and practical 7-day fitness plan.

User information:

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Requirements:

1. Return exactly 7 days.
2. Include a focus for every day.
3. Include warm-up.
4. Include main exercises.
5. Include sets/repetitions or duration.
6. Include cooldown.
7. Include recovery advice.
8. Include a safety note.
9. Prefer bodyweight or home-friendly exercises.
10. Keep the plan realistic.
11. Keep the plan progressive.
12. Do not diagnose medical conditions.
13. Do not prescribe medical treatment.
14. Keep the answer concise.
"""

    # -----------------------------------------------------
    # GEMINI REQUEST
    # -----------------------------------------------------

    response = client.models.generate_content(

        model=settings.workout_model,

        contents=prompt,

        config={
    "response_mime_type": "application/json",
    "response_schema": WorkoutPlan,
    "max_output_tokens": 3500,
},

    )

    # -----------------------------------------------------
    # READ GEMINI RESPONSE
    # -----------------------------------------------------

    if response.parsed:

        parsed = response.parsed

    else:

        parsed = WorkoutPlan.model_validate_json(
            response.text
        )

    # -----------------------------------------------------
    # RETURN JSON
    # -----------------------------------------------------

    return parsed.model_dump_json(
        indent=2
    )


# =========================================================
# UPDATE WORKOUT USING USER FEEDBACK
# =========================================================

def update_workout_plan(

    user,

    original_plan: str,

    feedback: str,

):

    settings = get_settings()

    # -----------------------------------------------------
    # MOCK MODE
    # -----------------------------------------------------

    if settings.mock_ai:

        return (

            original_plan

            + "\n\nUPDATED FROM USER FEEDBACK:\n"

            + feedback

        )

    # -----------------------------------------------------
    # GEMINI CLIENT
    # -----------------------------------------------------

    client = _client()

    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
Update the following 7-day fitness plan.

User:

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Original plan:

{original_plan}

User feedback:

{feedback}

Requirements:

1. Return exactly 7 days.
2. Apply the user's feedback.
3. Keep the plan practical.
4. Keep the plan safe.
5. Preserve useful parts of the original plan.
6. Include warm-up.
7. Include exercises.
8. Include cooldown.
9. Include recovery advice.
10. Include a safety note.
11. Keep the answer concise.
"""

    # -----------------------------------------------------
    # GEMINI REQUEST
    # -----------------------------------------------------

    response = client.models.generate_content(

        model=settings.workout_model,

        contents=prompt,

       config={
    "response_mime_type": "application/json",
    "response_schema": WorkoutPlan,
    "max_output_tokens": 3500,
},

    )

    # -----------------------------------------------------
    # READ RESPONSE
    # -----------------------------------------------------

    if response.parsed:

        parsed = response.parsed

    else:

        parsed = WorkoutPlan.model_validate_json(
            response.text
        )

    # -----------------------------------------------------
    # RETURN JSON
    # -----------------------------------------------------

    return parsed.model_dump_json(
        indent=2
    )