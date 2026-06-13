import feedparser
import json
import os

# 目标 RSS 源（以 China Daily 为例）
RSS_URL = "https://www.chinadaily.com.cn/rss/world_rss.xml"
OUTPUT_FILE = "data/news.json"
VOCAB_FILE = "data/vocab_news.json"

def fetch_news():
    print(f"正在抓取 {RSS_URL} 的新闻...")
    feed = feedparser.parse(RSS_URL)
    
    news_list = []
    vocab_list = []
    
    for entry in feed.entries:
        news_item = {
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.published
        }
        news_list.append(news_item)
        
        # 简单提取标题中的单词作为词汇（可自行扩展）
        title_words = entry.title.split()
        vocab_list.extend(title_words)
    
    # 确保 data 文件夹存在
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # 保存新闻数据
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    print(f"新闻数据已保存到 {OUTPUT_FILE}")
    
    # 保存词汇数据（去重）
    unique_vocab = list(set(vocab_list))
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_vocab, f, ensure_ascii=False, indent=2)
    print(f"词汇数据已保存到 {VOCAB_FILE}")

if __name__ == "__main__":
    fetch_news()
