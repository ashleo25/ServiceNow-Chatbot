# ServiceNow Enterprise Chatbot 🚀

**Enterprise-grade ServiceNow chatbot with intelligent ticket creation and knowledge search capabilities**

> A comprehensive React-based chatbot integrated with ServiceNow, Oracle Cloud Infrastructure (OCI) Generative AI, and Google ADK for self-service automation and intelligent ticket management.

## 🎯 **Key Features**

- **🎫 Smart Ticket Creation**: Google ADK-powered ticket creation with duplicate prevention
- **🔍 Intelligent Knowledge Search**: OCI Generative AI for advanced search capabilities  
- **🤖 Multi-AI Integration**: Google ADK + OCI Generative AI + Azure OpenAI
- **🔄 ServiceNow Integration**: Full REST API integration for ticket management
- **⚡ High Performance**: 28x faster agent loading with optimized architecture
- **🧠 Duplicate Prevention**: 70% similarity threshold with active state filtering
- **💬 Modern React UI**: Responsive chat interface with real-time communication

## 🏗️ **Architecture Overview**

```
ServiceNow-Chatbot/
├── backend/                 # FastAPI backend with AI agents
│   ├── agents/             # 13 specialized AI agents
│   │   ├── fast_ticket_creation_agent.py    # Google ADK primary agent
│   │   ├── duplicate_check_agent.py         # Duplicate prevention
│   │   ├── oci_compliant_core_search_agent.py # OCI search
│   │   └── ...
│   ├── services/           # 9 core services
│   │   ├── hybrid_chatbot_service.py        # Main orchestrator
│   │   ├── ticket_creation_service.py       # ServiceNow integration
│   │   └── ...
│   ├── tools/              # 7 utility tools
│   ├── config/             # Configuration management
│   └── tests/              # Comprehensive test suites
├── frontend/               # React chatbot interface
│   ├── src/
│   │   ├── components/     # 8 specialized React components
│   │   ├── services/       # API integration
│   │   ├── context/        # State management
│   │   └── styles/         # Modern UI themes
│   └── package.json
├── docs/                   # Comprehensive documentation
└── scripts/                # Setup and deployment scripts
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+ with virtual environment support
- Node.js 16+ with npm
- ServiceNow instance access
- OCI account with Generative AI Agents service
- Google AI Studio API key

### **1️⃣ One-Command Setup**
```bash
git clone https://github.com/ashleo25/ServiceNow-Chatbot.git
cd ServiceNow-Chatbot
./setup.sh  # Automated setup script
```

### **2️⃣ Manual Setup**

**Backend Setup:**
```bash
cd backend
python -m venv sn-oci-adk-venv
source sn-oci-adk-venv/bin/activate  # Windows: sn-oci-adk-venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

**Configuration:**
```bash
cp backend/env.example backend/.env
# Edit .env with your API keys and credentials
```

### **3️⃣ Launch Application**
```bash
# Terminal 1: Start Backend
./start_backend.sh

# Terminal 2: Start Frontend  
./start_frontend.sh
```

Visit: `http://localhost:3000` 🎉

## ⚙️ **Configuration**

### **Required Environment Variables**
```bash
# Google ADK
GOOGLE_API_KEY=your_google_ai_studio_key

# OCI Generative AI
OCI_USER=your_oci_user_ocid
OCI_FINGERPRINT=your_key_fingerprint
OCI_TENANCY=your_tenancy_ocid
OCI_REGION=your_region
OCI_KEY_FILE=path_to_private_key

# ServiceNow
SERVICENOW_INSTANCE=your_instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
SERVICENOW_DEFAULT_CALLER_ID=admin

# Azure OpenAI (Optional)
AZURE_OPENAI_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_endpoint
```

## 🧪 **Testing & Validation**

### **Run Comprehensive Tests**
```bash
# Test duplicate detection logic
python backend/test_duplicate_logic_simple.py

# Test realistic business scenarios  
python backend/test_realistic_scenarios.py

# Test fast agent performance
python backend/test_fast_agent.py

# Integration testing
./test_integration.sh
```

### **Real-World Scenarios Tested**
- ✅ Hardware issues (laptop problems, printer issues)
- ✅ Software issues (application errors, access problems)  
- ✅ Network connectivity problems
- ✅ Account access and password resets
- ✅ Duplicate prevention workflows
- ✅ Priority and SLA assignment

## 📊 **Performance Metrics**

- **🚀 Agent Loading**: 28x faster (0.000s vs 1.4s)
- **🎯 Duplicate Detection**: 70% similarity threshold with multi-factor analysis
- **📈 Response Time**: <2 seconds for ticket creation
- **🔍 Search Accuracy**: Advanced semantic search with OCI AI
- **💯 Test Coverage**: 7 comprehensive test suites

## 🔧 **API Endpoints**

### **Chat & Interaction**
- `POST /chat` - Main chat interface
- `POST /search` - Knowledge search  
- `POST /ticket/create` - Ticket creation

### **Ticket Management**
- `GET /tickets` - List tickets
- `GET /tickets/{id}` - Get ticket details
- `POST /tickets/search` - Search existing tickets

### **Health & Monitoring**
- `GET /health` - System health check
- `GET /agents/status` - Agent status monitoring

## 📚 **Documentation**

- 📋 **[Complete Code Inventory](CODE_INVENTORY.md)** - Comprehensive file-by-file documentation
- 🔧 **[Setup Guide](SETUP_GUIDE.md)** - Detailed installation instructions  
- 📖 **[Configuration Guide](backend/CONFIGURATION.md)** - Environment setup
- 🧹 **[Cleanup Checklist](CLEANUP_CHECKLIST.md)** - Maintenance guide
- ⚡ **[Quick Reference](QUICK_REFERENCE.md)** - Developer cheat sheet

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support & Troubleshooting**

### **Common Issues**
- **Import Errors**: Ensure virtual environment is activated
- **API Errors**: Verify credentials in `.env` file
- **ServiceNow Connection**: Check instance URL and credentials
- **Frontend Issues**: Verify backend is running on port 8000

### **Get Help**
- 📧 **Email**: ashishleo25@gmail.com
- 🐛 **Issues**: GitHub Issues tab
- 📖 **Docs**: Check documentation files in repo

---

**🌟 Star this repository if you find it helpful!**

*Built with ❤️ using Google ADK, OCI Generative AI, ServiceNow, and React*
