import os
import subprocess
import requests
import sys

# PASTE YOUR VERCEL URL HERE
SERVER_URL = "https://autofixer-backend.vercel.app/analyze-and-fix"

# Extensions to watch
WATCH_EXT = ('.dart', '.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp')

def get_changed_files():
    try:
        # Get files changed in the last commit
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        return subprocess.check_output(cmd).decode().splitlines()
    except:
        return []

def main():
    print("🕵️ AI Logic Scanner initialized...")
    
    files = get_changed_files()
    if not files:
        print("No file changes detected.")
        return

    changes_made = False

    for file_path in files:
        if not os.path.exists(file_path): continue
        if not file_path.endswith(WATCH_EXT): continue

        print(f"🚀 Analyzing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
            
        try:
            # Send code to your secure backend
            payload = {"code": code, "filename": file_path}
            resp = requests.post(SERVER_URL, json=payload, timeout=30)
            
            if resp.status_code == 200:
                result = resp.json().get("result")
                
                if result == "NO_CHANGES_NEEDED":
                    print(f"✅ {file_path} is clean.")
                elif result:
                    # Only apply if the AI actually changed something
                    if result.strip() != code.strip():
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(result)
                        print(f"🐛 Fixed Logic/Runtime error in {file_path}")
                        changes_made = True
            else:
                print(f"⚠️ Server Error: {resp.text}")

        except Exception as e:
            print(f"⚠️ Connection Failed: {e}")

if __name__ == "__main__":
    main()