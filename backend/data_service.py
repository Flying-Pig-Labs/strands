"""
Data service layer for Richmond Tech Community demo.
Provides high-level data access methods for the agent/API layer.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from models.database import DynamoDBManager
import re

logger = logging.getLogger(__name__)


class RichmondTechDataService:
    """High-level data service for Richmond tech community information."""
    
    def __init__(self, table_name: str = "RichmondTechCommunity", region: str = "us-east-1"):
        """Initialize the data service."""
        self.db = DynamoDBManager(table_name=table_name, region=region)
        
    def get_next_tech_meetup(self, keywords: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next tech meetup in Richmond.
        
        Args:
            keywords: Optional list of keywords to filter events
            
        Returns:
            Dict containing event details or None if no events found
        """
        try:
            upcoming_events = self.db.get_upcoming_events(days_ahead=90)
            
            if not upcoming_events:
                return None
            
            # Filter by keywords if provided
            if keywords:
                filtered_events = []
                for event in upcoming_events:
                    event_text = (
                        f"{event.get('title', '')} {event.get('description', '')} "
                        f"{' '.join(event.get('tags', []))} {event.get('meetup_name', '')}"
                    ).lower()
                    
                    if any(keyword.lower() in event_text for keyword in keywords):
                        filtered_events.append(event)
                
                upcoming_events = filtered_events
            
            if not upcoming_events:
                return None
            
            # Return the next event
            next_event = upcoming_events[0]
            
            # Enrich with venue and meetup details
            venue = self.db.get_venue(next_event.get('venue_id', '').replace('venue_', ''))
            if venue:
                next_event['venue_details'] = venue
            
            logger.info(f"Found next tech meetup: {next_event['title']}")
            return next_event
            
        except Exception as e:
            logger.error(f"Error getting next tech meetup: {e}")
            return None
    
    def search_events_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for events related to a specific topic/technology.
        
        Args:
            topic: Technology or topic to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching events
        """
        try:
            events = self.db.search_events(topic)
            
            # Sort by date and limit results
            events = sorted(events, key=lambda x: (x['date'], x['start_time']))[:limit]
            
            # Enrich with venue details
            for event in events:
                venue = self.db.get_venue(event.get('venue_id', '').replace('venue_', ''))
                if venue:
                    event['venue_details'] = venue
            
            logger.info(f"Found {len(events)} events for topic '{topic}'")
            return events
            
        except Exception as e:
            logger.error(f"Error searching events by topic '{topic}': {e}")
            return []
    
    def get_meetup_groups_by_category(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Get meetup groups, optionally filtered by category.
        
        Args:
            category: Category to filter by (e.g., 'programming_language', 'cloud_computing')
            
        Returns:
            List of meetup groups
        """
        try:
            meetups = self.db.get_all_meetups()
            
            if category:
                meetups = [m for m in meetups if m.get('category') == category]
            
            # Sort by member count (most popular first)
            meetups = sorted(meetups, key=lambda x: x.get('member_count', 0), reverse=True)
            
            logger.info(f"Found {len(meetups)} meetup groups" + (f" in category '{category}'" if category else ""))
            return meetups
            
        except Exception as e:
            logger.error(f"Error getting meetup groups: {e}")
            return []
    
    def get_venue_information(self, venue_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a venue.
        
        Args:
            venue_name: Name or partial name of the venue
            
        Returns:
            Venue details or None if not found
        """
        try:
            venues = self.db.get_all_venues()
            
            # Search for venue by name (case-insensitive partial match)
            matching_venues = [
                v for v in venues 
                if venue_name.lower() in v['name'].lower()
            ]
            
            if not matching_venues:
                return None
            
            # Return the best match (exact match preferred, otherwise first match)
            venue = next(
                (v for v in matching_venues if v['name'].lower() == venue_name.lower()),
                matching_venues[0]
            )
            
            # Add upcoming events at this venue
            upcoming_events = self.db.get_upcoming_events(days_ahead=60)
            venue_events = [
                e for e in upcoming_events 
                if e.get('venue_id') == venue['id']
            ]
            venue['upcoming_events'] = venue_events[:5]  # Next 5 events
            
            logger.info(f"Found venue: {venue['name']}")
            return venue
            
        except Exception as e:
            logger.error(f"Error getting venue information for '{venue_name}': {e}")
            return None
    
    def get_tech_companies_info(self, industry: str = None) -> List[Dict[str, Any]]:
        """
        Get information about tech companies in Richmond.
        
        Args:
            industry: Optional industry filter
            
        Returns:
            List of company information
        """
        try:
            companies = self.db.get_all_companies()
            
            if industry:
                companies = [
                    c for c in companies 
                    if industry.lower() in c.get('industry', '').lower()
                ]
            
            # Sort by size (employee count)
            companies = sorted(companies, key=lambda x: x.get('employee_count', 0), reverse=True)
            
            logger.info(f"Found {len(companies)} tech companies" + (f" in {industry}" if industry else ""))
            return companies
            
        except Exception as e:
            logger.error(f"Error getting tech companies: {e}")
            return []
    
    def get_events_this_week(self) -> List[Dict[str, Any]]:
        """Get all tech events happening this week."""
        try:
            events = self.db.get_upcoming_events(days_ahead=7)
            
            # Filter to only this week
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            this_week_events = []
            for event in events:
                event_date = datetime.fromisoformat(event['date']).date()
                if week_start.date() <= event_date <= week_end.date():
                    this_week_events.append(event)
            
            # Enrich with venue details
            for event in this_week_events:
                venue = self.db.get_venue(event.get('venue_id', '').replace('venue_', ''))
                if venue:
                    event['venue_details'] = venue
            
            logger.info(f"Found {len(this_week_events)} events this week")
            return this_week_events
            
        except Exception as e:
            logger.error(f"Error getting events this week: {e}")
            return []
    
    def get_popular_meetups(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most popular meetup groups by member count."""
        try:
            meetups = self.db.get_all_meetups()
            
            # Sort by member count and limit
            popular_meetups = sorted(
                meetups, 
                key=lambda x: x.get('member_count', 0), 
                reverse=True
            )[:limit]
            
            # Add upcoming events for each meetup
            for meetup in popular_meetups:
                events = self.db.get_events_by_meetup(meetup['id'])
                meetup['upcoming_events'] = events[:3]  # Next 3 events
            
            logger.info(f"Found {len(popular_meetups)} popular meetups")
            return popular_meetups
            
        except Exception as e:
            logger.error(f"Error getting popular meetups: {e}")
            return []
    
    def find_events_by_speaker(self, speaker_name: str) -> List[Dict[str, Any]]:
        """Find events by speaker name."""
        try:
            all_events = self.db.get_upcoming_events(days_ahead=180)
            
            # Search for speaker in event details
            matching_events = [
                event for event in all_events
                if speaker_name.lower() in event.get('speaker', '').lower()
            ]
            
            logger.info(f"Found {len(matching_events)} events by speaker '{speaker_name}'")
            return matching_events
            
        except Exception as e:
            logger.error(f"Error finding events by speaker '{speaker_name}': {e}")
            return []
    
    def get_venue_events(self, venue_name: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get all events at a specific venue."""
        try:
            venue = self.get_venue_information(venue_name)
            if not venue:
                return []
            
            events = self.db.get_upcoming_events(days_ahead=days_ahead)
            venue_events = [
                event for event in events
                if event.get('venue_id') == venue['id']
            ]
            
            logger.info(f"Found {len(venue_events)} events at {venue_name}")
            return venue_events
            
        except Exception as e:
            logger.error(f"Error getting events for venue '{venue_name}': {e}")
            return []
    
    def get_tech_community_summary(self) -> Dict[str, Any]:
        """Get a summary of the Richmond tech community."""
        try:
            venues = self.db.get_all_venues()
            companies = self.db.get_all_companies()
            meetups = self.db.get_all_meetups()
            upcoming_events = self.db.get_upcoming_events(days_ahead=30)
            
            # Calculate statistics
            total_members = sum(m.get('member_count', 0) for m in meetups)
            total_employees = sum(c.get('employee_count', 0) for c in companies)
            
            # Get popular technologies from events
            tech_mentions = {}
            for event in upcoming_events:
                for tag in event.get('tags', []):
                    tech_mentions[tag] = tech_mentions.get(tag, 0) + 1
            
            popular_techs = sorted(tech_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
            
            summary = {
                'overview': {
                    'total_venues': len(venues),
                    'total_companies': len(companies),
                    'total_meetup_groups': len(meetups),
                    'total_upcoming_events': len(upcoming_events),
                    'total_community_members': total_members,
                    'total_tech_employees': total_employees
                },
                'popular_technologies': [tech[0] for tech in popular_techs],
                'largest_meetups': sorted(meetups, key=lambda x: x.get('member_count', 0), reverse=True)[:3],
                'major_employers': sorted(companies, key=lambda x: x.get('employee_count', 0), reverse=True)[:3],
                'upcoming_highlights': upcoming_events[:5]
            }
            
            logger.info("Generated tech community summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating community summary: {e}")
            return {}
    
    def natural_language_search(self, query: str) -> Dict[str, Any]:
        """
        Process natural language queries about the Richmond tech community.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict with search results and metadata
        """
        try:
            query_lower = query.lower()
            results = {
                'query': query,
                'results': {},
                'suggestions': []
            }
            
            # Pattern matching for common queries
            if any(word in query_lower for word in ['next', 'upcoming', 'when']):
                if any(word in query_lower for word in ['meetup', 'event']):
                    next_event = self.get_next_tech_meetup()
                    if next_event:
                        results['results']['next_event'] = next_event
                        results['suggestions'].append("Check out other upcoming events")
            
            # Technology-specific searches
            tech_keywords = ['python', 'javascript', 'java', 'react', 'aws', 'cloud', 'ai', 'machine learning']
            found_tech = [tech for tech in tech_keywords if tech in query_lower]
            
            if found_tech:
                for tech in found_tech:
                    events = self.search_events_by_topic(tech, limit=5)
                    if events:
                        results['results'][f'{tech}_events'] = events
            
            # Venue searches
            venue_keywords = ['startup virginia', 'common house', 'vcu']
            found_venues = [venue for venue in venue_keywords if venue in query_lower]
            
            if found_venues:
                for venue_name in found_venues:
                    venue_info = self.get_venue_information(venue_name)
                    if venue_info:
                        results['results'][f'{venue_name.replace(" ", "_")}_info'] = venue_info
            
            # Company searches
            if any(word in query_lower for word in ['company', 'companies', 'work', 'jobs']):
                companies = self.get_tech_companies_info()
                results['results']['companies'] = companies[:5]  # Top 5
            
            # Community overview
            if any(word in query_lower for word in ['overview', 'summary', 'about', 'community']):
                summary = self.get_tech_community_summary()
                results['results']['community_summary'] = summary
            
            logger.info(f"Processed natural language query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error processing natural language query '{query}': {e}")
            return {'query': query, 'results': {}, 'error': str(e)}


# Convenience functions for common use cases
def get_richmond_tech_info(query: str, table_name: str = "RichmondTechCommunity") -> Dict[str, Any]:
    """Convenience function for getting Richmond tech info."""
    service = RichmondTechDataService(table_name=table_name)
    return service.natural_language_search(query)


def get_next_meetup_info(table_name: str = "RichmondTechCommunity") -> Optional[Dict[str, Any]]:
    """Convenience function for getting the next meetup."""
    service = RichmondTechDataService(table_name=table_name)
    return service.get_next_tech_meetup()


if __name__ == "__main__":
    # Example usage and testing
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = RichmondTechDataService()
    
    # Test queries
    print("=== Richmond Tech Community Data Service Tests ===\n")
    
    # Test 1: Next meetup
    print("1. Next tech meetup:")
    next_event = service.get_next_tech_meetup()
    if next_event:
        print(f"   {next_event['title']}")
        print(f"   Date: {next_event['date'][:10]} at {next_event['start_time']}")
        print(f"   Venue: {next_event['venue_name']}")
    else:
        print("   No upcoming events found")
    
    # Test 2: Python events
    print("\n2. Python-related events:")
    python_events = service.search_events_by_topic("Python", limit=3)
    for event in python_events:
        print(f"   - {event['title']} on {event['date'][:10]}")
    
    # Test 3: Venue info
    print("\n3. Startup Virginia info:")
    venue_info = service.get_venue_information("Startup Virginia")
    if venue_info:
        print(f"   Address: {venue_info['address']}")
        print(f"   Capacity: {venue_info['capacity']} people")
        print(f"   Upcoming events: {len(venue_info.get('upcoming_events', []))}")
    
    # Test 4: Natural language search
    print("\n4. Natural language search - 'What's the next tech meetup?':")
    nl_results = service.natural_language_search("What's the next tech meetup in Richmond?")
    if 'next_event' in nl_results['results']:
        event = nl_results['results']['next_event']
        print(f"   {event['title']} on {event['date'][:10]} at {event['venue_name']}")
    
    # Test 5: Community summary
    print("\n5. Community summary:")
    summary = service.get_tech_community_summary()
    if summary:
        overview = summary.get('overview', {})
        print(f"   Meetup groups: {overview.get('total_meetup_groups', 0)}")
        print(f"   Companies: {overview.get('total_companies', 0)}")
        print(f"   Community members: {overview.get('total_community_members', 0):,}")
        print(f"   Upcoming events: {overview.get('total_upcoming_events', 0)}")
        print(f"   Popular technologies: {', '.join(summary.get('popular_technologies', [])[:5])}")
    
    print("\n=== Tests completed ===")