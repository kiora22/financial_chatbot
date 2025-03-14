from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine


class BudgetCategory(SQLModel, table=True):
    """Model representing budget categories."""
    __tablename__ = "budget_categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    parent_category_id: Optional[int] = Field(default=None, foreign_key="budget_categories.id")
    
    # Relationships
    parent_category: Optional["BudgetCategory"] = Relationship(
        sa_relationship_kwargs={"remote_side": "BudgetCategory.id"}
    )
    child_categories: List["BudgetCategory"] = Relationship(
        back_populates="parent_category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    line_items: List["BudgetLineItem"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class BudgetLineItem(SQLModel, table=True):
    """Model representing budget line items."""
    __tablename__ = "budget_line_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="budget_categories.id")
    name: str
    amount: float
    period: str  # monthly, quarterly, annual
    fiscal_year: int
    notes: str = ""
    
    # Relationships
    category: BudgetCategory = Relationship(back_populates="line_items")
    modifications: List["BudgetModification"] = Relationship(
        back_populates="line_item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class BudgetModification(SQLModel, table=True):
    """Model representing budget modifications."""
    __tablename__ = "budget_modifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    line_item_id: int = Field(foreign_key="budget_line_items.id")
    previous_amount: float
    new_amount: float
    modification_date: datetime = Field(default_factory=datetime.now)
    user_id: str  # For simple prototype, this can be a string identifier
    justification: str
    
    # Relationships
    line_item: BudgetLineItem = Relationship(back_populates="modifications")


def init_db(db_url: str):
    """Initialize the database with the schema."""
    engine = create_engine(db_url, echo=True)
    SQLModel.metadata.create_all(engine)
    return engine