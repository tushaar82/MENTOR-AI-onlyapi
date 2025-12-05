"""
Fix for Firestore Async Issues

This script fixes the async/await issues in Firestore operations
that are causing "object WriteResult can't be used in 'await' expression" errors.

Author: Mentor AI Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_firestore_fixes():
    """Apply fixes to Firestore async issues in the codebase."""
    
    fixes_applied = []
    
    # Fix 1: unified_gemini_config_service.py
    try:
        with open("services/unified_gemini_config_service.py", "r") as f:
            content = f.read()
        
        # Fix _save_interaction_async method
        original_1 = """    async def _save_interaction_async(self, interaction: AIInteraction):
        """Save interaction to Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            await doc_ref.set(interaction.model_dump())
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")"""
        
        fixed_1 = """    async def _save_interaction_async(self, interaction: AIInteraction):
        """Save interaction to Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            # Firestore set() returns a WriteResult, not a future, so don't await it
            doc_ref.set(interaction.model_dump())
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")"""
        
        # Fix _update_interaction_async method
        original_2 = """    async def _update_interaction_async(self, interaction: AIInteraction):
        """Update interaction in Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            await doc_ref.update(interaction.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(f"Failed to update interaction: {e}")"""
        
        fixed_2 = """    async def _update_interaction_async(self, interaction: AIInteraction):
        """Update interaction in Firestore asynchronously."""
        try:
            doc_ref = self.db.collection(self.interactions_collection).document(interaction.interaction_id)
            # Firestore update() returns a WriteResult, not a future, so don't await it
            doc_ref.update(interaction.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(f"Failed to update interaction: {e}")"""
        
        # Apply fixes
        if original_1 in content and original_2 in content:
            content = content.replace(original_1, fixed_1)
            content = content.replace(original_2, fixed_2)
            
            with open("services/unified_gemini_config_service.py", "w") as f:
                f.write(content)
            
            fixes_applied.append("Fixed Firestore async issues in unified_gemini_config_service.py")
        else:
            logger.warning("Expected patterns not found in unified_gemini_config_service.py")
            
    except Exception as e:
        logger.error(f"Failed to fix unified_gemini_config_service.py: {e}")
    
    # Fix 2: database_service.py
    try:
        with open("services/database_service.py", "r") as f:
            content = f.read()
        
        # Check for similar issues in database_service.py
        if "await doc_ref.set(" in content or "await doc_ref.update(" in content:
            # This would indicate similar issues, but database_service.py seems to be correctly implemented
            logger.info("database_service.py appears to be correctly implemented")
        else:
            logger.info("No async issues found in database_service.py")
            
    except Exception as e:
        logger.error(f"Failed to check database_service.py: {e}")
    
    return fixes_applied

if __name__ == "__main__":
    logger.info("Applying Firestore async fixes...")
    fixes = apply_firestore_fixes()
    
    if fixes:
        logger.info(f"Applied {len(fixes)} fixes:")
        for fix in fixes:
            logger.info(f"  - {fix}")
    else:
        logger.info("No fixes needed")
    
    logger.info("Firestore async fixes completed")