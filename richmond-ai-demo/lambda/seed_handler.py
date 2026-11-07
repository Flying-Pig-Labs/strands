"""
Richmond Data Seed Handler

Lambda function to populate DynamoDB with Richmond tech community sample data.
"""
import json
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Seed Richmond tech community data"""
    
    try:
        table_name = os.getenv('DYNAMODB_TABLE', 'RichmondData-dev')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Generate sample data
        sample_data = generate_richmond_data()
        
        # Insert data
        inserted_count = 0
        for item in sample_data:
            table.put_item(Item=item)
            inserted_count += 1
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': f'Successfully inserted {inserted_count} items',
                'items': inserted_count,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

def generate_richmond_data() -> list:
    """Generate Richmond tech community sample data"""
    
    data = []
    base_date = datetime.now()
    
    # Venues
    venues = [
        {
            'pk': 'VENUE#startup-virginia',
            'sk': 'INFO',
            'entity_type': 'venue',
            'name': 'Startup Virginia',
            'address': '1717 East Cary Street, Richmond, VA 23219',
            'capacity': 200,
            'amenities': ['WiFi', 'Parking', 'AV Equipment', 'Catering'],
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'VENUE#common-house',
            'sk': 'INFO',
            'entity_type': 'venue',
            'name': 'Common House RVA',
            'address': '305 S 2nd St, Richmond, VA 23204',
            'capacity': 150,
            'amenities': ['WiFi', 'Coffee', 'Meeting Rooms', 'Parking'],
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'VENUE#vcu-engineering',
            'sk': 'INFO',
            'entity_type': 'venue',
            'name': 'VCU School of Engineering',
            'address': '401 W Main St, Richmond, VA 23284',
            'capacity': 300,
            'amenities': ['WiFi', 'Parking', 'Lecture Halls', 'Labs'],
            'created_at': base_date.isoformat()
        }
    ]
    
    # Companies
    companies = [
        {
            'pk': 'COMPANY#capital-one',
            'sk': 'INFO',
            'entity_type': 'company',
            'name': 'Capital One',
            'employees': 50000,
            'tech_stack': ['AWS', 'Python', 'Java', 'React', 'Kubernetes'],
            'hiring': True,
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'COMPANY#carmax',
            'sk': 'INFO',
            'entity_type': 'company',
            'name': 'CarMax',
            'employees': 25000,
            'tech_stack': ['C#', '.NET', 'SQL Server', 'Angular', 'Azure'],
            'hiring': True,
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'COMPANY#flying-pig-labs',
            'sk': 'INFO',
            'entity_type': 'company',
            'name': 'Flying Pig Labs',
            'employees': 45,
            'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Vue.js', 'Docker'],
            'hiring': True,
            'created_at': base_date.isoformat()
        }
    ]
    
    # Meetup Groups
    groups = [
        {
            'pk': 'GROUP#rva-cloud-wranglers',
            'sk': 'INFO',
            'entity_type': 'group',
            'name': 'RVA Cloud Wranglers',
            'members': 220,
            'focus': 'AWS, Cloud Architecture, DevOps',
            'meeting_frequency': 'Monthly',
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'GROUP#richmond-python',
            'sk': 'INFO',
            'entity_type': 'group',
            'name': 'Richmond Python User Group',
            'members': 180,
            'focus': 'Python, Data Science, Web Development',
            'meeting_frequency': 'Monthly',
            'created_at': base_date.isoformat()
        },
        {
            'pk': 'GROUP#rva-js',
            'sk': 'INFO',
            'entity_type': 'group',
            'name': 'RVA.js',
            'members': 160,
            'focus': 'JavaScript, Node.js, React, Vue',
            'meeting_frequency': 'Monthly',
            'created_at': base_date.isoformat()
        }
    ]
    
    # Events
    events = []
    for i in range(12):
        event_date = base_date + timedelta(days=7*i)
        events.append({
            'pk': f'EVENT#{uuid.uuid4().hex[:8]}',
            'sk': 'INFO',
            'entity_type': 'event',
            'name': f'Tech Event {i+1}',
            'date': event_date.isoformat(),
            'venue': venues[i % len(venues)]['name'],
            'attendees': 50 + (i * 10),
            'topics': ['Cloud', 'AI/ML', 'Web Development', 'DevOps'][i % 4],
            'created_at': base_date.isoformat()
        })
    
    # Combine all data
    data.extend(venues)
    data.extend(companies)
    data.extend(groups)
    data.extend(events)
    
    return data