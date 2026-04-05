# 分析 NLSC 下載模式並改進自動下載

import re
import requests
import time
from urllib.parse import urlparse, parse_qs

def analyze_javascript_pattern():
    """分析 JavaScript __doPostBack 模式"""
    print("=== 分析 NLSC 下載模式 ===")
    print()
    
    # 分析 JavaScript 代碼
    js_code = "javascript:__doPostBack('ctl00$ContentPlaceHolder1$lViewOpenFiles$ctrl3$lnkBtnDownloadFile','')"
    
    print("原始 JavaScript 代碼:")
    print(f"  {js_code}")
    print()
    
    # 解析 __doPostBack 參數
    pattern = r"__doPostBack\('([^']+)','([^']*)'\)"
    match = re.search(pattern, js_code)
    
    if match:
        event_target = match.group(1)
        event_argument = match.group(2)
        
        print("解析結果:")
        print(f"  EventTarget: {event_target}")
        print(f"  EventArgument: {event_argument}")
        print()
        
        # 分析控件結構
        print("控件分析:")
        print("  ctl00$ContentPlaceHolder1$lViewOpenFiles$ctrl3$lnkBtnDownloadFile")
        print("  │")
        print("  ├─ ctl00: 主控件容器")
        print("  ├─ ContentPlaceHolder1: 內容佔位符")
        print("  ├─ lViewOpenFiles: 檔案列表視圖")
        print("  ├─ ctrl3: 第三個控件 (檔案項目)")
        print("  └─ lnkBtnDownloadFile: 下載按鈕")
        print()
        
        return event_target, event_argument
    else:
        print("❌ 無法解析 JavaScript 代碼")
        return None, None

def create_postback_request(event_target, event_argument):
    """建立 POST 請求模擬 __doPostBack"""
    print("=== 建立 POST 請求 ===")
    print()
    
    # NLSC 基礎 URL
    base_url = "https://whgis-nlsc.moi.gov.tw/Opendata/Files.aspx"
    
    # 模擬 ASP.NET POSTBACK 參數
    post_data = {
        '__EVENTTARGET': event_target,
        '__EVENTARGUMENT': event_argument,
        '__VIEWSTATE': '',  # 需要先獲取
        '__VIEWSTATEGENERATOR': '',
        '__EVENTVALIDATION': ''
    }
    
    print("POST 請求參數:")
    for key, value in post_data.items():
        print(f"  {key}: {value}")
    print()
    
    return base_url, post_data

def get_viewstate(session, url):
    """獲取頁面的 VIEWSTATE"""
    print("=== 獲取頁面 VIEWSTATE ===")
    
    try:
        response = session.get(url)
        if response.status_code == 200:
            # 解析 HTML 獲取 VIEWSTATE
            html = response.text
            
            # 查找 VIEWSTATE
            viewstate_pattern = r'name="__VIEWSTATE" value="([^"]*)"'
            viewstate_match = re.search(viewstate_pattern, html)
            
            if viewstate_match:
                viewstate = viewstate_match.group(1)
                print(f"✅ 獲取 VIEWSTATE: {len(viewstate)} 字元")
                return viewstate
            else:
                print("❌ 找不到 VIEWSTATE")
                return None
        else:
            print(f"❌ 無法獲取頁面: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ 獲取 VIEWSTATE 失敗: {e}")
        return None

def test_postback_download():
    """測試 POSTBACK 下載"""
    print("=== 測試 POSTBACK 下載 ===")
    print()
    
    # 分析 JavaScript 模式
    event_target, event_argument = analyze_javascript_pattern()
    
    if not event_target:
        print("❌ 無法分析 JavaScript 模式")
        return False
    
    # 建立 POST 請求
    base_url, post_data = create_postback_request(event_target, event_argument)
    
    # 建立會話
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': base_url,
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    
    # 獲取 VIEWSTATE
    viewstate = get_viewstate(session, base_url)
    if viewstate:
        post_data['__VIEWSTATE'] = viewstate
    
    try:
        print("發送 POST 請求...")
        response = session.post(base_url, data=post_data, timeout=30)
        
        print(f"回應狀態: {response.status_code}")
        print(f"內容長度: {len(response.content)} bytes")
        print(f"內容類型: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            # 檢查是否為檔案下載
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"Content-Type: {content_type}")
            print(f"Content-Disposition: {content_disposition}")
            
            if 'application/octet-stream' in content_type or 'attachment' in content_disposition:
                print("✅ 成功觸發檔案下載!")
                
                # 獲取檔案名稱
                filename_pattern = r'filename="?([^"]+)"?'
                filename_match = re.search(filename_pattern, content_disposition)
                filename = filename_match.group(1) if filename_match else 'downloaded_file.zip'
                
                print(f"檔案名稱: {filename}")
                
                # 儲存檔案
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 檔案已儲存: {filename} ({len(response.content)} bytes)")
                return True
            else:
                print("⚠️ 不是檔案下載，可能是頁面重新載入")
                print("回應內容預覽:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return False
        else:
            print(f"❌ POST 請求失敗: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ POST 請求異常: {e}")
        return False

def analyze_download_urls():
    """分析可能的下載 URL 模式"""
    print("=== 分析下載 URL 模式 ===")
    print()
    
    # 基於 ASP.NET 模式的可能 URL
    url_patterns = [
        # 直接下載端點
        "https://whgis-nlsc.moi.gov.tw/DownloadFile.ashx",
        "https://whgis-nlsc.moi.gov.tw/DownloadHandler.ashx",
        "https://whgis-nlsc.moi.gov.tw/FileDownload.ashx",
        "https://whgis-nlsc.moi.gov.tw/GetFile.ashx",
        
        # 帶參數的下載端點
        "https://whgis-nlsc.moi.gov.tw/DownloadFile.ashx?file=TOWN_MOI",
        "https://whgis-nlsc.moi.gov.tw/DownloadFile.ashx?id=TOWN_MOI",
        "https://whgis-nlsc.moi.gov.tw/DownloadFile.ashx?name=TOWN_MOI.zip",
        
        # 原有的 DownlaodFiles 端點 (修正拼寫)
        "https://whgis-nlsc.moi.gov.tw/DownloadFiles.ashx?oid=1437",
        "https://whgis-nlsc.moi.gov.tw/DownloadFiles.ashx?oid=1436",
        "https://whgis-nlsc.moi.gov.tw/DownloadFiles.ashx?oid=1435",
        
        # 新的端點模式
        "https://whgis-nlsc.moi.gov.tw/api/download/TOWN_MOI",
        "https://whgis-nlsc.moi.gov.tw/api/files/TOWN_MOI.zip",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    successful_urls = []
    
    for i, url in enumerate(url_patterns, 1):
        print(f"測試 {i}/{len(url_patterns)}: {url}")
        
        try:
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                
                print(f"  ✅ 狀態: {response.status_code}")
                print(f"  📄 類型: {content_type}")
                print(f"  📏 長度: {content_length} bytes")
                
                if int(content_length) > 1000:  # 大於 1KB
                    successful_urls.append(url)
                    print(f"  🎯 可能的有效端點!")
                else:
                    print(f"  ⚠️ 檔案太小")
            else:
                print(f"  ❌ 狀態: {response.status_code}")
        
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
        
        time.sleep(0.5)
    
    print(f"\n=== 測試結果 ===")
    print(f"成功的 URL: {len(successful_urls)}")
    for url in successful_urls:
        print(f"  {url}")
    
    return successful_urls

def create_improved_download_function():
    """建立改進的下載函數"""
    print("=== 建立改進的下載函數 ===")
    print()
    
    improved_code = '''
def improved_download_township_boundaries_nlsc(target_dir="data", force_download=False):
    """改進的 NLSC 鄉鎮邊界下載函數"""
    print("\\n" + "=" * 60)
    print("🌐 改進的 NLSC 鄉鎮邊界下載")
    print("=" * 60)
    
    # 安全建立目標目錄
    target_path = safe_mkdir(target_dir)
    
    # 檢查是否已存在檔案
    township_files = [
        target_path / "TOWN_MOI.shp",
        target_path / "TOWN_MOI.shx", 
        target_path / "TOWN_MOI.dbf",
        target_path / "TOWN_MOI.prj"
    ]
    
    existing_files = [f for f in township_files if f.exists()]
    all_files_exist = len(existing_files) == len(township_files)
    
    if all_files_exist and not force_download:
        print(f"✅ 所有鄉鎮邊界檔案已存在")
        return True
    
    # 方法 1: 嘗試 POSTBACK 下載
    print("\\n🔄 嘗試 POSTBACK 下載...")
    if test_postback_download():
        return True
    
    # 方法 2: 嘗試直接 URL 模式
    print("\\n🔄 嘗試直接 URL 模式...")
    successful_urls = analyze_download_urls()
    
    for url in successful_urls:
        try:
            print(f"\\n📥 嘗試下載: {url}")
            response = requests.get(url, timeout=30, stream=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                
                if int(content_length) > 1000 and 'zip' in content_type:
                    # 下載並解壓縮
                    import zipfile
                    import io
                    
                    file_content = b''
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file_content += chunk
                    
                    with zipfile.ZipFile(io.BytesIO(file_content)) as zip_file:
                        file_list = zip_file.namelist()
                        
                        if any('TOWN' in f.upper() for f in file_list):
                            for filename in file_list:
                                if any(ext in filename.upper() for ext in ['.SHP', '.SHX', '.DBF', '.PRJ']):
                                    zip_file.extract(filename, target_path)
                            
                            print(f"✅ 成功下載並解壓縮: {url}")
                            return True
        
        except Exception as e:
            print(f"  ❌ 下載失敗: {e}")
    
    # 方法 3: 原有方法
    print("\\n🔄 使用原有下載方法...")
    return download_township_boundaries_nlsc(target_dir, force_download)
'''
    
    print("改進的下載函數特色:")
    print("  1. POSTBACK 模擬 - 基於 JavaScript __doPostBack")
    print("  2. 直接 URL 嘗試 - 多種可能的下載端點")
    print("  3. 原有方法後備 - 使用現有的 DownlaodFiles 端點")
    print("  4. 多重錯誤處理 - 確保在各種情況下都能工作")
    print()
    
    return improved_code

def main():
    """主要分析函數"""
    print("=== NLSC 下載模式分析 ===")
    print("=" * 50)
    
    # 1. 分析 JavaScript 模式
    analyze_javascript_pattern()
    
    # 2. 測試 POSTBACK 下載
    print("\\n" + "=" * 50)
    test_postback_download()
    
    # 3. 分析 URL 模式
    print("\\n" + "=" * 50)
    analyze_download_urls()
    
    # 4. 產生改進的函數
    print("\\n" + "=" * 50)
    create_improved_download_function()

if __name__ == "__main__":
    main()
else:
    print("=== NLSC 下載模式分析模組 ===")
    print("使用 main() 執行完整分析")
