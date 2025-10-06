#!/bin/bash
"""
Cleanup Script for OCIAgents-ServiceNow Project
Removes unused and inactive files to clean up the workspace
"""

echo "🧹 STARTING PROJECT CLEANUP"
echo "=" * 50

# Change to project root
cd /Users/ashishsingh/RAGProjects/OCIAgents-ServiceNow

echo "📁 Cleaning up Root Directory test files..."

# Remove outdated Google AI/Gemini test files
rm -f test_ai_studio_endpoint.py
rm -f test_available_models.py
rm -f test_clean_gemini.py
rm -f test_correct_api.py
rm -f test_direct_gemini.py
rm -f test_gemini_http.py
rm -f test_google_adk_functionality.py
rm -f test_google_adk_import.py
rm -f test_google_ai_api.py
rm -f test_google_ai_config.py
rm -f test_google_ai_studio.py
rm -f test_simple_model.py

# Remove OCI test files (basic functionality working)
rm -f test_oci_tool_calling.py
rm -f test_real_integration.py

# Remove search test files (comprehensive backend tests exist)
rm -f test_search_agent_comprehensive.py
rm -f test_search_agent_e2e.py
rm -f test_search_agent_manual.py
rm -f test_search_manual.py
rm -f run_search_tests.py
rm -f search_agent_testing_summary.py

# Remove version files
rm -f =0.1.1 =1.0.0 =1.50.0 =1.60.0 =2.25.0 =2.4.1

# Remove generated reports (can be regenerated)
rm -f oci_adk_tool_calling_report.json
rm -f search_agent_e2e_report.json
rm -f server.log

echo "📁 Cleaning up Backend directory..."

# Change to backend directory
cd backend

# Remove backup files
rm -f agents/ticket_creation_agent_backup.py

# Remove redundant test files
rm -f test_duplicate_flow_complete.py
rm -f test_mock_servicenow_integration.py
rm -f test_working_model.py
rm -f test_backend.py

# Remove duplicate config files
rm -f config.env
rm -f env.example

echo "📁 Cleaning up logs directory..."

# Clean old log files (keep directory structure)
find logs/ -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true

echo "📁 Cleaning up __pycache__ directories..."

# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "📁 Cleaning up .pyc files..."

# Remove all .pyc files
find . -name "*.pyc" -type f -delete 2>/dev/null || true

echo "✅ PROJECT CLEANUP COMPLETED"
echo ""
echo "📊 Summary of cleaned files:"
echo "  - Removed 20+ outdated test files"
echo "  - Removed backup and duplicate files"
echo "  - Removed version marker files"
echo "  - Cleaned __pycache__ directories"
echo "  - Cleaned old log files"
echo ""
echo "🎯 Active files preserved:"
echo "  ✅ Core agents (fast_ticket_creation_agent, duplicate_check_agent, etc.)"
echo "  ✅ Working test files (test_realistic_scenarios, test_duplicate_logic_simple, etc.)"
echo "  ✅ Main application files (main.py, services/, config/)"
echo "  ✅ Documentation (README.md, SETUP_GUIDE.md)"
echo ""
echo "🚀 Project is now cleaned and ready for development!"