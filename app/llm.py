import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"


def proofread_text(text: str) -> str:
    prompt = f"""
너는 문서 교열 보조 AI다.

아래 OCR 텍스트에서 명백한 OCR 오류나
문맥상 이상한 부분만 찾아라.

중요한 규칙:
1. OCR 텍스트 전체를 다시 작성하지 마라.
2. 문제가 없는 문장은 출력하지 마라.
3. 문제가 의심되는 부분만 최대 10개까지 출력하라.
4. 각 문제는 짧게 설명하라.
5. 확실하지 않은 내용은 억지로 수정하지 마라.
6. 분석 결과 문제가 없다면 "특이사항 없음"이라고만 답하라.

반드시 다음 형식을 사용하라.

[문제 1]
원문: 문제가 있는 짧은 부분
문제: 왜 이상한지
수정안: 어떻게 수정할지

[문제 2]
원문: 문제가 있는 짧은 부분
문제: 왜 이상한지
수정안: 어떻게 수정할지

...

[OCR TEXT]
{text}
"""

    print("Ollama 요청 시작")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 512,
            },
        },
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    result = data.get("response", "").strip()

    print("Ollama 응답 완료")
    print("생성 토큰 수:", data.get("eval_count"))
    print("응답 길이:", len(result))

    if not result:
        print("Ollama 응답이 비어 있습니다.")
        print("Ollama 전체 응답:", data)

        return "AI 교열 결과가 생성되지 않았습니다."

    return result