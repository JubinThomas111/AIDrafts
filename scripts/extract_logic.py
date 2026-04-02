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
    
    try:
        # 2. Initialize Clients - Forcing v1 for stability
        client = genai.Client(api_key=gemini_key, http_options={'api_version': 'v1'})
        gh = Github(auth=Auth.Token(token))
        repo = gh.get_repo(repo_name)

        if not pr_num or pr_num == "None":
            print("⚠️ No PR number found.")
            return
            
        pull_request = repo.get_pull(int(pr_num))
        files = pull_request.get_files()

        full_code_context = ""
        for file in files:
            # Skip deleted files
            if file.status == "removed":
                continue
                
            print(f"📄 Fetching full content for: {file.filename}")
            # We get the 'raw' content of the file from the branch, not just the diff
            content = repo.get_contents(file.filename, ref=pull_request.head.sha)
            file_text = content.decoded_content.decode("utf-8")
            full_code_context += f"\n\n--- FULL FILE: {file.filename} ---\n{file_text}\n"

        if not full_code_context:
            print("⚠️ No code files found to analyze.")
            return

        # 3. AI Generation - Requesting Logic Analysis
        print("🤖 Analyzing Full Code Logic with Gemini 2.0-Flash...")
        
        prompt = f"""
        Act as a Senior Technical Writer. 
        Analyze the logic of the following files and generate a comprehensive 'Technical Overview'.
        Focus on:
        1. The primary purpose of the code.
        2. Key functions/classes and how they interact.
        3. Logic flow for security or data processing.

        CODE CONTEXT:
        {full_code_context[:15000]} 
        """

        # Note: Using 'gemini-2.0-flash' as it is the current global stable workhorse
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # 4. Post the Comment
        comment_body = f"## 🧩 Technical Logic Overview\n\n{response.text}\n\n---\n*Generated from full file context*"
        pull_request.create_issue_comment(comment_body)
            
        print("🚀 Success! Logic overview posted.")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
