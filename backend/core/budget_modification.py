from typing import Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from datetime import datetime

from config.logging_config import setup_logging
from utils.schema import BudgetCategory, BudgetLineItem, BudgetModification

# Set up logging
logger = setup_logging("budget_modification")


class BudgetModificationEngine:
    """Engine for handling budget modifications."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize the budget modification engine."""
        self.db_session = db_session
        logger.info("Budget modification engine initialized")
    
    async def apply_modification(
        self,
        parsed_request: Dict[str, Any],
        user_id: str
    ) -> Tuple[bool, str, Optional[BudgetModification]]:
        """
        Apply a budget modification based on the parsed request.
        
        Args:
            parsed_request: The parsed budget modification request
            user_id: The ID of the user making the modification
            
        Returns:
            A tuple containing:
            - Success flag (bool)
            - Message (str)
            - The created BudgetModification object if successful, None otherwise
        """
        try:
            logger.info(f"Applying budget modification for request: {parsed_request}")
            
            # For Phase 1, we'll mock the modification process
            # In later phases, this will actually modify the database
            
            # Mock successful modification
            mock_modification = BudgetModification(
                id=1,
                line_item_id=1,
                previous_amount=10000.0,
                new_amount=11000.0,
                modification_date=datetime.now(),
                user_id=user_id,
                justification=parsed_request.get("justification", "No justification provided")
            )
            
            logger.info(f"Successfully applied budget modification")
            return True, "Budget modified successfully", mock_modification
        
        except Exception as e:
            logger.error(f"Error applying budget modification: {str(e)}")
            return False, f"Error applying budget modification: {str(e)}", None
    
    async def validate_modification(
        self,
        parsed_request: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate a budget modification request.
        
        Args:
            parsed_request: The parsed budget modification request
            
        Returns:
            A tuple containing:
            - Validity flag (bool)
            - Validation message (str)
        """
        try:
            logger.info(f"Validating budget modification request: {parsed_request}")
            
            # Extract request details
            action = parsed_request.get("action")
            category = parsed_request.get("category")
            line_item = parsed_request.get("line_item")
            amount = parsed_request.get("amount")
            percent = parsed_request.get("percent")
            
            # Check for required fields
            if not action:
                return False, "Missing action (increase, decrease, or set)"
            
            if not category and not line_item:
                return False, "Missing budget category or line item to modify"
            
            if not amount and not percent:
                return False, "Missing amount or percentage for modification"
            
            # For Phase 1, we'll assume all validated requests are valid
            # In later phases, this will perform more thorough validation
            
            logger.info("Budget modification request is valid")
            return True, "Modification request is valid"
        
        except Exception as e:
            logger.error(f"Error validating budget modification: {str(e)}")
            return False, f"Error validating budget modification: {str(e)}"
    
    async def get_modification_history(
        self,
        line_item_id: int
    ) -> list:
        """
        Get the modification history for a line item.
        
        Args:
            line_item_id: The ID of the line item
            
        Returns:
            A list of BudgetModification objects
        """
        try:
            logger.info(f"Retrieving modification history for line item {line_item_id}")
            
            # For Phase 1, we'll return mock data
            # In later phases, this will retrieve from the database
            
            # Mock modifications history
            mock_modifications = [
                {
                    "id": 1,
                    "line_item_id": line_item_id,
                    "previous_amount": 10000.0,
                    "new_amount": 12000.0,
                    "modification_date": datetime(2025, 1, 15),
                    "user_id": "user123",
                    "justification": "Increased allocation due to Q1 campaign"
                },
                {
                    "id": 2,
                    "line_item_id": line_item_id,
                    "previous_amount": 12000.0,
                    "new_amount": 11000.0,
                    "modification_date": datetime(2025, 2, 10),
                    "user_id": "user123",
                    "justification": "Adjusted based on performance metrics"
                }
            ]
            
            logger.info(f"Retrieved {len(mock_modifications)} modifications for line item {line_item_id}")
            return mock_modifications
        
        except Exception as e:
            logger.error(f"Error retrieving modification history: {str(e)}")
            return []


# Create a singleton instance
budget_modification_engine = BudgetModificationEngine()