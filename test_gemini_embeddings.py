#!/usr/bin/env python3
"""
Test script for Gemini embeddings implementation.
This script tests the basic functionality of the GeminiEmbeddings class.

Usage:
    python test_gemini_embeddings.py

Make sure to set your GOOGLE_API_KEY environment variable before running.
"""

import os
from PineconeSDK import GeminiEmbeddings

def test_gemini_embeddings():
    """Test the Gemini embeddings functionality."""
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable is not set!")
        print("Please set your Google API key in the .env file or environment variables.")
        print("Get your API key from: https://ai.google.dev/")
        return False
    
    try:
        print("🚀 Testing Gemini embeddings...")
        
        # Initialize embeddings
        embeddings = GeminiEmbeddings()
        print(f"✅ GeminiEmbeddings initialized successfully")
        print(f"📏 Embedding dimensions: {embeddings.embedding_dimensions}")
        
        # Test embedding a single query
        test_query = "Python developer with machine learning experience"
        print(f"📝 Testing query embedding: '{test_query}'")
        
        query_embedding = embeddings.embed_query(test_query)
        print(f"✅ Query embedding successful - dimensions: {len(query_embedding)}")
        
        # Test embedding multiple documents
        test_documents = [
            "Senior Python developer with 5 years experience",
            "Machine learning engineer specializing in NLP",
            "Full-stack developer with React and Node.js skills"
        ]
        print(f"📄 Testing document embeddings for {len(test_documents)} documents")
        
        doc_embeddings = embeddings.embed_documents(test_documents)
        print(f"✅ Document embeddings successful - {len(doc_embeddings)} embeddings created")
        
        # Verify all embeddings have the same dimensions
        dimensions_check = all(len(emb) == embeddings.embedding_dimensions for emb in doc_embeddings)
        if dimensions_check:
            print("✅ All embeddings have consistent dimensions")
        else:
            print("❌ Embedding dimensions are inconsistent")
            return False
        
        print("\n🎉 All tests passed! Gemini embeddings are working correctly.")
        print("Your setup is ready for the OptiPlan AI service.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini embeddings: {str(e)}")
        print("Possible issues:")
        print("- Invalid GOOGLE_API_KEY")
        print("- No internet connection")
        print("- API rate limits reached")
        return False

if __name__ == "__main__":
    success = test_gemini_embeddings()
    exit(0 if success else 1) 