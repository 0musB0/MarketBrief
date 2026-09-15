import os
import re
import json
from google import genai
from google.genai import types

# 1. 클라이언트 초기화
client = genai.Client()

# 2. 프롬프트 로드
with open("prompt.txt", "r", encoding="utf-8") as f:
    system_instruction = f.read()

# 3. 최신 모델(gemini-3.6-flash) 및 chats 세션으로 웹 검색 호출
chat = client.chats.create(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[{"google_search": {}}],
        temperature=0.2,
    ),
)

response = chat.send_message("오늘자 한국 투자자 관점의 증시 브리핑을 작성해서 data.json 규격에 맞게 출력해줘.")
text = response.text

# 4. JSON 파싱 및 유효성 검사
match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
json_str = match.group(1) if match else text.strip()

data = json.loads(json_str)

assert len(data["market"]["rows"]) > 0
for row in data["market"]["rows"]:
    assert len(row["c"]) == len(data["market"]["head"])

# 5. 파일 저장
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("data.json 갱신 완료")
