from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from config.logging_config import setup_logging
from backend.core.llm_processor import llm_processor
from backend.core.budget_modification import budget_modification_engine

# Set up logging
logger = setup_logging("budget_router")

# Create router
router = APIRouter()


class BudgetCategoryCreate(BaseModel):
    """Model for creating budget categories."""
    name: str
    description: str = ""
    parent_category_id: Optional[int] = None


class BudgetCategoryResponse(BaseModel):
    """Model for budget category responses."""
    id: int
    name: str
    description: str
    parent_category_id: Optional[int] = None


class BudgetLineItemCreate(BaseModel):
    """Model for creating budget line items."""
    category_id: int
    name: str
    amount: float
    period: str  # monthly, quarterly, annual
    fiscal_year: int
    notes: str = ""


class BudgetLineItemResponse(BaseModel):
    """Model for budget line item responses."""
    id: int
    category_id: int
    name: str
    amount: float
    period: str
    fiscal_year: int
    notes: str


class BudgetModificationCreate(BaseModel):
    """Model for creating budget modifications."""
    line_item_id: int
    new_amount: float
    user_id: str
    justification: str


class BudgetModificationResponse(BaseModel):
    """Model for budget modification responses."""
    id: int
    line_item_id: int
    previous_amount: float
    new_amount: float
    modification_date: datetime
    user_id: str
    justification: str


@router.get("/categories", response_model=List[BudgetCategoryResponse])
async def get_budget_categories():
    """Get all budget categories."""
    try:
        logger.info("Retrieving all budget categories")
        
        # For now, return mock data
        # In later phases, this will retrieve from the database
        mock_categories = [
            BudgetCategoryResponse(
                id=1,
                name="Marketing",
                description="Marketing and advertising expenses",
                parent_category_id=None
            ),
            BudgetCategoryResponse(
                id=2,
                name="Operations",
                description="Operational expenses",
                parent_category_id=None
            ),
            BudgetCategoryResponse(
                id=3,
                name="R&D",
                description="Research and development expenses",
                parent_category_id=None
            ),
            BudgetCategoryResponse(
                id=4,
                name="Social Media Ads",
                description="Social media advertising expenses",
                parent_category_id=1
            )
        ]
        
        return mock_categories
    except Exception as e:
        logger.error(f"Error retrieving budget categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving budget categories: {str(e)}")


@router.post("/categories", response_model=BudgetCategoryResponse)
async def create_budget_category(category: BudgetCategoryCreate):
    """Create a new budget category."""
    try:
        logger.info(f"Creating new budget category: {category.name}")
        
        # For now, return mock data
        # In later phases, this will create in the database
        mock_category = BudgetCategoryResponse(
            id=5,  # Mock ID
            name=category.name,
            description=category.description,
            parent_category_id=category.parent_category_id
        )
        
        return mock_category
    except Exception as e:
        logger.error(f"Error creating budget category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating budget category: {str(e)}")


@router.get("/line-items", response_model=List[BudgetLineItemResponse])
async def get_budget_line_items(category_id: Optional[int] = None):
    """Get budget line items, optionally filtered by category."""
    try:
        logger.info(f"Retrieving budget line items, category_id filter: {category_id}")
        
        # For now, return mock data
        # In later phases, this will retrieve from the database
        mock_line_items = [
            BudgetLineItemResponse(
                id=1,
                category_id=1,
                name="Social Media Advertising",
                amount=10000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Facebook, Twitter, LinkedIn"
            ),
            BudgetLineItemResponse(
                id=2,
                category_id=1,
                name="Content Production",
                amount=5000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Blog posts, videos, infographics"
            ),
            BudgetLineItemResponse(
                id=3,
                category_id=2,
                name="Office Rent",
                amount=8000.0,
                period="monthly",
                fiscal_year=2025,
                notes="Main office"
            )
        ]
        
        # Filter by category if provided
        if category_id is not None:
            mock_line_items = [item for item in mock_line_items if item.category_id == category_id]
        
        return mock_line_items
    except Exception as e:
        logger.error(f"Error retrieving budget line items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving budget line items: {str(e)}")


@router.post("/line-items", response_model=BudgetLineItemResponse)
async def create_budget_line_item(line_item: BudgetLineItemCreate):
    """Create a new budget line item."""
    try:
        logger.info(f"Creating new budget line item: {line_item.name}")
        
        # For now, return mock data
        # In later phases, this will create in the database
        mock_line_item = BudgetLineItemResponse(
            id=4,  # Mock ID
            category_id=line_item.category_id,
            name=line_item.name,
            amount=line_item.amount,
            period=line_item.period,
            fiscal_year=line_item.fiscal_year,
            notes=line_item.notes
        )
        
        return mock_line_item
    except Exception as e:
        logger.error(f"Error creating budget line item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating budget line item: {str(e)}")


class NaturalLanguageModification(BaseModel):
    """Model for natural language budget modification requests."""
    text: str
    user_id: str


@router.post("/modifications", response_model=BudgetModificationResponse)
async def create_budget_modification(modification: BudgetModificationCreate):
    """Create a new budget modification."""
    try:
        logger.info(f"Creating budget modification for line item: {modification.line_item_id}")
        
        # Validate the modification
        valid, message = await budget_modification_engine.validate_modification({
            "line_item_id": modification.line_item_id,
            "new_amount": modification.new_amount,
            "justification": modification.justification
        })
        
        if not valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Apply the modification
        success, message, modification_obj = await budget_modification_engine.apply_modification(
            parsed_request={
                "line_item_id": modification.line_item_id,
                "new_amount": modification.new_amount,
                "justification": modification.justification
            },
            user_id=modification.user_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Convert to response model
        response = BudgetModificationResponse(
            id=modification_obj.id,
            line_item_id=modification_obj.line_item_id,
            previous_amount=modification_obj.previous_amount,
            new_amount=modification_obj.new_amount,
            modification_date=modification_obj.modification_date,
            user_id=modification_obj.user_id,
            justification=modification_obj.justification
        )
        
        return response
    except Exception as e:
        logger.error(f"Error creating budget modification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating budget modification: {str(e)}")


@router.post("/modifications/natural-language", response_model=BudgetModificationResponse)
async def create_budget_modification_nl(request: NaturalLanguageModification):
    """Create a budget modification from natural language request."""
    try:
        logger.info(f"Processing natural language budget modification request")
        
        # Parse the natural language request
        parsed_request = await llm_processor.parse_budget_modification(request.text)
        logger.info(f"Parsed request: {parsed_request}")
        
        # Extract necessary information
        category_name = parsed_request.get("category")
        line_item_name = parsed_request.get("line_item")
        action = parsed_request.get("action")
        amount = parsed_request.get("amount")
        percent = parsed_request.get("percent")
        justification = parsed_request.get("justification", "No justification provided")
        
        # For now, mock finding the line item ID based on name
        # In later phases, this would look up the actual line item from the database
        line_item_id = 1  # Mock ID
        current_amount = 10000.0  # Mock current amount
        
        # Calculate new amount based on action
        new_amount = current_amount
        if action == "increase" and amount is not None:
            new_amount = current_amount + amount
        elif action == "decrease" and amount is not None:
            new_amount = current_amount - amount
        elif action == "set" and amount is not None:
            new_amount = amount
        elif action == "increase" and percent is not None:
            new_amount = current_amount * (1 + percent / 100)
        elif action == "decrease" and percent is not None:
            new_amount = current_amount * (1 - percent / 100)
        
        # Apply the modification
        success, message, modification_obj = await budget_modification_engine.apply_modification(
            parsed_request={
                "line_item_id": line_item_id,
                "new_amount": new_amount,
                "justification": justification,
                "action": action,
                "category": category_name,
                "line_item": line_item_name
            },
            user_id=request.user_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Convert to response model
        response = BudgetModificationResponse(
            id=modification_obj.id,
            line_item_id=modification_obj.line_item_id,
            previous_amount=modification_obj.previous_amount,
            new_amount=modification_obj.new_amount,
            modification_date=modification_obj.modification_date,
            user_id=modification_obj.user_id,
            justification=modification_obj.justification
        )
        
        return response
    except Exception as e:
        logger.error(f"Error creating natural language budget modification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing natural language budget request: {str(e)}")


@router.get("/modifications/{line_item_id}", response_model=List[BudgetModificationResponse])
async def get_budget_modifications(line_item_id: int):
    """Get modification history for a budget line item."""
    try:
        logger.info(f"Retrieving modification history for line item: {line_item_id}")
        
        # For now, return mock data
        # In later phases, this will retrieve from the database
        mock_modifications = [
            BudgetModificationResponse(
                id=1,
                line_item_id=line_item_id,
                previous_amount=10000.0,
                new_amount=12000.0,
                modification_date=datetime(2025, 1, 15),
                user_id="user123",
                justification="Increased allocation due to Q1 campaign"
            ),
            BudgetModificationResponse(
                id=2,
                line_item_id=line_item_id,
                previous_amount=12000.0,
                new_amount=11000.0,
                modification_date=datetime(2025, 2, 10),
                user_id="user123",
                justification="Adjusted based on performance metrics"
            )
        ]
        
        return mock_modifications
    except Exception as e:
        logger.error(f"Error retrieving budget modifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving budget modifications: {str(e)}")