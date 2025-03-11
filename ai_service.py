import anthropic
from loguru import logger
from config import ANTHROPIC_API_KEY
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class AIService:
    def __init__(self):
        try:
            self.client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
            self.model = "claude-3-7-sonnet-20250219"
            # Add conversation history storage
            self.conversation_history = []
            logger.info("AIService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AIService: {str(e)}")
            raise

    def get_conversation_history(self) -> list:
        """Return the current conversation history"""
        return self.conversation_history

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError)
    )
    def improve_writing(self, content: str) -> str:
        """Get writing improvement suggestions from Claude with retry logic"""
        try:
            logger.debug(f"Requesting writing improvements for content length: {len(content)}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.3,
                system="You are a professional editor. Your task is to improve writing for clarity and conciseness while maintaining the original meaning.",
                messages=[{
                    "role": "user",
                    "content": f"Please improve this writing for clarity and conciseness:\n\n{content}"
                }]
            )
            
            improved_text = response.content[0].text
            logger.info("Successfully received writing improvements")
            return improved_text

        except anthropic.APIError as e:
            logger.error(f"API error in improve_writing: {str(e)}")
            if getattr(e, 'status_code', None) == 401:
                return "Authentication error: Check your API key"
            elif getattr(e, 'status_code', None) == 400:
                return "Bad request: Check your parameters"
            elif getattr(e, 'status_code', None) == 429:
                return "Rate limit exceeded: Slow down requests"
            else:
                return f"API error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in improve_writing: {str(e)}")
            return f"Error getting improvements: {str(e)}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError)
    )
    def analyze_content(self, content: str) -> str:
        """Analyze content structure and provide feedback with retry logic"""
        try:
            logger.debug(f"Requesting content analysis for text length: {len(content)}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.1,
                system="You are a content analysis expert. Provide clear, structured feedback focusing on organization, clarity, and specific improvement suggestions.",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this text and provide feedback on:
                    1. Overall structure
                    2. Clarity and readability
                    3. Specific improvement suggestions
                    
                    Text to analyze:
                    {content}"""
                }]
            )
            
            analysis = response.content[0].text
            logger.info("Successfully received content analysis")
            return analysis

        except anthropic.APIError as e:
            logger.error(f"API error in analyze_content: {str(e)}")
            if getattr(e, 'status_code', None) == 401:
                return "Authentication error: Check your API key"
            elif getattr(e, 'status_code', None) == 400:
                return "Bad request: Check your parameters"
            elif getattr(e, 'status_code', None) == 429:
                return "Rate limit exceeded: Slow down requests"
            else:
                return f"API error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in analyze_content: {str(e)}")
            return f"Error analyzing content: {str(e)}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(anthropic.RateLimitError)
    )
    def chat_with_context(self, user_message: str) -> str:
        """Chat with Claude using conversation history"""
        try:
            logger.debug(f"Sending message with conversation history. Message length: {len(user_message)}")
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add assistant's response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            logger.info("Successfully received response with conversation context")
            return assistant_message

        except anthropic.APIError as e:
            logger.error(f"API error in chat_with_context: {str(e)}")
            if getattr(e, 'status_code', None) == 401:
                return "Authentication error: Check your API key"
            elif getattr(e, 'status_code', None) == 400:
                return "Bad request: Check your parameters"
            elif getattr(e, 'status_code', None) == 429:
                return "Rate limit exceeded: Slow down requests"
            else:
                return f"API error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in chat_with_context: {str(e)}")
            return f"Error in conversation: {str(e)}"