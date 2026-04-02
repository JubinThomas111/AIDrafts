import os
import sys
from github import Github, Auth

def main():
    # 1. Environment Setup
    token = os.getenv("GH_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    
    if not token or not repo_name:
        print("❌ Error: GH_TOKEN or GITHUB_REPOSITORY environment variables are missing.")
        sys.exit(1)

    try:
        # 2. Initialize GitHub Client
        gh = Github(auth=Auth.Token(token))
        repo = gh.get_repo(repo_name)

        # 3. Fetch the 30 most recent Pull Requests (Merged or Open)
        print(f"🔍 Auditing the last 30 PRs in {repo_name}...\n")
        pulls = repo.get_pulls(state='all', sort='updated', direction='desc')[:30]

        missing_count = 0
        
        print(f"{'PR #':<8} | {'Status':<10} | {'AI Doc Status'}")
        print("-" * 50)

        for pr in pulls:
            # We look for the specific header used by our AI script
            SIGNATURE = "## 🧩 Technical Logic Overview"
            
            # Fetch all comments on the PR
            comments = pr.get_issue_comments()
            
            # CHECK LOGIC: Does any comment contain our signature?
            has_ai_doc = any(SIGNATURE in c.body for c in comments)

            status_label = "MERGED" if pr.merged else pr.state.upper()
            
            if not has_ai_doc:
                doc_status = "❌ MISSING"
                missing_count += 1
                print(f"{pr.number:<8} | {status_label:<10} | {doc_status} -> {pr.title}")
            else:
                doc_status = "✅ FOUND"
                print(f"{pr.number:<8} | {status_label:<10} | {doc_status} -> {pr.title}")

        print("-" * 50)
        if missing_count > 0:
            print(f"\n📢 Audit Complete: {missing_count} PRs require documentation.")
            print("👉 Use the 'Manual Trigger' in GitHub Actions to backfill these PR numbers.")
        else:
            print("\n✨ All audited PRs are fully documented!")

    except Exception as e:
        print(f"❌ Audit Failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
