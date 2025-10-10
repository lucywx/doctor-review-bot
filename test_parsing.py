#!/usr/bin/env python3
"""Test JSON parsing logic"""

import json

# This is what OpenAI actually returned
raw_response = """[{"source":"LookP","snippet":"Dr Tang is the best gynae I ever met. She is very responsible and dedicated to her job. She have the passion in her job instead of buisness minded like other gynae I met. Is a blessing to have an excellent dr!","rating":null,"author_name":"SK","review_date":"2022-12-01","url":"LookP"},{"source":"LookP","snippet":"Dr Tang is good, smart and very experienced gynae. I am grateful to have Dr. Tang performed a myomectomy on me, she is caring, skillful and positive along my operation and recovery. Thanks Dr. Tang! Even though there always a long wait for the check up but is worth.","rating":null,"author_name":"LST","review_date":"2021-06-16","url":"LookP"},{"source":"LookP via Gynaecologist Reviews Malaysia","snippet":"You won't regret to wait as she will provide you her professionalism. I went others to check up my postpartum wound... healing faster.","rating":null,"author_name":null,"review_date":"2019-09","url":"LookP"},{"source":"LookP via Gynaecologist Reviews Malaysia","snippet":"Grateful to have found Dr Tang through a close friend. Dr Tang performed a total hysterectomy on me and the surgery was very successful and I did not suffer much. Thanks to her skill and experience. I would recommend all my girlfriends to go to Dr Tang as she's smart , experienced and quick in making decision . Her friendly and jovial character puts her patients at ease.","rating":null,"author_name":null,"review_date":"2019-03","url":"LookP"},{"source":"Lowyat.net","snippet":"Waiting time is long but she is quite friendly and caring. Ps: first consultation ( new patient) is more expensive.","rating":null,"author_name":"jasmine0085","review_date":"2014-03-25","url":"Lowyat.net"}]"""

print("Testing JSON parsing...")
print(f"Raw response length: {len(raw_response)}")
print(f"Starts with [: {raw_response.strip().startswith('[')}")
print(f"Ends with ]: {raw_response.strip().endswith(']')}")

# Try to parse
try:
    data = json.loads(raw_response)
    print(f"\n✅ JSON parsing successful!")
    print(f"Number of reviews: {len(data)}")

    for i, review in enumerate(data, 1):
        print(f"\n{i}. {review['source']}")
        print(f"   Author: {review.get('author_name', 'N/A')}")
        print(f"   Date: {review.get('review_date', 'N/A')}")
        print(f"   Snippet: {review['snippet'][:60]}...")

except json.JSONDecodeError as e:
    print(f"\n❌ JSON parsing failed: {e}")
