import argparse
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# Configuration - Update these values
# ============================================

# API Key - loads from environment or can be overridden
ENKRYPT_API_KEY = os.getenv('ENKRYPTAI_API_KEY')

# Uncomment and set if you want to override the API key from environment
# ENKRYPT_API_KEY = "YOUR ENKRYPTAI API KEY HERE"

# Specify either test name OR task ID (at least one is required)
TEST_NAME = "ENTER TEST NAME HERE"
TASK_ID = ""

# Output file path for the summary results (set to None to skip saving)
OUTPUT_FILE = "redteam_summary.json"

# ============================================
# Command-line argument support
# ============================================
# Command-line args override the values above.
#
# Usage:
#   python get_redteaming_summary.py --test-name "my_test"
#   python get_redteaming_summary.py --task-id "abc123"
#   python get_redteaming_summary.py --test-name "my_test" --output results.json
#   python get_redteaming_summary.py --api-key "sk-..." --test-name "my_test"

parser = argparse.ArgumentParser(
    description="Fetch red team test summary from the Enkrypt AI API."
)
parser.add_argument("--test-name", help="Red team test name")
parser.add_argument("--task-id", help="Red team task ID")
parser.add_argument("--output", help="Output file path for the summary (default: redteam_summary.json)")
parser.add_argument("--api-key", help="Enkrypt AI API key (overrides env variable)")

args = parser.parse_args()

if args.api_key:
    ENKRYPT_API_KEY = args.api_key
if args.test_name:
    TEST_NAME = args.test_name
if args.task_id:
    TASK_ID = args.task_id
if args.output:
    OUTPUT_FILE = args.output

# ============================================
# Get Red Team Summary
# ============================================

if not ENKRYPT_API_KEY:
    print("❌ ENKRYPTAI_API_KEY not found in environment variables")
    print("Please set your API key in the .env file, uncomment the override above,")
    print("or pass --api-key on the command line.")
    exit(1)

if not TEST_NAME and not TASK_ID:
    print("❌ Please set either TEST_NAME or TASK_ID (in-file or via --test-name / --task-id)")
    exit(1)

print("=== Fetching Red Team Summary ===")
if TEST_NAME:
    print(f"📋 Test Name: {TEST_NAME}")
if TASK_ID:
    print(f"🆔 Task ID:   {TASK_ID}")

url = "https://api.enkryptai.com/redteam/v3/results/summary"

headers = {"apikey": ENKRYPT_API_KEY}
if TEST_NAME:
    headers["X-Enkrypt-Test-Name"] = TEST_NAME
if TASK_ID:
    headers["X-Enkrypt-Task-ID"] = TASK_ID

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    result = response.json()
    formatted = json.dumps(result, indent=2)

    print(f"\n✅ Summary retrieved successfully\n")
    print(formatted)

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, "w") as f:
            f.write(formatted)
        print(f"\n📁 Summary saved to: {OUTPUT_FILE}")

except requests.exceptions.HTTPError as e:
    print(f"❌ API request failed (HTTP {response.status_code}): {e}")
    print("\n💡 Make sure your API key is valid.")
except requests.exceptions.RequestException as e:
    print(f"❌ Network error: {e}")
except json.JSONDecodeError:
    print("❌ Failed to parse API response as JSON")
    print(f"Raw response:\n{response.text}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
