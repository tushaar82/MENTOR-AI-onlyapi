# Database Manager Script

This directory contains the database manager script for the Mentor AI Platform.

## Overview

The `database_manager.py` script provides functionality to:
- Initialize all Firestore collections with proper structure
- Delete all data from Firestore collections while preserving collection structure
- Display collection statistics
- Backup data before deletion
- Perform dry-run operations to preview changes

## Features

- **Collection Initialization**: Creates all collections defined in the database models
- **Data Deletion**: Safely deletes all data while preserving collection structure
- **Statistics**: Shows document counts and estimated sizes for all collections
- **Backup**: Optional backup of data before deletion
- **Dry Run**: Preview operations without executing them
- **Safety Features**: Confirmation prompts and environment checks
- **Batch Operations**: Efficient batch processing for large datasets

## Setup

1. Ensure you have Firebase credentials configured in your environment:
   ```bash
   export FIREBASE_CREDENTIALS_PATH="path/to/your/firebase-credentials.json"
   export FIREBASE_PROJECT_ID="your-project-id"
   ```

2. Make sure you have the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Commands

```bash
# Initialize all collections
python scripts/database_manager.py --init

# Delete all data (with confirmation)
python scripts/database_manager.py --clear

# Show collection statistics
python scripts/database_manager.py --stats

# Reset database (clear and reinitialize)
python scripts/database_manager.py --reset
```

### Advanced Commands

```bash
# Dry run to see what would be deleted
python scripts/database_manager.py --clear --dry-run

# Backup data before clearing
python scripts/database_manager.py --clear --backup

# Specify custom backup directory
python scripts/database_manager.py --clear --backup --backup-dir /path/to/backups

# Full reset with backup
python scripts/database_manager.py --reset --backup
```

## Collections Managed

The script manages the following Firestore collections:

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

## Safety Features

### Confirmation Prompts
- Requires explicit confirmation before deleting data
- Shows total document count and collection breakdown
- Requires typing "DELETE" to confirm

### Dry Run Mode
- Preview operations without executing them
- Shows what would be deleted without actually deleting
- Safe way to verify operations

### Backup Functionality
- Optional backup before deletion
- Saves data to JSON files with timestamps
- Organized by collection name

### Environment Checks
- Validates Firebase connection before operations
- Comprehensive error handling
- Detailed logging for troubleshooting

## Examples

### Development Setup
```bash
# Initialize collections for development
python scripts/database_manager.py --init

# Check collection stats
python scripts/database_manager.py --stats
```

### Testing Workflow
```bash
# Clear test data with backup
python scripts/database_manager.py --clear --backup

# Reset to clean state
python scripts/database_manager.py --reset --backup
```

### Production Safety
```bash
# Always use dry run first
python scripts/database_manager.py --clear --dry-run

# Review the output, then proceed with backup
python scripts/database_manager.py --clear --backup
```

## Output Examples

### Statistics Output
```
Collection Statistics:
================================================================================
ai_interactions:
  Documents: 1250
  Size: ~2.45 MB
parent_insights:
  Documents: 342
  Size: ~0.87 MB
================================================================================
```

### Deletion Confirmation
```
================================================================================
WARNING: This will delete ALL data from your Firestore collections!
================================================================================
Total documents to be deleted: 1592

Collection breakdown:
  - ai_interactions: 1250 documents
  - parent_insights: 342 documents
================================================================================
This action cannot be undone!

Type 'DELETE' to confirm deletion:
> DELETE
```

### Dry Run Output
```
[DRY RUN] Would delete the following:
  - ai_interactions: 1250 documents
  - parent_insights: 342 documents
```

## Troubleshooting

### Connection Issues
- Verify Firebase credentials path is correct
- Check that service account has necessary permissions
- Ensure project ID matches your Firebase project

### Permission Errors
- Make sure service account has "Firestore Data Owner" role
- Verify IAM permissions in Google Cloud Console

### Large Datasets
- Script uses batch operations (500 docs per batch)
- Monitor for rate limiting with very large datasets
- Consider running during off-peak hours

### Backup Issues
- Ensure backup directory has write permissions
- Check available disk space for large backups
- Verify backup files are created successfully

## Best Practices

1. **Always use dry run first**: Preview operations before executing
2. **Backup before deletion**: Keep copies of important data
3. **Test in development**: Verify operations in non-production environment
4. **Monitor logs**: Check output for errors and warnings
5. **Use appropriate permissions**: Service account should have minimal required permissions

## Integration with CI/CD

The script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Reset Test Database
  run: |
    python scripts/database_manager.py --reset --backup
  env:
    FIREBASE_CREDENTIALS_PATH: ${{ secrets.FIREBASE_CREDENTIALS_PATH }}
    FIREBASE_PROJECT_ID: ${{ secrets.FIREBASE_PROJECT_ID }}
```

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify Firebase configuration and permissions
3. Review the troubleshooting section above
4. Check the main project documentation