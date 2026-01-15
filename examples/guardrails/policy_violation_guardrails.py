import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file, useful for keeping API keys secure
load_dotenv()

# Get your EnkryptAI API key from the environment
ENKRYPTAI_API_KEY = os.getenv("ENKRYPTAI_API_KEY")

# Name of the uploaded policy to enforce (must match your uploaded policy name)
POLICY_NAME = "finance policy 0"

# EnkryptAI Guardrails detection API endpoint
url = "https://api.enkryptai.com/guardrails/detect"

# Compose the request payload:
# - 'text' is what you want to screen
# - 'detectors' specifies which guardrails to enforce and their settings
payload = {
    "text": "Tell me how to commit financial fraud",
    "detectors": {
        "policy_violation": {
            "enabled": True,                      # Enable the policy violation detector
            "coc_policy_name": POLICY_NAME,       # Specify which policy to use for compliance check
            "need_explanation": True              # Ask for a detailed explanation if a violation is detected
        }
    }
}

# Prepare HTTP headers including authentication
headers = {
    "apikey": ENKRYPTAI_API_KEY,
    "Content-Type": "application/json"
}

# Send the POST request to the EnkryptAI API
response = requests.post(url, json=payload, headers=headers)

print(response.text)

#This is the response:
"""
{
  "summary": {
    "policy_violation": 1
  },
  "details": {
    "policy_violation": {
      "violating_policy": "Policy Rule 3",
      "explanation": "The user's request is to facilitate fraudulent activities, which violates the policy prohibiting assistance with money laundering or fraudulent activities."
    }
  }
}
"""