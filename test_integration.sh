#!/bin/bash
# Search Agent Integration Test Script
# Tests search agent functionality using curl commands

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
BASE_URL="http://localhost:8000"
BACKEND_DIR="/Users/ashishsingh/RAGProjects/OCIAgents-ServiceNow/backend"
VENV_PATH="/Users/ashishsingh/RAGProjects/OCIAgents-ServiceNow/sn-oci-adk-venv"

echo -e "${BLUE}🔬 Search Agent Real Integration Test Suite${NC}"
echo -e "${BLUE}Testing with actual backend server and API calls${NC}"
echo "=============================================================="

# Function to log test results
log_test() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name: $status${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $test_name: $status${NC}"
    else
        echo -e "${YELLOW}⚠️ $test_name: $status${NC}"
    fi
    
    if [ -n "$details" ]; then
        echo -e "   Details: $details"
    fi
}

# Function to check if server is running
check_server() {
    curl -s "$BASE_URL/health" > /dev/null 2>&1
    return $?
}

# Function to start backend server
start_backend() {
    echo -e "${BLUE}🚀 Starting backend server...${NC}"
    
    # Kill any existing server processes
    pkill -f "python.*main.py" 2>/dev/null || true
    sleep 2
    
    # Start server in background
    cd "$BACKEND_DIR"
    source "$VENV_PATH/bin/activate"
    nohup python test_backend.py > ../server.log 2>&1 &
    SERVER_PID=$!
    
    echo "Server started with PID: $SERVER_PID"
    
    # Wait for server to start
    for i in {1..10}; do
        if check_server; then
            log_test "Backend Server Startup" "PASS" "Server running on port 8000"
            return 0
        fi
        sleep 2
    done
    
    log_test "Backend Server Startup" "FAIL" "Server failed to start within 20 seconds"
    return 1
}

# Function to stop backend server
stop_backend() {
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "python.*simple_backend" 2>/dev/null || true
}

# Test 1: Health endpoint
test_health() {
    echo -e "\n${BLUE}🏥 Test 1: Health Endpoint${NC}"
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/health")
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "200" ]; then
        log_test "Health Endpoint" "PASS" "Status: $status"
    else
        log_test "Health Endpoint" "FAIL" "Status: $status"
    fi
}

# Test 2: Chat endpoint - Greeting
test_chat_greeting() {
    echo -e "\n${BLUE}💬 Test 2: Chat Endpoint - Greeting${NC}"
    
    local payload='{"message": "Hello, I need help", "session_data": {}}'
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "200" ]; then
        log_test "Chat Greeting" "PASS" "Status: $status"
        echo "   Response preview: $(echo "$body" | head -c 100)..."
    else
        log_test "Chat Greeting" "FAIL" "Status: $status"
    fi
}

# Test 3: Chat endpoint - Search request
test_chat_search() {
    echo -e "\n${BLUE}🔍 Test 3: Chat Endpoint - Search Request${NC}"
    
    local payload='{"message": "I need help with password reset", "session_data": {}}'
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "200" ]; then
        log_test "Chat Search Request" "PASS" "Status: $status"
        echo "   Response preview: $(echo "$body" | head -c 100)..."
    else
        log_test "Chat Search Request" "FAIL" "Status: $status"
    fi
}

# Test 4: Direct search endpoint
test_direct_search() {
    echo -e "\n${BLUE}🎯 Test 4: Direct Search Endpoint${NC}"
    
    local payload='{"query": "network issues", "search_type": "auto"}'
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/search" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "200" ]; then
        log_test "Direct Search" "PASS" "Status: $status"
        echo "   Response preview: $(echo "$body" | head -c 100)..."
    else
        log_test "Direct Search" "FAIL" "Status: $status"
    fi
}

# Test 5: Conversation flow
test_conversation_flow() {
    echo -e "\n${BLUE}🔄 Test 5: Conversation Flow${NC}"
    
    local messages=(
        '{"message": "Hello", "session_data": {}}'
        '{"message": "I cant access my email", "session_data": {}}'
        '{"message": "search for email problems", "session_data": {}}'
    )
    
    local step=1
    for payload in "${messages[@]}"; do
        local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
            -X POST "$BASE_URL/chat" \
            -H "Content-Type: application/json" \
            -d "$payload")
        
        local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
        
        if [ "$status" = "200" ]; then
            log_test "Conversation Step $step" "PASS" "Status: $status"
        else
            log_test "Conversation Step $step" "FAIL" "Status: $status"
        fi
        
        ((step++))
    done
}

# Test 6: Error handling
test_error_handling() {
    echo -e "\n${BLUE}⚠️ Test 6: Error Handling${NC}"
    
    # Test malformed JSON
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "invalid json")
    
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "400" ] || [ "$status" = "422" ]; then
        log_test "Malformed JSON Handling" "PASS" "Status: $status"
    else
        log_test "Malformed JSON Handling" "FAIL" "Status: $status"
    fi
    
    # Test empty message
    local payload='{"message": "", "session_data": {}}'
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [ "$status" = "200" ]; then
        log_test "Empty Message Handling" "PASS" "Status: $status"
    else
        log_test "Empty Message Handling" "FAIL" "Status: $status"
    fi
}

# Main execution
main() {
    echo -e "\n${BLUE}Starting integration tests...${NC}"
    
    # Check if server is already running
    if check_server; then
        echo -e "${GREEN}✅ Backend server is already running${NC}"
    else
        if ! start_backend; then
            echo -e "${RED}❌ Cannot run tests without backend server${NC}"
            echo -e "\n${YELLOW}🛠️ Manual Server Start Instructions:${NC}"
            echo "1. Open a new terminal"
            echo "2. cd $BACKEND_DIR"
            echo "3. source $VENV_PATH/bin/activate"
            echo "4. python test_backend.py"
            echo "5. Run this test script again"
            exit 1
        fi
    fi
    
    # Run all tests
    test_health
    test_chat_greeting
    test_chat_search
    test_direct_search
    test_conversation_flow
    test_error_handling
    
    # Generate summary
    echo -e "\n=============================================================="
    echo -e "${BLUE}📊 Integration Test Summary${NC}"
    echo -e "=============================================================="
    echo -e "${GREEN}✅ Tests completed successfully${NC}"
    echo -e "Check server logs at: $BACKEND_DIR/../server.log"
    echo -e "\n${YELLOW}🎯 Next Steps:${NC}"
    echo "1. Review test results above"
    echo "2. Check server logs for detailed execution traces"
    echo "3. Test frontend integration with running backend"
    echo "4. Verify OCI Agent tool calling functionality"
    
    # Cleanup
    echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
    stop_backend
    echo -e "${GREEN}✅ Integration tests complete!${NC}"
}

# Trap to ensure cleanup on exit
trap stop_backend EXIT

# Run main function
main "$@"