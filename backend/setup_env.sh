#!/bin/bash

# Setup script to create .env file from template
echo "Setting up environment configuration..."

# Copy config.env to .env
if [ -f "config.env" ]; then
    cp config.env .env
    echo "✅ Created .env file from config.env"
    echo ""
    echo "📝 Next steps:"
    echo "1. Edit .env file with your actual credentials:"
    echo "   - Azure OpenAI API Key and Endpoint"
    echo "   - OCI credentials and endpoint IDs"
    echo "   - ServiceNow credentials (if using)"
    echo ""
    echo "2. Get Azure OpenAI credentials from:"
    echo "   https://portal.azure.com -> Azure OpenAI -> Your Resource"
    echo ""
    echo "3. Get OCI credentials from:"
    echo "   https://cloud.oracle.com -> Identity & Security -> API Keys"
    echo ""
    echo "4. Start the backend server:"
    echo "   source ../sn-oci-adk-venv/bin/activate && python main.py"
else
    echo "❌ config.env file not found!"
    exit 1
fi
