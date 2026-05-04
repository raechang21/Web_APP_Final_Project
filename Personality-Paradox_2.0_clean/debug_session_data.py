"""
診斷工具：檢查 Flask session 中存儲的測驗數據
"""
import os
import pickle
from flask.sessions import SecureCookieSessionInterface

def read_session_file(session_dir, session_filename):
    """讀取 Flask session 文件內容"""
    session_path = os.path.join(session_dir, session_filename)
    #測試
    try:
        with open(session_path, 'rb') as f:
            data = pickle.load(f)
            
        print(f"\n{'='*60}")
        print(f"Session 文件: {session_filename}")
        print(f"{'='*60}\n")
        
        # 檢查關鍵數據
        keys_to_check = ['mbti', 'bigfive_scores', 'zodiac', 'dark_triad_scores', 'analysis']
        
        for key in keys_to_check:
            if key in data:
                print(f"✅ {key}:")
                if isinstance(data[key], dict):
                    for sub_key, value in data[key].items():
                        if isinstance(value, float):
                            print(f"   {sub_key}: {value:.2f}")
                        elif isinstance(value, dict):
                            print(f"   {sub_key}:")
                            for k, v in value.items():
                                if isinstance(v, float):
                                    print(f"      {k}: {v:.2f}")
                                else:
                                    print(f"      {k}: {v}")
                        else:
                            print(f"   {sub_key}: {value}")
                else:
                    print(f"   {data[key]}")
                print()
            else:
                print(f"❌ {key}: 不存在\n")
        
        # 顯示完整原始數據
        print(f"\n{'='*60}")
        print("完整 Session 數據:")
        print(f"{'='*60}\n")
        for key, value in data.items():
            print(f"{key}: {value}")
            print()
            
    except Exception as e:
        print(f"❌ 讀取失敗: {e}")

if __name__ == '__main__':
    session_dir = 'flask_session'
    
    # 列出所有 session 文件
    if os.path.exists(session_dir):
        session_files = [f for f in os.listdir(session_dir) if not f.startswith('.')]
        
        if session_files:
            print(f"找到 {len(session_files)} 個 session 文件:\n")
            for i, filename in enumerate(session_files, 1):
                print(f"{i}. {filename}")
            
            # 讀取每個 session 文件
            for filename in session_files:
                read_session_file(session_dir, filename)
        else:
            print("沒有找到 session 文件")
    else:
        print(f"❌ {session_dir} 目錄不存在")
