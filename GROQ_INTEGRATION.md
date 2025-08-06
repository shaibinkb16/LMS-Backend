# Groq LLM Integration for LMS

This document explains how to set up and use Groq for automatic quiz generation in the Learning Management System.

## 🚀 Quick Setup

### 1. Get a Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the API key

### 2. Configure Environment

Create or update your `.env` file in the `Backend` directory:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Test the Integration

Run the test script to verify everything is working:

```bash
cd Backend
python test_groq.py
```

## 🔧 Technical Details

### Model Configuration

- **Model**: `llama3-70b-8192`
- **Provider**: Groq
- **Temperature**: 0.5 (balanced creativity and consistency)
- **Framework**: LangChain with ChatGroq

### How It Works

1. **PDF Upload**: When an admin uploads a PDF, the system extracts text using PyMuPDF
2. **Text Processing**: The extracted text is limited to 3000 characters for API efficiency
3. **Quiz Generation**: LangChain sends the text to Groq with a structured prompt
4. **Response Parsing**: The system parses the JSON response and validates the quiz structure
5. **Fallback**: If Groq fails, the system falls back to mock quiz generation

### Prompt Structure

The system uses a structured prompt template:

```
You are an educational quiz generator. Based on the following text, generate {num_questions} multiple choice questions.
Each question should have 4 options (A, B, C, D) with only one correct answer.

Text: {text}

Return the questions in this exact JSON format:
[
    {
        "question": "Question text here?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "Option A"
    }
]

Make sure the questions are relevant to the content and the correct answer is one of the options.
Be concise and focus on key concepts from the text.
```

## 🛠️ Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**
   - Make sure you've created a `.env` file in the Backend directory
   - Verify the API key is correctly copied

2. **"Error generating quiz with Groq"**
   - Check your internet connection
   - Verify your Groq API key is valid
   - Check your Groq account balance/limits

3. **"Invalid quiz structure generated"**
   - The LLM response wasn't in the expected JSON format
   - The system will automatically fall back to mock questions

### Testing

Use the provided test script to verify your setup:

```bash
python test_groq.py
```

This will test both the Groq integration and the mock fallback.

## 📊 Performance

- **Response Time**: Typically 1-3 seconds per quiz generation
- **Accuracy**: High-quality questions based on document content
- **Reliability**: Includes fallback mechanisms for robustness

## 🔄 Migration from OpenAI

If you were previously using OpenAI, the system now prioritizes Groq but maintains backward compatibility:

1. Set `GROQ_API_KEY` for primary LLM
2. Keep `OPENAI_API_KEY` as fallback (optional)
3. The system will automatically use Groq when available

## 📝 API Usage

The quiz generation is handled automatically when:
- Admins upload PDFs via `/admin/upload_pdf`
- The system extracts text and generates quizzes
- Quizzes are stored in the database for employee access

No additional API calls are needed from the frontend - everything is handled server-side. 