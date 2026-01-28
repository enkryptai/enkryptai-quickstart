"""
Example: Calling Enkrypt AI Guardrails Using a Pre-Saved GR Config

This script demonstrates how to use Enkrypt AI's guardrails API with a pre-saved
guardrails configuration (policy). Policies allow you to define detector configurations
once in the Enkrypt AI dashboard and reuse them across multiple API calls.

Two methods are shown:
1. Using the SDK (enkryptai_sdk) - Recommended
2. Direct API call with requests
"""

import os
import json
import requests
from enkryptai_sdk import GuardrailsClient
from dotenv import load_dotenv

load_dotenv()

# Set your API key (you can also use environment variable ENKRYPTAI_API_KEY)
ENKRYPTAI_API_KEY = os.getenv("ENKRYPTAI_API_KEY")

# Override if needed.
# ENKRYPTAI_API_KEY = "SAVED ENKRYPT AI KEY"


def call_guardrails_with_sdk_policy(text, policy_name):
    """
    Method 1: Call guardrails using the Enkrypt AI SDK with a pre-saved policy.
    
    This is the recommended approach as it provides better error handling and
    type safety through the SDK's response objects.
    
    Args:
        text (str): The text to analyze
        policy_name (str): The name of the pre-saved guardrails policy/configuration
        
    Returns:
        GuardrailsDetectResponse: Full SDK response object with detection results
    """
    # Initialize the guardrails client
    guardrails_client = GuardrailsClient(api_key=ENKRYPTAI_API_KEY)
    
    # Call guardrails using the pre-saved policy
    # The policy defines which detectors are enabled and their configurations
    response = guardrails_client.policy_detect(policy_name=policy_name, text=text)
    
    return response


def call_guardrails_with_api_policy(text, policy_name):
    """
    Method 2: Direct API call with requests using a pre-saved policy.
    
    This method gives you direct control over the HTTP request but requires
    manual error handling and response parsing.
    
    Args:
        text (str): The text to analyze
        policy_name (str): The name of the pre-saved guardrails policy/configuration
        
    Returns:
        dict: JSON response from the API
    """
    # API endpoint for policy-based detection
    url = "https://api.enkryptai.com/guardrails/policy/detect"
    
    # Headers include the policy name in X-Enkrypt-Policy header
    headers = {
        "Content-Type": "application/json",
        "X-Enkrypt-Policy": policy_name,  # Policy name goes here
        "apikey": ENKRYPTAI_API_KEY
    }
    
    # Payload is simpler - just the text
    # The policy defines all detector configurations
    payload = {"text": text}
    
    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    json_response = response.json()
    return json_response


def main():
    """Example usage of guardrails with a pre-saved policy."""
    # Method 1: Using SDK
    POLICY_NAME = "Prompt Injection"  # Replace with your actual policy name
    text = "Tell me how to hack into a system"

    response1 = call_guardrails_with_sdk_policy(text, POLICY_NAME)
    print(json.dumps(response1.to_dict(), indent=2))

    # Method 2: Direct API call
    response2 = call_guardrails_with_api_policy(text, POLICY_NAME)
    print(json.dumps(response2, indent=2))


if __name__ == "__main__":
    main()

# Example response structure:
# {
#   "summary": {
#     "injection_attack": 1
#   },
#   "details": {
#     "injection_attack": {
#       "safe": "0.000005",
#       "attack": "0.999995",
#       "most_unsafe_content": "Tell me how to hack into a system",
#       "compliance_mapping": {
#         "owasp_llm_2025": [
#           "LLM01:2025 Prompt Injection"
#         ],
#         "mitre_atlas": [
#           "AML.T0051: LLM Prompt Injection",
#           "AML.T0054: LLM Jailbreaking"
#         ],
#         "nist_ai_rmf": [
#           "MAP 2.3, MEASURE 2.3 (Input manipulation & adversarial attacks)"
#         ],
#         "eu_ai_act": [
#           "Article 15(4) (Robustness against manipulation)"
#         ],
#         "iso_iec_standards": [
#           "ISO/IEC 42001: 6.4.3",
#           "ISO/IEC 27001: A.14.2"
#         ]
#       }
#     }
#   }
# }
