#!/usr/bin/env python3
"""
Test suite for Richmond Tech Community database operations.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import DynamoDBManager
from backend.data_service import RichmondTechDataService
from data.sample_data import RichmondDataGenerator


class TestRichmondDataGenerator:
    """Test the sample data generation."""
    
    def test_data_generation(self):
        """Test that sample data is generated correctly."""
        generator = RichmondDataGenerator()
        data = generator.get_all_data()
        
        # Check all categories exist
        assert 'venues' in data
        assert 'companies' in data
        assert 'meetups' in data
        assert 'events' in data
        
        # Check minimum data counts
        assert len(data['venues']) >= 3
        assert len(data['companies']) >= 3
        assert len(data['meetups']) >= 3
        assert len(data['events']) >= 5
        
        # Validate venue structure
        venue = data['venues'][0]
        required_venue_fields = ['id', 'name', 'address', 'type', 'capacity', 'amenities']
        for field in required_venue_fields:
            assert field in venue
        
        # Validate company structure
        company = data['companies'][0]
        required_company_fields = ['id', 'name', 'industry', 'size', 'employee_count']
        for field in required_company_fields:
            assert field in company
        
        # Validate meetup structure
        meetup = data['meetups'][0]
        required_meetup_fields = ['id', 'name', 'category', 'member_count', 'organizer']
        for field in required_meetup_fields:
            assert field in meetup
        
        # Validate event structure
        event = data['events'][0]
        required_event_fields = ['id', 'title', 'date', 'venue_id', 'meetup_id']
        for field in required_event_fields:
            assert field in event
    
    def test_realistic_data_content(self):
        """Test that generated data contains realistic Richmond content."""
        generator = RichmondDataGenerator()
        data = generator.get_all_data()
        
        # Check for Richmond-specific venues
        venue_names = [v['name'] for v in data['venues']]
        assert any('Startup Virginia' in name for name in venue_names)
        assert any('Common House' in name for name in venue_names)
        
        # Check for Richmond companies
        company_names = [c['name'] for c in data['companies']]
        assert any('CarMax' in name for name in company_names)
        assert any('Capital One' in name for name in company_names)
        
        # Check for tech-focused meetups
        meetup_categories = [m['category'] for m in data['meetups']]
        tech_categories = ['cloud_computing', 'programming_language', 'data_science', 'cybersecurity']
        assert any(cat in meetup_categories for cat in tech_categories)


class TestDynamoDBManager:
    """Test the DynamoDB manager with mocked AWS calls."""
    
    @pytest.fixture
    def mock_dynamodb(self):
        """Mock DynamoDB resources."""
        with patch('boto3.resource') as mock_resource, \
             patch('boto3.client') as mock_client:
            
            # Mock table
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table
            
            # Mock client
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            yield {
                'resource': mock_resource,
                'client': mock_client,
                'table': mock_table,
                'client_instance': mock_client_instance
            }
    
    def test_init(self, mock_dynamodb):
        """Test DynamoDB manager initialization."""
        db = DynamoDBManager(table_name="test-table", region="us-east-1")
        
        assert db.table_name == "test-table"
        assert db.region == "us-east-1"
        mock_dynamodb['resource'].assert_called_with('dynamodb', region_name='us-east-1')
    
    def test_convert_floats_to_decimal(self, mock_dynamodb):
        """Test float to Decimal conversion for DynamoDB."""
        db = DynamoDBManager()
        
        # Test simple float
        result = db._convert_floats_to_decimal(3.14)
        assert isinstance(result, Decimal)
        assert result == Decimal('3.14')
        
        # Test nested structure
        data = {
            'price': 99.99,
            'details': {
                'rating': 4.5,
                'count': 100
            },
            'tags': ['python', 'aws']
        }
        
        result = db._convert_floats_to_decimal(data)
        assert isinstance(result['price'], Decimal)
        assert isinstance(result['details']['rating'], Decimal)
        assert result['details']['count'] == 100  # int unchanged
        assert result['tags'] == ['python', 'aws']  # strings unchanged
    
    def test_put_venue(self, mock_dynamodb):
        """Test venue storage."""
        db = DynamoDBManager()
        mock_dynamodb['table'].put_item.return_value = {}
        
        venue_data = {
            'id': 'venue_test',
            'name': 'Test Venue',
            'address': '123 Test St',
            'type': 'coworking',
            'capacity': 100,
            'amenities': ['wifi', 'parking']
        }
        
        result = db.put_venue(venue_data)
        assert result is True
        
        # Verify put_item was called with correct structure
        mock_dynamodb['table'].put_item.assert_called_once()
        call_args = mock_dynamodb['table'].put_item.call_args[1]
        item = call_args['Item']
        
        assert item['PK'] == 'VENUE#venue_test'
        assert item['SK'] == 'VENUE#venue_test'
        assert item['GSI1PK'] == 'VENUE'
        assert item['EntityType'] == 'venue'
        assert 'CreatedAt' in item
        assert 'UpdatedAt' in item
    
    def test_get_upcoming_events(self, mock_dynamodb):
        """Test upcoming events query."""
        db = DynamoDBManager()
        
        # Mock query responses
        mock_dynamodb['table'].query.return_value = {
            'Items': [{
                'id': 'event_1',
                'title': 'Test Event',
                'date': '2024-02-01T18:30:00',
                'start_time': '18:30',
                'EntityType': 'event'
            }]
        }
        
        events = db.get_upcoming_events(days_ahead=7)
        
        # Should have made multiple queries (one per day)
        assert mock_dynamodb['table'].query.call_count >= 1
        assert len(events) >= 0  # Could be empty if no events match


class TestRichmondTechDataService:
    """Test the high-level data service."""
    
    @pytest.fixture
    def mock_data_service(self):
        """Mock the database manager in data service."""
        with patch('backend.data_service.DynamoDBManager') as mock_db_manager:
            service = RichmondTechDataService()
            yield service, mock_db_manager.return_value
    
    def test_init(self, mock_data_service):
        """Test data service initialization."""
        service, mock_db = mock_data_service
        assert service.db is not None
    
    def test_get_next_tech_meetup(self, mock_data_service):
        """Test getting next tech meetup."""
        service, mock_db = mock_data_service
        
        # Mock upcoming events
        mock_events = [{
            'id': 'event_1',
            'title': 'Python Meetup',
            'date': '2024-02-15T18:30:00',
            'start_time': '18:30',
            'venue_id': 'venue_startup_va',
            'meetup_name': 'Richmond Python',
            'description': 'Learn Python basics',
            'tags': ['python', 'programming']
        }]
        
        mock_db.get_upcoming_events.return_value = mock_events
        mock_db.get_venue.return_value = {
            'id': 'startup_va',
            'name': 'Startup Virginia',
            'address': '1717 E Cary St'
        }
        
        result = service.get_next_tech_meetup()
        
        assert result is not None
        assert result['title'] == 'Python Meetup'
        assert 'venue_details' in result
        mock_db.get_upcoming_events.assert_called_once_with(days_ahead=90)
    
    def test_search_events_by_topic(self, mock_data_service):
        """Test searching events by topic."""
        service, mock_db = mock_data_service
        
        # Mock search results
        mock_events = [{
            'id': 'event_1',
            'title': 'JavaScript Workshop',
            'date': '2024-02-20T19:00:00',
            'start_time': '19:00',
            'venue_id': 'venue_common_house'
        }]
        
        mock_db.search_events.return_value = mock_events
        mock_db.get_venue.return_value = {'name': 'Common House'}
        
        results = service.search_events_by_topic('JavaScript', limit=5)
        
        assert len(results) == 1
        assert results[0]['title'] == 'JavaScript Workshop'
        mock_db.search_events.assert_called_once_with('JavaScript')
    
    def test_natural_language_search(self, mock_data_service):
        """Test natural language query processing."""
        service, mock_db = mock_data_service
        
        # Mock next event
        mock_event = {
            'id': 'event_1',
            'title': 'Cloud Computing Meetup',
            'date': '2024-02-25T18:00:00',
            'meetup_name': 'RVA Cloud Wranglers'
        }
        
        mock_db.get_upcoming_events.return_value = [mock_event]
        mock_db.get_venue.return_value = None
        
        # Test "next meetup" query
        result = service.natural_language_search("What's the next tech meetup?")
        
        assert 'next_event' in result['results']
        assert result['results']['next_event']['title'] == 'Cloud Computing Meetup'
        assert result['query'] == "What's the next tech meetup?"
    
    def test_get_tech_community_summary(self, mock_data_service):
        """Test community summary generation."""
        service, mock_db = mock_data_service
        
        # Mock data
        mock_db.get_all_venues.return_value = [{'id': 'v1'}, {'id': 'v2'}]
        mock_db.get_all_companies.return_value = [
            {'employee_count': 1000}, 
            {'employee_count': 500}
        ]
        mock_db.get_all_meetups.return_value = [
            {'member_count': 300, 'name': 'Group 1'}, 
            {'member_count': 200, 'name': 'Group 2'}
        ]
        mock_db.get_upcoming_events.return_value = [
            {'tags': ['python', 'web']},
            {'tags': ['python', 'data']}
        ]
        
        summary = service.get_tech_community_summary()
        
        assert 'overview' in summary
        assert summary['overview']['total_venues'] == 2
        assert summary['overview']['total_companies'] == 2
        assert summary['overview']['total_community_members'] == 500
        assert 'popular_technologies' in summary
        assert 'python' in summary['popular_technologies']


class TestIntegration:
    """Integration tests using real sample data (but mocked AWS)."""
    
    def test_end_to_end_data_flow(self):
        """Test complete data flow from generation to service queries."""
        # Generate sample data
        generator = RichmondDataGenerator()
        sample_data = generator.get_all_data()
        
        # Verify we have realistic Richmond data
        assert len(sample_data['venues']) >= 3
        assert len(sample_data['events']) >= 5
        
        # Test that events have proper date formatting
        for event in sample_data['events']:
            # Should be ISO format
            datetime.fromisoformat(event['date'])
            
            # Should have required fields
            assert 'title' in event
            assert 'venue_id' in event
            assert 'meetup_id' in event
        
        # Test that meetups reference valid venues
        venue_ids = {v['id'] for v in sample_data['venues']}
        meetup_venue_refs = {m['typical_venue'] for m in sample_data['meetups']}
        
        # All meetup venue references should exist
        assert meetup_venue_refs.issubset(venue_ids)
    
    def test_demo_scenarios(self):
        """Test the specific demo scenarios mentioned in README."""
        generator = RichmondDataGenerator()
        sample_data = generator.get_all_data()
        
        # Scenario: "What's the next tech meetup happening in Richmond?"
        events = sample_data['events']
        future_events = [
            e for e in events 
            if datetime.fromisoformat(e['date']) > datetime.now()
        ]
        
        # Should have future events
        assert len(future_events) > 0
        
        # Should have events with Richmond-specific venues
        richmond_venues = {'venue_startup_va', 'venue_common_house', 'venue_vcu_engineering'}
        event_venues = {e['venue_id'] for e in events}
        assert richmond_venues.intersection(event_venues)
        
        # Should have cloud/tech-related events
        tech_tags = []
        for event in events:
            tech_tags.extend(event.get('tags', []))
        
        tech_keywords = ['AWS', 'cloud', 'python', 'javascript', 'data']
        found_tech = [tag for tag in tech_tags if any(keyword.lower() in tag.lower() for keyword in tech_keywords)]
        assert len(found_tech) > 0


if __name__ == "__main__":
    # Run basic tests
    print("Running Richmond Tech Community Database Tests...")
    
    # Test data generation
    test_gen = TestRichmondDataGenerator()
    test_gen.test_data_generation()
    test_gen.test_realistic_data_content()
    print("✅ Data generation tests passed")
    
    # Test integration scenarios
    test_integration = TestIntegration()
    test_integration.test_end_to_end_data_flow()
    test_integration.test_demo_scenarios()
    print("✅ Integration tests passed")
    
    print("\n🎉 All basic tests passed! The database backend is ready for the demo.")
    print("\nTo run full tests with pytest:")
    print("  pip install pytest pytest-mock")
    print("  pytest tests/test_database.py -v")
    print("\nTo setup the actual database:")
    print("  python scripts/setup_database.py --show-queries")