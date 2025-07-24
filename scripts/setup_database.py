#!/usr/bin/env python3
"""
Database setup script for Richmond Tech Community demo.
Creates DynamoDB table and loads sample data.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from data.sample_data import RichmondDataGenerator
from models.database import DynamoDBManager


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('database_setup.log')
        ]
    )


def create_table(db_manager: DynamoDBManager, force: bool = False) -> bool:
    """Create the DynamoDB table."""
    logger = logging.getLogger(__name__)
    
    if force:
        logger.info("Force flag set - clearing existing data")
        db_manager.clear_all_data()
    
    success = db_manager.create_table_if_not_exists()
    if success:
        logger.info("✅ DynamoDB table created/verified successfully")
    else:
        logger.error("❌ Failed to create DynamoDB table")
    
    return success


def load_sample_data(db_manager: DynamoDBManager, regenerate: bool = False) -> dict:
    """Load sample data into DynamoDB."""
    logger = logging.getLogger(__name__)
    
    # Generate sample data
    logger.info("Generating Richmond tech community sample data...")
    generator = RichmondDataGenerator()
    
    if regenerate:
        logger.info("Regenerating fresh sample data")
    
    sample_data = generator.get_all_data()
    
    # Log data summary
    logger.info("Generated sample data:")
    for category, items in sample_data.items():
        logger.info(f"  {category.title()}: {len(items)} items")
    
    # Load data into DynamoDB
    logger.info("Loading data into DynamoDB...")
    results = db_manager.bulk_load_data(sample_data)
    
    # Log results
    total_loaded = sum(results.values())
    total_expected = sum(len(items) for items in sample_data.values())
    
    if total_loaded == total_expected:
        logger.info(f"✅ Successfully loaded all {total_loaded} items")
    else:
        logger.warning(f"⚠️  Loaded {total_loaded}/{total_expected} items")
    
    for category, count in results.items():
        expected = len(sample_data[category])
        status = "✅" if count == expected else "❌"
        logger.info(f"  {status} {category.title()}: {count}/{expected}")
    
    return results


def verify_data(db_manager: DynamoDBManager) -> bool:
    """Verify that data was loaded correctly."""
    logger = logging.getLogger(__name__)
    
    logger.info("Verifying loaded data...")
    
    try:
        # Test basic queries
        venues = db_manager.get_all_venues()
        companies = db_manager.get_all_companies()
        meetups = db_manager.get_all_meetups()
        events = db_manager.get_upcoming_events(days_ahead=90)
        
        logger.info(f"Verification results:")
        logger.info(f"  Venues: {len(venues)}")
        logger.info(f"  Companies: {len(companies)}")
        logger.info(f"  Meetups: {len(meetups)}")
        logger.info(f"  Events: {len(events)}")
        
        # Test specific queries
        next_event = db_manager.get_next_meetup_event()
        if next_event:
            logger.info(f"  Next event: {next_event['title']} on {next_event['date'][:10]}")
        else:
            logger.warning("  No upcoming events found")
        
        # Test search functionality
        js_events = db_manager.search_events("JavaScript")
        logger.info(f"  JavaScript events: {len(js_events)}")
        
        # Test venue lookup
        startup_va_events = [e for e in events if e.get('venue_name') == 'Startup Virginia']
        logger.info(f"  Events at Startup Virginia: {len(startup_va_events)}")
        
        if all([venues, companies, meetups, events]):
            logger.info("✅ Data verification passed")
            return True
        else:
            logger.error("❌ Data verification failed - some collections are empty")
            return False
            
    except Exception as e:
        logger.error(f"❌ Data verification failed with error: {e}")
        return False


def show_sample_queries(db_manager: DynamoDBManager):
    """Demonstrate sample queries for the demo."""
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "="*50)
    logger.info("SAMPLE QUERIES FOR DEMO")
    logger.info("="*50)
    
    # Next tech meetup
    next_event = db_manager.get_next_meetup_event()
    if next_event:
        logger.info(f"\n🎯 DEMO QUERY: 'What's the next tech meetup in Richmond?'")
        logger.info(f"   Answer: {next_event['title']}")
        logger.info(f"   Date: {next_event['date'][:10]} at {next_event['start_time']}")
        logger.info(f"   Venue: {next_event['venue_name']}")
        logger.info(f"   Address: {next_event['venue_address']}")
    
    # Cloud events
    cloud_events = db_manager.search_events("cloud")
    if cloud_events:
        logger.info(f"\n☁️  DEMO QUERY: 'Are there any cloud computing events?'")
        for event in cloud_events[:2]:  # Show first 2
            logger.info(f"   - {event['title']} on {event['date'][:10]}")
    
    # Python events
    python_events = db_manager.search_events("Python")
    if python_events:
        logger.info(f"\n🐍 DEMO QUERY: 'When is the next Python meetup?'")
        for event in python_events[:1]:  # Show first 1
            logger.info(f"   - {event['title']} on {event['date'][:10]} at {event['venue_name']}")
    
    # Venue info
    venues = db_manager.get_all_venues()
    startup_va = next((v for v in venues if v['name'] == 'Startup Virginia'), None)
    if startup_va:
        logger.info(f"\n🏢 DEMO QUERY: 'Tell me about Startup Virginia'")
        logger.info(f"   Address: {startup_va['address']}")
        logger.info(f"   Capacity: {startup_va['capacity']} people")
        logger.info(f"   Amenities: {', '.join(startup_va['amenities'])}")
    
    # Companies
    companies = db_manager.get_all_companies()
    carmax = next((c for c in companies if c['name'] == 'CarMax'), None)
    if carmax:
        logger.info(f"\n🚗 DEMO QUERY: 'What tech companies are in Richmond?'")
        logger.info(f"   CarMax: {carmax['industry']}, {carmax['employee_count']:,} employees")
        logger.info(f"   Tech Stack: {', '.join(carmax['tech_stack'][:3])}...")
    
    logger.info("\n" + "="*50)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup Richmond Tech Community database')
    parser.add_argument('--table-name', default='RichmondTechCommunity', 
                       help='DynamoDB table name')
    parser.add_argument('--region', default='us-east-1', 
                       help='AWS region')
    parser.add_argument('--force', action='store_true', 
                       help='Force recreate table and clear existing data')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--skip-data', action='store_true', 
                       help='Skip loading sample data')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify existing data')
    parser.add_argument('--show-queries', action='store_true', 
                       help='Show sample demo queries')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Richmond Tech Community database setup")
    logger.info(f"Table: {args.table_name}, Region: {args.region}")
    
    # Initialize database manager
    try:
        db_manager = DynamoDBManager(table_name=args.table_name, region=args.region)
        logger.info("✅ Connected to DynamoDB")
    except Exception as e:
        logger.error(f"❌ Failed to connect to DynamoDB: {e}")
        return 1
    
    # Verify only mode
    if args.verify_only:
        success = verify_data(db_manager)
        if args.show_queries:
            show_sample_queries(db_manager)
        return 0 if success else 1
    
    # Create table
    if not create_table(db_manager, force=args.force):
        return 1
    
    # Load sample data (unless skipped)
    if not args.skip_data:
        results = load_sample_data(db_manager, regenerate=args.force)
        
        # Verify the loaded data
        if not verify_data(db_manager):
            logger.warning("Data verification failed, but continuing...")
    
    # Show sample queries
    if args.show_queries:
        show_sample_queries(db_manager)
    
    logger.info("✅ Database setup completed successfully!")
    logger.info("\nTo test the database, you can run:")
    logger.info("  python scripts/setup_database.py --verify-only --show-queries")
    logger.info("\nThe database is now ready for the Richmond Tech Community demo!")
    
    return 0


if __name__ == "__main__":
    exit(main())