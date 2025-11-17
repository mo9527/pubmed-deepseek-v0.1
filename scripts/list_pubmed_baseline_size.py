import ftplib
import os

def connect_ftp():
    ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
    ftp.login()
    ftp.cwd("/pubmed/baseline/")
    return ftp

def list_gz_files():
    ftp = connect_ftp()
    files = []
    for f in ftp.mlsd():
        files.append(
            {
                "filename": f[0],
                "size": int(f[1]["size"])/1024/1024
            }
        )
    ftp.quit()
    return files

if __name__ == "__main__":
    files = list_gz_files()
    total_size = sum([f["size"] for f in files])

    print(f'总文件大小:{total_size:.2f} MB')