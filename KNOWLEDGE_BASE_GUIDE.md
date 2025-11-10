# AWS Bedrock Knowledge Base Integration Guide

## 🧠 What is a Knowledge Base?

AWS Bedrock Knowledge Bases enable **RAG (Retrieval Augmented Generation)** - the ability to enhance Claude's responses with information from your own documents and data sources.

### Benefits:
- 📚 **Domain-specific knowledge** - Claude can answer questions about your documents
- 🎯 **Accurate citations** - Responses include source references
- 🔄 **Always up-to-date** - Update your knowledge base without retraining
- 🔒 **Secure** - Your data stays in your AWS account

---

## 🚀 Quick Start

### 1. Create a Knowledge Base in AWS Bedrock Console

1. **Navigate to AWS Bedrock Console**
   - Open AWS Console → Bedrock → Knowledge bases
   - Click "Create knowledge base"

2. **Configure Knowledge Base**
   - **Name:** e.g., "Gaming Strategy KB"
   - **Description:** e.g., "League of Legends strategies and guides"
   - **IAM Role:** Create new or use existing (needs S3 and Bedrock permissions)

3. **Add Data Source**
   - **S3 bucket:** Select or create an S3 bucket
   - **Data location:** s3://your-bucket/knowledge-base/
   - **Upload documents:** PDF, TXT, MD, HTML, DOC, DOCX
   - **Supported formats:** Text documents, web pages, structured data

4. **Configure Embedding Model**
   - **Model:** Amazon Titan Embeddings G1 - Text (recommended)
   - **Chunk strategy:** Default (300 tokens with 20% overlap)

5. **Vector Database**
   - **Option 1:** OpenSearch Serverless (managed, easy)
   - **Option 2:** Pinecone, Redis, or custom

6. **Sync Data**
   - Click "Sync" to process your documents
   - This creates vector embeddings of your content
   - Wait for sync to complete (may take a few minutes)

7. **Copy Knowledge Base ID**
   - After creation, copy the Knowledge Base ID (e.g., `ABCDEFGHIJ`)

---

## ⚙️ Configuration

### Update .env File

```bash
# Enable Knowledge Base
KNOWLEDGE_BASE_ID=ABCDEFGHIJ  # Your KB ID from AWS Console
KNOWLEDGE_BASE_ENABLED=true
KB_MAX_RESULTS=5
```

### Required IAM Permissions

Your AWS credentials need these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate"
            ],
            "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
        }
    ]
}
```

---

## 📡 API Endpoints

### 1. Knowledge Base Retrieval

Retrieve relevant documents without generating a response.

**Endpoint:** `POST /api/knowledge/retrieve`

**Request:**
```json
{
  "query": "What are the best team fight strategies?",
  "max_results": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Team fights should focus on positioning...",
      "score": 0.89,
      "location": {"s3Location": {"uri": "s3://..."}},
      "metadata": {}
    }
  ],
  "query": "What are the best team fight strategies?",
  "count": 5,
  "timestamp": "2025-01-15T10:30:00"
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/knowledge/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the best team fight strategies?",
    "max_results": 5
  }'
```

---

### 2. Chat with Knowledge Base (Streaming)

Stream chat response enhanced with knowledge base retrieval.

**Endpoint:** `POST /api/chat/stream`

**Request:**
```json
{
  "message": "What are the best champions for top lane?",
  "use_knowledge_base": true,
  "conversation_history": []
}
```

**How it works:**
1. System retrieves relevant documents from your knowledge base
2. Adds context to Claude's system prompt
3. Claude generates response using both its training and your documents
4. Streams response in real-time

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best champions for top lane?",
    "use_knowledge_base": true
  }'
```

---

### 3. Frontend Integration

The frontend can easily enable knowledge base features:

**Update `frontend/js/chat.js`:**

```javascript
// Add toggle for knowledge base in UI
const useKnowledgeBase = document.getElementById('useKnowledgeBase');

// Modify the request
const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.chatStream}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: message,
        conversation_history: state.getHistory(),
        use_knowledge_base: useKnowledgeBase.checked  // Enable KB
    })
});
```

**Add to HTML:**
```html
<div class="kb-toggle">
    <input type="checkbox" id="useKnowledgeBase">
    <label for="useKnowledgeBase">Use Knowledge Base (RAG)</label>
</div>
```

---

## 🎯 Usage Examples

### Example 1: Gaming Strategy Guide

**Knowledge Base Contents:**
- `league-of-legends-guide.pdf`
- `champion-strategies.md`
- `team-compositions.txt`

**Query:**
```json
{
  "message": "What's the best strategy for early game as jungler?",
  "use_knowledge_base": true
}
```

**Response:**
Claude will cite your documents and provide strategies based on your guides.

---

### Example 2: Product Documentation

**Knowledge Base Contents:**
- API documentation
- User guides
- FAQ documents

**Query:**
```json
{
  "message": "How do I configure the email settings?",
  "use_knowledge_base": true
}
```

**Response:**
Claude provides accurate, citation-backed answers from your docs.

---

## 🔧 Advanced Features

### Multiple Retrieval Strategies

The backend supports three retrieval strategies:

1. **`retrieve_from_knowledge_base()`**
   - Returns raw documents
   - No response generation
   - Useful for building custom UI

2. **`stream_response_with_knowledge()`**
   - Retrieves context first
   - Adds to system prompt
   - Full streaming support

3. **`retrieve_and_generate()` (AWS native)**
   - Uses AWS Bedrock's RetrieveAndGenerate API
   - Managed citations
   - Simpler but less control

### Custom Knowledge Base Per Request

```json
{
  "message": "Your question here",
  "use_knowledge_base": true,
  "knowledge_base_id": "CUSTOM_KB_ID"
}
```

---

## 📊 Best Practices

### Document Preparation

✅ **Do:**
- Use clear, well-structured documents
- Include headers and sections
- Keep documents under 50MB each
- Use descriptive filenames

❌ **Don't:**
- Upload scanned images (use OCR first)
- Include duplicate content
- Use overly technical jargon without context

### Chunking Strategy

- **Default:** 300 tokens, 20% overlap (recommended)
- **Long documents:** Increase chunk size to 500 tokens
- **FAQ-style:** Decrease chunk size to 200 tokens

### Query Optimization

✅ **Good queries:**
- "What are the best strategies for team fights in mid game?"
- "How do I configure the API authentication?"

❌ **Poor queries:**
- "Tell me everything" (too broad)
- "What's in the docs?" (too vague)

---

## 🐛 Troubleshooting

### Knowledge Base Not Found
```
[ERROR] Knowledge base not found. Please verify the knowledge base ID.
```

**Solution:**
- Check the Knowledge Base ID in .env matches AWS Console
- Verify the KB is in the same region as your API (us-east-1)

### Access Denied
```
[ERROR] Access denied to knowledge base. Please check IAM permissions.
```

**Solution:**
- Add `bedrock:Retrieve` and `bedrock:RetrieveAndGenerate` to IAM policy
- Ensure KB resource ARN is included

### No Results Returned
```
{
  "results": [],
  "count": 0
}
```

**Solution:**
- Verify knowledge base has been synced
- Check if your query matches document content
- Try broader search terms

### Sync Failed

**Solution:**
- Check S3 bucket permissions
- Verify IAM role has access to S3
- Ensure documents are in supported formats

---

## 💰 Cost Considerations

### Knowledge Base Costs:
- **Vector storage:** ~$0.50/GB/month (OpenSearch Serverless)
- **Embedding generation:** ~$0.10/1000 pages
- **Retrieval:** ~$0.004/1000 requests

### Optimization Tips:
- Keep documents relevant and concise
- Use appropriate chunk sizes
- Cache frequent queries if possible

---

## 📚 Example Data Sources

### Gaming Content
```
knowledge-base/
├── champions/
│   ├── top-lane-champions.md
│   ├── jungle-strategies.md
│   └── support-guide.md
├── game-mechanics/
│   ├── objectives.md
│   └── team-fighting.md
└── meta/
    ├── season-14-meta.md
    └── patch-notes.md
```

### Company Documentation
```
knowledge-base/
├── api-docs/
│   ├── authentication.md
│   ├── endpoints.md
│   └── rate-limits.md
├── user-guides/
│   ├── getting-started.md
│   └── advanced-features.md
└── faq/
    └── common-questions.md
```

---

## 🎓 Next Steps

1. **Create your first Knowledge Base** in AWS Console
2. **Upload sample documents** to test retrieval
3. **Configure the .env file** with your KB ID
4. **Restart the backend** to load new configuration
5. **Test the `/api/knowledge/retrieve` endpoint**
6. **Enable KB in chat requests** for RAG responses

---

## 📞 Support

For issues with:
- **AWS Bedrock KB:** Check AWS Bedrock documentation
- **API Integration:** See README.md
- **Permissions:** Review IAM policy guide above

---

**Enhance your AI chat with domain-specific knowledge! 🚀**
