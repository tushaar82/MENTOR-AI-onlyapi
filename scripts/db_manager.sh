#!/bin/bash

# Database Manager Helper Script
# This script provides convenient shortcuts for common database operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "database_manager.py" ]]; then
    print_error "database_manager.py not found in current directory"
    print_error "Please run this script from scripts directory"
    exit 1
fi

# Set environment variable for Firebase credentials path if not set
if [[ -z "$FIREBASE_CREDENTIALS_PATH" ]]; then
    export FIREBASE_CREDENTIALS_PATH="../config/firebase-credentials.json"
fi

if [[ -z "$FIREBASE_PROJECT_ID" ]]; then
    export FIREBASE_PROJECT_ID="mentor-ai-test"
fi

# Show usage
show_usage() {
    print_header "Database Manager Helper"
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  init       Initialize all Firestore collections"
    echo "  clear      Delete all data from collections"
    echo "  stats      Show collection statistics"
    echo "  reset      Clear and reinitialize collections"
    echo "  backup     Backup all collections to JSON files"
    echo ""
    echo "Options:"
    echo "  --dry-run  Preview actions without executing"
    echo "  --backup   Create backup before deletion"
    echo ""
    echo "Examples:"
    echo "  $0 init                    # Initialize collections"
    echo "  $0 clear                    # Delete all data"
    echo "  $0 clear --dry-run          # Preview deletion"
    echo "  $0 clear --backup            # Delete with backup"
    echo "  $0 reset --backup            # Reset with backup"
    echo "  $0 stats                    # Show statistics"
}

# Main script logic
case "${1:-}" in
    "init")
        print_status "Initializing Firestore collections..."
        python3 database_manager.py --init
        ;;
    "clear")
        if [[ "${2:-}" == "--dry-run" ]]; then
            print_warning "Dry run mode - no data will be deleted"
            python3 database_manager.py --clear --dry-run
        elif [[ "${2:-}" == "--backup" ]]; then
            print_status "Creating backup before clearing data..."
            python3 database_manager.py --clear --backup
        else
            print_warning "This will delete ALL data from Firestore collections!"
            read -p "Are you sure you want to continue? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                python3 database_manager.py --clear
            else
                print_status "Operation cancelled by user"
            fi
        fi
        ;;
    "stats")
        print_status "Getting collection statistics..."
        python3 database_manager.py --stats
        ;;
    "reset")
        if [[ "${2:-}" == "--backup" ]]; then
            print_status "Creating backup before resetting database..."
            python3 database_manager.py --reset --backup
        else
            print_warning "This will delete ALL data and reinitialize collections!"
            read -p "Are you sure you want to continue? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                python3 database_manager.py --reset
            else
                print_status "Operation cancelled by user"
            fi
        fi
        ;;
    "backup")
        print_status "Creating backup of all collections..."
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        for collection in ai_interactions parent_insights engagement_metrics communication_history intervention_alerts prediction_results communication_suggestions engagement_challenges achievements parent_resources resource_usage; do
            print_status "Backing up $collection..."
            python3 database_manager.py --stats > /tmp/stats.json
            python3 -c "
import asyncio
import sys
sys.path.append('.')
from database_manager import DatabaseManager

async def backup_single_collection(collection_name, backup_dir):
    db_manager = DatabaseManager()
    await db_manager.connect()
    await db_manager.backup_collection(collection_name, f'{backup_dir}/{collection_name}.json')
    await db_manager.disconnect()

asyncio.run(backup_single_collection('$collection', '$BACKUP_DIR'))
" &
        done
        
        wait
        print_status "Backup completed: $BACKUP_DIR"
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac