import os
import sys
from sqlmodel import Session, SQLModel, create_engine

# Add the parent directory to the path so we can import from our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.logging_config import setup_logging
from utils.schema import BudgetCategory, BudgetLineItem, BudgetModification

# Set up logging
logger = setup_logging("init_db")


def init_database():
    """Initialize the database with schema."""
    logger.info(f"Initializing database at {settings.sqlite_db_path}")
    
    # Ensure the directory for the database exists
    os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)
    
    # Create database engine
    engine = create_engine(settings.database_url)
    
    # Create database schema
    logger.info("Creating database schema")
    SQLModel.metadata.create_all(engine)
    
    logger.info("Database schema created successfully")
    return engine


def populate_sample_data(engine):
    """Populate the database with sample data."""
    logger.info("Populating database with sample data")
    
    with Session(engine) as session:
        # Check if we already have data
        existing_categories = session.query(BudgetCategory).first()
        if existing_categories:
            logger.info("Database already contains data, skipping sample data creation")
            return
        
        # Create budget categories
        marketing = BudgetCategory(name="Marketing", description="Marketing and advertising expenses")
        operations = BudgetCategory(name="Operations", description="Operational expenses")
        rnd = BudgetCategory(name="R&D", description="Research and development expenses")
        
        session.add(marketing)
        session.add(operations)
        session.add(rnd)
        session.commit()
        
        # Create budget line items
        line_items = [
            BudgetLineItem(
                category_id=marketing.id,
                name="Social Media Advertising",
                amount=10000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Facebook, Twitter, LinkedIn"
            ),
            BudgetLineItem(
                category_id=marketing.id,
                name="Content Production",
                amount=5000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Blog posts, videos, infographics"
            ),
            BudgetLineItem(
                category_id=operations.id,
                name="Office Rent",
                amount=8000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Main office"
            ),
            BudgetLineItem(
                category_id=operations.id,
                name="Utilities",
                amount=2000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Electricity, water, internet"
            ),
            BudgetLineItem(
                category_id=rnd.id,
                name="Software Development",
                amount=15000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Salaries and tools"
            )
        ]
        
        for item in line_items:
            session.add(item)
        
        session.commit()
        logger.info(f"Added {len(line_items)} budget line items")
        
        # Create a sample budget modification
        social_media = session.query(BudgetLineItem).filter_by(name="Social Media Advertising").first()
        
        if social_media:
            modification = BudgetModification(
                line_item_id=social_media.id,
                previous_amount=social_media.amount,
                new_amount=12000.0,
                user_id="admin",
                justification="Increased allocation due to Q1 campaign"
            )
            
            # Update the line item amount
            social_media.amount = modification.new_amount
            
            session.add(modification)
            session.commit()
            logger.info("Added sample budget modification")
    
    logger.info("Sample data created successfully")


if __name__ == "__main__":
    """Run database initialization when script is executed directly."""
    engine = init_database()
    populate_sample_data(engine)
    logger.info("Database initialization complete")