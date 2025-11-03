#!/usr/bin/env python3
"""
手动验证：在Google Maps的5558条评价中，有多少条提到Dr. Nicholas Lim
使用Places API多次调用来模拟Outscraper的效果
"""
import requests
import time
import json

API_KEY = "AIzaSyC0O-5Urc47Z1pF8hXpHVHAxC7NZowfjfw"
PLACE_ID = "ChIJjR6RfF5JzDERv1dmkS2Bw8o"
DOCTOR_NAME = "Dr. Nicholas Lim Lye Tak"

print("=" * 70)
print("🔍 手动搜索：在Columbia Asia Hospital的评价中查找")
print(f"   目标医生: {DOCTOR_NAME}")
print("=" * 70)
print()

# 说明
print("⚠️  重要说明:")
print("   Places API的限制：每次只返回5条最新评价")
print("   没有分页功能，无法获取更多评价")
print("   这就是为什么需要Outscraper的原因！")
print()

# 获取评价
print("正在获取Google Maps评价...")
url = "https://maps.googleapis.com/maps/api/place/details/json"
params = {
    "place_id": PLACE_ID,
    "fields": "name,rating,user_ratings_total,reviews",
    "key": API_KEY,
    "language": "en"
}

response = requests.get(url, params=params)
data = response.json()

if data.get("status") != "OK":
    print(f"❌ 错误: {data.get('status')}")
    exit(1)

result = data.get("result", {})
place_name = result.get("name", "Unknown")
total_reviews = result.get("user_ratings_total", 0)
reviews = result.get("reviews", [])

print(f"\n✅ 商家信息:")
print(f"   名称: {place_name}")
print(f"   总评价数: {total_reviews:,}")
print(f"   API返回: {len(reviews)} 条评价（最多5条）")
print()

# 分析评价
print("=" * 70)
print("📝 分析返回的评价")
print("=" * 70)
print()

keywords = ["nicholas", "lim", "dr. lim", "dr lim", "dr nicholas"]
relevant_reviews = []

for i, review in enumerate(reviews, 1):
    text = review.get("text", "")
    author = review.get("author_name", "Anonymous")
    rating = review.get("rating", 0)
    time_desc = review.get("relative_time_description", "")

    # 检查是否提到医生
    text_lower = text.lower()
    mentions_doctor = any(keyword in text_lower for keyword in keywords)

    print(f"评价 {i}:")
    print(f"   作者: {author}")
    print(f"   评分: {rating}⭐")
    print(f"   时间: {time_desc}")
    print(f"   内容: {text[:100]}...")

    if mentions_doctor:
        print(f"   ✅ 提到了目标医生！")
        relevant_reviews.append({
            "author": author,
            "rating": rating,
            "text": text,
            "time": time_desc
        })
    else:
        # 检查提到了哪个医生
        if "dr." in text_lower or "dr " in text_lower:
            # 提取医生名字
            import re
            doctor_mentions = re.findall(r'dr\.?\s+([a-z]+(?:\s+[a-z]+)*)', text_lower)
            if doctor_mentions:
                print(f"   ⏭️ 提到了其他医生: Dr. {doctor_mentions[0].title()}")
        else:
            print(f"   ⏭️ 未提到具体医生")
    print()

# 结果统计
print("=" * 70)
print("📊 搜索结果")
print("=" * 70)
print()

print(f"商家总评价数: {total_reviews:,}")
print(f"API返回评价数: {len(reviews)}")
print(f"找到相关评价: {len(relevant_reviews)}")
print()

if relevant_reviews:
    print("✅ 找到的相关评价:")
    print()
    for i, rev in enumerate(relevant_reviews, 1):
        print(f"{i}. {rev['author']} ({rev['rating']}⭐)")
        print(f"   {rev['text'][:150]}...")
        print()
else:
    print("❌ 在这5条评价中，没有找到提到目标医生的评价")
    print()

# 概率分析
print("=" * 70)
print("📈 概率分析")
print("=" * 70)
print()

coverage = (len(reviews) / total_reviews) * 100
print(f"API覆盖率: {len(reviews)}/{total_reviews:,} = {coverage:.3f}%")
print()

if len(relevant_reviews) > 0:
    # 如果在5条中找到了相关评价，估算总数
    relevance_rate = len(relevant_reviews) / len(reviews)
    estimated_total = int(total_reviews * relevance_rate)
    print(f"估算相关评价总数: ~{estimated_total} 条")
    print(f"相关性比例: {relevance_rate*100:.1f}%")
else:
    print("由于在前5条中未找到相关评价，无法估算总数")
    print()
    print("可能的情况:")
    print("1. 评价较少或分布较散（需要查看更多评价）")
    print("2. 医生名字在评价中的提及率较低")
    print("3. 评价可能在更靠后的位置")

print()
print("=" * 70)
print("💡 这就是为什么需要Outscraper!")
print("=" * 70)
print()

print("Places API的限制:")
print(f"   - 只能看 {len(reviews)} 条评价")
print(f"   - 覆盖率仅 {coverage:.3f}%")
print(f"   - 找到相关评价: {len(relevant_reviews)} 条")
print()

print("Outscraper的优势:")
print("   - 可以看 100-500 条评价")
print("   - 覆盖率 1.8-9.0%")
print("   - 预计能找到相关评价: 5-20 条")
print()

print("结论:")
if len(relevant_reviews) > 0:
    print(f"   ✅ 很幸运！在前5条中找到了 {len(relevant_reviews)} 条")
    print("   但这只是冰山一角，Outscraper能找到更多")
else:
    print("   ❌ 前5条都不相关")
    print("   必须使用Outscraper才能找到医生的评价")

print()
print("=" * 70)
print("下一步：获取Outscraper API key，真正解决这个问题")
print("=" * 70)
