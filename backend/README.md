# Richmond Tech Community - Backend & Database

This directory contains the backend/database layer for the Richmond-specific MCP + Strands AI Agent demo.

## 🏗️ Architecture Overview

The backend consists of three main components:

1. **Sample Data Generation** (`data/sample_data.py`) - Creates realistic Richmond tech community data
2. **Database Layer** (`models/database.py`) - DynamoDB operations and data models  
3. **Data Service** (`backend/data_service.py`) - High-level business logic and natural language processing

## 📊 Data Model

The system uses a single DynamoDB table with a composite key structure:

### Table Structure: `RichmondTechCommunity`
- **Primary Key**: `PK` (Partition Key) + `SK` (Sort Key)
- **GSI1**: `GSI1PK` + `GSI1SK` for efficient queries
- **Billing**: Pay-per-request

### Entity Types

#### Venues
```
PK: VENUE#{venue_id}
SK: VENUE#{venue_id}
GSI1PK: VENUE
GSI1SK: {venue_name}
```

#### Companies  
```
PK: COMPANY#{company_id}
SK: COMPANY#{company_id}
GSI1PK: COMPANY
GSI1SK: {company_name}
```

#### Meetup Groups
```
PK: MEETUP#{meetup_id}
SK: MEETUP#{meetup_id}
GSI1PK: MEETUP
GSI1SK: {meetup_name}
```

#### Events
```
PK: EVENT#{event_id}
SK: EVENT#{event_id}
GSI1PK: EVENT#{YYYY-MM-DD}
GSI1SK: {start_time}
```

## 🎯 Sample Data Overview

The generated sample data includes:

### 🏢 **5 Venues**
- **Startup Virginia** - Premier startup incubator (150 capacity)
- **Common House** - Upscale downtown event space (200 capacity)
- **VCU School of Engineering** - University venue (300 capacity)
- **Capital One Café** - Casual meetup space (50 capacity)
- **Libbie Mill Library** - Modern library facilities (80 capacity)

### 🏢 **5 Companies**
- **CarMax** - Fortune 500 automotive tech (25K employees)
- **Capital One** - Major fintech presence (50K employees)
- **Flying Pig Labs** - Boutique software development (15 employees)
- **Dominion Energy** - Energy tech division (16K employees)
- **WillowTree** - Mobile development company (300 employees)

### 👥 **5 Meetup Groups**
- **RVA Cloud Wranglers** - Cloud computing (450 members)
- **Richmond Python User Group** - Python programming (320 members)
- **RVA.js** - JavaScript development (280 members)
- **Richmond Data Science Meetup** - ML/Analytics (190 members)
- **RVA Cybersecurity Guild** - Information security (220 members)

### 📅 **12 Events** (Next 3 months)
- Weekly rotating events from different meetup groups
- Realistic speakers from local companies
- Appropriate venues based on group size and topic
- Tech-focused topics (AWS, Python, React, AI, Security)

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
```bash
# Set up AWS CLI or use environment variables
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Create Database and Load Data
```bash
# Full setup with sample data
python scripts/setup_database.py --show-queries

# Or step by step:
python scripts/setup_database.py          # Create table and load data
python scripts/setup_database.py --verify-only --show-queries  # Test queries
```

### 4. Generate Fresh Sample Data (Optional)
```bash
python data/sample_data.py                # Creates JSON files in data/
```

## 🧪 Testing

### Run Basic Tests
```bash
python tests/test_database.py
```

### Run Full Test Suite
```bash
pip install pytest pytest-mock
pytest tests/test_database.py -v
```

### Test Database Setup
```bash
python scripts/setup_database.py --verify-only
```

## 📚 Usage Examples

### Direct Database Operations
```python
from models.database import DynamoDBManager

# Initialize
db = DynamoDBManager(table_name="RichmondTechCommunity")

# Get next event
events = db.get_upcoming_events(days_ahead=30)
next_event = events[0] if events else None

# Search events
python_events = db.search_events("Python")

# Get venue info
venue = db.get_venue("startup_va")
```

### High-Level Data Service
```python
from backend.data_service import RichmondTechDataService

# Initialize service
service = RichmondTechDataService()

# Natural language queries
result = service.natural_language_search("What's the next tech meetup?")

# Specific queries
next_meetup = service.get_next_tech_meetup()
python_events = service.search_events_by_topic("Python")
venue_info = service.get_venue_information("Startup Virginia")
```

### Convenience Functions
```python
from backend.data_service import get_richmond_tech_info, get_next_meetup_info

# Quick queries
info = get_richmond_tech_info("next JavaScript meetup")
next_event = get_next_meetup_info()
```

## 🎯 Demo Queries

The system is designed to handle these demo scenarios:

### "What's the next tech meetup happening in Richmond?"
```python
service = RichmondTechDataService()
event = service.get_next_tech_meetup()
# Returns: "Serverless Architecture Best Practices on July 31st at Startup Virginia"
```

### "Are there any Python events coming up?"
```python
events = service.search_events_by_topic("Python", limit=3)
# Returns list of Python-related events with dates and venues
```

### "Tell me about Startup Virginia"
```python
venue = service.get_venue_information("Startup Virginia")
# Returns venue details, capacity, amenities, upcoming events
```

### "What tech companies are in Richmond?"
```python
companies = service.get_tech_companies_info()
# Returns CarMax, Capital One, etc. with employee counts and tech stacks
```

## 🔍 Key Features for MCP Integration

### Optimized for Agent Queries
- **Natural language processing** - Handles conversational queries
- **Flexible search** - Find events by topic, speaker, venue, or date range
- **Rich context** - Returns venue details, meetup info, and related data
- **Future-focused** - Emphasizes upcoming events and relevant information

### MCP Tool Functions
The data service provides these key functions for MCP tools:

1. **`get_next_tech_meetup()`** - Primary demo query
2. **`search_events_by_topic()`** - Technology-specific searches  
3. **`get_venue_information()`** - Venue details and logistics
4. **`natural_language_search()`** - Flexible query processing
5. **`get_tech_community_summary()`** - Overview and statistics

### Error Handling
- Graceful degradation when AWS services are unavailable
- Comprehensive logging for debugging
- Input validation and sanitization
- Type hints and structured responses

## 📊 Performance Considerations

### DynamoDB Optimization
- **Single table design** - Minimizes queries and costs
- **Composite key structure** - Efficient access patterns
- **GSI for queries** - Optimized secondary access
- **Pay-per-request billing** - Cost-effective for demo usage

### Query Patterns
- **Get next event**: Single GSI query by date range
- **Search by topic**: Scan with filter (acceptable for demo data size)
- **Get venue events**: GSI query + filter
- **Popular meetups**: Single query with client-side sorting

### Caching Opportunities
- Venue and company data (rarely changes)
- Meetup group information (stable)
- Popular technology tags (computed from events)

## 🚀 Deployment Notes

### Lambda Compatibility
- **CommonJS modules** - Uses `require()` for Lambda compatibility
- **Decimal handling** - Converts DynamoDB Decimal types to float
- **Error boundary** - Handles AWS service exceptions gracefully
- **Lightweight dependencies** - Optimized for cold starts

### Environment Variables
```bash
# Required for production
DYNAMODB_TABLE_NAME=RichmondTechCommunity
AWS_REGION=us-east-1

# Optional
LOG_LEVEL=INFO
```

### IAM Permissions
The Lambda function needs these DynamoDB permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/RichmondTechCommunity",
        "arn:aws:dynamodb:us-east-1:*:table/RichmondTechCommunity/index/*"
      ]
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

**"Table not found"**
```bash
python scripts/setup_database.py  # Create table
```

**"No upcoming events"** 
```bash
python data/sample_data.py        # Regenerate with current dates
python scripts/setup_database.py --force  # Reload data
```

**"AWS credentials not found"**
```bash
aws configure                     # Set up credentials
# OR set environment variables
```

**"Import errors"**
```bash
pip install -r requirements.txt   # Install dependencies
export PYTHONPATH=$PWD            # Add current dir to path
```

### Debug Queries
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed DynamoDB logging
service = RichmondTechDataService()
service.natural_language_search("debug query")
```

## 📁 File Structure

```
backend/
├── README.md                 # This file
├── data_service.py          # High-level business logic
│
data/
├── sample_data.py           # Sample data generation
├── venues.json              # Generated venue data
├── companies.json           # Generated company data  
├── meetups.json             # Generated meetup data
└── events.json              # Generated event data

models/
└── database.py              # DynamoDB operations

scripts/
└── setup_database.py       # Database setup script

tests/
└── test_database.py        # Test suite
```

## 🔗 Integration Points

This backend integrates with:
- **MCP Server** - Provides tools for agent queries
- **Strands Agent** - Powers the AI reasoning layer
- **Lambda Handler** - Serverless API endpoint
- **API Gateway** - HTTP interface for queries

The data service is designed to be the primary interface between the AI agent and the Richmond tech community data, providing rich, contextual responses optimized for conversational AI interactions.