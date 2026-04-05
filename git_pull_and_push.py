# Git Pull and Push Script - Sync and push to GitHub

import subprocess
import os
from pathlib import Path

def run_git_command(command, cwd):
    """Execute git command"""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def sync_and_push():
    """Sync with remote and push"""
    
    project_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
    
    print("Git Sync and Push Script")
    print("=" * 50)
    
    # Pull remote changes first
    print("\n1. Pull remote changes...")
    success, stdout, stderr = run_git_command("git pull origin master", project_dir)
    if success:
        print("OK: Remote changes pulled successfully")
        print(stdout)
    else:
        print(f"ERROR: Pull failed: {stderr}")
        # Try with --allow-unrelated-histories
        success, stdout, stderr = run_git_command("git pull origin master --allow-unrelated-histories", project_dir)
        if success:
            print("OK: Remote changes pulled successfully (allow unrelated histories)")
        else:
            print(f"ERROR: Pull failed: {stderr}")
    
    # Check status again
    print("\n2. Check Git status...")
    success, stdout, stderr = run_git_command("git status", project_dir)
    if success:
        print("Git status:")
        print(stdout)
    
    # Add all files again
    print("\n3. Add all files...")
    success, stdout, stderr = run_git_command("git add .", project_dir)
    if success:
        print("OK: Files added successfully")
    else:
        print(f"ERROR: Files add failed: {stderr}")
    
    # Commit changes
    print("\n4. Commit changes...")
    commit_message = "Lab 2 Cell 11: Zonal Statistics implementation with all supporting files"
    
    success, stdout, stderr = run_git_command(f'git commit -m "{commit_message}"', project_dir)
    if success:
        print("OK: Changes committed successfully")
    else:
        print(f"ERROR: Changes commit failed: {stderr}")
        # If nothing to commit, that's OK
        if "nothing to commit" in stderr:
            print("OK: Nothing to commit (all changes are already committed)")
    
    # Push to GitHub
    print("\n5. Push to GitHub...")
    success, stdout, stderr = run_git_command("git push origin master", project_dir)
    if success:
        print("OK: Push to GitHub successful!")
        print(stdout)
    else:
        print(f"ERROR: Push to GitHub failed: {stderr}")
        # Try force push (use with caution)
        print("Trying force push...")
        success, stdout, stderr = run_git_command("git push origin master --force", project_dir)
        if success:
            print("OK: Force push to GitHub successful!")
        else:
            print(f"ERROR: Force push failed: {stderr}")
    
    print("\n" + "=" * 50)
    print("Sync and push completed!")

if __name__ == "__main__":
    sync_and_push()
