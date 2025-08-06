import json
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from ..core.config import settings

class LLMQuizGenerator:
    def __init__(self):
        # Initialize Groq LLM
        self.llm = ChatGroq(
            temperature=0.5,
            model_name="llama3-70b-8192",
            api_key=settings.GROQ_API_KEY
        )
    
    async def generate_quiz_from_text(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions from PDF text using Groq"""
        
        if not settings.GROQ_API_KEY:
            # Fallback to mock quiz if no API key
            return self._generate_mock_quiz(num_questions)
        
        try:
            # Create prompt template for quiz generation
            prompt_template = ChatPromptTemplate.from_template("""
            You are an educational quiz generator. Based on the following text, generate {num_questions} multiple choice questions.
            Each question should have 4 options (A, B, C, D) with only one correct answer.
            
            Text: {text}
            
            Return the questions in this exact JSON format:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A"
                }}
            ]
            
            Make sure the questions are relevant to the content and the correct answer is one of the options.
            Be concise and focus on key concepts from the text.
            """)
            
            # Limit text length for API efficiency
            limited_text = text[:3000] if len(text) > 3000 else text
            
            # Create the chain
            chain = prompt_template | self.llm
            
            # Generate quiz
            response = chain.invoke({
                "text": limited_text,
                "num_questions": num_questions
            })
            
            # Parse the response
            content = response.content
            
            # Try to extract JSON from the response
            try:
                # Look for JSON array in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    questions = json.loads(json_str)
                else:
                    # If no JSON array found, try to parse the entire response
                    questions = json.loads(content)
                
                # Validate the structure
                if isinstance(questions, list) and len(questions) > 0:
                    # Ensure each question has the required fields
                    validated_questions = []
                    for q in questions:
                        if isinstance(q, dict) and 'question' in q and 'options' in q and 'answer' in q:
                            if isinstance(q['options'], list) and len(q['options']) == 4:
                                validated_questions.append(q)
                    
                    if validated_questions:
                        return validated_questions[:num_questions]
                
                # If validation fails, fall back to mock quiz
                print(f"Invalid quiz structure generated, using fallback")
                return self._generate_mock_quiz(num_questions)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Response content: {content}")
                return self._generate_mock_quiz(num_questions)
            
        except Exception as e:
            print(f"Error generating quiz with Groq: {e}")
            # Fallback to mock quiz
            return self._generate_mock_quiz(num_questions)
    
    def _generate_mock_quiz(self, num_questions: int) -> List[Dict[str, Any]]:
        """Generate mock quiz questions for testing"""
        mock_questions = [
            {
                "question": "What is the main purpose of this document?",
                "options": ["To inform", "To entertain", "To persuade", "To confuse"],
                "answer": "To inform"
            },
            {
                "question": "Which of the following is NOT mentioned in the document?",
                "options": ["Key concepts", "Important dates", "Contact information", "Fictional characters"],
                "answer": "Fictional characters"
            },
            {
                "question": "What should readers do after reading this document?",
                "options": ["Forget about it", "Take action", "Share with friends", "Ignore completely"],
                "answer": "Take action"
            },
            {
                "question": "How many main sections does this document have?",
                "options": ["One", "Two", "Three", "Four"],
                "answer": "Three"
            },
            {
                "question": "What is the recommended approach mentioned in the document?",
                "options": ["Quick reading", "Thorough analysis", "Skimming", "Ignoring"],
                "answer": "Thorough analysis"
            }
        ]
        
        return mock_questions[:num_questions] 