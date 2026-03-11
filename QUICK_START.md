# Nova Forge — Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Node.js 18+ with pnpm
- AWS Account (for Bedrock access)

### Step 1: Set Up Environment Variables

Create `.env` file in `research_agent/`:

```bash
# AWS Bedrock credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional: Supermemory
SUPERMEMORY_API_KEY=your_api_key

# Agent configuration
AGENT_URL=http://localhost:7777
```

### Step 2: Install Dependencies

```bash
# Backend dependencies
cd research_agent
pip install -e .
# OR with uv:
uv install

# Frontend dependencies
cd ../chat-app
pnpm install
```

### Step 3: Start the Backend

```bash
cd research_agent
python main.py
```

Expected output:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:7777
```

### Step 4: Test Backend Health

```bash
# In another terminal
curl http://localhost:7777/health
# Response: {"status":"ok"}
```

### Step 5: Start the Frontend

```bash
cd chat-app
pnpm dev
```

Visit: `http://localhost:3000/ingest`

## 🧪 Quick Tests

### Test 1: Basic Import Check

```bash
cd research_agent
python -c "from services.arxiv_client import ArxivClient; print('✓ ArxivClient OK')"
python -c "from services.supermemory import SupermemoryService; print('✓ SupermemoryService OK')"
python -c "from workflows.pasa_workflow import PaSaWorkflow; print('✓ PaSaWorkflow OK')"
```

### Test 2: Run Comprehensive Test Suite

```bash
cd research_agent
python test_api.py
```

This runs 50+ test cases covering:
- Module imports
- Component initialization
- API endpoints
- Data validation
- Error handling

### Test 3: arXiv Search Test

```python
python -c "
from services.arxiv_client import ArxivClient
client = ArxivClient()
papers = client.search('quantum computing', max_results=2)
print(f'Found {len(papers)} papers')
for p in papers:
    print(f'  - {p.title}')
"
```

### Test 4: Supermemory Operations

```python
python -c "
from services.supermemory import SupermemoryService
service = SupermemoryService()
doc = service.add_paper(
    paper_id='test-2401.00001',
    title='Test Paper',
    content='This is test content',
    abstract='Test abstract',
    authors=['Dr. Test'],
    categories=['cs.AI']
)
print(f'✓ Document stored: {doc.id}')
"
```

### Test 5: Manual API Test

```bash
# Start a new ingestion job
curl -X POST http://localhost:7777/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "container_tag": "test-ml",
    "max_candidates": 3,
    "citation_expansion": true
  }'

# Response: {"job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}

# Check job status (use the job_id from response)
curl http://localhost:7777/ingest/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Response: {"status": "processing", "progress": 50, ...}
```

### Test 6: Frontend Integration

1. Go to `http://localhost:3000/ingest`
2. Select a preset (e.g., "AI Research")
3. Click "Start Ingestion"
4. Watch logs update in real-time
5. View results and click "View in Knowledge Graph"
6. Navigate to graph tab to see visualization

## 📊 Expected Results

### Successful Backend Startup
```
INFO:     Uvicorn running on http://0.0.0.0:7777
INFO:     Application startup complete
```

### Successful Test Run
```
✓ NovaLiteClient imported successfully
✓ ArxivClient imported successfully
✓ SupermemoryService imported successfully
✓ PaSaWorkflow imported successfully
✓ FastAPI app imported successfully
... (50+ tests)

TEST SUMMARY
Total Tests: 50+
Passed: 50+
Failed: 0
```

### Successful Paper Search
```
Found 5 papers
  - Attention Is All You Need
  - BERT: Pre-training of Deep Bidirectional Transformers
  - GPT-2: Language Models are Unsupervised Multitask Learners
  ...
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Ensure you're in `research_agent` directory and ran `pip install -e .` |
| AWS auth error | Check AWS credentials in `.env` file and IAM permissions |
| arXiv timeout | Normal - retry or wait; arXiv API can be slow |
| Port 7777 in use | Kill process: `lsof -ti:7777 \| xargs kill -9` |
| Node modules error | Run `pnpm install` in `chat-app` directory |
| Cannot connect to agent | Ensure backend is running: `python main.py` |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `research_agent/main.py` | Backend entry point |
| `research_agent/services/` | Core services (Nova, arXiv, Supermemory) |
| `research_agent/workflows/pasa_workflow.py` | Main ingestion workflow |
| `chat-app/app/pages/ingest.vue` | Ingestion UI |
| `chat-app/app/pages/graph.vue` | Visualization UI |
| `chat-app/server/api/ingest.post.ts` | Frontend-to-backend bridge |

## 🎯 Common Tasks

### Add New Paper Source
1. Create new service in `research_agent/services/`
2. Implement search method
3. Add to `PaSaWorkflow` constructor
4. Update tests

### Add New Frontend Page
1. Create `.vue` file in `chat-app/app/pages/`
2. Add API call to `chat-app/server/api/`
3. Use components from `chat-app/app/components/`

### Debug an Issue
1. Enable verbose logging: `export LOG_LEVEL=DEBUG`
2. Check `.env` variables
3. Run test suite: `python test_api.py`
4. Check browser console (F12)
5. Check terminal output

## 📚 Next Steps

1. **Basic Testing**: Run `python test_api.py`
2. **Manual Testing**: Test endpoints with curl
3. **UI Testing**: Try ingestion on frontend
4. **Integration**: Connect to real Supermemory instance
5. **Deployment**: Set up production environment

## 🤝 Need Help?

- Check `IMPLEMENTATION_SUMMARY.md` for detailed documentation
- Review `update.md` for architecture details
- Check logs in terminal for error messages
- Ensure all environment variables are set

## ✅ Success Checklist

- [ ] `.env` file created with AWS credentials
- [ ] Dependencies installed (`pip install -e .`, `pnpm install`)
- [ ] Backend runs without errors (`python main.py`)
- [ ] Health endpoint responds (`curl http://localhost:7777/health`)
- [ ] Frontend starts (`pnpm dev`)
- [ ] Test suite passes (`python test_api.py`)
- [ ] Can search arXiv papers
- [ ] Can start ingestion job
- [ ] Can view results in frontend

---

**Status**: Ready to use  
**Last Updated**: 2024  
**Tested**: ✅ All core components