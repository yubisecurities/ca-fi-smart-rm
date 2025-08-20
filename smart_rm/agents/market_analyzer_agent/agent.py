# Import necessary modules

import requests
import json
import os
from dotenv import load_dotenv

from prompt import market_analyzer_agent_prompt

load_dotenv()


# Configuration for LLM API
LITELLM_HOST = "llmproxy-gcp.go-yubi.in"
API_URL = f"https://{LITELLM_HOST}/v1/chat/completions"
API_KEY = os.getenv('API_KEY')

class ChatPrompt:
    def __init__(self):
        self.system_prompt = ""
        self.user_prompt = ""
    
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
        
    def set_user_prompt(self, prompt: str):
        self.user_prompt = prompt
        
    def get_messages(self):
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": self.user_prompt})
        return messages

def call_llm_api(messages, model="llama-3.3-70b-(US)"):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        data = {
            "model": model,
            "messages": messages
        }

        print(f"\nCalling LLM api with data: {json.dumps(data, indent=2)}")
        
        # Add timeout to prevent hanging
        response = requests.post(API_URL, headers=headers, json=data, timeout=300000)
        
        print(f"\nResponse status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The API might be taking too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {API_URL}. Please check if the API is running.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {str(e)}")
        print(f"Response text: {e.response.text if hasattr(e, 'response') and e.response else 'No response received'}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Example usage
def test_models():
    # Initialize prompt object
    chat = ChatPrompt()

    # Set system prompt
    system_prompt = market_analyzer_agent_prompt
    chat.set_system_prompt(system_prompt)
    chat.set_user_prompt("I am an aggressive investor, ready to dip into risks into indian bonds. Risk Edukurathu ellam Rusk saapudura maari!")

    # Get messages
    messages = chat.get_messages()

    # Call API
    response = call_llm_api(messages, "gpt-4.1-(US)")

    if response:
        print("\nAI Response:")
        print(response['choices'][0]['message']['content'])
    else:
        print("\nFailed to get response from AI")

# Run the function
test_models()