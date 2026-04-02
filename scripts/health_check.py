import os
import sys
from google import genai

def main():
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("❌ Health Check Failed: GEMINI_API_KEY is missing from Secrets.")
        sys.exit(1)

    try:
        # Initializing with the same stable v1 logic we used in the main script
        client = genai.Client(api_key=gemini_key, http_options={'api_version': 'v1'})
        
        print("📡 Pinging Gemini 2.5-Flash...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello! This is a system health check. Respond with 'Online'."
        )
        
        if "Online" in response.text:
            print("✅ API Status: Healthy. Gemini is responding correctly.")
        else:
            print(f"⚠️ API Status: Partial. Response received but unexpected: {response.text}")
            
    except Exception as e:
        print(f"❌ Health Check Failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
