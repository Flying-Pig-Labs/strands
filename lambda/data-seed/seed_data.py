"""
Richmond Tech Community Data Seeder
Seeds DynamoDB with Richmond, VA tech community data for the demo
"""

import json
import os
import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from aws_lambda_powertools import Logger

# Initialize logger
logger = Logger()

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

class RichmondDataSeeder:
    """Seeds DynamoDB with Richmond tech community data"""
    
    def __init__(self):
        self.table = dynamodb.Table(TABLE_NAME)
    
    def get_sample_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get sample Richmond tech community data"""
        
        # Calculate dates for upcoming meetups
        today = datetime.now()
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)
        
        return {
            'meetups': [
                {
                    'pk': 'meetup#rva-cloud-wranglers',
                    'sk': '2024-07-31',
                    'type': 'meetup',
                    'name': 'RVA Cloud Wranglers',
                    'title': 'AWS Lambda Best Practices Workshop',
                    'date': '2024-07-31',
                    'time': '6:30 PM',
                    'venue': 'Common House RVA',
                    'address': '306 E Grace St, Richmond, VA 23219',
                    'description': 'Join us for a hands-on workshop covering AWS Lambda best practices, including performance optimization, error handling, and monitoring.',
                    'organizer': 'Richmond Cloud Engineers',
                    'capacity': 50,
                    'registered': 32,
                    'tech_stack': ['AWS', 'Lambda', 'Python', 'Node.js'],
                    'skill_level': 'Intermediate'
                },
                {
                    'pk': 'meetup#rva-js-group',
                    'sk': '2024-08-05',
                    'type': 'meetup',
                    'name': 'RVA JavaScript User Group',
                    'title': 'Modern React Patterns and State Management',
                    'date': '2024-08-05',
                    'time': '7:00 PM',
                    'venue': 'Startup Virginia',
                    'address': '2810 E Broad St, Richmond, VA 23223',
                    'description': 'Deep dive into modern React patterns, context API, and state management solutions like Zustand and Redux Toolkit.',
                    'organizer': 'RVA JS Community',
                    'capacity': 40,
                    'registered': 28,
                    'tech_stack': ['JavaScript', 'React', 'TypeScript', 'Node.js'],
                    'skill_level': 'Intermediate to Advanced'
                },
                {
                    'pk': 'meetup#richmond-python',
                    'sk': '2024-08-12',
                    'type': 'meetup',
                    'name': 'Richmond Python User Group',
                    'title': 'Building AI Applications with Python and LangChain',
                    'date': '2024-08-12',
                    'time': '6:00 PM',
                    'venue': 'Capital One Labs',
                    'address': '4851 Lake Brook Dr, Glen Allen, VA 23060',
                    'description': 'Learn how to build AI-powered applications using Python, LangChain, and modern LLM APIs.',
                    'organizer': 'Richmond Python Society',
                    'capacity': 60,
                    'registered': 45,
                    'tech_stack': ['Python', 'AI/ML', 'LangChain', 'OpenAI'],
                    'skill_level': 'Beginner to Intermediate'
                },
                {
                    'pk': 'meetup#rva-devops',
                    'sk': '2024-08-20',
                    'type': 'meetup',
                    'name': 'RVA DevOps Meetup',
                    'title': 'Infrastructure as Code with Terraform and CDK',
                    'date': '2024-08-20',
                    'time': '6:30 PM',
                    'venue': 'Flying Pig Labs',
                    'address': '1237 W Broad St, Richmond, VA 23220',
                    'description': 'Compare and contrast infrastructure automation using Terraform and AWS CDK, with live demos and best practices.',
                    'organizer': 'Richmond DevOps Community',
                    'capacity': 35,
                    'registered': 22,
                    'tech_stack': ['Terraform', 'AWS CDK', 'Docker', 'Kubernetes'],
                    'skill_level': 'Intermediate'
                }
            ],
            'companies': [
                {
                    'pk': 'company#carmax',
                    'sk': 'info',
                    'type': 'company',
                    'name': 'CarMax',
                    'industry': 'E-commerce/Automotive',
                    'size': '25,000+',
                    'headquarters': 'Richmond, VA',
                    'founded': '1993',
                    'description': 'The nation\'s largest retailer of used cars, known for innovation in automotive e-commerce and customer experience.',
                    'tech_stack': ['Java', 'React', 'AWS', 'Microservices', 'Kubernetes'],
                    'career_page': 'https://careers.carmax.com',
                    'notable_projects': ['Omnichannel customer experience', 'AI-powered vehicle recommendations', 'Mobile app development']
                },
                {
                    'pk': 'company#capital-one',
                    'sk': 'info',
                    'type': 'company',
                    'name': 'Capital One',
                    'industry': 'Financial Services',
                    'size': '50,000+',
                    'headquarters': 'McLean, VA (Major Richmond presence)',
                    'founded': '1994',
                    'description': 'Digital-first bank and Fortune 500 company with significant technology operations in Richmond.',
                    'tech_stack': ['Python', 'Java', 'AWS', 'Machine Learning', 'React', 'Scala'],
                    'career_page': 'https://www.capitalonecareers.com',
                    'notable_projects': ['Cloud-first banking infrastructure', 'Real-time fraud detection', 'Mobile banking innovation']
                },
                {
                    'pk': 'company#flying-pig-labs',
                    'sk': 'info',
                    'type': 'company',
                    'name': 'Flying Pig Labs',
                    'industry': 'Software Development/Consulting',
                    'size': '10-50',
                    'headquarters': 'Richmond, VA',
                    'founded': '2015',
                    'description': 'Custom software development and consulting firm specializing in web applications and digital transformation.',
                    'tech_stack': ['Ruby on Rails', 'React', 'Node.js', 'AWS', 'PostgreSQL'],
                    'career_page': 'https://flyingpiglabs.com/careers',
                    'notable_projects': ['E-commerce platforms', 'Healthcare applications', 'SaaS products']
                },
                {
                    'pk': 'company#startup-virginia',
                    'sk': 'info',
                    'type': 'company',
                    'name': 'Startup Virginia',
                    'industry': 'Startup Incubator/Accelerator',
                    'size': '10-25',
                    'headquarters': 'Richmond, VA',
                    'founded': '2013',
                    'description': 'Virginia\'s premier startup incubator and accelerator, supporting early-stage companies across the state.',
                    'tech_stack': ['Various (supports portfolio companies)', 'Startup ecosystem tools'],
                    'career_page': 'https://startupvirginia.org/jobs',
                    'notable_projects': ['Startup acceleration programs', 'Entrepreneur mentorship', 'Venture capital connections']
                }
            ],
            'venues': [
                {
                    'pk': 'venue#common-house-rva',
                    'sk': 'info',
                    'type': 'venue',
                    'name': 'Common House RVA',
                    'address': '306 E Grace St, Richmond, VA 23219',
                    'neighborhood': 'Jackson Ward',
                    'capacity': 100,
                    'amenities': ['WiFi', 'Projector', 'Sound system', 'Catering options', 'Parking'],
                    'description': 'Modern event space in historic Jackson Ward, popular for tech meetups and startup events.',
                    'contact': 'events@commonhouserva.com',
                    'website': 'https://commonhouserva.com',
                    'pricing': 'Varies by event size and duration',
                    'tech_friendly': True
                },
                {
                    'pk': 'venue#startup-virginia',
                    'sk': 'info',
                    'type': 'venue',
                    'name': 'Startup Virginia',
                    'address': '2810 E Broad St, Richmond, VA 23223',
                    'neighborhood': 'Church Hill',
                    'capacity': 75,
                    'amenities': ['High-speed WiFi', 'Multiple meeting rooms', 'AV equipment', 'Kitchen facilities', 'Free parking'],
                    'description': 'Startup incubator space that regularly hosts tech community events and meetups.',
                    'contact': 'hello@startupvirginia.org',
                    'website': 'https://startupvirginia.org',
                    'pricing': 'Community events often free or low-cost',
                    'tech_friendly': True
                },
                {
                    'pk': 'venue#capital-one-labs',
                    'sk': 'info',
                    'type': 'venue',
                    'name': 'Capital One Labs',
                    'address': '4851 Lake Brook Dr, Glen Allen, VA 23060',
                    'neighborhood': 'Glen Allen',
                    'capacity': 150,
                    'amenities': ['Enterprise WiFi', 'Multiple conference rooms', 'State-of-the-art AV', 'Catering services', 'Ample parking'],
                    'description': 'Corporate campus with modern facilities, occasionally hosts large tech community events.',
                    'contact': 'community@capitalone.com',
                    'website': 'https://www.capitalone.com',
                    'pricing': 'Sponsored events typically free',
                    'tech_friendly': True
                },
                {
                    'pk': 'venue#flying-pig-labs',
                    'sk': 'info',
                    'type': 'venue',
                    'name': 'Flying Pig Labs Office',
                    'address': '1237 W Broad St, Richmond, VA 23220',
                    'neighborhood': 'The Fan',
                    'capacity': 40,
                    'amenities': ['Fast WiFi', 'Projector', 'Whiteboard', 'Coffee/snacks', 'Street parking'],
                    'description': 'Cozy office space in The Fan district, great for smaller, intimate tech gatherings.',
                    'contact': 'hello@flyingpiglabs.com',
                    'website': 'https://flyingpiglabs.com',
                    'pricing': 'Community events by arrangement',
                    'tech_friendly': True
                }
            ]
        }
    
    def seed_data(self) -> Dict[str, Any]:
        """Seed the DynamoDB table with Richmond tech data"""
        try:
            data = self.get_sample_data()
            items_created = 0
            
            # Seed meetups
            for meetup in data['meetups']:
                self.table.put_item(Item=meetup)
                items_created += 1
                logger.info(f"Created meetup: {meetup['name']}")
            
            # Seed companies
            for company in data['companies']:
                self.table.put_item(Item=company)
                items_created += 1
                logger.info(f"Created company: {company['name']}")
            
            # Seed venues
            for venue in data['venues']:
                self.table.put_item(Item=venue)
                items_created += 1
                logger.info(f"Created venue: {venue['name']}")
            
            return {
                'success': True,
                'items_created': items_created,
                'categories': {
                    'meetups': len(data['meetups']),
                    'companies': len(data['companies']),
                    'venues': len(data['venues'])
                },
                'message': f'Successfully seeded {items_created} items into {TABLE_NAME}'
            }
            
        except Exception as e:
            logger.error(f"Failed to seed data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to seed data into DynamoDB'
            }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for data seeding"""
    try:
        seeder = RichmondDataSeeder()
        result = seeder.seed_data()
        
        return {
            'statusCode': 200 if result['success'] else 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Unexpected error during data seeding'
            })
        }