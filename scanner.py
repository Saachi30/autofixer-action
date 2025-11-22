import os
import subprocess
import requests
import sys

# YOUR DEPLOYED BACKEND URL
SERVER_URL = "https://autofixer-backend.vercel.app/analyze-and-fix"

# Files to analyze for logic/bugs
WATCH_EXT = ('.dart', '.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.cpp', '.html', '.css')

# Additional files to include in the context tree (for link/import checking)
ASSET_EXT = ('.json', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.xml', '.yml', '.yaml')

def get_repo_file_tree():
    """Generates a list of all relevant files in the repo for context."""
    print("DEBUG: Generating repository file map...")
    try:
        cmd = ["git", "ls-files"]
        output = subprocess.check_output(cmd).decode().splitlines()
        
        relevant_files = [
            f for f in output 
            if f.endswith(WATCH_EXT) or f.endswith(ASSET_EXT)
        ]
        return relevant_files
    except Exception as e:
        print(f"⚠️ Could not generate file tree: {e}")
        return []

def get_changed_files():
    print("DEBUG: 1. Starting git operations...")
    try:
        print("DEBUG: 2. Fetching git history...")
        subprocess.run(["git", "fetch", "--no-tags", "--prune", "--depth=5"], check=False)

        print("DEBUG: 3. Running git diff...")
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        raw_output = result.stdout.strip()
        print(f"DEBUG: 4. Raw git output: '{raw_output}'")
        
        if not raw_output:
            return []
            
        return raw_output.splitlines()
    except Exception as e:
        print(f"⚠️ Git Error: {e}")
        return []

def get_analysis_comment(file_path, score, summary, tips):
    """Formats the analysis as a comment block based on file extension."""
    content = f"AI ANALYSIS:\n Quality Score: {score}/100\n Summary: {summary}\n Tips:\n{tips}"
    
    if file_path.endswith('.py'):
        # Python style (#)
        return '\n'.join([f"# {line}" for line in content.splitlines()]) + "\n\n"
    elif file_path.endswith('.html'):
        # HTML style (<!-- -->)
        return f"<!--\n{content}\n-->\n\n"
    else:
        # C-style for JS, TS, Java, Dart, C++, CSS (/* */)
        return f"/*\n{content}\n*/\n\n"

def main():
    print("🕵️ AI Autofixer initialized...")
    
    files = get_changed_files()
    print(f"Files found in commit: {files}")

    if not files:
        print("Stopping: No file changes detected.")
        return

    file_tree = get_repo_file_tree()
    print(f"Indexed {len(file_tree)} files in repository for context.")

    changes_made = False

    for file_path in files:
        if not os.path.exists(file_path): 
            print(f"Skipping {file_path} (File deleted or not found)")
            continue
        
        if not file_path.endswith(WATCH_EXT): 
            print(f"Skipping {file_path} (Not a supported code file)")
            continue

        print(f"Sending {file_path} to AI...")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            payload = {
                "code": code, 
                "filename": file_path,
                "file_tree": file_tree
            }
            
            resp = requests.post(SERVER_URL, json=payload, timeout=60)
            
            if resp.status_code == 200:
                data = resp.json()
                
                result_code = data.get("fixed_code", "")
                summary = data.get("pr_summary", "No summary provided.")
                score = data.get("quality_score", 0)
                tips = data.get("improvement_tips", "")

                # Generate the comment block
                analysis_comment = get_analysis_comment(file_path, score, summary, tips)
                
                # Determine content: use fixed code if available, else original code
                final_code_body = result_code if result_code else code
                
                # Prepend the analysis comment to the code
                final_content = analysis_comment + final_code_body

                # Write to file (This ensures the comment is always added)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                print(f"Added Analysis Comment & Fixes to {file_path}")
                print(f"Score: {score}/100 | 📝 Summary: {summary}")
                changes_made = True
            
            else:
                print(f"❌ Server Error {resp.status_code}: {resp.text}")

        except Exception as e:
            print(f"⚠️ Connection Failed: {e}")

    if changes_made:
        print("Changes successfully written to disk.")
    else:
        print("Script finished. No changes made.")

if __name__ == "__main__":
    main()