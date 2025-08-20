# Import necessary modules

import requests
import json
import os
from dotenv import load_dotenv

from prompt import market_analyzer_agent_prompt
from helpers.nse import get_stock_index, get_stock
from helpers.listings import get_current_listings

load_dotenv()


# Configuration for LLM API
LITELLM_HOST = "llmproxy-gcp.go-yubi.in"
API_URL = f"https://{LITELLM_HOST}/v1/chat/completions"
API_KEY = os.getenv('API_KEY')

class ChatPrompt:
    def __init__(self):
        self.user_prompt = ""
        self.system_prompts = []

    def add_system_prompt(self, prompt: str):
        self.system_prompts.append(prompt)
        
    def set_user_prompt(self, prompt: str):
        self.user_prompt = prompt
        
    def get_messages(self):
        messages = []
        
        for prompt in self.system_prompts:
            messages.append({"role": "system", "content": prompt})

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

        # print(f"\nCalling LLM api with data: {json.dumps(data, indent=2)}")
        
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
    chat.add_system_prompt(market_analyzer_agent_prompt)
    chat.add_system_prompt(f"The available bonds in our platforms json -> {get_current_listings()}")
    chat.add_system_prompt(f"Today's Nifty 50 JSON data -> {get_stock_index("NIFTY 50")}")
    chat.set_user_prompt("The client is an safe investor, ready to dip into low risk into indian bonds. Coolie Power House maa!!!")

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