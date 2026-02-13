from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Category, Recipe


def _nl(items: list[str]) -> str:
    """Store ingredients as newline-delimited text."""
    return "\n".join(items)


# PUBLIC_INTERFACE
def seed_if_empty(db: Session) -> None:
    """Seed initial categories and recipes if the database is empty."""
    existing_category = db.execute(select(Category).limit(1)).scalar_one_or_none()
    if existing_category is not None:
        return

    categories = [
        Category(name="Breakfast"),
        Category(name="Lunch"),
        Category(name="Dinner"),
        Category(name="Dessert"),
        Category(name="Drinks"),
    ]
    db.add_all(categories)
    db.flush()  # get IDs

    by_name = {c.name: c for c in categories}

    recipes = [
        Recipe(
            title="Retro Blueberry Pancakes",
            description="Fluffy pancakes with a sweet blueberry pop—Saturday morning vibes.",
            image_url="https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "1 cup flour",
                    "2 tbsp sugar",
                    "2 tsp baking powder",
                    "1 cup milk",
                    "1 egg",
                    "1 cup blueberries",
                    "Butter for pan",
                ]
            ),
            instructions=(
                "Whisk dry ingredients. Add milk and egg, mix until just combined. "
                "Fold in blueberries. Cook on a buttered skillet until golden on both sides."
            ),
            category_id=by_name["Breakfast"].id,
        ),
        Recipe(
            title="Neon Avocado Toast",
            description="Crispy toast, creamy avocado, and a zing of lime.",
            image_url="https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "2 slices sourdough",
                    "1 ripe avocado",
                    "1/2 lime",
                    "Salt + pepper",
                    "Chili flakes (optional)",
                ]
            ),
            instructions=(
                "Toast bread. Mash avocado with lime, salt, and pepper. "
                "Spread thickly and finish with chili flakes."
            ),
            category_id=by_name["Breakfast"].id,
        ),
        Recipe(
            title="Classic Diner Grilled Cheese",
            description="Golden, melty, and unapologetically nostalgic.",
            image_url="https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "2 slices bread",
                    "2 slices cheddar",
                    "1 tbsp butter",
                ]
            ),
            instructions="Butter bread, sandwich cheese, grill low and slow until crisp and gooey.",
            category_id=by_name["Lunch"].id,
        ),
        Recipe(
            title="Cosmic Tomato Soup",
            description="Smooth tomato soup with a basil swirl—pairs perfectly with grilled cheese.",
            image_url="https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "1 tbsp olive oil",
                    "1 small onion",
                    "2 cloves garlic",
                    "1 can crushed tomatoes",
                    "2 cups broth",
                    "Salt + pepper",
                    "Basil (optional)",
                ]
            ),
            instructions=(
                "Sauté onion and garlic. Add tomatoes and broth. Simmer 15 minutes, blend smooth, "
                "season to taste, garnish with basil."
            ),
            category_id=by_name["Lunch"].id,
        ),
        Recipe(
            title="Synthwave Stir-Fry",
            description="Fast, bright, and packed with crunch—weeknight hero.",
            image_url="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "2 cups mixed veggies",
                    "1 tbsp soy sauce",
                    "1 tsp honey",
                    "1 tsp sesame oil",
                    "1 clove garlic",
                    "Cooked rice to serve",
                ]
            ),
            instructions=(
                "Stir-fry veggies hot and quick. Add garlic, then soy sauce, honey, and sesame oil. "
                "Toss, serve over rice."
            ),
            category_id=by_name["Dinner"].id,
        ),
        Recipe(
            title="Arcade Brownie Squares",
            description="Fudgy brownies with crispy edges—high score dessert.",
            image_url="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "1/2 cup butter",
                    "1 cup sugar",
                    "2 eggs",
                    "1/3 cup cocoa powder",
                    "1/2 cup flour",
                    "Pinch of salt",
                ]
            ),
            instructions=(
                "Mix melted butter + sugar. Beat in eggs. Fold in cocoa, flour, salt. "
                "Bake at 175°C / 350°F for ~20-25 minutes."
            ),
            category_id=by_name["Dessert"].id,
        ),
        Recipe(
            title="Minty Pixel Milkshake",
            description="Cool mint shake with chocolate chip crunch.",
            image_url="https://images.unsplash.com/photo-1589733955941-5eeaf752f6dd?auto=format&fit=crop&w=1200&q=60",
            ingredients=_nl(
                [
                    "2 cups vanilla ice cream",
                    "3/4 cup milk",
                    "1/2 tsp peppermint extract",
                    "Chocolate chips",
                ]
            ),
            instructions="Blend ice cream, milk, and peppermint. Stir in chips. Serve cold.",
            category_id=by_name["Drinks"].id,
        ),
    ]

    db.add_all(recipes)
    db.commit()
