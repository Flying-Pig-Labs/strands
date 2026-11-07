"""
Database models and operations for Richmond Tech Community demo.
Handles DynamoDB interactions for venues, companies, meetups, and events.
"""

import boto3
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from dataclasses import dataclass, asdict
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger(__name__)


class DynamoDBManager:
    """Manages DynamoDB operations for the Richmond tech demo."""
    
    def __init__(self, table_name: str = "RichmondTechCommunity", region: str = "us-east-1"):
        """Initialize DynamoDB connection."""
        self.table_name = table_name
        self.region = region
        
        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        
        # Initialize DynamoDB client for table operations
        self.client = boto3.client('dynamodb', region_name=region)
    
    def create_table_if_not_exists(self):
        """Create the DynamoDB table if it doesn't exist."""
        try:
            # Check if table exists
            self.table.load()
            logger.info(f"Table {self.table_name} already exists")
            return True
            
        except self.client.exceptions.ResourceNotFoundException:
            logger.info(f"Creating table {self.table_name}")
            
            # Create table with composite key structure
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'PK', 'KeyType': 'HASH'},    # Partition Key
                    {'AttributeName': 'SK', 'KeyType': 'RANGE'}   # Sort Key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'PK', 'AttributeType': 'S'},
                    {'AttributeName': 'SK', 'AttributeType': 'S'},
                    {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                    {'AttributeName': 'GSI1SK', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'GSI1',
                        'KeySchema': [
                            {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                            {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'RichmondTechDemo'},
                    {'Key': 'Environment', 'Value': 'demo'}
                ]
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            logger.info(f"Table {self.table_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return False
    
    def _convert_floats_to_decimal(self, obj: Any) -> Any:
        """Convert float values to Decimal for DynamoDB compatibility."""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    def _convert_decimal_to_float(self, obj: Any) -> Any:
        """Convert Decimal values back to float for JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        return obj
    
    def put_venue(self, venue_data: Dict[str, Any]) -> bool:
        """Store venue data in DynamoDB."""
        try:
            item = self._convert_floats_to_decimal(venue_data.copy())
            item.update({
                'PK': f"VENUE#{venue_data['id']}",
                'SK': f"VENUE#{venue_data['id']}",
                'GSI1PK': 'VENUE',
                'GSI1SK': venue_data['name'],
                'EntityType': 'venue',
                'CreatedAt': datetime.utcnow().isoformat(),
                'UpdatedAt': datetime.utcnow().isoformat()
            })
            
            self.table.put_item(Item=item)
            logger.info(f"Stored venue: {venue_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing venue {venue_data['id']}: {e}")
            return False
    
    def put_company(self, company_data: Dict[str, Any]) -> bool:
        """Store company data in DynamoDB."""
        try:
            item = self._convert_floats_to_decimal(company_data.copy())
            item.update({
                'PK': f"COMPANY#{company_data['id']}",
                'SK': f"COMPANY#{company_data['id']}",
                'GSI1PK': 'COMPANY',
                'GSI1SK': company_data['name'],
                'EntityType': 'company',
                'CreatedAt': datetime.utcnow().isoformat(),
                'UpdatedAt': datetime.utcnow().isoformat()
            })
            
            self.table.put_item(Item=item)
            logger.info(f"Stored company: {company_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing company {company_data['id']}: {e}")
            return False
    
    def put_meetup(self, meetup_data: Dict[str, Any]) -> bool:
        """Store meetup group data in DynamoDB."""
        try:
            item = self._convert_floats_to_decimal(meetup_data.copy())
            item.update({
                'PK': f"MEETUP#{meetup_data['id']}",
                'SK': f"MEETUP#{meetup_data['id']}",
                'GSI1PK': 'MEETUP',
                'GSI1SK': meetup_data['name'],
                'EntityType': 'meetup',
                'CreatedAt': datetime.utcnow().isoformat(),
                'UpdatedAt': datetime.utcnow().isoformat()
            })
            
            self.table.put_item(Item=item)
            logger.info(f"Stored meetup: {meetup_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing meetup {meetup_data['id']}: {e}")
            return False
    
    def put_event(self, event_data: Dict[str, Any]) -> bool:
        """Store event data in DynamoDB."""
        try:
            item = self._convert_floats_to_decimal(event_data.copy())
            event_date = event_data['date'][:10]  # YYYY-MM-DD format
            
            item.update({
                'PK': f"EVENT#{event_data['id']}",
                'SK': f"EVENT#{event_data['id']}",
                'GSI1PK': f"EVENT#{event_date}",
                'GSI1SK': event_data['start_time'],
                'EntityType': 'event',
                'CreatedAt': datetime.utcnow().isoformat(),
                'UpdatedAt': datetime.utcnow().isoformat()
            })
            
            self.table.put_item(Item=item)
            logger.info(f"Stored event: {event_data['title']} on {event_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing event {event_data['id']}: {e}")
            return False
    
    def get_venue(self, venue_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific venue by ID."""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"VENUE#{venue_id}",
                    'SK': f"VENUE#{venue_id}"
                }
            )
            
            if 'Item' in response:
                return self._convert_decimal_to_float(response['Item'])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving venue {venue_id}: {e}")
            return None
    
    def get_all_venues(self) -> List[Dict[str, Any]]:
        """Retrieve all venues."""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq('VENUE')
            )
            
            venues = [self._convert_decimal_to_float(item) for item in response['Items']]
            logger.info(f"Retrieved {len(venues)} venues")
            return venues
            
        except Exception as e:
            logger.error(f"Error retrieving venues: {e}")
            return []
    
    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Retrieve all companies."""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq('COMPANY')
            )
            
            companies = [self._convert_decimal_to_float(item) for item in response['Items']]
            logger.info(f"Retrieved {len(companies)} companies")
            return companies
            
        except Exception as e:
            logger.error(f"Error retrieving companies: {e}")
            return []
    
    def get_all_meetups(self) -> List[Dict[str, Any]]:
        """Retrieve all meetup groups."""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq('MEETUP')
            )
            
            meetups = [self._convert_decimal_to_float(item) for item in response['Items']]
            logger.info(f"Retrieved {len(meetups)} meetups")
            return meetups
            
        except Exception as e:
            logger.error(f"Error retrieving meetups: {e}")
            return []
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Retrieve upcoming events within specified days."""
        try:
            events = []
            current_date = datetime.now()
            
            # Query events for each day in the range
            for i in range(days_ahead):
                query_date = (current_date + timedelta(days=i)).strftime('%Y-%m-%d')
                
                response = self.table.query(
                    IndexName='GSI1',
                    KeyConditionExpression=Key('GSI1PK').eq(f'EVENT#{query_date}')
                )
                
                day_events = [self._convert_decimal_to_float(item) for item in response['Items']]
                events.extend(day_events)
            
            # Sort by date and time
            events.sort(key=lambda x: (x['date'], x['start_time']))
            logger.info(f"Retrieved {len(events)} upcoming events")
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving upcoming events: {e}")
            return []
    
    def get_events_by_meetup(self, meetup_id: str) -> List[Dict[str, Any]]:
        """Retrieve all events for a specific meetup group."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('meetup_id').eq(meetup_id) & Attr('EntityType').eq('event')
            )
            
            events = [self._convert_decimal_to_float(item) for item in response['Items']]
            events.sort(key=lambda x: (x['date'], x['start_time']))
            logger.info(f"Retrieved {len(events)} events for meetup {meetup_id}")
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events for meetup {meetup_id}: {e}")
            return []
    
    def search_events(self, query: str) -> List[Dict[str, Any]]:
        """Search events by title, description, or tags."""
        try:
            response = self.table.scan(
                FilterExpression=Attr('EntityType').eq('event') & (
                    Attr('title').contains(query) |
                    Attr('description').contains(query) |
                    Attr('tags').contains(query)
                )
            )
            
            events = [self._convert_decimal_to_float(item) for item in response['Items']]
            events.sort(key=lambda x: (x['date'], x['start_time']))
            logger.info(f"Found {len(events)} events matching '{query}'")
            return events
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    def get_next_meetup_event(self, meetup_name: str = None) -> Optional[Dict[str, Any]]:
        """Get the next upcoming event, optionally filtered by meetup name."""
        try:
            current_datetime = datetime.now()
            upcoming_events = self.get_upcoming_events(days_ahead=90)
            
            # Filter by meetup name if provided
            if meetup_name:
                upcoming_events = [
                    event for event in upcoming_events 
                    if meetup_name.lower() in event.get('meetup_name', '').lower()
                ]
            
            # Filter to only future events
            future_events = []
            for event in upcoming_events:
                event_datetime = datetime.fromisoformat(event['date'])
                if event_datetime.date() >= current_datetime.date():
                    future_events.append(event)
            
            if future_events:
                return future_events[0]  # Return the next event
            return None
            
        except Exception as e:
            logger.error(f"Error getting next meetup event: {e}")
            return None
    
    def bulk_load_data(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """Bulk load all data into DynamoDB."""
        results = {'venues': 0, 'companies': 0, 'meetups': 0, 'events': 0}
        
        try:
            # Load venues
            for venue in data.get('venues', []):
                if self.put_venue(venue):
                    results['venues'] += 1
            
            # Load companies
            for company in data.get('companies', []):
                if self.put_company(company):
                    results['companies'] += 1
            
            # Load meetups
            for meetup in data.get('meetups', []):
                if self.put_meetup(meetup):
                    results['meetups'] += 1
            
            # Load events
            for event in data.get('events', []):
                if self.put_event(event):
                    results['events'] += 1
            
            logger.info(f"Bulk load completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error during bulk load: {e}")
            return results
    
    def clear_all_data(self) -> bool:
        """Clear all data from the table (for testing/reset)."""
        try:
            # Scan all items
            response = self.table.scan()
            items = response['Items']
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            
            # Delete all items
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={'PK': item['PK'], 'SK': item['SK']})
            
            logger.info(f"Cleared {len(items)} items from table")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False


# Utility functions for common queries
def find_tech_meetups_in_richmond(db_manager: DynamoDBManager) -> List[Dict[str, Any]]:
    """Find all tech meetups in Richmond area."""
    return db_manager.get_all_meetups()


def get_next_richmond_tech_event(db_manager: DynamoDBManager) -> Optional[Dict[str, Any]]:
    """Get the next tech event happening in Richmond."""
    return db_manager.get_next_meetup_event()


def search_events_by_technology(db_manager: DynamoDBManager, technology: str) -> List[Dict[str, Any]]:
    """Search for events related to a specific technology."""
    return db_manager.search_events(technology)


def get_venue_info(db_manager: DynamoDBManager, venue_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific venue."""
    venues = db_manager.get_all_venues()
    for venue in venues:
        if venue_name.lower() in venue['name'].lower():
            return venue
    return None


if __name__ == "__main__":
    # Example usage and testing
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database manager
    db = DynamoDBManager()
    
    # Create table if needed
    if db.create_table_if_not_exists():
        print("Database initialized successfully")
    
    # Load sample data
    from data.sample_data import RichmondDataGenerator
    generator = RichmondDataGenerator()
    sample_data = generator.get_all_data()
    
    # Bulk load data
    results = db.bulk_load_data(sample_data)
    print(f"Loaded data: {results}")
    
    # Test queries
    print("\nNext tech event:", get_next_richmond_tech_event(db))
    print("\nJavaScript events:", search_events_by_technology(db, "JavaScript"))
    print("\nCommon House venue:", get_venue_info(db, "Common House"))