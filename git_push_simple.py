# Git Push Script - Push results to GitHub

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

def push_to_github():
    """Push results to GitHub"""
    
    # Set paths
    project_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
    repo_url = "https://github.com/thumbb44110-creator/week6_exercise6.git"
    
    print("Git Push Script - Push results to GitHub")
    print("=" * 50)
    print(f"Project directory: {project_dir}")
    print(f"Repository: {repo_url}")
    
    # Check if directory exists
    if not project_dir.exists():
        print(f"ERROR: Project directory not found {project_dir}")
        return False
    
    # Git init
    print("\n1. Initialize Git repository...")
    success, stdout, stderr = run_git_command("git init", project_dir)
    if success:
        print("OK: Git initialized successfully")
    else:
        print(f"ERROR: Git initialization failed: {stderr}")
    
    # Set remote repository
    print("\n2. Set remote repository...")
    success, stdout, stderr = run_git_command(f"git remote add origin {repo_url}", project_dir)
    if success:
        print("OK: Remote repository set successfully")
    else:
        print(f"ERROR: Remote repository setup failed: {stderr}")
    
    # Check git status
    print("\n3. Check Git status...")
    success, stdout, stderr = run_git_command("git status", project_dir)
    if success:
        print("Git status:")
        print(stdout)
    else:
        print(f"ERROR: Git status check failed: {stderr}")
    
    # Add all files
    print("\n4. Add all files...")
    success, stdout, stderr = run_git_command("git add .", project_dir)
    if success:
        print("OK: Files added successfully")
    else:
        print(f"ERROR: Files add failed: {stderr}")
    
    # Commit changes
    print("\n5. Commit changes...")
    commit_message = "Lab 2 Cell 11: Zonal Statistics - Township Decision Table Complete Implementation"
    
    success, stdout, stderr = run_git_command(f'git commit -m "{commit_message}"', project_dir)
    if success:
        print("OK: Changes committed successfully")
    else:
        print(f"ERROR: Changes commit failed: {stderr}")
        # Try simple message
        simple_message = "Lab 2 Cell 11 complete"
        success, stdout, stderr = run_git_command(f'git commit -m "{simple_message}"', project_dir)
        if success:
            print("OK: Changes committed successfully (simple message)")
        else:
            print(f"ERROR: Changes commit failed: {stderr}")
    
    # Push to GitHub
    print("\n6. Push to GitHub...")
    success, stdout, stderr = run_git_command("git push -u origin main", project_dir)
    if success:
        print("OK: Push to GitHub successful")
        print(stdout)
    else:
        print(f"ERROR: Push to GitHub failed: {stderr}")
        # Try master branch
        success, stdout, stderr = run_git_command("git push -u origin master", project_dir)
        if success:
            print("OK: Push to GitHub successful (master branch)")
            print(stdout)
        else:
            print(f"ERROR: Push to GitHub failed: {stderr}")
    
    # Show important files
    print("\n7. Important files list:")
    important_files = [
        "cell11_notebook_final.py",
        "cell11_complete.py", 
        "cell11_success_summary.md",
        "township_decision_table.csv",
        "Week6-Student.ipynb"
    ]
    
    for filename in important_files:
        filepath = project_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  OK {filename} ({size} bytes)")
        else:
            print(f"  MISSING {filename}")
    
    print("\n" + "=" * 50)
    print("Git push script completed!")
    print("If push failed, please check:")
    print("1. GitHub credentials")
    print("2. Network connection")
    print("3. Repository permissions")
    print("4. Branch name (main/master)")

if __name__ == "__main__":
    push_to_github()
