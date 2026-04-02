import os
import sys
from github import Github, Auth
from google import genai

def main():
    token = os.getenv("GH_TOKEN") 
    gemini_key = os.getenv("GEMINI_API_KEY")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_num = os.getenv("PR_NUMBER")
    
    try:
        # 1. Initialize Clients - Forcing v1 for production stability
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
            if file.status == "removed":
                continue
                
            print(f"📄 Fetching full content: {file.filename}")
            content = repo.get_contents(file.filename, ref=pull_request.head.sha)
            file_text = content.decoded_content.decode("utf-8")
            full_code_context += f"\n\n--- FILE: {file.filename} ---\n{file_text}\n"

        if not full_code_context:
            print("⚠️ No code files found.")
            return

        # 2. THE FIX: Using Gemini 2.5-Flash
        print("🤖 Analyzing Logic with Gemini 2.5-Flash (Current Stable)...")
        
        prompt = f"""
        Act as a Senior Technical Writer. 
        Analyze the logic of the following security implementation and generate a guide.
        Do not explain the class structure.
        Generate the following format:
        1. Overview of the feature - Max 5 sentences
        2. Prerequisites to enable or consume the feature that is a requirement
        3. How-to section - write down the steps in the correct sequence
        4. Limitations 
        5. Dependencies

        CODE:
        {full_code_context[:15000]} 
        """

        # Switched to 2.5-flash to resolve the 404
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        # 3. Post the Comment
        comment_body = f"## 🧩 Security Logic Overview\n\n{response.text}\n\n---\n*Verified Production Build (2.5-Flash)*"
        pull_request.create_issue_comment(comment_body)
            
        print("🚀 Success!")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
