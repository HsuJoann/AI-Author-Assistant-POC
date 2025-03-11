# GitHub Copilot Instructions - Claude 3.7 Sonnet API (Python)

This file provides Python-specific instructions for GitHub Copilot to understand the correct patterns and best practices when working with Claude 3.7 Sonnet via the Anthropic API.

## Model Identifier

When making API calls to Claude 3.7 Sonnet, always use the specific model identifier:

```python
model = "claude-3-7-sonnet-20250219"
```

## Setup

```python
import anthropic
import os

# Initialize the client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
```

## Basic Messages API Call

```python
def call_claude_3_7_sonnet(prompt):
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Access the response text
    response_text = message.content[0].text
    return response_text
```

## Multi-turn Conversations

```python
def have_conversation_with_claude():
    conversation = [
        {"role": "user", "content": "Hello, Claude 3.7 Sonnet!"}
    ]
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=conversation
    )
    
    # Add Claude's response to the conversation history
    conversation.append({"role": "assistant", "content": response.content[0].text})
    
    # Add user's next message
    conversation.append({"role": "user", "content": "Tell me more about your capabilities"})
    
    # Get next response
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=conversation
    )
    
    return response
```

## Including Images

```python
import base64

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Send message with image to Claude 3.7 Sonnet
def analyze_image(image_path, question):
    base64_image = encode_image_to_base64(image_path)
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    )
    
    return response.content[0].text
```

## Using System Prompts

```python
def get_response_with_system_prompt(user_prompt, system_prompt):
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.content[0].text
```

## Tools/Function Calling

```python
def use_weather_tool(location):
    # Define the tool
    weather_tool = {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
    
    # First request to Claude
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        messages=[
            {"role": "user", "content": f"What's the weather in {location}?"}
        ],
        tools=[weather_tool]
    )
    
    # Check if Claude wants to use a tool
    if response.content[0].type == "tool_use":
        tool_use = response.content[0]
        tool_input = tool_use.input
        tool_call_id = tool_use.id
        
        # Call external weather API or service (hypothetical function)
        weather_data = get_actual_weather(tool_input["location"])
        
        # Send tool result back to Claude
        final_response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            messages=[
                {"role": "user", "content": f"What's the weather in {location}?"},
                {"role": "assistant", "content": [tool_use]},
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_call_id,
                            "result": weather_data
                        }
                    ]
                }
            ]
        )
        
        return final_response.content[0].text
    else:
        return response.content[0].text
```

## Streaming Responses

```python
def stream_from_claude():
    with client.messages.stream(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Write a short poem about AI"}
        ]
    ) as stream:
        # Initialize empty string to collect the full response
        full_response = ""
        
        # Process each chunk as it arrives
        for chunk in stream:
            if chunk.type == "content_block_delta" and chunk.delta.type == "text":
                chunk_text = chunk.delta.text
                full_response += chunk_text
                print(chunk_text, end="", flush=True)
        
        return full_response
```

## Adjusting Parameters

```python
def get_creative_response(prompt):
    """Get more creative, varied responses from Claude 3.7 Sonnet"""
    return client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2048,
        temperature=0.9,  # Higher temperature for more creativity
        top_p=0.95,
        messages=[
            {"role": "user", "content": prompt}
        ]
    ).content[0].text

def get_factual_response(prompt):
    """Get more deterministic, factual responses from Claude 3.7 Sonnet"""
    return client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2048,
        temperature=0.1,  # Lower temperature for more deterministic output
        top_p=0.8,
        messages=[
            {"role": "user", "content": prompt}
        ]
    ).content[0].text
```

## Error Handling

```python
def safe_claude_call(prompt):
    try:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except anthropic.APIError as e:
        if e.status_code == 401:
            return "Authentication error: Check your API key"
        elif e.status_code == 400:
            return "Bad request: Check your parameters"
        elif e.status_code == 429:
            return "Rate limit exceeded: Slow down requests"
        else:
            return f"API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
```

## Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(anthropic.RateLimitError)
)
def call_claude_with_retry(prompt):
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text
```

## Best Practices for Claude 3.7 Sonnet

1. Store API keys in environment variables, never hardcode them
2. Set appropriate `max_tokens` based on expected response length (1-4096)
3. Use streaming for long-form content to improve user experience
4. When processing images, ensure they are properly encoded and under 5MB each
5. For complex tasks, use a lower temperature (0.0-0.3) for more deterministic outputs
6. For creative tasks, use a higher temperature (0.7-1.0) for more varied outputs
7. Use system prompts to guide Claude's behavior for consistent results
8. Implement proper error handling for production applications
9. Consider a token counting function to estimate costs when making high-volume calls
