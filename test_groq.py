#!/usr/bin/env python3
"""
Test script for Groq LLM integration in the LMS
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_quiz_gen import LLMQuizGenerator

# Load environment variables
load_dotenv()

async def test_groq_quiz_generation():
    """Test the Groq quiz generation functionality"""
    
    print("🧪 Testing Groq LLM Quiz Generation")
    print("=" * 50)
    
    # Check if GROQ_API_KEY is set
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set GROQ_API_KEY in your .env file")
        return False
    
    print(f"✅ GROQ_API_KEY found: {groq_api_key[:10]}...")
    
    # Sample text for testing
    sample_text = """
    FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ 
    based on standard Python type hints. The key features are: Fast: Very high performance, 
    on par with NodeJS and Go (thanks to Starlette and Pydantic). Fast to code: Increase the 
    speed to develop features by about 200% to 300%. Fewer bugs: Reduce about 40% of human 
    induced errors. Intuitive: Great editor support. Completion everywhere and less time 
    debugging. Easy: Designed to be easy to use and learn. Less time reading docs. Short: 
    Minimize code duplication. Multiple features from each parameter declaration. Robust: 
    Get production-ready code. With automatic interactive documentation. Standards-based: 
    Based on (and fully compatible with) OpenAPI (previously known as Swagger) and JSON Schema.
    """
    
    try:
        # Initialize the quiz generator
        print("🔄 Initializing LLMQuizGenerator...")
        quiz_generator = LLMQuizGenerator()
        
        # Generate quiz
        print("🔄 Generating quiz from sample text...")
        questions = await quiz_generator.generate_quiz_from_text(sample_text, num_questions=3)
        
        if questions:
            print(f"✅ Successfully generated {len(questions)} questions!")
            print("\n📝 Generated Questions:")
            print("-" * 30)
            
            for i, question in enumerate(questions, 1):
                print(f"\n{i}. {question['question']}")
                for j, option in enumerate(question['options'], 1):
                    marker = "✓" if option == question['answer'] else " "
                    print(f"   {marker} {j}. {option}")
            
            return True
        else:
            print("❌ No questions generated")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

async def test_mock_fallback():
    """Test the mock quiz fallback when no API key is available"""
    
    print("\n🧪 Testing Mock Quiz Fallback")
    print("=" * 50)
    
    # Temporarily unset the API key
    original_key = os.environ.get("GROQ_API_KEY")
    os.environ["GROQ_API_KEY"] = ""
    
    try:
        quiz_generator = LLMQuizGenerator()
        questions = await quiz_generator.generate_quiz_from_text("Sample text", num_questions=2)
        
        if questions:
            print(f"✅ Mock fallback working: {len(questions)} questions generated")
            return True
        else:
            print("❌ Mock fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in mock fallback test: {e}")
        return False
    finally:
        # Restore the original API key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key

async def main():
    """Main test function"""
    print("🚀 LMS Groq Integration Test")
    print("=" * 50)
    
    # Test 1: Groq integration
    groq_success = await test_groq_quiz_generation()
    
    # Test 2: Mock fallback
    mock_success = await test_mock_fallback()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Groq Integration: {'✅ PASS' if groq_success else '❌ FAIL'}")
    print(f"Mock Fallback: {'✅ PASS' if mock_success else '❌ FAIL'}")
    
    if groq_success and mock_success:
        print("\n🎉 All tests passed! Groq integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 