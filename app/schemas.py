from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight_loss",
    "muscle_gain",
    "general_wellness",
    "flexibility",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=100,
    )

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=400,
    )

    goal: Goal

    intensity: Intensity

    @field_validator(
        "username",
        "user_id",
    )
    @classmethod
    def strip_text(cls, value):

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be blank"
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=100,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )


class WorkoutDay(BaseModel):

    day: str

    focus: str

    warm_up: str

    exercises: list[str]

    cooldown: str

    recovery_tip: str


class WorkoutPlan(BaseModel):

    title: str

    safety_note: str

    days: list[WorkoutDay]


class NutritionTip(BaseModel):

    tip: str

    hydration: str

    recovery: str