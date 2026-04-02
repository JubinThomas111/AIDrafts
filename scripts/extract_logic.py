import os
import sys
from github import Github, Auth
from google import genai

def main():
    # 1. Environment Setup
    token = os.getenv("GH_TOKEN") 
    gemini_key = os.getenv("GEMINI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_num = os.getenv("PR_NUMBER")
    
    if not token or not gemini_key:
        print(f"❌ Error: Missing credentials. Check GitHub Secrets.")
        sys.exit(1)

    try:
        # 2. Initialize Clients - Using Stable v1
        client = genai.Client(api_key=gemini_key, http_options={'api_version': 'v1'})
        gh = Github(auth=Auth.Token(token))
        repo = gh.get_repo(repo_name)

        if not pr_num or pr_num == "None":
            print("⚠️ No PR number found.")
            return
            
        pull_request = repo.get_pull(int(pr_num))
        files = pull_request.get_files()

        diff_content = ""
        for file in files:
            if file.patch:
                diff_content += f"\n--- File: {file.filename} ---\n{file.patch}\n"

        if not diff_content:
            print("⚠️ No code changes detected.")
            return

        # 3. AI Generation - SWITCHED TO GEMINI 2.5 FLASH (Current Stable)
        print("🤖 Consulting Stable Gemini 2.5-Flash (v1)...")
        prompt = f"""
        Act as a Senior Technical Writer. 
        Analyze the following code changes and generate a concise 'How-to' guide.
        In the following format:
        Overview
        Prerequisites
        How-to
        Dependencies
        
        CODE DIFFS:
        {diff_content[:8000]}
        """

        # Using the new stable model ID to fix the 404 error
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        # 4. Post the Comment
        comment_body = f"## 📘 AI Documentation Draft\n\n{response.text}\n\n---\n*Verified Production Build*"
        pull_request.create_issue_comment(comment_body)
            
        print("🚀 Success! Documentation posted to PR.")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
