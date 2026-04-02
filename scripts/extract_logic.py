import os
import sys
from github import Github, Auth
from google import genai

def main():
    # 1. Environment Setup - Explicitly using your 'GH_TOKEN' secret name
    token = os.getenv("GH_TOKEN") 
    gemini_key = os.getenv("GEMINI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_num = os.getenv("PR_NUMBER")
    
    # Validation: Fail early if secrets are missing
    if not token or not gemini_key:
        print(f"❌ Error: Missing credentials. Token: {bool(token)}, Key: {bool(gemini_key)}")
        sys.exit(1)

    try:
        # 2. Initialize Clients - FORCING STABLE V1
        # This is the specific fix to prevent the 404 NOT_FOUND error.
        client = genai.Client(api_key=gemini_key, http_options={'api_version': 'v1'})
        gh = Github(auth=Auth.Token(token))
        repo = gh.get_repo(repo_name)

        # 3. Target the Pull Request
        if not pr_num or pr_num == "None":
            print("⚠️ No PR number found. This script is optimized for Pull Requests.")
            return
            
        print(f"🔍 Context: Analyzing PR #{pr_num}")
        pull_request = repo.get_pull(int(pr_num))
        files = pull_request.get_files()

        diff_content = ""
        for file in files:
            if file.patch:
                diff_content += f"\n--- File: {file.filename} ---\n{file.patch}\n"

        if not diff_content:
            print("⚠️ No code changes detected in this PR.")
            return

        # 4. AI Generation - Using Triple Quotes to prevent SyntaxErrors
        print("🤖 Consulting Stable Gemini 1.5-Flash (v1)...")
        prompt = f"""
        Act as a Senior Technical Writer. 
        Analyze the following code changes and generate a concise 'How-to' guide. It should include the following sections:
        Overview Summary
        Prerequisites
        How-to
        Dependencies
        
        CODE DIFFS:
        {diff_content[:8000]}
        """

        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        if not response.text:
            print("⚠️ AI returned an empty response.")
            return

        # 5. Post the Comment to the PR
        comment_body = f"## 📘 AI Documentation Draft\n\n{response.text}\n\n---\n*Verified Production Build*"
        pull_request.create_issue_comment(comment_body)
            
        print("🚀 Success! Documentation posted to the PR.")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
