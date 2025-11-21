import os
import glob
import math
from lxml import etree
from qdrant_client import QdrantClient, models
# 导入 SentenceTransformer 库
from sentence_transformers import SentenceTransformer

# --- 配置 ---
COLLECTION_NAME = "pubmed" # 集合名称略作修改以区分
QDRANT_HOST = "localhost" # 替换为您的 Qdrant 服务地址
QDRANT_PORT = 6333
# SentenceTransformer 将直接从 Hugging Face Hub 下载模型（如果本地没有缓存）
MODEL_NAME = "BAAI/bge-m3" 
XML_ROOT_DIR = "pubmed_baseline/xml" # 您的 XML 文件根目录
BATCH_FILE_SIZE = 10         # 每批次处理的文件数量

BGE_M3_DIMENSION = 1024
# 定义 PubMed XML 的常用命名空间
NS = {'pubmed': 'http://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_250101.dtd'}

# --- 核心函数 (XML 解析) ---

def parse_pubmed_xml(xml_file_path):
    """解析单个 PubMed XML 文件，返回文章列表。"""
    try:
        # 使用 lxml 解析，它可以处理大型文件和命名空间
        tree = etree.parse(xml_file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"⚠️ 无法解析文件 {xml_file_path}: {e}")
        return []
        
    articles = []
    
    for article_node in root.findall('.//PubmedArticle'):
        try:
            pmid = article_node.xpath('.//PMID/text()')[0]
            
            title_node = article_node.xpath('.//ArticleTitle')
            title = title_node[0].text.strip() if title_node and title_node[0].text else "No Title"

            abstract_parts = article_node.xpath('.//AbstractText/text()')
            abstract = ' '.join(part.strip() for part in abstract_parts if part).strip()
            
            authors = []
            for author in article_node.xpath('.//AuthorList/Author'):
                last_name = author.xpath('./LastName/text()')
                fore_names = author.xpath('./ForeName/text()')
                if last_name and fore_names:
                    authors.append(f"{last_name[0]}, {fore_names[0]}")
                elif last_name:
                    authors.append(last_name[0])

            date_revised_parts = article_node.xpath('.//DateRevised')
            update_date = None
            if date_revised_parts:
                date_node = date_revised_parts[0]
                year = date_node.xpath('./Year/text()')[0]
                month = date_node.xpath('./Month/text()')[0]
                day = date_node.xpath('./Day/text()')[0]
                update_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            journal_title_node = article_node.xpath('.//Journal/Title/text()')
            journal_title = journal_title_node[0] if journal_title_node else None

            # 嵌入源文本 (Title + Abstract)
            embedding_text = f"Title: {title}. Abstract: {abstract}"

            articles.append({
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'update_date': update_date,
                'journal_title': journal_title,
                'embedding_text': embedding_text,
            })
            
        except Exception:
            # 忽略解析失败的文章
            continue
            
    print(f"✅ 文件 {os.path.basename(xml_file_path)} 解析完成，提取 {len(articles)} 篇文章。")
    return articles


def ingest_to_qdrant(articles, model, client):
    """生成嵌入并批量上传到 Qdrant。"""
    
    embedding_texts = [art['embedding_text'] for art in articles]
    
    print(f"🧠 正在生成 {len(articles)} 篇文章的 SentenceTransformer 嵌入...")
    
    # --- 关键更改：使用 SentenceTransformer.encode ---
    # BGE-M3 模型是 SentenceTransformer 兼容的，所以直接调用 encode 即可
    dense_vectors = model.encode(
        sentences=embedding_texts, 
        batch_size=32,
        normalize_embeddings=True, # 建议启用归一化，这对向量检索非常关键
        show_progress_bar=False
    ).tolist()
    
    points = []
    for i, article in enumerate(articles):
        payload = {
            "pmid": article['pmid'],
            "title": article['title'],
            "abstract": article['abstract'],
            "authors": article['authors'],
            "update_date": article['update_date'],
            "journal_title": article['journal_title'],
        }

        # 构造 PointStruct
        try:
            point_id = int(article['pmid'])
        except ValueError:
            point_id = article['pmid']

        points.append(models.PointStruct(
            id=point_id, 
            vector=dense_vectors[i],
            payload=payload
        ))

    # 批量上传
    print(f"\n⬆️ 正在批量上传 {len(points)} 个 Points 到 Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=points,
        batch_size=128
    )

    print("✅ 数据入库完成！")


def main(payload:dict = None):
    if not os.path.isdir(XML_ROOT_DIR):
        print(f"❌ 错误：XML 文件目录不存在或路径不正确: {XML_ROOT_DIR}")
        exit()

    try:
        print(f"🧠 正在加载 SentenceTransformer 模型: {MODEL_NAME}")
        # SentenceTransformer 会自动检查本地缓存，如果 D:\bge-m3 已经下载好了，
        # 它会优先从缓存加载。否则它会从 Hugging Face Hub 下载。
        model = SentenceTransformer(MODEL_NAME)
        print("🎉 模型加载成功！")
        
        # 初始化 Qdrant 客户端
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # 确保集合存在 (仅在开始时创建一次)
        print(f"\n⚙️ 检查/创建 Qdrant 集合: {COLLECTION_NAME}")
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=BGE_M3_DIMENSION, distance=models.Distance.COSINE),
        )

    except Exception as e:
        print(f"❌ 初始化失败 (模型或 Qdrant 连接): {e}")
        exit()
        
    # 获取所有 XML 文件
    # 使用 os.path.join 确保路径分隔符在不同系统上正确
    all_xml_files = glob.glob(os.path.join(XML_ROOT_DIR, "*.xml"))
    total_files = len(all_xml_files)
    
    if total_files == 0:
        print(f"⚠️ 目录 {XML_ROOT_DIR} 中未找到任何 XML 文件。")
        exit()

    total_batches = math.ceil(total_files / BATCH_FILE_SIZE)
    total_articles_ingested = 0

    # 循环处理文件批次 (每 10 个文件一组)
    for i in range(0, total_files, BATCH_FILE_SIZE):
        file_batch = all_xml_files[i:i + BATCH_FILE_SIZE]
        
        print(f"\n--- 🚀 正在处理文件批次 {i // BATCH_FILE_SIZE + 1}/{total_batches} (文件数: {len(file_batch)}) ---")
        
        articles_to_ingest = []
        
        # 1. 解析和聚合所有文件中的文章
        for file_path in file_batch:
            current_file_articles = parse_pubmed_xml(file_path)
            articles_to_ingest.extend(current_file_articles)
            
        print(f"聚合完成：本文件批次共 {len(articles_to_ingest)} 篇文章准备入库。")
        
        # 2. 生成嵌入并入库
        if articles_to_ingest:
            ingest_to_qdrant(articles_to_ingest, model, client)
            total_articles_ingested += len(articles_to_ingest)
        else:
            print("警告：本批次未解析到有效文章，跳过入库。")

    print("\n--- 🏁 所有文件批次处理完成 ---")
    final_count = client.count(collection_name=COLLECTION_NAME, exact=True).count
    print(f"最终 Qdrant 集合 '{COLLECTION_NAME}' 中包含 {final_count} 个向量，共处理文章 {total_articles_ingested} 篇。")
    
    
# --- 主执行逻辑 ---
if __name__ == "__main__":
    main()