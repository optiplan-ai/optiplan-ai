# Deploying OptiPlan AI Service to Vercel

This guide walks you through deploying your FastAPI service with Gemini AI embeddings to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Google API Key**: Get from [Google AI Studio](https://ai.google.dev/)
3. **Pinecone API Key**: Get from [Pinecone Console](https://www.pinecone.io/)
4. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Project

### 1.1 Verify Files Structure

Ensure your `ai/` directory contains:
```
ai/
├── main.py                    # FastAPI app (modified for Vercel)
├── PineconeSDK.py            # Gemini embeddings implementation
├── configs.py                # Configuration
├── requirements.txt          # Dependencies
├── vercel.json              # Vercel configuration
├── baml_client/             # BAML client
├── baml_src/                # BAML source
└── test_gemini_embeddings.py # Test script
```

### 1.2 Verify Requirements

Ensure your `requirements.txt` includes all necessary dependencies:
```
fastapi
uvicorn
pinecone-client
langchain-pinecone
langchain
google-generativeai
baml-py
python-dotenv
```

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from the ai directory**:
   ```bash
   cd ai
   vercel
   ```

4. **Follow the prompts**:
   - Choose your scope (personal or team)
   - Link to existing project or create new
   - Confirm settings

### Option B: Deploy via Vercel Dashboard

1. **Go to [vercel.com/dashboard](https://vercel.com/dashboard)**

2. **Click "New Project"**

3. **Import your Git repository**

4. **Configure project settings**:
   - **Root Directory**: Set to `ai/` 
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (not needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

5. **Click "Deploy"**

## Step 3: Configure Environment Variables

### 3.1 Add Environment Variables in Vercel Dashboard

1. Go to your project dashboard on Vercel
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables:

| Variable Name | Value | Environment |
|---------------|-------|-------------|
| `GOOGLE_API_KEY` | `your_google_api_key_here` | Production, Preview, Development |
| `PINECONE_API_KEY` | `your_pinecone_api_key_here` | Production, Preview, Development |

### 3.2 Using Vercel CLI

Alternatively, you can set environment variables via CLI:

```bash
# Set for production
vercel env add GOOGLE_API_KEY production
vercel env add PINECONE_API_KEY production

# Set for preview
vercel env add GOOGLE_API_KEY preview  
vercel env add PINECONE_API_KEY preview

# Set for development
vercel env add GOOGLE_API_KEY development
vercel env add PINECONE_API_KEY development
```

## Step 4: Test Your Deployment

### 4.1 Check Health Endpoint

Once deployed, test your API:

```bash
curl https://your-project-name.vercel.app/health-check
```

Expected response:
```json
{
  "message": "Service is up and running"
}
```

### 4.2 Test Root Endpoint

```bash
curl https://your-project-name.vercel.app/
```

Expected response:
```json
{
  "message": "OptiPlan AI Service - Powered by Gemini AI Embeddings",
  "status": "healthy"
}
```

### 4.3 View API Documentation

Visit `https://your-project-name.vercel.app/docs` to see the interactive API documentation.

## Step 5: Usage Examples

### Generate Tasks
```bash
curl -X POST "https://your-project-name.vercel.app/generate-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_123",
    "manager_id": "mgr_456", 
    "project_description": "Build a mobile app for task management"
  }'
```

### Index Users
```bash
curl -X POST "https://your-project-name.vercel.app/index-users" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "proj_123",
    "manager_id": "mgr_456",
    "users": [
      {
        "id": "user_1",
        "name": "John Doe",
        "primary_domain": "backend",
        "skills": [
          {
            "name": "Python",
            "category": "backend",
            "experience_years": 5,
            "proficiency_score": 85
          }
        ]
      }
    ]
  }'
```

## Troubleshooting

### Common Issues

1. **Cold Start Timeout**: 
   - Vercel functions have a cold start time. The first request might be slower.
   - Consider upgrading to Vercel Pro for better performance.

2. **Function Timeout**:
   - Default timeout is 10 seconds for Hobby plan, 60 seconds for Pro.
   - Large embedding operations might timeout on Hobby plan.

3. **Memory Limits**:
   - Hobby plan: 1024 MB
   - Pro plan: 3008 MB

4. **API Rate Limits**:
   - Google API has rate limits
   - Pinecone has rate limits
   - Consider implementing retry logic for production use

### Debugging

1. **Check Vercel Logs**:
   ```bash
   vercel logs
   ```

2. **Check Function Logs**:
   - Go to Vercel Dashboard → Functions → View logs

3. **Test Locally**:
   ```bash
   vercel dev
   ```

## Production Considerations

### Performance Optimization

1. **Connection Pooling**: Implement connection pooling for Pinecone
2. **Caching**: Add caching for frequently accessed embeddings  
3. **Batch Processing**: Process multiple requests together when possible
4. **Async Operations**: Use async/await for I/O operations

### Security

1. **API Key Management**: Use Vercel's environment variables (never commit keys)
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **CORS**: Configure CORS properly for web applications
4. **Input Validation**: Validate all input data thoroughly

### Monitoring

1. **Vercel Analytics**: Enable Vercel Analytics for monitoring
2. **Error Tracking**: Consider adding Sentry or similar for error tracking
3. **Custom Logging**: Add structured logging for debugging

## Scaling

For high-traffic applications, consider:

1. **Vercel Pro Plan**: Higher limits and better performance
2. **Edge Functions**: Use Vercel Edge Functions for global distribution
3. **Database Optimization**: Optimize Pinecone index configuration
4. **Caching Layer**: Add Redis or similar for caching

## Cost Considerations

- **Vercel**: Hobby plan is free with limits, Pro plan starts at $20/month
- **Google AI API**: Pay per API call (check current pricing)
- **Pinecone**: Free tier available, paid plans for production use

## Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **Pinecone Docs**: [docs.pinecone.io](https://docs.pinecone.io/)
- **Google AI Docs**: [ai.google.dev](https://ai.google.dev/) 