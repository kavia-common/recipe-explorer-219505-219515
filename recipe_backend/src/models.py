from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db import Base


class Category(Base):
    """Recipe category model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False, index=True)

    recipes = relationship("Recipe", back_populates="category", cascade="all,delete")


class Recipe(Base):
    """Recipe model."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    image_url = Column(Text, nullable=True)

    # Minimal JSON storage without adding new dependencies:
    # store as newline-delimited text.
    ingredients = Column(Text, nullable=False, default="")
    instructions = Column(Text, nullable=False, default="")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    category = relationship("Category", back_populates="recipes")
    favorites = relationship("Favorite", back_populates="recipe", cascade="all,delete")


class Favorite(Base):
    """Favorite mapping for a user and a recipe (no auth; demo user_id supported)."""

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)

    recipe = relationship("Recipe", back_populates="favorites")
