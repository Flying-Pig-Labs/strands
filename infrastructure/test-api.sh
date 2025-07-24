#!/bin/bash

# Strands Richmond Demo - API Testing Script
# Comprehensive testing of deployed API endpoints

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Richmond MCP + Strands AI Agent API${NC}"

# Get API URL from stack outputs
API_URL=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' --output text 2>/dev/null)

if [ -z "$API_URL" ]; then
    echo -e "${RED}❌ Could not retrieve API URL. Stack may not be deployed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API URL: $API_URL${NC}"

# Test 1: Health Check
echo -e "\n${BLUE}Test 1: Health Check${NC}"
echo "Testing: GET ${API_URL}health"

HEALTH_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" "${API_URL}health")
HEALTH_BODY=$(echo $HEALTH_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $HEALTH_STATUS"
echo "Response Body:"
echo $HEALTH_BODY | jq '.' 2>/dev/null || echo $HEALTH_BODY

if [ "$HEALTH_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

# Test 2: Data Seeding
echo -e "\n${BLUE}Test 2: Data Seeding${NC}"
echo "Testing: POST ${API_URL}seed-data"

SEED_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}seed-data")
SEED_BODY=$(echo $SEED_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
SEED_STATUS=$(echo $SEED_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $SEED_STATUS"
echo "Response Body:"
echo $SEED_BODY | jq '.' 2>/dev/null || echo $SEED_BODY

if [ "$SEED_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Data seeding successful${NC}"
else
    echo -e "${YELLOW}⚠️  Data seeding may have issues (could be already seeded)${NC}"
fi

# Wait a moment for data to be available
sleep 2

# Test 3: Query About Richmond Meetups
echo -e "\n${BLUE}Test 3: Richmond Meetups Query${NC}"
MEETUP_QUERY='{"query": "What tech meetups are happening in Richmond?"}'
echo "Testing: POST ${API_URL}ask"
echo "Query: $MEETUP_QUERY"

MEETUP_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}ask" \
  -H "Content-Type: application/json" \
  -d "$MEETUP_QUERY")

MEETUP_BODY=$(echo $MEETUP_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
MEETUP_STATUS=$(echo $MEETUP_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $MEETUP_STATUS"
echo "Response Body:"
echo $MEETUP_BODY | jq '.' 2>/dev/null || echo $MEETUP_BODY

if [ "$MEETUP_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Meetup query successful${NC}"
else
    echo -e "${RED}❌ Meetup query failed${NC}"
fi

# Test 4: Query About Richmond Companies
echo -e "\n${BLUE}Test 4: Richmond Companies Query${NC}"
COMPANY_QUERY='{"query": "Tell me about tech companies in Richmond, VA"}'
echo "Testing: POST ${API_URL}ask"
echo "Query: $COMPANY_QUERY"

COMPANY_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}ask" \
  -H "Content-Type: application/json" \
  -d "$COMPANY_QUERY")

COMPANY_BODY=$(echo $COMPANY_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
COMPANY_STATUS=$(echo $COMPANY_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $COMPANY_STATUS"
echo "Response Body:"
echo $COMPANY_BODY | jq '.' 2>/dev/null || echo $COMPANY_BODY

if [ "$COMPANY_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Company query successful${NC}"
else
    echo -e "${RED}❌ Company query failed${NC}"
fi

# Test 5: Query About Venues
echo -e "\n${BLUE}Test 5: Richmond Venues Query${NC}"
VENUE_QUERY='{"query": "Where do tech meetups happen in Richmond?"}'
echo "Testing: POST ${API_URL}ask"
echo "Query: $VENUE_QUERY"

VENUE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}ask" \
  -H "Content-Type: application/json" \
  -d "$VENUE_QUERY")

VENUE_BODY=$(echo $VENUE_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
VENUE_STATUS=$(echo $VENUE_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $VENUE_STATUS"
echo "Response Body:"
echo $VENUE_BODY | jq '.' 2>/dev/null || echo $VENUE_BODY

if [ "$VENUE_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Venue query successful${NC}"
else
    echo -e "${RED}❌ Venue query failed${NC}"
fi

# Test 6: General AI Query (Non-Richmond)
echo -e "\n${BLUE}Test 6: General AI Query${NC}"
GENERAL_QUERY='{"query": "What are the benefits of using serverless architecture?"}'
echo "Testing: POST ${API_URL}ask"
echo "Query: $GENERAL_QUERY"

GENERAL_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}ask" \
  -H "Content-Type: application/json" \
  -d "$GENERAL_QUERY")

GENERAL_BODY=$(echo $GENERAL_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
GENERAL_STATUS=$(echo $GENERAL_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $GENERAL_STATUS"
echo "Response Body:"
echo $GENERAL_BODY | jq '.' 2>/dev/null || echo $GENERAL_BODY

if [ "$GENERAL_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ General query successful${NC}"
else
    echo -e "${RED}❌ General query failed${NC}"
fi

# Test 7: Error Handling - Invalid Request
echo -e "\n${BLUE}Test 7: Error Handling${NC}"
INVALID_QUERY='{"invalid": "missing query field"}'
echo "Testing: POST ${API_URL}ask"
echo "Query: $INVALID_QUERY"

INVALID_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_URL}ask" \
  -H "Content-Type: application/json" \
  -d "$INVALID_QUERY")

INVALID_BODY=$(echo $INVALID_RESPONSE | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
INVALID_STATUS=$(echo $INVALID_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $INVALID_STATUS"
echo "Response Body:"
echo $INVALID_BODY | jq '.' 2>/dev/null || echo $INVALID_BODY

if [ "$INVALID_STATUS" == "400" ]; then
    echo -e "${GREEN}✅ Error handling working correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Expected 400 status code for invalid request${NC}"
fi

# Test 8: CORS Headers
echo -e "\n${BLUE}Test 8: CORS Headers${NC}"
echo "Testing CORS preflight request"

CORS_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X OPTIONS "${API_URL}ask" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type")

CORS_STATUS=$(echo $CORS_RESPONSE | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Status Code: $CORS_STATUS"

if [ "$CORS_STATUS" == "200" ] || [ "$CORS_STATUS" == "204" ]; then
    echo -e "${GREEN}✅ CORS preflight successful${NC}"
else
    echo -e "${YELLOW}⚠️  CORS preflight may have issues${NC}"
fi

# Summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "=================================="
echo "API Endpoint: $API_URL"
echo ""
echo "✅ Tests should show 200 status codes for successful requests"
echo "✅ Health check should return service status"
echo "✅ Data seeding should populate DynamoDB"
echo "✅ Richmond-specific queries should use local data"
echo "✅ General queries should work without local data"
echo "✅ Error handling should return appropriate status codes"
echo ""

# Performance note
echo -e "${YELLOW}💡 Performance Notes:${NC}"
echo "- First API calls may be slow due to Lambda cold starts"
echo "- Subsequent calls should be faster (warm Lambda)"
echo "- Consider implementing API warming for production use"
echo ""

# Monitoring suggestion
echo -e "${BLUE}📈 Monitoring:${NC}"
echo "View real-time logs:"
echo "aws logs tail /aws/lambda/\$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==\`LambdaFunctionName\`].OutputValue' --output text) --profile personal --follow"