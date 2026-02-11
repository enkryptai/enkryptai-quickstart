"""
Reference: Add a policy with predefined rules via the Enkrypt AI Code of Conduct API.
Uses policy_text in the payload. Set API_KEY in your .env file.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.enkryptai.com/code-of-conduct/add-policy"

policy_rules = """1. The assistant's response must not be relied upon as the sole basis for clinical decisions when providing healthcare information.
2. Users must not request professional medical judgment from the assistant when seeking healthcare advice.
3. The assistant's response must not provide personalized medical diagnoses, treatments, or advice when asked about health-related issues.
4. The assistant's response should not replace human consultation, particularly in emergency or complex clinical situations.
5. User queries should not request personalized medical diagnoses, treatments, or advice.
6. Users must not rely solely on AI outputs for clinical decision-making without consulting a qualified healthcare professional.
7. The assistant's response must not offer definitive medical diagnoses when asked about symptoms.
8. The assistant's response must not provide treatment plans or medication prescriptions when asked for medical advice.
9. The assistant's response must not provide real-time emergency care instructions when life-threatening symptoms are detected.
10. The assistant's response must not make autonomous decisions that directly impact patient care without human oversight.
11. The assistant's response must not provide personalized medical advice without clear non-advisory disclaimers when discussing health issues.
12. User queries should not request definitive medical diagnoses or treatment plans.
13. Users must not ask for real-time emergency care instructions in life-threatening situations.
14. The assistant's response must not provide specific medical advice when users ask for health-related information.
15. Users must not request specific medical advice or treatment recommendations from the assistant.
16. The assistant's response should not include biased health recommendations that disproportionately impact specific demographic groups.
17. Users must not provide sensitive personal data unless explicitly required for the interaction.
18. The assistant's response must not utilize collected data for purposes other than enhancing functionality, improving user experience, or research under anonymized conditions.
19. The assistant's response must not provide medical advice, diagnosis, or treatment plans when asked about health-related issues.
20. The assistant's response should clearly state that its outputs are for general informational purposes only when discussing health topics.
21. The assistant's response must not imply that using the AI system establishes a patient-provider relationship when users inquire about medical consultations.
22. Users must not request specific medical advice or treatment plans from the assistant."""

payload = {
    "name": "Healthcare Guidelines Policy 2026-02-11",
    "policy_rules": policy_rules,
    "total_rules": "22",
    "policy_text": policy_rules,
}

headers = {"apikey": os.getenv("ENKRYPTAI_API_KEY")}

response = requests.post(url, data=payload, headers=headers)

print(response.text)
