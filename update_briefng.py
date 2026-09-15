import os
import re
import json
from google import genai
from google.genai import types

# 1. 제미나이 클라이언트 초기화 (GEMINI_API_KEY 환경변수 필요)
client = genai.Client()

with open("prompt.txt", "r", encoding="utf-8") as f:
    system_instruction = f.read()

# 2. 웹 검색 도구를 활성화하여 요청
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="오늘자 한국 투자자 관점의 증시 브리핑을 작성해서 data.json 규격에 맞게 출력해줘.",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[{"google_search": {}}],
        temperature=0.2,
    ),
)

text = response.text

# 3. JSON 코드 블록 추출 및 검증
match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
json_str = match.group(1) if match else text.strip()

data = json.loads(json_str)

# 행/열 구조 검증
assert len(data["market"]["rows"]) > 0
for row in data["market"]["rows"]:
    assert len(row["c"]) == len(data["market"]["head"])

# 4. 파일 덮어쓰기
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data.json 갱신 완료")
