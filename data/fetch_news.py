import feedparser
import json
import time
import re
from datetime import datetime
from collections import defaultdict

# ========== 配置区 ==========
RSS_URLS = [
    ("China", "http://www.chinadaily.com.cn/rss/china_rss.xml"),
    ("World", "http://www.chinadaily.com.cn/rss/world_rss.xml"),
    ("Business", "http://www.chinadaily.com.cn/rss/business_rss.xml"),
    ("Tech", "http://www.chinadaily.com.cn/rss/tech_rss.xml"),
    ("Sports", "http://www.chinadaily.com.cn/rss/sports_rss.xml"),
    ("Culture", "http://www.chinadaily.com.cn/rss/culture_rss.xml"),
]

# 加载词汇库
with open("vocabulary.json", "r", encoding="utf-8") as f:
    VOCAB = json.load(f)

# ========== 工具函数 ==========
def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.lower()

def extract_words(text):
    return list(set(clean_text(text).split()))

def get_vocab_matches(title, summary):
    words = extract_words(title) + extract_words(summary)
    matched = {}
    for word in words:
        if word in VOCAB:
            matched[word] = VOCAB[word]
    return matched

# ========== 主程序 ==========
all_news = []
vocab_news_map = defaultdict(list)

for category, url in RSS_URLS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = entry.get("published", "")
            try:
                pub_time = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                pub_time_str = pub_time.strftime("%Y-%m-%d %H:%M:%S")
                date_str = pub_time.strftime("%Y-%m-%d")
            except:
                pub_time_str = published
                date_str = published[:10] if len(published) >= 10 else "unknown"

            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")

            matched_vocab = get_vocab_matches(title, summary)

            news_item = {
                "title": title,
                "link": link,
                "summary": summary,
                "published": pub_time_str,
                "date": date_str,
                "category": category,
                "vocab": matched_vocab
            }
            all_news.append(news_item)

            for word in matched_vocab:
                vocab_news_map[word].append({
                    "title": title,
                    "link": link,
                    "date": date_str,
                    "category": category
                })
        print(f"抓取 {category} 成功，共 {len(feed.entries)} 条")
    except Exception as e:
        print(f"抓取 {category} 失败: {e}")
    time.sleep(1)

all_news.sort(key=lambda x: x["published"], reverse=True)

# 按日期分组
news_by_date = defaultdict(list)
for item in all_news:
    news_by_date[item["date"]].append(item)

sorted_dates = sorted(news_by_date.keys(), reverse=True)
news_grouped = {date: news_by_date[date] for date in sorted_dates}

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_grouped, f, ensure_ascii=False, indent=2)
print(f"新闻已按日期分组保存，共 {len(sorted_dates)} 天")

# 词汇分析
vocab_output = []
for word, word_info in VOCAB.items():
    if word in vocab_news_map:
        vocab_output.append({
            "word": word,
            "meaning": word_info["meaning"],
            "extension": word_info["extension"],
            "related_news": vocab_news_map[word]
        })
vocab_output.sort(key=lambda x: x["word"])

with open("data/vocab_news.json", "w", encoding="utf-8") as f:
    json.dump(vocab_output, f, ensure_ascii=False, indent=2)
print(f"词汇分析完成，共 {len(vocab_output)} 个重点词")
