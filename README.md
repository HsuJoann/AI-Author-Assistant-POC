# Simplified Author Assistant

A Python-based writing assistance tool leveraging Claude 3.7 Sonnet AI to help authors improve their writing through automated suggestions, content analysis, and interactive conversations.

## Features

- **Writing Improvement**: Get suggestions to enhance clarity and conciseness while maintaining original meaning
- **Content Analysis**: Receive structured feedback on organization, clarity, and specific improvement suggestions
- **Interactive Chat**: Engage in contextual conversations with AI about your writing
- **Conversation History**: Track and maintain chat history for continuous context
- **Error Handling**: Robust error management with automatic retries for rate limits

## Technical Details

- **AI Model**: Claude 3.7 Sonnet (model ID: `claude-3-7-sonnet-20250219`)
- **API Integration**: Anthropic API
- **Logging**: Loguru for comprehensive logging
- **Retry Logic**: Tenacity for handling rate limits and temporary failures

## Installation

```bash
# Clone the repository
git clone [repository-url]

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
set ANTHROPIC_API_KEY=your_api_key_here  # Windows
# or
export ANTHROPIC_API_KEY=your_api_key_here  # Unix/Linux
```

## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your Anthropic API key to `.env`:
   ```plaintext
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from ai_service import AIService

# Initialize the service
ai_service = AIService()

# Improve writing
improved_text = ai_service.improve_writing("Your text here")

# Analyze content
analysis = ai_service.analyze_content("Your content here")

# Chat with context
response = ai_service.chat_with_context("Your question here")

# View conversation history
history = ai_service.get_conversation_history()

# Clear conversation history
ai_service.clear_conversation()
```

## Configuration

The service uses the following default parameters:

- Writing Improvement:
  - Max Tokens: 2048
  - Temperature: 0.3
- Content Analysis:
  - Max Tokens: 1024
  - Temperature: 0.1
- Interactive Chat:
  - Max Tokens: 2048
  - Temperature: 0.7

## Error Handling

The service handles common API errors including:
- Authentication errors (401)
- Bad requests (400)
- Rate limiting (429)
- General API errors

## Dependencies

- `anthropic`: For Claude AI API integration
- `loguru`: For logging
- `tenacity`: For retry logic

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your chosen license here]

## Contact

[Add your contact information here]cd c:/Users/jingh/python_code_folder/Simplified Author Assitant