import os
import tempfile
from pathlib import Path

from celery import Celery

from app.jobs import update_job
from app.ocr import extract_text_from_pdf
from app.llm import proofread_text


celery_app = Celery(
    "ongyeol",
    broker="redis://localhost:6379/0",
)


@celery_app.task
def process_document(
    job_id: str,
    file_data: bytes,
    filename: str,
):
    temp_path = None

    try:
        print(f"[{job_id}] 작업 시작")

        update_job(
            job_id,
            status="running",
            progress=5,
            stage="preparing",
        )

        # --------------------------------------------------
        # 1. 업로드된 PDF를 임시 파일로 저장
        # --------------------------------------------------

        suffix = Path(filename).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        print(
            f"[{job_id}] "
            f"임시 파일 저장: {temp_path}"
        )

        # --------------------------------------------------
        # 2. OCR
        # --------------------------------------------------

        update_job(
            job_id,
            progress=20,
            stage="ocr",
        )

        print(f"[{job_id}] OCR 시작")

        ocr_text = extract_text_from_pdf(
            temp_path
        )

        print(f"[{job_id}] OCR 완료")

        update_job(
            job_id,
            progress=50,
            stage="ocr_completed",
        )

        # --------------------------------------------------
        # 3. Ollama AI 교열
        # --------------------------------------------------

        update_job(
            job_id,
            progress=60,
            stage="ai_proofreading",
        )

        print(f"[{job_id}] AI 교열 시작")

        proofread_result = proofread_text(
            ocr_text
        )

        print(f"[{job_id}] AI 교열 완료")

        # --------------------------------------------------
        # 4. 결과 저장
        # --------------------------------------------------

        update_job(
            job_id,
            progress=90,
            stage="saving",
        )

        result = {
            "filename": filename,
            "ocr_text": ocr_text,
            "proofread_result": proofread_result,
        }

        update_job(
            job_id,
            status="succeeded",
            progress=100,
            stage="completed",
            result=result,
        )

        print(f"[{job_id}] 작업 완료")

        return {
            "job_id": job_id,
            "status": "succeeded",
        }

    except Exception as e:
        print(
            f"[{job_id}] 오류 발생: {e}"
        )

        update_job(
            job_id,
            status="failed",
            stage="error",
            error=str(e),
        )

        raise

    finally:
        # --------------------------------------------------
        # 5. 임시 파일 삭제
        # --------------------------------------------------

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

            print(
                f"[{job_id}] "
                f"임시 파일 삭제"
            )

@celery_app.task
def process_document(job_id, file_data, filename):
    temp_path = None

    try:
        print(f"[{job_id}] 작업 시작")

        update_job(
            job_id,
            status="running",
            progress=5,
            stage="preparing"
        )

        # PDF 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(file_data)
            temp_path = f.name

        print(f"[{job_id}] PDF 저장 완료")

        # OCR
        update_job(
            job_id,
            progress=20,
            stage="ocr"
        )

        print(f"[{job_id}] OCR 시작")

        ocr_text = extract_text_from_pdf(temp_path)

        print(f"[{job_id}] OCR 완료")
        print(f"[{job_id}] OCR 글자 수: {len(ocr_text)}")

        # AI 교열
        update_job(
            job_id,
            progress=60,
            stage="proofreading"
        )

        print(f"[{job_id}] AI 교열 시작")

        proofread_result = proofread_text(ocr_text)

        print(f"[{job_id}] AI 교열 완료")
        print(f"[{job_id}] AI 결과 글자 수: {len(proofread_result)}")

        # 결과 저장
        result = {
            "filename": filename,
            "ocr_text": ocr_text,
            "proofread_result": proofread_result,
        }

        update_job(
            job_id,
            status="succeeded",
            progress=100,
            stage="completed",
            result=result
        )

        print(f"[{job_id}] 작업 완료")

        return result

    except Exception as e:
        print(f"[{job_id}] 작업 실패: {e}")

        update_job(
            job_id,
            status="failed",
            stage="failed",
            error=str(e)
        )

        raise

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[{job_id}] 임시 파일 삭제")