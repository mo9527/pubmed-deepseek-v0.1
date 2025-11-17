from huggingface_hub import snapshot_download
import os



local_download_dir = "D:/bge-m3"
os.makedirs(local_download_dir, exist_ok=True)


snapshot_download(repo_id="BAAI/bge-m3", 
                    local_dir=local_download_dir, 
                    local_dir_use_symlinks=False,
                    allow_patterns=[
                        "*.bin", 
                        "*.pt", 
                        "*.json", 
                        "*.model"
                    ]
                    )
print(f'文件下载完成')
