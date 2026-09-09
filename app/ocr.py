from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(pdf_path: str) -> str:
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF 파일을 찾을 수 없습니다: {pdf_path}"
        )

    print(f"OCR 시작: {pdf_path}")

    pages = convert_from_path(
        pdf_path,
        dpi=200,
    )

    results = []

    for page_number, page in enumerate(pages, start=1):
        print(
            f"OCR 처리 중: "
            f"{page_number}/{len(pages)}"
        )

        text = pytesseract.image_to_string(
            page,
            lang="kor+eng",
        )

        results.append(
            f"===== PAGE {page_number} =====\n"
            f"{text.strip()}"
        )

    return "\n\n".join(results)