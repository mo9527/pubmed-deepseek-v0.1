import ftplib
import os
import gzip
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

FTP_HOST = "ftp.ncbi.nlm.nih.gov"
FTP_DIR = "/pubmed/baseline/"
SAVE_DIR = "pubmed_baseline"     # 保存目录
MAX_WORKERS = 4                  

os.makedirs(SAVE_DIR, exist_ok=True)


def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_DIR)
    return ftp


def list_pubmed_files():
    ftp = connect_ftp()
    files = [f for f in ftp.nlst() if f.endswith(".gz")]
    ftp.quit()
    return files[:10] #test 取前10个文件


def download_with_resume(filename):
    local_path = os.path.join(SAVE_DIR, filename)
    
    ftp = connect_ftp()

    try:
        size = ftp.size(filename)
    except Exception as e:
        print(f"无法获取远程文件大小 {filename}: {e}")
        return

    if os.path.exists(local_path) and os.path.getsize(local_path) == size:
        print(f"[跳过] 已存在 {filename}")
        ftp.quit()
        return

    local_size = 0
    if os.path.exists(local_path):
        local_size = os.path.getsize(local_path)

    # 从断点续传
    with open(local_path, "ab") as f:
        print(f"[下载] {filename} (从 {local_size}/{size} 字节)")
        
        def callback(data):
            f.write(data)

        # 从 local_size 开始下载
        ftp.retrbinary(f"RETR {filename}", callback, rest=local_size)

    ftp.quit()
    print(f"下载完毕：{filename}")


def unzip_gz(file_path):
    """解压 .gz 文件"""
    if not file_path.endswith(".gz"):
        return

    # 1. 构造输出文件的正确路径，例如： pubmed_baseline/xml/pubmed23n0001.xml
    output_dir = os.path.join(SAVE_DIR, 'xml')
    os.makedirs(output_dir, exist_ok=True)
    
    base_filename = os.path.basename(file_path) #  pubmed23n0001.xml.gz
    output_filename = base_filename[:-3] #  pubmed23n0001.xml
    output_filepath = os.path.join(output_dir, output_filename)

    # 2. 检查目标文件是否已存在
    if os.path.exists(output_filepath):
        print(f"[跳过] 已存在解压后的文件 {output_filepath}")
        return
    
    print(f"[解压] {file_path} → {output_filepath}")
    with gzip.open(file_path, "rb") as f_in:
        # 3. 打开目标文件路径进行写入，而不是目录
        with open(output_filepath, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def main():
    print("连接到 NCBI PubMed FTP 服务器...")
    files = list_pubmed_files()
    print(f"找到 {len(files)} 个 baseline 文件。开始下载...")

    # 并发下载
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {
            executor.submit(download_with_resume, fname): fname
            for fname in files
        }
        for future in as_completed(future_to_file):
            fname = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                print(f"[错误] 下载 {fname} 失败: {e}")

    print("文件下载完成，开始解压...")

    # 解压所有 gz
    for gz in files:
        unzip_gz(os.path.join(SAVE_DIR, gz))

    print("PubMed baseline 下载与解压完成！")


if __name__ == "__main__":
    main()
