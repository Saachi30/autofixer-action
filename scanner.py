import os
import subprocess
import requests
import sys

SERVER_URL = "https://autofixer-backend.vercel.app/analyze-and-fix"

# File types to check
WATCH_EXT = ('.dart', '.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.rs', '.java', '.cpp', '.html', '.css')

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
        print(f"Git Error: {e}")
        return []

def main():
    print("AI Autofixer initialized...")
    
    files = get_changed_files()
    print(f"Files found in commit: {files}")

    if not files:
        print("Stopping: No file changes detected.")
        # Optional: Uncomment below to scan ALL files if diff fails (for testing)
        # print("⚠️ Falling back to scanning ALL files for test...")
        # files = [f for f in os.listdir('.') if f.endswith(WATCH_EXT)]
        return

    changes_made = False

    for file_path in files:
        # Check if file exists
        if not os.path.exists(file_path): 
            print(f"Skipping {file_path} (File deleted or not found)")
            continue
        
        # Check extension
        if not file_path.endswith(WATCH_EXT): 
            print(f"Skipping {file_path} (Not a supported code file)")
            continue

        print(f"Sending {file_path} to AI...")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            payload = {"code": code, "filename": file_path}
            resp = requests.post(SERVER_URL, json=payload, timeout=60)
            
            if resp.status_code == 200:
                result = resp.json().get("result")
                print(f"✅ AI Response received for {file_path}")
                
                if result == "NO_CHANGES_NEEDED":
                    print(f"AI says: {file_path} is clean.")
                elif result:
                    clean_result = result.strip()
                    if clean_result != code.strip():
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(clean_result)
                        print(f"🐛 FIX APPLIED to {file_path}")
                        changes_made = True
                    else:
                        print(f"🤔 AI returned code, but it was identical.")
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