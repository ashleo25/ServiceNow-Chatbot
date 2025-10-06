# Configuration Guide

## Environment Setup

### 1. Create .env file

Run the setup script:
```bash
cd backend
./setup_env.sh
```

Or manually copy the template:
```bash
cp config.env .env
```

### 2. Configure Azure OpenAI

Get your Azure OpenAI credentials from the Azure Portal:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the following values to your `.env` file:

```bash
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 3. Configure OCI (Optional)

If you want to use OCI Agents, get your OCI credentials:

1. Go to [OCI Console](https://cloud.oracle.com)
2. Navigate to Identity & Security > API Keys
3. Create a new API key and download the private key
4. Copy the following values to your `.env` file:

```bash
OCI_TENANCY_ID=ocid1.tenancy.oc1..aaaaaaa...
OCI_USER_ID=ocid1.user.oc1..aaaaaaa...
OCI_FINGERPRINT=aa:bb:cc:dd:ee:ff:gg:hh:ii:jj:kk:ll:mm:nn:oo:pp
OCI_PRIVATE_KEY_PATH=path/to/your/private_key.pem
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..aaaaaaa...
SEARCH_AGENT_ENDPOINT_ID=ocid1.agentendpoint.oc1..aaaaaaa...
TICKET_AGENT_ENDPOINT_ID=ocid1.agentendpoint.oc1..aaaaaaa...
```

### 4. Configure ServiceNow (Optional)

If you want to use ServiceNow integration:

```bash
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

## Testing the Configuration

### Test Azure OpenAI
```bash
cd backend
source ../sn-oci-adk-venv/bin/activate
python -c "
from services.azure_openai_service import AzureOpenAIService
service = AzureOpenAIService()
result = service.detect_intent('My laptop is not working')
print(f'Intent: {result[\"intent\"]}')
print(f'Confidence: {result[\"confidence\"]}')
print(f'Using Azure: {service.use_azure}')
"
```

### Test Hybrid System
```bash
cd backend
source ../sn-oci-adk-venv/bin/activate
python -c "
from services.hybrid_chatbot_service import HybridChatbotService
chatbot = HybridChatbotService()
result = chatbot.process_message('My laptop is not working')
print(f'Response: {result[\"response\"]}')
print(f'AI Provider: {result[\"ai_provider\"]}')
"
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_API_VERSION` | API version | No | `2024-02-15-preview` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name | No | `gpt-4` |
| `OCI_TENANCY_ID` | OCI tenancy OCID | Optional | `ocid1.tenancy.oc1..aaaaaaa...` |
| `OCI_USER_ID` | OCI user OCID | Optional | `ocid1.user.oc1..aaaaaaa...` |
| `OCI_FINGERPRINT` | OCI API key fingerprint | Optional | `aa:bb:cc:dd:ee:ff...` |
| `OCI_PRIVATE_KEY_PATH` | Path to OCI private key | Optional | `./keys/oci_key.pem` |
| `OCI_COMPARTMENT_ID` | OCI compartment OCID | Optional | `ocid1.compartment.oc1..aaaaaaa...` |
| `SEARCH_AGENT_ENDPOINT_ID` | OCI search agent endpoint | Optional | `ocid1.agentendpoint.oc1..aaaaaaa...` |
| `TICKET_AGENT_ENDPOINT_ID` | OCI ticket agent endpoint | Optional | `ocid1.agentendpoint.oc1..aaaaaaa...` |

## Troubleshooting

### Azure OpenAI Issues
- **Error: "API key not found"**: Check your `AZURE_OPENAI_API_KEY` in `.env`
- **Error: "Invalid endpoint"**: Verify your `AZURE_OPENAI_ENDPOINT` URL
- **Error: "Deployment not found"**: Check your `AZURE_OPENAI_DEPLOYMENT_NAME`

### OCI Issues
- **Error: "Configuration incomplete"**: Ensure all OCI variables are set
- **Error: "Private key not found"**: Check the path in `OCI_PRIVATE_KEY_PATH`
- **Error: "Agent endpoint not found"**: Verify your agent endpoint IDs

### General Issues
- **Error: "Module not found"**: Run `pip install -r requirements.txt`
- **Error: "Port already in use"**: Change `API_PORT` in `.env` or kill existing process
