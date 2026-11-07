"""
Sample Data Loader for Richmond AI Agent Demo

This module loads sample Richmond-specific data into DynamoDB
for the AI agent to query and use in responses.
"""

import json
import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_sample_data() -> List[Dict[str, Any]]:
    """Generate sample Richmond data for the demo"""
    
    # Current date for generating future events
    now = datetime.now()
    
    sample_data = [
        # Tech Meetups
        {
            'id': str(uuid.uuid4()),
            'type': 'meetup',
            'name': 'RVA Cloud Wranglers',
            'description': 'Monthly meetup for cloud computing enthusiasts in Richmond',
            'date': (now + timedelta(days=7)).isoformat(),
            'venue': 'Common House',
            'address': '230 W Main St, Richmond, VA 23220',
            'capacity': 50,
            'topic': 'AWS Serverless Architecture Best Practices',
            'organizer': 'Richmond Tech Collective',
            'tags': ['aws', 'cloud', 'serverless', 'tech']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'meetup',
            'name': 'Richmond Python User Group',
            'description': 'Monthly Python meetup for developers of all skill levels',
            'date': (now + timedelta(days=14)).isoformat(),
            'venue': 'Startup Virginia',
            'address': '1717 E Cary St, Richmond, VA 23223',
            'capacity': 75,
            'topic': 'Building AI Applications with Python',
            'organizer': 'RVA Python Developers',
            'tags': ['python', 'programming', 'ai', 'development']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'meetup',
            'name': 'Data Science RVA',
            'description': 'Richmond area data science and analytics community',
            'date': (now + timedelta(days=21)).isoformat(),
            'venue': 'VCU Innovation Gateway',
            'address': '737 N 5th St, Richmond, VA 23219',
            'capacity': 60,
            'topic': 'Machine Learning for Business Intelligence',
            'organizer': 'Richmond Data Scientists',
            'tags': ['data-science', 'machine-learning', 'analytics', 'business']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'meetup',
            'name': 'RVA DevOps',
            'description': 'DevOps practices, tools, and culture in Richmond',
            'date': (now + timedelta(days=28)).isoformat(),
            'venue': 'Capital One Labs',
            'address': '15070 Capital One Dr, Richmond, VA 23238',
            'capacity': 40,
            'topic': 'Infrastructure as Code with Terraform',
            'organizer': 'Richmond DevOps Community',
            'tags': ['devops', 'infrastructure', 'terraform', 'automation']
        },
        
        # Companies
        {
            'id': str(uuid.uuid4()),
            'type': 'company',
            'name': 'Capital One',
            'industry': 'Financial Services',
            'description': 'Digital banking and financial services company with major Richmond presence',
            'employees': 50000,
            'founded': 1994,
            'headquarters': 'McLean, VA',
            'richmond_office': '15070 Capital One Dr, Richmond, VA 23238',
            'tech_focus': ['fintech', 'cloud', 'data-science', 'mobile'],
            'notable_projects': ['Capital One Mobile App', 'Eno Virtual Assistant', 'Capital One Shopping']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'company',
            'name': 'CarMax',
            'industry': 'Automotive Retail',
            'description': 'Fortune 500 used car retailer headquartered in Richmond',
            'employees': 30000,
            'founded': 1993,
            'headquarters': '12800 Tuckahoe Creek Pkwy, Richmond, VA 23238',
            'tech_focus': ['e-commerce', 'data-analytics', 'mobile', 'logistics'],
            'notable_projects': ['CarMax.com', 'CarMax Mobile App', 'Inventory Management System']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'company',
            'name': 'Flying Pig Labs',
            'industry': 'Software Development',
            'description': 'Richmond-based software development and consulting company',
            'employees': 25,
            'founded': 2010,
            'headquarters': '1717 E Cary St, Richmond, VA 23223',
            'tech_focus': ['web-development', 'mobile-apps', 'consulting', 'startups'],
            'notable_projects': ['Custom Web Applications', 'Mobile App Development', 'Startup Consulting']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'company',
            'name': 'Hourly',
            'industry': 'HR Technology',
            'description': 'HR technology platform for hourly workers',
            'employees': 150,
            'founded': 2018,
            'headquarters': '1717 E Cary St, Richmond, VA 23223',
            'tech_focus': ['hr-tech', 'mobile', 'saas', 'workforce-management'],
            'notable_projects': ['Hourly Platform', 'Mobile Workforce App', 'HR Analytics']
        },
        
        # Venues
        {
            'id': str(uuid.uuid4()),
            'type': 'venue',
            'name': 'Common House',
            'description': 'Co-working space and event venue in downtown Richmond',
            'address': '230 W Main St, Richmond, VA 23220',
            'capacity': 100,
            'amenities': ['wifi', 'projector', 'catering', 'parking'],
            'suitable_for': ['meetups', 'conferences', 'workshops', 'networking'],
            'contact': 'events@commonhouseva.com',
            'website': 'https://commonhouseva.com'
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'venue',
            'name': 'Startup Virginia',
            'description': 'Startup incubator and event space in Shockoe Bottom',
            'address': '1717 E Cary St, Richmond, VA 23223',
            'capacity': 150,
            'amenities': ['wifi', 'av-equipment', 'kitchen', 'parking'],
            'suitable_for': ['startup-events', 'pitch-competitions', 'workshops', 'meetups'],
            'contact': 'info@startupvirginia.org',
            'website': 'https://startupvirginia.org'
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'venue',
            'name': 'VCU Innovation Gateway',
            'description': 'VCU research and innovation hub',
            'address': '737 N 5th St, Richmond, VA 23219',
            'capacity': 200,
            'amenities': ['wifi', 'presentation-tech', 'labs', 'parking'],
            'suitable_for': ['academic-events', 'research-presentations', 'tech-talks', 'conferences'],
            'contact': 'gateway@vcu.edu',
            'website': 'https://innovation.vcu.edu'
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'venue',
            'name': 'The Frontier Project',
            'description': 'Creative co-working space and community hub',
            'address': '412 N 2nd St, Richmond, VA 23219',
            'capacity': 75,
            'amenities': ['wifi', 'flexible-seating', 'kitchen', 'outdoor-space'],
            'suitable_for': ['creative-meetups', 'workshops', 'networking', 'small-conferences'],
            'contact': 'hello@thefrontierproject.org',
            'website': 'https://thefrontierproject.org'
        },
        
        # Events
        {
            'id': str(uuid.uuid4()),
            'type': 'event',
            'name': 'Richmond Startup Weekend',
            'description': '54-hour event where developers, designers, and business people come together',
            'date': (now + timedelta(days=45)).isoformat(),
            'venue': 'Startup Virginia',
            'address': '1717 E Cary St, Richmond, VA 23223',
            'duration': '3 days',
            'organizer': 'Techstars',
            'topics': ['entrepreneurship', 'startups', 'innovation', 'networking'],
            'registration_fee': 50,
            'includes': ['meals', 'mentorship', 'prizes']
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'event',
            'name': 'RVA Tech Summit',
            'description': 'Annual technology conference for the Richmond region',
            'date': (now + timedelta(days=60)).isoformat(),
            'venue': 'Greater Richmond Convention Center',
            'address': '403 N 3rd St, Richmond, VA 23219',
            'duration': '2 days',
            'organizer': 'Richmond Technology Council',
            'topics': ['emerging-tech', 'digital-transformation', 'cybersecurity', 'ai'],
            'expected_attendees': 500,
            'registration_fee': 199
        },
        
        # Resources
        {
            'id': str(uuid.uuid4()),
            'type': 'resource',
            'name': 'Richmond Technology Council',
            'description': 'Non-profit organization supporting the Richmond tech community',
            'website': 'https://www.richmondtechnologycouncil.com',
            'services': ['networking', 'advocacy', 'education', 'events'],
            'contact': 'info@richmondtechnologycouncil.com'
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'resource',
            'name': 'Activation Capital',
            'description': 'Venture capital firm focused on B2B software companies',
            'website': 'https://activationcapital.com',
            'location': 'Richmond, VA',
            'focus': ['b2b-software', 'saas', 'fintech', 'healthtech'],
            'stage': ['seed', 'series-a']
        }
    ]
    
    return sample_data


def load_data_to_dynamodb(table_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Load data into DynamoDB table"""
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)
        
        # Batch write items
        with table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)
        
        logger.info(f"Successfully loaded {len(data)} items to {table_name}")
        
        return {
            'status': 'success',
            'items_loaded': len(data),
            'table': table_name
        }
        
    except Exception as e:
        logger.error(f"Error loading data to DynamoDB: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'table': table_name
        }


def lambda_handler(event, context):
    """
    Lambda handler for loading sample data
    This is triggered by CloudFormation custom resource
    """
    
    import cfnresponse
    
    try:
        table_name = event.get('ResourceProperties', {}).get('TableName') or \
                    context.invoked_function_arn.split(':')[3] + '-richmond-data'
        
        if 'DYNAMODB_TABLE' in event:
            table_name = event['DYNAMODB_TABLE']
        elif 'DYNAMODB_TABLE' in context.environment:
            table_name = context.environment['DYNAMODB_TABLE']
        
        logger.info(f"Loading sample data to table: {table_name}")
        
        # Get sample data
        sample_data = get_sample_data()
        
        # Load to DynamoDB
        result = load_data_to_dynamodb(table_name, sample_data)
        
        if result['status'] == 'success':
            logger.info("Sample data loaded successfully")
            # Send success response to CloudFormation
            cfnresponse.send(
                event, 
                context, 
                cfnresponse.SUCCESS, 
                result,
                physicalResourceId=f"SampleData-{table_name}"
            )
        else:
            logger.error(f"Failed to load sample data: {result['error']}")
            cfnresponse.send(
                event, 
                context, 
                cfnresponse.FAILED, 
                result,
                physicalResourceId=f"SampleData-{table_name}"
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}")
        cfnresponse.send(
            event, 
            context, 
            cfnresponse.FAILED, 
            {'error': str(e)},
            physicalResourceId="SampleDataLoader"
        )


# For standalone execution
if __name__ == "__main__":
    import os
    
    # Load environment variables
    table_name = os.getenv('DYNAMODB_TABLE', 'richmond-data')
    
    print(f"Loading sample data to table: {table_name}")
    
    # Generate and load data
    sample_data = get_sample_data()
    result = load_data_to_dynamodb(table_name, sample_data)
    
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result['status'] == 'success':
        print(f"\n✅ Successfully loaded {result['items_loaded']} items!")
        print("\nSample items loaded:")
        for item in sample_data[:3]:  # Show first 3 items
            print(f"- {item['type']}: {item['name']}")
        print(f"... and {len(sample_data) - 3} more items")
    else:
        print(f"\n❌ Error loading data: {result['error']}")