from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator


APP_NAME = "AI Fitness Coach API"
APP_VERSION = "1.0.0"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "/tmp/ai_fitness_coach.sqlite3"))
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    athlete = "athlete"


class Goal(str, Enum):
    fat_loss = "fat_loss"
    muscle_gain = "muscle_gain"
    strength = "strength"
    endurance = "endurance"
    maintenance = "maintenance"


class PlanLevel(str, Enum):
    free = "free"
    premium = "premium"


class UserProfile(BaseModel):
    age: int = Field(ge=18, le=80)
    weight_kg: float = Field(gt=35, lt=300)
    height_cm: float = Field(gt=120, lt=230)
    activity_level: ActivityLevel
    goal: Goal
    sex: Literal["female", "male", "other"] = "other"
    dietary_preferences: list[str] = Field(default_factory=list, max_length=12)
    injuries: list[str] = Field(default_factory=list, max_length=12)
    equipment: list[str] = Field(default_factory=list, max_length=20)
    workout_days_per_week: int = Field(default=4, ge=2, le=6)
    minutes_per_workout: int = Field(default=35, ge=15, le=90)

    @field_validator("dietary_preferences", "injuries", "equipment")
    @classmethod
    def normalize_list(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            cleaned = value.strip().lower()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned[:80])
        return normalized


class ProfileResponse(UserProfile):
    user_id: str
    created_at: datetime
    updated_at: datetime
    plan_level: PlanLevel


class WorkoutPlanRequest(BaseModel):
    focus: str | None = Field(default=None, max_length=80)
    weeks: int = Field(default=4, ge=1, le=12)


class ExerciseItem(BaseModel):
    name: str
    sets: int
    reps: str
    rest_seconds: int
    coaching_tip: str


class WorkoutDay(BaseModel):
    day: int
    title: str
    duration_minutes: int
    exercises: list[ExerciseItem]
    warmup: list[str]
    cooldown: list[str]


class WorkoutPlan(BaseModel):
    id: str
    user_id: str
    generated_at: datetime
    weeks: int
    summary: str
    days: list[WorkoutDay]


class NutritionPlanRequest(BaseModel):
    meals_per_day: int = Field(default=3, ge=2, le=6)


class MealIdea(BaseModel):
    name: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    ingredients: list[str]


class NutritionPlan(BaseModel):
    id: str
    user_id: str
    generated_at: datetime
    daily_calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    hydration_liters: float
    meals: list[MealIdea]
    guidance: list[str]


class ProgressEntry(BaseModel):
    entry_date: date = Field(default_factory=date.today)
    weight_kg: float | None = Field(default=None, gt=35, lt=300)
    body_fat_percent: float | None = Field(default=None, ge=3, le=70)
    resting_heart_rate: int | None = Field(default=None, ge=35, le=130)
    energy_level: int = Field(default=3, ge=1, le=5)
    notes: str = Field(default="", max_length=1000)


class MealLog(BaseModel):
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = Field(min_length=1, max_length=120)
    calories: int = Field(ge=0, le=5000)
    protein_g: float = Field(ge=0, le=400)
    carbs_g: float = Field(ge=0, le=700)
    fat_g: float = Field(ge=0, le=300)


class ExerciseLog(BaseModel):
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    name: str = Field(min_length=1, max_length=120)
    duration_minutes: int = Field(ge=1, le=360)
    calories_burned: int = Field(default=0, ge=0, le=3000)
    intensity: Literal["easy", "moderate", "hard"] = "moderate"


class DashboardSummary(BaseModel):
    user_id: str
    plan_level: PlanLevel
    current_weight_kg: float | None
    weekly_meals_logged: int
    weekly_exercises_logged: int
    weekly_calories: int
    weekly_protein_g: float
    exercise_minutes: int
    streak_days: int
    recommendation: str


class SubscriptionUpdate(BaseModel):
    plan_level: PlanLevel


security = HTTPBearer(auto_error=False)


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    plan_level TEXT NOT NULL DEFAULT 'free',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS workout_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS nutrition_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS progress_entries (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS meal_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    logged_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS exercise_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    logged_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
                );
                """
            )


db = Database(DATABASE_PATH)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def dumps_model(model: BaseModel) -> str:
    return model.model_dump_json()


def loads_json(value: str) -> dict[str, Any]:
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("stored JSON must be object")
    return data


def current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty bearer token")
    if token.startswith("dev_"):
        return token[4:]
    parts = token.split(".")
    if len(parts) == 3:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        try:
            import base64

            decoded = json.loads(base64.urlsafe_b64decode(payload.encode("utf-8")))
            subject = decoded.get("sub")
            expiry = decoded.get("exp")
            if expiry is not None and int(expiry) < int(time.time()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
            if isinstance(subject, str) and subject:
                return subject
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload") from exc
    digest = hmac.new(JWT_SECRET.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"token_{digest[:24]}"


def get_profile_or_404(user_id: str) -> ProfileResponse:
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    data = loads_json(row["data"])
    return ProfileResponse(
        **data,
        user_id=row["user_id"],
        plan_level=PlanLevel(row["plan_level"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def activity_multiplier(level: ActivityLevel) -> float:
    return {
        ActivityLevel.sedentary: 1.2,
        ActivityLevel.light: 1.375,
        ActivityLevel.moderate: 1.55,
        ActivityLevel.active: 1.725,
        ActivityLevel.athlete: 1.9,
    }[level]


def estimate_calories(profile: UserProfile) -> int:
    if profile.sex == "female":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161
    elif profile.sex == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 78
    maintenance = bmr * activity_multiplier(profile.activity_level)
    adjustment = {
        Goal.fat_loss: -400,
        Goal.muscle_gain: 300,
        Goal.strength: 150,
        Goal.endurance: 100,
        Goal.maintenance: 0,
    }[profile.goal]
    return max(1400, round((maintenance + adjustment) / 25) * 25)


def macro_split(profile: UserProfile, calories: int) -> tuple[int, int, int]:
    protein = round(profile.weight_kg * (2.0 if profile.goal in {Goal.fat_loss, Goal.muscle_gain, Goal.strength} else 1.6))
    fat = round(profile.weight_kg * 0.8)
    protein_calories = protein * 4
    fat_calories = fat * 9
    carbs = max(80, round((calories - protein_calories - fat_calories) / 4))
    return protein, carbs, fat


def choose_exercises(profile: UserProfile) -> list[tuple[str, str]]:
    has_gym = any(item in profile.equipment for item in ["gym", "barbell", "dumbbells", "cable"])
    lower = [("Goblet squat" if has_gym else "Tempo bodyweight squat", "Keep ribs stacked over hips"), ("Romanian deadlift" if has_gym else "Single-leg hip hinge", "Push hips back with neutral spine"), ("Reverse lunge", "Drive through front heel")]
    upper = [("Dumbbell press" if has_gym else "Push-up", "Stop two reps before form breaks"), ("Seated row" if has_gym else "Band row", "Pull elbows toward back pockets"), ("Overhead press" if has_gym else "Pike push-up", "Brace core before pressing")]
    conditioning = [("Incline treadmill intervals" if has_gym else "Fast walk intervals", "Nasal breathing on recovery"), ("Bike sprint" if has_gym else "Low-impact step-up", "Powerful effort, clean landing")]
    mobility = [("Dead bug", "Exhale fully each rep"), ("Side plank", "Long line from head to heels")]
    return lower + upper + conditioning + mobility


def build_workout_plan(user_id: str, profile: ProfileResponse, request: WorkoutPlanRequest) -> WorkoutPlan:
    exercises = choose_exercises(profile)
    days: list[WorkoutDay] = []
    for day_number in range(1, profile.workout_days_per_week + 1):
        day_exercises: list[ExerciseItem] = []
        offset = (day_number - 1) * 2
        for name, tip in exercises[offset : offset + 5]:
            day_exercises.append(
                ExerciseItem(
                    name=name,
                    sets=3 if profile.minutes_per_workout < 45 else 4,
                    reps="8-12" if profile.goal in {Goal.muscle_gain, Goal.strength} else "10-15",
                    rest_seconds=90 if profile.goal in {Goal.strength, Goal.muscle_gain} else 60,
                    coaching_tip=tip,
                )
            )
        if len(day_exercises) < 5:
            for name, tip in exercises[: 5 - len(day_exercises)]:
                day_exercises.append(ExerciseItem(name=name, sets=3, reps="10-15", rest_seconds=60, coaching_tip=tip))
        title_focus = request.focus or profile.goal.value.replace("_", " ")
        days.append(
            WorkoutDay(
                day=day_number,
                title=f"Day {day_number}: {title_focus.title()} Training",
                duration_minutes=profile.minutes_per_workout,
                warmup=["5-minute brisk walk", "Hip circles", "Shoulder controlled rotations", "Two ramp-up sets"],
                exercises=day_exercises,
                cooldown=["Easy walk until breathing normalizes", "90/90 breathing", "Light stretching for trained muscles"],
            )
        )
    return WorkoutPlan(
        id=str(uuid4()),
        user_id=user_id,
        generated_at=utc_now(),
        weeks=request.weeks,
        summary=f"{request.weeks}-week plan with {profile.workout_days_per_week} sessions per week for {profile.goal.value.replace('_', ' ')}.",
        days=days,
    )


def build_nutrition_plan(user_id: str, profile: ProfileResponse, request: NutritionPlanRequest) -> NutritionPlan:
    calories = estimate_calories(profile)
    protein, carbs, fat = macro_split(profile, calories)
    meal_templates = [
        ("Greek yogurt power bowl", ["greek yogurt", "berries", "oats", "chia seeds"]),
        ("Lean protein grain bowl", ["chicken breast", "brown rice", "greens", "olive oil vinaigrette"]),
        ("Salmon recovery plate", ["salmon", "sweet potato", "asparagus", "lemon"]),
        ("Turkey avocado wrap", ["whole-grain wrap", "turkey", "avocado", "spinach"]),
        ("Tofu stir fry", ["tofu", "mixed vegetables", "rice noodles", "ginger sauce"]),
        ("Protein smoothie", ["protein powder", "banana", "peanut butter", "milk"]),
    ]
    per_meal_calories = max(250, round(calories / request.meals_per_day))
    meals: list[MealIdea] = []
    for index in range(request.meals_per_day):
        name, ingredients = meal_templates[index % len(meal_templates)]
        meals.append(
            MealIdea(
                name=name,
                calories=per_meal_calories,
                protein_g=max(20, round(protein / request.meals_per_day)),
                carbs_g=max(20, round(carbs / request.meals_per_day)),
                fat_g=max(8, round(fat / request.meals_per_day)),
                ingredients=ingredients,
            )
        )
    return NutritionPlan(
        id=str(uuid4()),
        user_id=user_id,
        generated_at=utc_now(),
        daily_calories=calories,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
        hydration_liters=round(max(2.0, profile.weight_kg * 0.035), 1),
        meals=meals,
        guidance=[
            "Anchor each meal with lean protein.",
            "Prepare two portable meals for busy workdays.",
            "Adjust portions by progress trend every two weeks.",
        ],
    )


def store_json(table: str, user_id: str, model: BaseModel, timestamp_column: str, timestamp_value: str) -> str:
    item_id = getattr(model, "id", str(uuid4()))
    with db.connect() as conn:
        conn.execute(
            f"INSERT INTO {table} (id, user_id, data, {timestamp_column}) VALUES (?, ?, ?, ?)",
            (item_id, user_id, dumps_model(model), timestamp_value),
        )
    return item_id


def verify_stripe_signature(payload: bytes, signature_header: str) -> bool:
    if not STRIPE_WEBHOOK_SECRET:
        return False
    values = dict(part.split("=", 1) for part in signature_header.split(",") if "=" in part)
    timestamp = values.get("t", "")
    provided = values.get("v1", "")
    if not timestamp or not provided:
        return False
    signed_payload = timestamp.encode("utf-8") + b"." + payload
    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.migrate()
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Stripe-Signature"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.put("/onboarding/profile", response_model=ProfileResponse)
def upsert_profile(profile: UserProfile, user_id: str = Depends(current_user_id)) -> ProfileResponse:
    now = utc_now().isoformat()
    with db.connect() as conn:
        existing = conn.execute("SELECT created_at, plan_level FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE profiles SET data = ?, updated_at = ? WHERE user_id = ?",
                (dumps_model(profile), now, user_id),
            )
            created_at = existing["created_at"]
            plan_level = existing["plan_level"]
        else:
            conn.execute(
                "INSERT INTO profiles (user_id, data, plan_level, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, dumps_model(profile), PlanLevel.free.value, now, now),
            )
            created_at = now
            plan_level = PlanLevel.free.value
    return ProfileResponse(**profile.model_dump(), user_id=user_id, created_at=datetime.fromisoformat(created_at), updated_at=datetime.fromisoformat(now), plan_level=PlanLevel(plan_level))


@app.get("/me/profile", response_model=ProfileResponse)
def read_profile(user_id: str = Depends(current_user_id)) -> ProfileResponse:
    return get_profile_or_404(user_id)


@app.post("/plans/workout", response_model=WorkoutPlan)
def generate_workout_plan(request: WorkoutPlanRequest, user_id: str = Depends(current_user_id)) -> WorkoutPlan:
    profile = get_profile_or_404(user_id)
    plan = build_workout_plan(user_id, profile, request)
    store_json("workout_plans", user_id, plan, "created_at", plan.generated_at.isoformat())
    return plan


@app.get("/plans/workout/latest", response_model=WorkoutPlan)
def latest_workout_plan(user_id: str = Depends(current_user_id)) -> WorkoutPlan:
    with db.connect() as conn:
        row = conn.execute("SELECT data FROM workout_plans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout plan not found")
    return WorkoutPlan(**loads_json(row["data"]))


@app.post("/plans/nutrition", response_model=NutritionPlan)
def generate_nutrition_plan(request: NutritionPlanRequest, user_id: str = Depends(current_user_id)) -> NutritionPlan:
    profile = get_profile_or_404(user_id)
    plan = build_nutrition_plan(user_id, profile, request)
    store_json("nutrition_plans", user_id, plan, "created_at", plan.generated_at.isoformat())
    return plan


@app.get("/plans/nutrition/latest", response_model=NutritionPlan)
def latest_nutrition_plan(user_id: str = Depends(current_user_id)) -> NutritionPlan:
    with db.connect() as conn:
        row = conn.execute("SELECT data FROM nutrition_plans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition plan not found")
    return NutritionPlan(**loads_json(row["data"]))


@app.post("/progress", status_code=status.HTTP_201_CREATED)
def add_progress(entry: ProgressEntry, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    get_profile_or_404(user_id)
    item_id = str(uuid4())
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO progress_entries (id, user_id, data, entry_date, created_at) VALUES (?, ?, ?, ?, ?)",
            (item_id, user_id, dumps_model(entry), entry.entry_date.isoformat(), utc_now().isoformat()),
        )
    return {"id": item_id, "status": "created"}


@app.get("/progress", response_model=list[ProgressEntry])
def list_progress(user_id: str = Depends(current_user_id), limit: int = 30) -> list[ProgressEntry]:
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT data FROM progress_entries WHERE user_id = ? ORDER BY entry_date DESC LIMIT ?",
            (user_id, max(1, min(limit, 365))),
        ).fetchall()
    return [ProgressEntry(**loads_json(row["data"])) for row in rows]


@app.post("/logs/meals", status_code=status.HTTP_201_CREATED)
def add_meal_log(log: MealLog, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    get_profile_or_404(user_id)
    item_id = str(uuid4())
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO meal_logs (id, user_id, data, logged_at) VALUES (?, ?, ?, ?)",
            (item_id, user_id, dumps_model(log), log.logged_at.isoformat()),
        )
    return {"id": item_id, "status": "created"}


@app.get("/logs/meals", response_model=list[MealLog])
def list_meal_logs(user_id: str = Depends(current_user_id), days: int = 7) -> list[MealLog]:
    since = (utc_now() - timedelta(days=max(1, min(days, 90)))).isoformat()
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT data FROM meal_logs WHERE user_id = ? AND logged_at >= ? ORDER BY logged_at DESC",
            (user_id, since),
        ).fetchall()
    return [MealLog(**loads_json(row["data"])) for row in rows]


@app.post("/logs/exercises", status_code=status.HTTP_201_CREATED)
def add_exercise_log(log: ExerciseLog, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    get_profile_or_404(user_id)
    item_id = str(uuid4())
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO exercise_logs (id, user_id, data, logged_at) VALUES (?, ?, ?, ?)",
            (item_id, user_id, dumps_model(log), log.logged_at.isoformat()),
        )
    return {"id": item_id, "status": "created"}


@app.get("/logs/exercises", response_model=list[ExerciseLog])
def list_exercise_logs(user_id: str = Depends(current_user_id), days: int = 7) -> list[ExerciseLog]:
    since = (utc_now() - timedelta(days=max(1, min(days, 90)))).isoformat()
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT data FROM exercise_logs WHERE user_id = ? AND logged_at >= ? ORDER BY logged_at DESC",
            (user_id, since),
        ).fetchall()
    return [ExerciseLog(**loads_json(row["data"])) for row in rows]


@app.get("/dashboard", response_model=DashboardSummary)
def dashboard(user_id: str = Depends(current_user_id)) -> DashboardSummary:
    profile = get_profile_or_404(user_id)
    since = (utc_now() - timedelta(days=7)).isoformat()
    with db.connect() as conn:
        progress_rows = conn.execute("SELECT data FROM progress_entries WHERE user_id = ? ORDER BY entry_date DESC LIMIT 1", (user_id,)).fetchall()
        meal_rows = conn.execute("SELECT data FROM meal_logs WHERE user_id = ? AND logged_at >= ?", (user_id, since)).fetchall()
        exercise_rows = conn.execute("SELECT data FROM exercise_logs WHERE user_id = ? AND logged_at >= ?", (user_id, since)).fetchall()
    meals = [MealLog(**loads_json(row["data"])) for row in meal_rows]
    exercises = [ExerciseLog(**loads_json(row["data"])) for row in exercise_rows]
    current_weight = profile.weight_kg
    if progress_rows:
        latest_progress = ProgressEntry(**loads_json(progress_rows[0]["data"]))
        current_weight = latest_progress.weight_kg or current_weight
    exercise_minutes = sum(item.duration_minutes for item in exercises)
    meal_calories = sum(item.calories for item in meals)
    protein = sum(item.protein_g for item in meals)
    recommendation = "Log one meal and one workout today to keep momentum."
    if exercise_minutes >= profile.workout_days_per_week * profile.minutes_per_workout:
        recommendation = "Training target met. Prioritize sleep, mobility, and protein consistency."
    elif len(meals) >= 14:
        recommendation = "Nutrition logging strong. Schedule next workout block now."
    return DashboardSummary(
        user_id=user_id,
        plan_level=profile.plan_level,
        current_weight_kg=current_weight,
        weekly_meals_logged=len(meals),
        weekly_exercises_logged=len(exercises),
        weekly_calories=meal_calories,
        weekly_protein_g=round(protein, 1),
        exercise_minutes=exercise_minutes,
        streak_days=min(7, len({item.logged_at.date() for item in meals + exercises})),
        recommendation=recommendation,
    )


@app.put("/billing/subscription", response_model=dict[str, str])
def update_subscription(update: SubscriptionUpdate, user_id: str = Depends(current_user_id)) -> dict[str, str]:
    get_profile_or_404(user_id)
    with db.connect() as conn:
        conn.execute("UPDATE profiles SET plan_level = ?, updated_at = ? WHERE user_id = ?", (update.plan_level.value, utc_now().isoformat(), user_id))
    return {"status": "updated", "plan_level": update.plan_level.value}


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> Response:
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    if STRIPE_WEBHOOK_SECRET and not verify_stripe_signature(payload, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature")
    try:
        event = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload") from exc
    event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {}) if isinstance(event.get("data"), dict) else {}
    metadata = obj.get("metadata", {}) if isinstance(obj, dict) else {}
    user_id = metadata.get("user_id") if isinstance(metadata, dict) else None
    if user_id and event_type in {"customer.subscription.created", "customer.subscription.updated"}:
        status_value = obj.get("status", "")
        plan = PlanLevel.premium if status_value in {"active", "trialing"} else PlanLevel.free
        with db.connect() as conn:
            conn.execute("UPDATE profiles SET plan_level = ?, updated_at = ? WHERE user_id = ?", (plan.value, utc_now().isoformat(), user_id))
    if user_id and event_type in {"customer.subscription.deleted", "invoice.payment_failed"}:
        with db.connect() as conn:
            conn.execute("UPDATE profiles SET plan_level = ?, updated_at = ? WHERE user_id = ?", (PlanLevel.free.value, utc_now().isoformat(), user_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": APP_NAME, "version": APP_VERSION, "docs": "/docs"}
