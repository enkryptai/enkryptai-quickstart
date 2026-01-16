import requests
import json
import os
import zipfile
from dotenv import load_dotenv

load_dotenv()

# ============================================
# Configuration - Update these values
# ============================================

# Specify the test name from your red team test
TEST_NAME = "ENTER_TEST_NAME_HERE"

# API Key - loads from environment or can be overridden
ENKRYPT_API_KEY = os.getenv('ENKRYPTAI_API_KEY')

# Uncomment and set if you want to override the API key from environment
# ENKRYPT_API_KEY = "YOUR_API_KEY_HERE"

# ============================================
# Download Red Team Results
# ============================================

if not ENKRYPT_API_KEY:
    print("❌ ENKRYPTAI_API_KEY not found in environment variables")
    print("Please set your API key in the .env file or uncomment the override above")
    exit(1)

if TEST_NAME == "ENTER_TEST_NAME_HERE":
    print("❌ Please update TEST_NAME with your actual test name")
    exit(1)

print("=== Downloading Red Team Results ===")
print(f"📥 Test Name: {TEST_NAME}")

url = "https://api.enkryptai.com/redteam/download-link"

headers = {
    "X-Enkrypt-Test-Name": TEST_NAME,
    "apikey": ENKRYPT_API_KEY
}

try:
    response = requests.get(url, headers=headers)
    result = response.json()
    
    if 'link' in result:
        download_url = result['link']
        print(f"\n✅ Download link received")
        print(f"📦 Downloading file from: {download_url}")
        
        # Download the file
        download_response = requests.get(download_url)
        
        if download_response.status_code == 200:
            # Save the file
            filename = f"{TEST_NAME.replace(' ', '_')}_redteam_results.zip"
            with open(filename, 'wb') as f:
                f.write(download_response.content)
            print(f"✅ File downloaded successfully: {filename}")
            
            # Extract the zip file
            extract_folder = f"{TEST_NAME.replace(' ', '_')}_redteam_results"
            print(f"\n📂 Extracting to: {extract_folder}/")
            
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            print(f"✅ File extracted successfully to: {extract_folder}/")
            
            # List extracted files
            extracted_files = os.listdir(extract_folder)
            print(f"\n📋 Extracted {len(extracted_files)} file(s):")
            for file in extracted_files[:10]:  # Show first 10 files
                print(f"   • {file}")
            if len(extracted_files) > 10:
                print(f"   ... and {len(extracted_files) - 10} more")
        else:
            print(f"❌ Failed to download file. Status code: {download_response.status_code}")
    else:
        print("❌ No download link found in response")
        print(f"Response: {json.dumps(result, indent=2)}")
        print("\n💡 Make sure the test has completed before downloading results.")
        
except Exception as e:
    print(f"❌ Error downloading results: {e}")
    print("\n💡 Make sure:")
    print("   • The test has completed")
    print("   • The test name is correct")
    print("   • Your API key is valid")
