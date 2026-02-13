from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryOut(BaseModel):
    """Category response model."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")

    class Config:
        from_attributes = True


class RecipeListOut(BaseModel):
    """Recipe list response model (short form for cards)."""

    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Recipe title")
    description: str = Field(..., description="Short description")
    image_url: Optional[str] = Field(None, description="External image URL")
    category_id: int = Field(..., description="Category ID")


class RecipeDetailOut(BaseModel):
    """Recipe detail response model."""

    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Recipe title")
    description: str = Field(..., description="Short description")
    image_url: Optional[str] = Field(None, description="External image URL")
    ingredients: List[str] = Field(..., description="Ingredient list")
    instructions: str = Field(..., description="Cooking instructions")
    category_id: int = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")


class FavoriteCreateIn(BaseModel):
    """Input model to add a recipe to favorites."""

    user_id: int = Field(..., description="User ID (demo user_id=1 is supported)")
    recipe_id: int = Field(..., description="Recipe ID to favorite")


class FavoriteOut(BaseModel):
    """Favorite response model."""

    id: int = Field(..., description="Favorite row ID")
    user_id: int = Field(..., description="User ID")
    recipe_id: int = Field(..., description="Recipe ID")
    recipe_title: str = Field(..., description="Recipe title")
    recipe_image_url: Optional[str] = Field(None, description="Recipe image URL")
