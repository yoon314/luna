# OnGyeol

PDF 문서를 업로드하면 OCR과 AI를 이용해 문서 내용을 분석하는 **OnGyeol 백엔드 프로토타입**입니다.

현재는 다음과 같은 테스트용 파이프라인으로 구성되어 있습니다.

```text
PDF
 ↓
FastAPI
 ↓
Redis
 ↓
Celery
 ↓
Tesseract OCR
 ↓
Ollama (Qwen3:4b)
 ↓
AI 교열 결과
```

> 현재 Tesseract와 Ollama는 테스트용으로 사용하고 있으며, 향후 문서 구조를 보존할 수 있는 OCR/문서 파싱 방식으로 개선할 예정입니다.

---

## Requirements

* macOS
* Python 3.10+
* Redis
* Tesseract
* Poppler
* Ollama

Python 패키지는 `requirements.txt`를 사용합니다.

---

## Installation

### 1. Repository clone

```bash
git clone <YOUR_REPOSITORY_URL>
cd ongyeol
```

### 2. Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python packages

```bash
pip install -r requirements.txt
```

### 4. Install system dependencies

```bash
brew install redis
brew install tesseract
brew install tesseract-lang
brew install poppler
```

### 5. Install Ollama model

Ollama를 설치한 후 Qwen3 4B 모델을 받습니다.

```bash
ollama pull qwen3:4b
```

---

## Run

프로젝트를 실행하려면 **터미널을 3개** 사용하는 것을 권장합니다.

### Terminal 1 — Redis

```bash
redis-server
```

Redis가 이미 실행 중이라면 생략할 수 있습니다.

확인:

```bash
redis-cli ping
```

정상적으로 실행 중이면:

```text
PONG
```

---

### Terminal 2 — Ollama

```bash
ollama serve
```

이미 Ollama가 실행 중이라면 생략할 수 있습니다.

---

### Terminal 3 — Celery Worker

```bash
cd ~/Desktop/ongyeol
source .venv/bin/activate

celery -A app.tasks.celery_app worker --loglevel=info
```

Celery가 정상적으로 실행되면 Worker가 준비되었다는 메시지가 표시됩니다.

---

### FastAPI 실행

별도의 터미널에서:

```bash
cd ~/Desktop/ongyeol
source .venv/bin/activate

uvicorn app.main:app --reload
```

서버가 실행되면:

```text
http://127.0.0.1:8000
```

에서 접근할 수 있습니다.

---

## API Docs

FastAPI는 자동으로 Swagger UI를 제공합니다.

브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:8000/docs
```

여기에서 API를 직접 실행하고 결과를 확인할 수 있습니다.

### `GET /`

서버가 정상적으로 실행 중인지 확인합니다.

응답:

```json
{
  "service": "OnGyeol Backend",
  "status": "running"
}
```

---

### `POST /documents`

PDF 파일을 업로드하고 작업을 시작합니다.

Swagger에서:

1. `POST /documents` 선택
2. **Try it out** 클릭
3. PDF 파일 선택
4. **Execute** 클릭

응답으로 `job_id`가 반환됩니다.

```json
{
  "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "queued"
}
```

---

### `GET /jobs/{job_id}`

`POST /documents`에서 받은 `job_id`를 사용하여 작업 상태를 확인합니다.

예:

```text
GET /jobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

처리 중에는 다음과 같이 상태가 변경됩니다.

```json
{
  "status": "running",
  "progress": 50,
  "stage": "ocr_completed"
}
```

작업이 완료되면:

```json
{
  "status": "succeeded",
  "progress": 100,
  "stage": "completed",
  "result": {
    "filename": "example.pdf",
    "ocr_text": "...",
    "proofread_result": "..."
  }
}
```

---

## Current Pipeline

현재 백엔드는 다음 순서로 동작합니다.

```text
1. PDF 업로드
      ↓
2. FastAPI가 Job 생성
      ↓
3. Redis에 Job 상태 저장
      ↓
4. Celery에 작업 전달
      ↓
5. Tesseract로 OCR
      ↓
6. Ollama(Qwen3:4b)로 AI 분석
      ↓
7. Redis에 결과 저장
      ↓
8. API에서 결과 확인
```

---

## Project Structure

```text
ongyeol/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── tasks.py
│   ├── jobs.py
│   ├── ocr.py
│   └── llm.py
│
├── requirements.txt
└── README.md
```

### 주요 파일

| 파일                 | 역할              |
| ------------------ | --------------- |
| `main.py`          | FastAPI API     |
| `tasks.py`         | Celery 작업       |
| `jobs.py`          | Redis Job 상태 관리 |
| `ocr.py`           | Tesseract OCR   |
| `llm.py`           | Ollama AI 분석    |
| `requirements.txt` | Python 의존성      |

---

## Development Status

현재는 **백엔드 파이프라인 검증 단계**입니다.

* [x] FastAPI
* [x] Redis
* [x] Celery
* [x] PDF 업로드
* [x] Tesseract OCR
* [x] Ollama 연동
* [ ] 문서 구조 보존 OCR
* [ ] OCR 정확도 개선
* [ ] AI 교열 로직 개선
* [ ] PostgreSQL
* [ ] S3
* [ ] 실제 점자 제작/교열 기능

향후 OCR을 단순 문자 인식 방식에서 **문서의 위치, 문단, 표, 읽기 순서 등의 구조를 보존하는 방식**으로 개선할 예정입니다.
