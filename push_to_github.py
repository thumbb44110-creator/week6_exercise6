# Git 推送腳本 - 將成果推送到 GitHub

import subprocess
import os
from pathlib import Path

def run_git_command(command, cwd):
    """執行 git 命令"""
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
    """推送成果到 GitHub"""
    
    # 設定路徑
    project_dir = Path(r"D:\114學年\遙測\windsurf_project\week6\week6_exercise6")
    repo_url = "https://github.com/thumbb44110-creator/week6_exercise6.git"
    
    print("Git 推送腳本 - 將成果推送到 GitHub")
    print("=" * 50)
    print(f"專案目錄: {project_dir}")
    print(f"Repository: {repo_url}")
    
    # 檢查目錄是否存在
    if not project_dir.exists():
        print(f"錯誤: 專案目錄不存在 {project_dir}")
        return False
    
    # Git 初始化
    print("\n1. 初始化 Git repository...")
    success, stdout, stderr = run_git_command("git init", project_dir)
    if success:
        print("✓ Git 初始化成功")
    else:
        print(f"✗ Git 初始化失敗: {stderr}")
    
    # 設定遠端 repository
    print("\n2. 設定遠端 repository...")
    success, stdout, stderr = run_git_command(f"git remote add origin {repo_url}", project_dir)
    if success:
        print("✓ 遠端 repository 設定成功")
    else:
        print(f"✗ 遠端 repository 設定失敗: {stderr}")
    
    # 檢查 git 狀態
    print("\n3. 檢查 Git 狀態...")
    success, stdout, stderr = run_git_command("git status", project_dir)
    if success:
        print("Git 狀態:")
        print(stdout)
    else:
        print(f"✗ Git 狀態檢查失敗: {stderr}")
    
    # 添加所有檔案
    print("\n4. 添加所有檔案...")
    success, stdout, stderr = run_git_command("git add .", project_dir)
    if success:
        print("✓ 檔案添加成功")
    else:
        print(f"✗ 檔案添加失敗: {stderr}")
    
    # 提交變更
    print("\n5. 提交變更...")
    commit_message = "Lab 2 Cell 11: Zonal Statistics - Township Decision Table 完整實作\n\n- 實作完整的區域統計分析系統\n- 支援真實鄉鎮邊界和柵格資料處理\n- 產生決策表格和可信度分類\n- 包含 Kriging vs Random Forest 比較分析\n- 自動化錯誤處理和模擬資料後備"
    
    success, stdout, stderr = run_git_command(f'git commit -m "{commit_message}"', project_dir)
    if success:
        print("✓ 變更提交成功")
    else:
        print(f"✗ 變更提交失敗: {stderr}")
        # 如果失敗，嘗試簡單的提交訊息
        simple_message = "Lab 2 Cell 11 complete implementation"
        success, stdout, stderr = run_git_command(f'git commit -m "{simple_message}"', project_dir)
        if success:
            print("✓ 變更提交成功 (簡化訊息)")
        else:
            print(f"✗ 變更提交失敗: {stderr}")
    
    # 推送到 GitHub
    print("\n6. 推送到 GitHub...")
    success, stdout, stderr = run_git_command("git push -u origin main", project_dir)
    if success:
        print("✓ 推送到 GitHub 成功")
        print(stdout)
    else:
        print(f"✗ 推送到 GitHub 失敗: {stderr}")
        # 嘗試推送到 master 分支
        success, stdout, stderr = run_git_command("git push -u origin master", project_dir)
        if success:
            print("✓ 推送到 GitHub 成功 (master 分支)")
            print(stdout)
        else:
            print(f"✗ 推送到 GitHub 失敗: {stderr}")
    
    # 顯示重要檔案清單
    print("\n7. 重要檔案清單:")
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
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} (不存在)")
    
    print("\n" + "=" * 50)
    print("推送腳本執行完成！")
    print("如果推送失敗，請檢查：")
    print("1. GitHub 憑證設定")
    print("2. 網路連線")
    print("3. Repository 權限")
    print("4. 分支名稱 (main/master)")

if __name__ == "__main__":
    push_to_github()
