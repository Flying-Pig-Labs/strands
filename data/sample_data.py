#!/usr/bin/env python3
"""
Sample data generation for Richmond, VA tech community demo.
Generates realistic data for meetups, venues, companies, and events.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

class RichmondDataGenerator:
    """Generates realistic sample data for Richmond tech community."""
    
    def __init__(self):
        self.venues = self._generate_venues()
        self.companies = self._generate_companies()
        self.meetups = self._generate_meetups()
        self.events = self._generate_events()
    
    def _generate_venues(self) -> List[Dict[str, Any]]:
        """Generate Richmond tech venues."""
        return [
            {
                "id": "venue_startup_va",
                "name": "Startup Virginia",
                "address": "1717 E Cary St, Richmond, VA 23223",
                "type": "coworking_space",
                "capacity": 150,
                "amenities": ["wifi", "parking", "kitchen", "presentation_screen"],
                "contact": {
                    "phone": "(804) 644-2476",
                    "email": "info@startupvirginia.org",
                    "website": "https://startupvirginia.org"
                },
                "description": "Richmond's premier startup incubator and coworking space"
            },
            {
                "id": "venue_common_house",
                "name": "Common House",
                "address": "305 W Broad St, Richmond, VA 23220",
                "type": "event_space",
                "capacity": 200,
                "amenities": ["wifi", "valet_parking", "catering", "av_equipment"],
                "contact": {
                    "phone": "(804) 612-1900",
                    "email": "events@commonhouserichmond.com",
                    "website": "https://commonhouserichmond.com"
                },
                "description": "Upscale event venue in downtown Richmond"
            },
            {
                "id": "venue_vcu_engineering",
                "name": "VCU School of Engineering",
                "address": "401 W Main St, Richmond, VA 23284",
                "type": "university",
                "capacity": 300,
                "amenities": ["wifi", "parking", "presentation_equipment", "recording"],
                "contact": {
                    "phone": "(804) 828-3565",
                    "email": "engineering@vcu.edu",
                    "website": "https://egr.vcu.edu"
                },
                "description": "VCU's engineering school with modern tech facilities"
            },
            {
                "id": "venue_capital_one_cafe",
                "name": "Capital One Café",
                "address": "11800 W Broad St, Richmond, VA 23233",
                "type": "cafe",
                "capacity": 50,
                "amenities": ["wifi", "coffee", "casual_seating"],
                "contact": {
                    "phone": "(804) 360-3780",
                    "website": "https://www.capitalone.com/local/richmond"
                },
                "description": "Modern café space for casual tech meetups"
            },
            {
                "id": "venue_libbie_mill",
                "name": "Libbie Mill Library",
                "address": "2100 Libbie Lake E St, Richmond, VA 23230",
                "type": "library",
                "capacity": 80,
                "amenities": ["wifi", "parking", "quiet_spaces", "group_rooms"],
                "contact": {
                    "phone": "(804) 501-5136",
                    "website": "https://henrico.lib.va.us"
                },
                "description": "Modern library with excellent tech facilities"
            }
        ]
    
    def _generate_companies(self) -> List[Dict[str, Any]]:
        """Generate Richmond tech companies."""
        return [
            {
                "id": "company_carmax",
                "name": "CarMax",
                "industry": "automotive_tech",
                "size": "large",
                "employee_count": 25000,
                "headquarters": "12800 Tuckahoe Creek Pkwy, Richmond, VA 23238",
                "tech_stack": ["Java", "Python", "React", "AWS", "Kubernetes"],
                "description": "Fortune 500 used car retailer with major tech operations",
                "founded": 1993,
                "careers_url": "https://careers.carmax.com",
                "notable_projects": ["Digital car buying platform", "Mobile app development", "Data analytics"]
            },
            {
                "id": "company_capital_one",
                "name": "Capital One",
                "industry": "fintech",
                "size": "large",
                "employee_count": 50000,
                "headquarters": "15000 Capital One Dr, Richmond, VA 23238",
                "tech_stack": ["Java", "Python", "Go", "AWS", "Machine Learning"],
                "description": "Major financial services company with significant tech presence",
                "founded": 1994,
                "careers_url": "https://www.capitalonecareers.com",
                "notable_projects": ["Mobile banking", "ML fraud detection", "Cloud infrastructure"]
            },
            {
                "id": "company_flying_pig_labs",
                "name": "Flying Pig Labs",
                "industry": "software_development",
                "size": "small",
                "employee_count": 15,
                "headquarters": "Richmond, VA",
                "tech_stack": ["Ruby on Rails", "JavaScript", "React", "PostgreSQL"],
                "description": "Boutique software development consultancy",
                "founded": 2010,
                "website": "https://flyingpiglabs.com",
                "notable_projects": ["Custom web applications", "E-commerce platforms", "API development"]
            },
            {
                "id": "company_dominion_energy",
                "name": "Dominion Energy",
                "industry": "energy_tech",
                "size": "large",
                "employee_count": 16000,
                "headquarters": "120 Tredegar St, Richmond, VA 23219",
                "tech_stack": ["C#", ".NET", "SQL Server", "Azure", "IoT"],
                "description": "Utility company with growing technology division",
                "founded": 1983,
                "careers_url": "https://careers.dominionenergy.com",
                "notable_projects": ["Smart grid technology", "Renewable energy systems", "Customer portal"]
            },
            {
                "id": "company_willow_tree",
                "name": "WillowTree",
                "industry": "mobile_development",
                "size": "medium",
                "employee_count": 300,
                "headquarters": "107 S West St, Charlottesville, VA 22902",
                "richmond_office": "Richmond, VA",
                "tech_stack": ["Swift", "Kotlin", "React Native", "Node.js", "AWS"],
                "description": "Leading mobile app development company with Richmond presence",
                "founded": 2007,
                "website": "https://willowtreeapps.com",
                "notable_projects": ["HBO Max mobile app", "National Geographic apps", "Enterprise mobile solutions"]
            }
        ]
    
    def _generate_meetups(self) -> List[Dict[str, Any]]:
        """Generate Richmond tech meetup groups."""
        return [
            {
                "id": "meetup_rva_cloud_wranglers",
                "name": "RVA Cloud Wranglers",
                "category": "cloud_computing",
                "description": "Richmond's premier cloud computing meetup focusing on AWS, Azure, and GCP",
                "organizer": "Sarah Chen",
                "organizer_company": "Capital One",
                "member_count": 450,
                "founded": "2019-03-15",
                "meeting_frequency": "monthly",
                "typical_venue": "venue_startup_va",
                "focus_areas": ["AWS", "Azure", "DevOps", "Serverless", "Containers"],
                "social_links": {
                    "meetup": "https://meetup.com/rva-cloud-wranglers",
                    "slack": "rva-cloud-wranglers.slack.com",
                    "github": "https://github.com/rva-cloud-wranglers"
                }
            },
            {
                "id": "meetup_richmond_python",
                "name": "Richmond Python User Group",
                "category": "programming_language",
                "description": "Python enthusiasts in the Richmond area sharing knowledge and projects",
                "organizer": "Michael Rodriguez",
                "organizer_company": "CarMax",
                "member_count": 320,
                "founded": "2017-09-20",
                "meeting_frequency": "monthly",
                "typical_venue": "venue_vcu_engineering",
                "focus_areas": ["Python", "Data Science", "Web Development", "Machine Learning"],
                "social_links": {
                    "meetup": "https://meetup.com/richmond-python",
                    "discord": "richmond-python",
                    "github": "https://github.com/richmond-python"
                }
            },
            {
                "id": "meetup_rva_js",
                "name": "RVA.js",
                "category": "programming_language",
                "description": "JavaScript developers building the future of web applications",
                "organizer": "Jessica Park",
                "organizer_company": "WillowTree",
                "member_count": 280,
                "founded": "2018-01-12",
                "meeting_frequency": "monthly",
                "typical_venue": "venue_common_house",
                "focus_areas": ["JavaScript", "React", "Node.js", "TypeScript", "Full-stack"],
                "social_links": {
                    "meetup": "https://meetup.com/rva-js",
                    "twitter": "@rvajs",
                    "discord": "rvajs"
                }
            },
            {
                "id": "meetup_richmond_data_science",
                "name": "Richmond Data Science Meetup",
                "category": "data_science",
                "description": "Data scientists, analysts, and ML engineers sharing insights and techniques",
                "organizer": "Dr. Amanda Johnson",
                "organizer_company": "VCU",
                "member_count": 190,
                "founded": "2020-06-08",
                "meeting_frequency": "monthly",
                "typical_venue": "venue_vcu_engineering",
                "focus_areas": ["Machine Learning", "Statistics", "Python", "R", "Data Visualization"],
                "social_links": {
                    "meetup": "https://meetup.com/richmond-data-science",
                    "linkedin": "richmond-data-science"
                }
            },
            {
                "id": "meetup_rva_cybersecurity",
                "name": "RVA Cybersecurity Guild",
                "category": "cybersecurity",
                "description": "Information security professionals protecting Richmond's digital infrastructure",
                "organizer": "David Kim",
                "organizer_company": "Dominion Energy",
                "member_count": 220,
                "founded": "2019-11-03",
                "meeting_frequency": "monthly",
                "typical_venue": "venue_startup_va",
                "focus_areas": ["Network Security", "Ethical Hacking", "Compliance", "Incident Response"],
                "social_links": {
                    "meetup": "https://meetup.com/rva-cybersecurity",
                    "website": "https://rvacybersecurity.org"
                }
            }
        ]
    
    def _generate_events(self) -> List[Dict[str, Any]]:
        """Generate upcoming tech events in Richmond."""
        base_date = datetime.now()
        events = []
        
        # Generate events for the next 3 months
        event_templates = [
            {
                "meetup_id": "meetup_rva_cloud_wranglers",
                "title": "Serverless Architecture Best Practices",
                "description": "Learn how to build scalable serverless applications on AWS Lambda",
                "speaker": "Alex Thompson",
                "speaker_bio": "Senior Cloud Architect at Capital One",
                "duration_hours": 2,
                "tags": ["AWS", "Lambda", "Serverless", "Architecture"]
            },
            {
                "meetup_id": "meetup_richmond_python",
                "title": "Building Machine Learning Pipelines with Python",
                "description": "End-to-end ML pipeline development using scikit-learn and pandas",
                "speaker": "Dr. Maria Santos",
                "speaker_bio": "Lead Data Scientist at CarMax",
                "duration_hours": 2.5,
                "tags": ["Python", "Machine Learning", "Data Science", "MLOps"]
            },
            {
                "meetup_id": "meetup_rva_js",
                "title": "Modern React Patterns and Performance",
                "description": "Advanced React techniques for building high-performance web apps",
                "speaker": "Jordan Liu",
                "speaker_bio": "Senior Frontend Engineer at WillowTree",
                "duration_hours": 2,
                "tags": ["React", "JavaScript", "Performance", "Frontend"]
            },
            {
                "meetup_id": "meetup_richmond_data_science",
                "title": "Deep Learning for Computer Vision",
                "description": "Practical applications of CNNs and transfer learning",
                "speaker": "Dr. Rachel Green",
                "speaker_bio": "Assistant Professor at VCU Engineering",
                "duration_hours": 3,
                "tags": ["Deep Learning", "Computer Vision", "TensorFlow", "AI"]
            },
            {
                "meetup_id": "meetup_rva_cybersecurity",
                "title": "Zero Trust Security Architecture",
                "description": "Implementing zero trust principles in enterprise environments",
                "speaker": "Marcus Johnson",
                "speaker_bio": "CISO at Dominion Energy",
                "duration_hours": 2,
                "tags": ["Security", "Zero Trust", "Enterprise", "Architecture"]
            }
        ]
        
        # Generate events for next 12 weeks
        for week in range(12):
            event_date = base_date + timedelta(weeks=week, days=3)  # Events on future Thursdays
            if week < len(event_templates):
                template = event_templates[week % len(event_templates)]
                
                # Find the meetup details
                meetup = next((m for m in self.meetups if m["id"] == template["meetup_id"]), None)
                if not meetup:
                    continue
                
                # Find typical venue
                venue = next((v for v in self.venues if v["id"] == meetup["typical_venue"]), None)
                
                event = {
                    "id": f"event_{uuid.uuid4().hex[:8]}",
                    "meetup_id": template["meetup_id"],
                    "meetup_name": meetup["name"],
                    "title": template["title"],
                    "description": template["description"],
                    "date": event_date.isoformat(),
                    "start_time": "18:30",
                    "end_time": f"{18 + int(template['duration_hours'])}:{30 if template['duration_hours'] % 1 else '00'}",
                    "venue_id": venue["id"] if venue else "venue_startup_va",
                    "venue_name": venue["name"] if venue else "Startup Virginia",
                    "venue_address": venue["address"] if venue else "1717 E Cary St, Richmond, VA 23223",
                    "speaker": template["speaker"],
                    "speaker_bio": template["speaker_bio"],
                    "capacity": venue["capacity"] if venue else 150,
                    "registered": min(venue["capacity"] - 20 if venue else 130, 
                                    int(meetup["member_count"] * 0.15)),  # ~15% turnout
                    "status": "upcoming",
                    "tags": template["tags"],
                    "requirements": ["Laptop recommended", "Basic programming knowledge"],
                    "cost": "Free",
                    "rsvp_url": f"https://meetup.com/{meetup['name'].lower().replace(' ', '-')}/events/{uuid.uuid4().hex[:8]}",
                    "parking_info": "Street parking available, paid parking in nearby garages"
                }
                events.append(event)
        
        return events
    
    def get_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return all generated data."""
        return {
            "venues": self.venues,
            "companies": self.companies,
            "meetups": self.meetups,
            "events": self.events
        }
    
    def save_to_files(self, output_dir: str = "data"):
        """Save data to JSON files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        data = self.get_all_data()
        for category, items in data.items():
            filename = os.path.join(output_dir, f"{category}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, default=str)
        
        print(f"Saved {sum(len(items) for items in data.values())} items to {output_dir}/")


if __name__ == "__main__":
    generator = RichmondDataGenerator()
    generator.save_to_files()
    
    # Print summary
    data = generator.get_all_data()
    print("\nGenerated Richmond Tech Community Data:")
    for category, items in data.items():
        print(f"  {category.title()}: {len(items)} items")
    
    # Show next few events
    print("\nUpcoming Events:")
    for event in sorted(data["events"][:5], key=lambda x: x["date"]):
        print(f"  {event['date'][:10]} - {event['title']} at {event['venue_name']}")