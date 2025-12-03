# Database Manager Script Plan

## Overview
This document outlines the plan for creating a database manager script that will:
1. Initialize all Firestore collections with proper structure
2. Delete all data from Firestore collections while preserving collection structure for testing purposes

## Script Structure

### File: `scripts/database_manager.py`

### Imports
```python
import os
import sys
import asyncio
import argparse
import logging
from typing import Dict, List, Any
from datetime import datetime

# Firebase imports
from firebase_admin import firestore
from google.cloud import firestore_v1

# Project imports
from utils.firebase_config import initialize_firebase, get_firestore_client
from models.database_models import DATABASE_SCHEMAS
```

### Main Components

#### 1. Database Connection Setup
- Initialize Firebase connection using existing `firebase_config.py`
- Get Firestore client instance
- Handle connection errors gracefully

#### 2. Collection Management Functions

##### `initialize_collections()`
- Create all collections defined in `DATABASE_SCHEMAS`
- Set up proper indexes based on schema definitions
- Log initialization status for each collection
- Handle collection creation errors

##### `delete_all_data()`
- Iterate through all collections in `DATABASE_SCHEMAS`
- Delete all documents from each collection
- Preserve collection structure and indexes
- Provide progress feedback during deletion
- Handle batch operations for efficiency

##### `get_collection_stats()`
- Get document count for each collection
- Display statistics before and after operations
- Help verify operations completed successfully

#### 3. Command Line Interface
- Use `argparse` for command-line arguments
- Support different operation modes:
  - `init`: Initialize collections
  - `clear`: Delete all data
  - `stats`: Show collection statistics
  - `reset`: Clear and reinitialize (default)

#### 4. Safety Features
- Confirmation prompts before destructive operations
- Dry-run mode to preview actions
- Backup option before clearing data
- Environment checks (require confirmation for production)

#### 5. Error Handling & Logging
- Comprehensive error handling for all operations
- Detailed logging with timestamps
- Progress indicators for long-running operations
- Rollback capabilities for failed operations

## Implementation Details

### Collections to Manage
Based on `DATABASE_SCHEMAS`, the script will handle these collections:

1. `ai_interactions` - AI interaction records
2. `parent_insights` - Parent insights and recommendations
3. `engagement_metrics` - Student engagement metrics
4. `communication_history` - Communication records
5. `intervention_alerts` - Intervention alerts
6. `prediction_results` - Predictive analytics results
7. `communication_suggestions` - AI-powered communication suggestions
8. `engagement_challenges` - Gamified engagement challenges
9. `achievements` - Parent and student achievements
10. `parent_resources` - AI-curated parent resources
11. `resource_usage` - Resource usage tracking

### Deletion Strategy
- Use batch operations for efficiency (max 500 operations per batch)
- Process collections in dependency order (child collections first)
- Track deleted documents for verification
- Handle rate limiting and retry logic

### Initialization Strategy
- Create collections if they don't exist
- Set up composite indexes as defined in schemas
- Create sample documents for structure validation (optional)
- Verify collection creation with test queries

## Usage Examples

```bash
# Initialize all collections
python scripts/database_manager.py --init

# Delete all data (with confirmation)
python scripts/database_manager.py --clear

# Show collection statistics
python scripts/database_manager.py --stats

# Reset database (clear and reinitialize)
python scripts/database_manager.py --reset

# Dry run to see what would be deleted
python scripts/database_manager.py --clear --dry-run

# Backup before clearing
python scripts/database_manager.py --clear --backup
```

## Environment Variables Required
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON
- `FIREBASE_PROJECT_ID`: Firebase project ID
- Optional: `ENVIRONMENT` to detect production vs development

## Safety Considerations
1. Always require explicit confirmation for data deletion
2. Implement dry-run mode to preview changes
3. Add production environment checks
4. Provide backup functionality
5. Log all operations for audit trail

## Testing Strategy
1. Test with mock Firebase emulator first
2. Verify collection creation and deletion
3. Test error handling scenarios
4. Validate batch operation efficiency
5. Test command-line interface thoroughly

## Next Steps
1. Implement the script based on this plan
2. Test with development environment
3. Add comprehensive error handling
4. Create documentation and usage examples
5. Add to CI/CD pipeline for automated testing