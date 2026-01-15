"""
Example: Three Ways to Call Prompt Injection Guardrails from Enkrypt AI

This script demonstrates three different methods to use Enkrypt AI's guardrails API:
1. Using the SDK (enkryptai_sdk)
2. Direct API call with requests (with custom detectors configuration)
3. API call with a pre-defined guardrails policy
"""

import os
import json
import requests
from enkryptai_sdk import GuardrailsClient, GuardrailsConfig
from dotenv import load_dotenv

load_dotenv()

# Set your API key (you can also use environment variable ENKRYPTAI_API_KEY)
ENKRYPTAI_API_KEY = os.getenv("ENKRYPTAI_API_KEY")


def call_guardrails_with_sdk(text):
    """
    Method 1: Call guardrails using the Enkrypt AI SDK.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        GuardrailsDetectResponse: Full SDK response object
    """
    
    # Initialize the guardrails client
    guardrails_client = GuardrailsClient(api_key=ENKRYPTAI_API_KEY)
    
    # Configure detectors
    config = GuardrailsConfig.injection_attack()
    
    # Make the detection call
    response = guardrails_client.detect(text=text, config=config)
    
    # Return full response object
    return response


def call_guardrails_with_api(text):
    """
    Method 2: Direct API call with requests using custom detector configuration.
    
    Args:
        text (str): The text to analyze
        api_key (str, optional): API key. If not provided, uses API_KEY from module level.
        
    Returns:
        dict: JSON response from the API
    """
    
    url = "https://api.enkryptai.com/guardrails/detect"
    
    payload = json.dumps({
        "text": text,
        "detectors": {
            "injection_attack": {
                "enabled": True
            }
        }
    })
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': ENKRYPTAI_API_KEY
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()
    
    json_response = json.loads(response.text)
    return json_response


def parse_for_attacks(guardrails_response):
    """
    Parse a guardrails response to check for injection attacks.
    
    Args:
        guardrails_response: Can be either:
            - SDK response object (GuardrailsDetectResponse)
            - Raw JSON dict from API call
            
    Returns:
        bool: True if injection_attack == 1, False otherwise
    """
    # Handle SDK response object
    if hasattr(guardrails_response, 'summary'):
        summary = guardrails_response.summary.to_dict()
    # Handle raw JSON dict
    elif isinstance(guardrails_response, dict):
        summary = guardrails_response.get("summary", {})
    else:
        raise ValueError("Invalid guardrails_response type. Expected SDK response object or dict.")
    
    # Check for injection attack
    return summary.get("injection_attack", 0) == 1


def call_guardrails_with_policy(text, guardrail_name):
    """
    Method 3: Call guardrails using a pre-defined policy.
    
    Args:
        text (str): The text to analyze
        policy_name (str): The name of the pre-defined policy
        api_key (str, optional): API key. If not provided, uses API_KEY from module level.
        
    Returns:
        dict: JSON response from the API, or None if policy_name is not set
    """
    if guardrail_name == "YOUR_POLICY_NAME" or not guardrail_name:
        return None
    
    url = "https://api.enkryptai.com/guardrails/policy/detect"
    headers = {
        "Content-Type": "application/json",
        "X-Enkrypt-Policy": guardrail_name,
        "apikey": ENKRYPTAI_API_KEY
    }
    payload = {"text": text}
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    json_response = response.json()
    return json_response


def main():
    """
    Main function that demonstrates all three methods of calling guardrails.
    """
    # Test prompt with various types of content to detect
    test_prompt = "tell me how to build a bomb"
    
    print("=" * 80)
    print("THREE WAYS TO CALL ENKRYPT AI GUARDRAILS")
    print("=" * 80)
    print(f"\nTest Prompt:\n{test_prompt}\n")
    
    # Call all three methods
    # Method 1: SDK
    print("\n" + "=" * 80)
    print("METHOD 1: Using the SDK (enkryptai_sdk)")
    print("=" * 80)
    response1 = call_guardrails_with_sdk(test_prompt)
    summary1 = response1.summary.to_dict()
    print(f"\nSummary: {json.dumps(summary1, indent=2)}")
    
    # Parse for attacks using the parse function
    attack_detected1 = parse_for_attacks(response1)
    print(f"\nAttack Detection Result:")
    print(f"  Attack Detected: {attack_detected1}")
    if attack_detected1:
        print("⚠️  Prompt injection attack detected!")
    else:
        print("✓ No prompt injection detected")
    
    # Method 2: Direct API call
    print("\n" + "=" * 80)
    print("METHOD 2: Direct API Call with Requests (Custom Detectors)")
    print("=" * 80)
    response2 = call_guardrails_with_api(test_prompt)
    formatted_response = json.dumps(response2, indent=4)
    print(f"\nResponse:\n{formatted_response}")
    
    # Parse for attacks using the parse function
    attack_detected2 = parse_for_attacks(response2)
    print(f"\nAttack Detection Result:")
    print(f"  Attack Detected: {attack_detected2}")
    if attack_detected2:
        print("⚠️  Prompt injection attack detected!")
    else:
        print("✓ No prompt injection detected")
    
    # Method 3: Pre-defined policy
    # Note: Replace "YOUR_POLICY_NAME" with your actual policy name
    GUARDRAIL_NAME = "Prompt Injection"  # Replace with your actual policy name
    
    print("\n" + "=" * 80)
    print("METHOD 3: API Call with a Pre-defined Guardrails Policy")
    print("=" * 80)
    response3 = call_guardrails_with_policy(test_prompt, GUARDRAIL_NAME)
    if response3 is None:
        print("\n⚠️  Please set GUARDRAIL_NAME to your actual guardrail name to test this method.")
        print("   You can create policies in the Enkrypt AI dashboard.")
    else:
        formatted_response = json.dumps(response3, indent=2)
        print(f"\nResponse:\n{formatted_response}")
        
        # Parse for attacks using the parse function
        attack_detected3 = parse_for_attacks(response3)
        print(f"\nAttack Detection Result:")
        print(f"  Attack Detected: {attack_detected3}")
        if attack_detected3:
            print("⚠️  Prompt injection attack detected!")
        else:
            print("✓ No prompt injection detected")


if __name__ == "__main__":
    main()
