from Bio import Entrez
import xml.etree.ElementTree as ET
import os

Entrez.email = os.getenv("PUBMED_EMAIL")
Entrez.api_key = os.getenv("PUBMED_API_KEY")


def search_pubmed(query, retmax=10):
    print('email:', os.getenv("PUBMED_EMAIL"))
    
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax, sort="relevance")
    record = Entrez.read(handle)
    ids = record["IdList"]
    fetch = Entrez.efetch(db="pubmed", id=ids, rettype="xml", retmode="text")
    articles = parse_pubmed_xml(fetch)
    return articles

def parse_pubmed_xml(handle):
    root = ET.fromstring(handle.read())
    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle", "")
        abstract = " ".join(a.text or "" for a in article.findall(".//AbstractText"))
        authors = ", ".join([
            (a.findtext("LastName", "") + " " + a.findtext("ForeName", ""))
            for a in article.findall(".//AuthorList/Author")
        ])
        results.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors
        })
    return results

if __name__ == '__main__':
    res = search_pubmed("What are the latest treatments for type 2 diabetes?")
    print(res)
