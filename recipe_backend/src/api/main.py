from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db import Base, engine, get_db_session
from src.models import Category, Favorite, Recipe
from src.schemas import (
    CategoryOut,
    FavoriteCreateIn,
    FavoriteOut,
    RecipeDetailOut,
    RecipeListOut,
)
from src.seed import seed_if_empty

openapi_tags = [
    {"name": "Health", "description": "Service health checks."},
    {"name": "Categories", "description": "Recipe categories."},
    {"name": "Recipes", "description": "Recipe browsing, searching, and details."},
    {"name": "Favorites", "description": "Demo favorites (no auth; user_id=1 supported)."},
]

app = FastAPI(
    title="Recipe Explorer API",
    description=(
        "Backend for the Recipe Explorer app. Provides categories, recipe browsing/search, "
        "and demo-user favorites.\n\n"
        "Notes:\n"
        "- No authentication is implemented; use user_id=1 for favorites.\n"
        "- Recipes include external image URLs."
    ),
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Allow local frontend dev and preview environments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _db_dep():
    """FastAPI dependency wrapper for db session context manager."""
    with get_db_session() as db:
        yield db


@app.on_event("startup")
def _on_startup() -> None:
    """Create tables (if needed) and seed initial data."""
    Base.metadata.create_all(bind=engine)
    with get_db_session() as db:
        seed_if_empty(db)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns a simple health payload if the service is running.",
    operation_id="get_health",
)
def health_check():
    """Health check endpoint for uptime and basic connectivity."""
    return {"status": "ok"}


@app.get(
    "/categories",
    response_model=List[CategoryOut],
    tags=["Categories"],
    summary="List categories",
    description="Returns all recipe categories.",
    operation_id="list_categories",
)
def list_categories(db: Session = Depends(_db_dep)) -> List[CategoryOut]:
    """List all categories."""
    cats = db.execute(select(Category).order_by(Category.name.asc())).scalars().all()
    return cats


def _ingredients_text(recipe: Recipe) -> str:
    return recipe.ingredients or ""


def _recipe_matches_q(recipe: Recipe, q: str) -> bool:
    ql = q.lower()
    return ql in (recipe.title or "").lower() or ql in _ingredients_text(recipe).lower()


@app.get(
    "/recipes",
    response_model=List[RecipeListOut],
    tags=["Recipes"],
    summary="List recipes",
    description=(
        "List recipes with optional filtering.\n\n"
        "Query params:\n"
        "- category_id: filter by category\n"
        "- q: search by title or ingredient substring"
    ),
    operation_id="list_recipes",
)
def list_recipes(
    category_id: Optional[int] = Query(None, description="Filter recipes by category_id"),
    q: Optional[str] = Query(None, description="Search by title/ingredients substring"),
    db: Session = Depends(_db_dep),
) -> List[RecipeListOut]:
    """List recipes, optionally filtered by category and search query."""
    stmt = select(Recipe)
    if category_id is not None:
        stmt = stmt.where(Recipe.category_id == category_id)

    # Minimal search implementation: title LIKE or ingredients LIKE
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Recipe.title.ilike(like), Recipe.ingredients.ilike(like)))

    recipes = db.execute(stmt.order_by(Recipe.id.asc())).scalars().all()

    return [
        RecipeListOut(
            id=r.id,
            title=r.title,
            description=r.description,
            image_url=r.image_url,
            category_id=r.category_id,
        )
        for r in recipes
    ]


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetailOut,
    tags=["Recipes"],
    summary="Get recipe details",
    description="Returns the full recipe details including ingredients and instructions.",
    operation_id="get_recipe",
)
def get_recipe(recipe_id: int, db: Session = Depends(_db_dep)) -> RecipeDetailOut:
    """Fetch a recipe by ID."""
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    category = db.get(Category, recipe.category_id)
    ingredients = [line.strip() for line in (recipe.ingredients or "").splitlines() if line.strip()]

    return RecipeDetailOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        image_url=recipe.image_url,
        ingredients=ingredients,
        instructions=recipe.instructions,
        category_id=recipe.category_id,
        category_name=category.name if category else "",
    )


@app.post(
    "/favorites",
    response_model=FavoriteOut,
    tags=["Favorites"],
    summary="Add favorite",
    description="Add a recipe to a user's favorites. No auth; use demo user_id=1.",
    operation_id="add_favorite",
)
def add_favorite(payload: FavoriteCreateIn, db: Session = Depends(_db_dep)) -> FavoriteOut:
    """Create a favorite mapping for (user_id, recipe_id)."""
    recipe = db.get(Recipe, payload.recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    fav = Favorite(user_id=payload.user_id, recipe_id=payload.recipe_id)
    db.add(fav)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Already favorited
        existing = db.execute(
            select(Favorite).where(
                Favorite.user_id == payload.user_id, Favorite.recipe_id == payload.recipe_id
            )
        ).scalar_one_or_none()
        if existing:
            return FavoriteOut(
                id=existing.id,
                user_id=existing.user_id,
                recipe_id=existing.recipe_id,
                recipe_title=recipe.title,
                recipe_image_url=recipe.image_url,
            )
        raise

    db.refresh(fav)
    return FavoriteOut(
        id=fav.id,
        user_id=fav.user_id,
        recipe_id=fav.recipe_id,
        recipe_title=recipe.title,
        recipe_image_url=recipe.image_url,
    )


@app.get(
    "/favorites",
    response_model=List[FavoriteOut],
    tags=["Favorites"],
    summary="List favorites",
    description="List favorites for a user (e.g. /favorites?user_id=1).",
    operation_id="list_favorites",
)
def list_favorites(
    user_id: int = Query(..., description="User ID to list favorites for (demo user_id=1)"),
    db: Session = Depends(_db_dep),
) -> List[FavoriteOut]:
    """List favorites for a given user."""
    stmt = (
        select(Favorite, Recipe)
        .join(Recipe, Recipe.id == Favorite.recipe_id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
    )
    rows = db.execute(stmt).all()

    return [
        FavoriteOut(
            id=f.id,
            user_id=f.user_id,
            recipe_id=f.recipe_id,
            recipe_title=r.title,
            recipe_image_url=r.image_url,
        )
        for (f, r) in rows
    ]
