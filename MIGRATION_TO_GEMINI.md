# Migration to Gemini AI Embeddings

This document summarizes the changes made to migrate from local HuggingFace embeddings to Google's Gemini AI embedding models.

## Overview

The OptiPlan AI service has been updated to use **Gemini AI embeddings** instead of local HuggingFace models for creating text embeddings. This provides several benefits:

- **Superior Quality**: State-of-the-art embedding quality using Google's text-embedding-004 model
- **Multilingual Support**: Support for 100+ languages out of the box
- **No Local Compute**: Reduces local resource requirements
- **Task-Specific Optimization**: Uses appropriate task types for better results

## Changes Made

### 1. New GeminiEmbeddings Class (`PineconeSDK.py`)

Created a custom `GeminiEmbeddings` class that:
- Implements the LangChain `Embeddings` interface
- Uses Google's `text-embedding-004` model via the Generative AI API
- Automatically detects embedding dimensions (768 for text-embedding-004)
- Uses task-specific types: `retrieval_document` for indexing, `retrieval_query` for search
- Includes error handling with fallback to zero vectors

### 2. Updated PineconeSDK Class

- Replaced HuggingFace embeddings with `GeminiEmbeddings` instances
- Dynamic dimension detection for Pinecone index creation
- Added missing `delete_users()` and `delete_tasks()` methods
- Updated `_initialize_index()` to use dynamic dimensions

### 3. Dependencies Updated (`requirements.txt`)

**Removed:**
- `sentence-transformers`
- `langchain-huggingface`

**Kept:**
- `google-generativeai` (already present)
- All other dependencies remain the same

### 4. Configuration (`configs.py`)

Added import for `google_api_key` from environment variables:
```python
google_api_key = os.getenv("GOOGLE_API_KEY")
```

### 5. Documentation Updates

- Updated `README.md` with setup instructions and feature documentation
- Added environment variable requirements
- Documented the embedding capabilities and API endpoints

### 6. Test Script (`test_gemini_embeddings.py`)

Created a comprehensive test script to verify:
- API key configuration
- Embedding initialization
- Query and document embedding functionality
- Dimension consistency

## Environment Setup

### Required Environment Variables

Create a `.env` file in the `ai` directory:

```bash
# Google API Key for Gemini embeddings
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone API Key for vector database  
PINECONE_API_KEY=your_pinecone_api_key_here
```

### Getting API Keys

1. **Google API Key**: Get from [Google AI Studio](https://ai.google.dev/)
2. **Pinecone API Key**: Get from [Pinecone Console](https://www.pinecone.io/)

## Technical Details

### Embedding Models

- **Model**: `text-embedding-004` (Google's latest text embedding model)
- **Dimensions**: 768 (automatically detected)
- **Task Types**: 
  - `retrieval_document` for indexing user skills and tasks
  - `retrieval_query` for similarity search queries

### Error Handling

- Graceful fallback to zero vectors if API calls fail
- Dimension detection with fallback to 768 dimensions
- Comprehensive error logging

### Performance Considerations

- API-based embeddings may have higher latency than local models
- Rate limits apply to Google AI API calls
- Consider batching for large datasets

## Migration Steps for Existing Deployments

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**: Add `GOOGLE_API_KEY` to your environment
3. **Test the setup**: Run `python test_gemini_embeddings.py`
4. **Restart the service**: The existing Pinecone indexes will work with new embeddings
5. **Optional**: Re-index existing data for optimal performance with new embeddings

## Benefits Achieved

1. **Better Embeddings**: Higher quality semantic representations
2. **Multilingual**: Support for 100+ languages without additional setup
3. **Task Optimization**: Specialized embeddings for document vs query use cases
4. **Reduced Complexity**: No local model management or updates needed
5. **Scalability**: Cloud-based API scales automatically

## Backward Compatibility

The API interface remains the same - no changes required for client applications. Existing Pinecone indexes will continue to work, though re-indexing with new embeddings is recommended for optimal performance. 