import requests
import time
from dotenv import load_dotenv
import os
import json

load_dotenv()

ENKRYPTAI_API_KEY = os.getenv("ENKRYPTAI_API_KEY")
ENKRYPTAI_GUARDRAILS_NAME = "ENKRYPTAI_GUARDRAILS_NAME"
LOGS_FILE_PATH = "logs.json"
BATCH_SIZE = 10  # Number of logs to process in each batch

def call_guardrails_batch(texts, guardrail_name, max_retries=5, initial_backoff=1):
    """
    Run text through Enkrypt AI guardrails to detect violations with exponential backoff for rate limits.
    
    Args:
        text (str): The text content to check
        guardrail_name (str): The name of the guardrail policy to use
        max_retries (int): Maximum number of retry attempts for 429 errors
        initial_backoff (int): Initial backoff time in seconds
        
    Returns:
        dict: Guardrails API response
    """

    url = "https://api.enkryptai.com/guardrails/policy/batch/detect"
    headers = {
        "Content-Type": "application/json",
        "apikey": ENKRYPTAI_API_KEY,
        "X-Enkrypt-Policy": guardrail_name
    }
    
    payload = {
        "texts": texts
    }
    
    backoff_time = initial_backoff
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Handle 429 Rate Limit errors
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"⚠️  Rate limit hit (429), retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponential backoff
                    continue
                else:
                    return {"error": f"Rate limit exceeded after {max_retries} attempts"}
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and "429" in str(e):
                print(f"⚠️  Rate limit detected, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(backoff_time)
                backoff_time *= 2
                continue
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
    
    return {"error": "Max retries exceeded"}

# Load logs from file
with open(LOGS_FILE_PATH, 'r') as file:
    logs = json.load(file)

# Extract prompts from logs
prompts = [log['prompt'] for log in logs]
total_prompts = len(prompts)

print(f"📊 Processing {total_prompts} logs in batches of {BATCH_SIZE}...")

# Process logs in batches
all_results = []
batch_count = 0

for i in range(0, total_prompts, BATCH_SIZE):
    batch_count += 1
    batch_end = min(i + BATCH_SIZE, total_prompts)
    batch_prompts = prompts[i:batch_end]
    
    print(f"\n🔄 Processing batch {batch_count} (logs {i+1}-{batch_end} of {total_prompts})...")
    
    # Call guardrails API for this batch
    batch_results = call_guardrails_batch(batch_prompts, ENKRYPTAI_GUARDRAILS_NAME)
    
    # Check if there was an error
    if "error" in batch_results:
        print(f"❌ Error in batch {batch_count}: {batch_results['error']}")
        # Store error information with batch details
        all_results.append({
            "batch": batch_count,
            "range": f"{i+1}-{batch_end}",
            "error": batch_results['error']
        })
    else:
        print(f"✅ Batch {batch_count} completed successfully")
        # Store results with batch information
        if isinstance(batch_results, dict) and 'results' in batch_results:
            # If API returns results in a 'results' field
            all_results.extend(batch_results['results'])
        elif isinstance(batch_results, list):
            # If API returns a list directly
            all_results.extend(batch_results)
        else:
            # Store the entire batch result
            all_results.append({
                "batch": batch_count,
                "range": f"{i+1}-{batch_end}",
                "results": batch_results
            })
    
    # Add a small delay between batches to avoid rate limiting
    if i + BATCH_SIZE < total_prompts:
        time.sleep(0.5)

print(f"\n✨ Processing complete! Processed {batch_count} batches.")

# Save the results to a new file in a pretty format
output_data = {
    "total_logs": total_prompts,
    "batch_size": BATCH_SIZE,
    "total_batches": batch_count,
    "results": all_results
}

with open('guardrails_results.json', 'w') as file:
    json.dump(output_data, file, indent=4)

print(f"💾 Results saved to guardrails_results.json")