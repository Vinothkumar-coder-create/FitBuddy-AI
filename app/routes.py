import json

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_generator import (
    generate_workout_gemini,
    update_workout_plan,
)
from app.schemas import FeedbackRequest, UserInput


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# =========================================================
# JSON HELPER
# =========================================================

def parse_json(value):
    """
    Convert Gemini/mock/Pydantic/dictionary output
    into a normal Python dictionary.
    """

    if value is None:
        return {}

    # Pydantic model
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass

    # Dictionary
    if isinstance(value, dict):
        return value

    # JSON string
    if isinstance(value, str):
        try:
            result = json.loads(value)

            if isinstance(result, dict):
                return result

        except Exception:
            pass

    # Object with __dict__
    if hasattr(value, "__dict__"):
        try:
            result = dict(value.__dict__)

            result.pop(
                "_sa_instance_state",
                None,
            )

            return result

        except Exception:
            pass

    return {}


# =========================================================
# LOCAL NUTRITION TIP
# =========================================================

def generate_local_nutrition_tip(user):
    """
    Generate basic nutrition and recovery information
    locally without making another Gemini API request.

    This saves one Gemini request every time a workout
    is generated.
    """

    if user.goal == "weight_loss":

        result = {
            "tip": (
                "Choose balanced meals with vegetables, "
                "fruit, whole grains, and a protein source."
            ),
            "hydration": (
                "Drink fluids regularly throughout the day "
                "and around exercise."
            ),
            "recovery": (
                "Prioritize sleep and allow your body "
                "enough time to recover between workouts."
            ),
        }

    elif user.goal == "muscle_gain":

        result = {
            "tip": (
                "Include a protein source in regular meals "
                "and choose balanced foods containing "
                "carbohydrates, protein, and healthy fats."
            ),
            "hydration": (
                "Drink fluids regularly before, during, "
                "and after exercise."
            ),
            "recovery": (
                "Prioritize sleep and recovery days so "
                "your body can recover between sessions."
            ),
        }

    elif user.goal == "flexibility":

        result = {
            "tip": (
                "Choose a balanced diet containing "
                "vegetables, fruits, whole grains, "
                "and adequate protein."
            ),
            "hydration": (
                "Stay hydrated throughout the day, "
                "especially around physical activity."
            ),
            "recovery": (
                "Use gentle mobility work and prioritize "
                "adequate sleep and recovery."
            ),
        }

    else:

        result = {
            "tip": (
                "Choose a variety of vegetables, fruits, "
                "whole grains, protein foods, and healthy fats."
            ),
            "hydration": (
                "Drink fluids regularly throughout the day "
                "and around exercise."
            ),
            "recovery": (
                "Prioritize sleep, balanced meals, and "
                "appropriate recovery between workouts."
            ),
        }

    return json.dumps(
        result,
        indent=2,
    )


# =========================================================
# FORM OPTIONS
# =========================================================

def template_options():

    return {
        "goals": [
            (
                "weight_loss",
                "Weight Loss",
            ),
            (
                "muscle_gain",
                "Muscle Gain",
            ),
            (
                "general_wellness",
                "General Wellness",
            ),
            (
                "flexibility",
                "Flexibility",
            ),
        ],

        "intensities": [
            (
                "low",
                "Low",
            ),
            (
                "medium",
                "Medium",
            ),
            (
                "high",
                "High",
            ),
        ],
    }


# =========================================================
# HOME PAGE
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=template_options(),
    )


# =========================================================
# GENERATE WORKOUT
# =========================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

):

    try:

        # -------------------------------------------------
        # 1. Validate user information
        # -------------------------------------------------

        user_data = UserInput(

            username=username,

            user_id=user_id,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity,

        )

        # -------------------------------------------------
        # 2. Save user
        # -------------------------------------------------

        user = save_user(
            user_data.model_dump()
        )

        # -------------------------------------------------
        # 3. Generate workout using Gemini
        # -------------------------------------------------

        # IMPORTANT:
        # This is now the ONLY Gemini request
        # made when clicking Generate.

        workout_plan = generate_workout_gemini(
            user_data
        )

        # -------------------------------------------------
        # 4. Generate nutrition locally
        # -------------------------------------------------

        # NO Gemini request here.

        nutrition_tip = generate_local_nutrition_tip(
            user_data
        )

        # -------------------------------------------------
        # 5. Save plan
        # -------------------------------------------------

        save_plan(
            user.user_id,
            workout_plan,
            nutrition_tip,
        )

        # -------------------------------------------------
        # 6. Convert output for HTML
        # -------------------------------------------------

        workout_plan_data = parse_json(
            workout_plan
        )

        nutrition_tip_data = parse_json(
            nutrition_tip
        )

        # -------------------------------------------------
        # 7. Show result page
        # -------------------------------------------------

        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan_data": workout_plan_data,

                "nutrition_tip_data": nutrition_tip_data,

                "message": (
                    "Your personalized plan "
                    "is ready."
                ),

            },

        )

    except Exception as exc:

        context = template_options()

        context["error"] = str(exc)

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context=context,

            status_code=500,

        )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

):

    try:

        # -------------------------------------------------
        # 1. Validate feedback
        # -------------------------------------------------

        request_data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback,

        )

        # -------------------------------------------------
        # 2. Find user
        # -------------------------------------------------

        user = get_user(
            request_data.user_id
        )

        if not user:

            raise ValueError(
                "User was not found."
            )

        # -------------------------------------------------
        # 3. Find workout plan
        # -------------------------------------------------

        plan = get_original_plan(
            request_data.user_id
        )

        if not plan:

            raise ValueError(
                "Workout plan was not found."
            )

        # -------------------------------------------------
        # 4. Get current plan
        # -------------------------------------------------

        current_plan = (
            plan.updated_plan
            or plan.original_plan
        )

        # -------------------------------------------------
        # 5. Update workout using Gemini
        # -------------------------------------------------

        # This makes ONE Gemini request when the
        # user submits feedback.

        updated_plan = update_workout_plan(

            user,

            current_plan,

            request_data.feedback,

        )

        # -------------------------------------------------
        # 6. Save updated plan
        # -------------------------------------------------

        update_plan(

            request_data.user_id,

            updated_plan,

            request_data.feedback,

        )

        # -------------------------------------------------
        # 7. Convert output
        # -------------------------------------------------

        workout_plan_data = parse_json(
            updated_plan
        )

        nutrition_tip_data = parse_json(
            plan.nutrition_tip
        )

        # -------------------------------------------------
        # 8. Show updated result
        # -------------------------------------------------

        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "user": user,

                "workout_plan_data": workout_plan_data,

                "nutrition_tip_data": nutrition_tip_data,

                "message": (
                    "Your plan was updated "
                    "using your feedback."
                ),

            },

        )

    except Exception as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )


# =========================================================
# ADMIN PAGE
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    token: str = "",
):
    settings = get_settings()

    # Check admin token
    if token != settings.admin_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token.",
        )

    users = get_all_users()
    plans = get_all_plans()

    plans_by_user = {}

    for plan in plans:

        # Convert original workout JSON into a Python dictionary
        original_plan_data = parse_json(
            plan.original_plan
        )

        # Convert updated workout JSON if it exists
        updated_plan_data = parse_json(
            plan.updated_plan
        )

        # Convert nutrition JSON
        nutrition_data = parse_json(
            plan.nutrition_tip
        )

        plan_data = {
            "id": plan.id,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
            "feedback": plan.feedback,
            "original_plan": original_plan_data,
            "updated_plan": updated_plan_data,
            "nutrition": nutrition_data,
        }

        plans_by_user.setdefault(
            plan.user_id,
            [],
        ).append(plan_data)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "plans_by_user": plans_by_user,
        },
    )


# =========================================================
# DELETE USER
# =========================================================

@router.post(
    "/delete-user/{user_id}",
)
def remove_user(
    user_id: str,
    token: str = "",
):
    settings = get_settings()

    # Check admin token
    if token != settings.admin_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token.",
        )

    # Delete user and all their plans
    deleted = delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # Return to admin dashboard
    return RedirectResponse(
        url=f"/view-all-users?token={token}",
        status_code=303,
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health():

    return {
        "status": "ok",
    }