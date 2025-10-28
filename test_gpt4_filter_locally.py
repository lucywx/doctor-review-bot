#!/usr/bin/env python3
"""
本地测试 GPT-4 过滤 Google Maps 评价的效果
"""
import os
import sys

# 模拟从 Places API 获取的5条评价
reviews = [
    {
        "author": "Reviewer 1",
        "rating": 5,
        "text": "Successful Hemorrhoid Surgery by Dr. Siva at Columbia Asia Hospital\n\nI would like to express my deepest gratitude to Dr. Siva and the amazing team at Columbia Asia Hospital for the outstanding care I received during my hemorrhoid surgery."
    },
    {
        "author": "Reviewer 2",
        "rating": 5,
        "text": "Just got discharged!\n\nI'd like to sincerely thank the nurses and staff at Columbia Asia Hospital for the excellent care I received during my stay. Your kindness, attentiveness, and professionalism made my experience much more comfortable."
    },
    {
        "author": "Reviewer 3",
        "rating": 5,
        "text": "Special thanks to Dr. Hyder Aazad\n\nMy wife was admitted to the emergency department in the middle of the night due to food poisoning, where we were attended to by Dr. Hyder and the ER team. From the very first moment, Dr. Hyder's calm demeanor and professionalism were evident."
    },
    {
        "author": "Reviewer 4",
        "rating": 5,
        "text": "Columbia Asia Hospital in Petaling Jaya (PJ) is one of the private medical facilities that left the deepest impression on me during my time receiving treatment there. Conveniently located right in the heart of PJ, the hospital offers easy access for patients."
    },
    {
        "author": "Reviewer 5",
        "rating": 5,
        "text": "I'm delighted with the wonderful service.The team was efficient,friendly and professional.From check-in to discharge, the process was fast and efficient. Overall my experience at Colombia Hosp PJ was excellent."
    }
]

doctor_name = "Dr. Nicholas Lim Lye Tak"
place_name = "Columbia Asia Hospital Petaling Jaya"

print("=" * 60)
print("本地测试: GPT-4 过滤 Google Maps 评价")
print("=" * 60)
print(f"\n医生: {doctor_name}")
print(f"地点: {place_name}")
print(f"原始评价数: {len(reviews)}")
print("\n" + "=" * 60)

# 显示评价
for i, review in enumerate(reviews, 1):
    print(f"\nReview {i}:")
    print(f"  Author: {review['author']}")
    print(f"  Rating: {review['rating']}⭐")
    print(f"  Text: {review['text'][:150]}...")

    # 简单检查是否提到医生名字
    text_lower = review['text'].lower()
    mentions_nicholas = 'nicholas' in text_lower
    mentions_lim = 'lim' in text_lower

    print(f"  Mentions 'nicholas': {mentions_nicholas}")
    print(f"  Mentions 'lim': {mentions_lim}")

    if mentions_nicholas and mentions_lim:
        print(f"  ✅ 可能与 {doctor_name} 相关")
    else:
        print(f"  ❌ 不相关（提到其他医生或只是医院评价）")

print("\n" + "=" * 60)
print("预期 GPT-4 过滤结果:")
print("=" * 60)
print("\n基于上述分析，GPT-4 应该:")
print("  ❌ 过滤掉 Review 1 (关于 Dr. Siva)")
print("  ❌ 过滤掉 Review 2 (关于护士和医院)")
print("  ❌ 过滤掉 Review 3 (关于 Dr. Hyder Aazad)")
print("  ❌ 过滤掉 Review 4 (只是医院评价)")
print("  ❌ 过滤掉 Review 5 (只是医院服务评价)")
print("\n  结果: 0 条评价关于 Dr. Nicholas Lim Lye Tak")
print("\n这是正确的行为！因为这5条评价确实都不是关于他的。")

print("\n" + "=" * 60)
print("现在测试实际的 GPT-4 过滤")
print("=" * 60)

# 检查是否有 OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("\n⚠️  OPENAI_API_KEY 未设置，无法测试实际的 GPT-4 过滤")
    print("请设置环境变量: export OPENAI_API_KEY='your_key'")
    sys.exit(0)

print("\n正在调用 GPT-4 分析评价...")

import asyncio
from openai import AsyncOpenAI

async def test_gpt4_filtering():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    reviews_text = "\n\n".join([
        f"Review {i+1}:\n{review['text']}"
        for i, review in enumerate(reviews)
    ])

    prompt = f"""You are analyzing Google Maps reviews for {place_name}.

Your task: Identify which reviews are specifically about **{doctor_name}** (the doctor).

Reviews to analyze:
{reviews_text}

Instructions:
1. Read each review carefully
2. A review is about {doctor_name} if it:
   - Mentions the doctor's name (or clear variations like "Dr. Lim" or "Nicholas")
   - Describes their medical care, diagnosis, treatment, or bedside manner
   - Is clearly a patient's experience with this specific doctor

3. A review is NOT about {doctor_name} if it:
   - Only mentions other doctors' names
   - Is about hospital facilities, nurses, admin staff, or general hospital experience
   - Doesn't mention any specific doctor

Output format:
Return ONLY a JSON array of review numbers that ARE about {doctor_name}.
Example: [1, 3] or [] if none match.

Your response:"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )

        result = response.choices[0].message.content.strip()
        print(f"\n✅ GPT-4 响应: {result}")

        # 解析结果
        import json
        import re

        json_match = re.search(r'\[[\d\s,]*\]', result)
        if json_match:
            relevant_indices = json.loads(json_match.group())

            print(f"\n📊 GPT-4 过滤结果:")
            print(f"  原始评价: {len(reviews)} 条")
            print(f"  相关评价: {len(relevant_indices)} 条")

            if relevant_indices:
                print(f"\n  相关评价编号: {relevant_indices}")
                for idx in relevant_indices:
                    if 1 <= idx <= len(reviews):
                        print(f"\n  Review {idx}:")
                        print(f"    {reviews[idx-1]['text'][:100]}...")
            else:
                print(f"\n  ✅ 正确！没有评价是关于 {doctor_name} 的")
        else:
            print(f"\n❌ 无法解析 GPT-4 响应")

    except Exception as e:
        print(f"\n❌ 错误: {e}")

# 运行测试
asyncio.run(test_gpt4_filtering())

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
