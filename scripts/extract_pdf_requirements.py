from pathlib import Path

pdf = Path("d:/UMEF/E1403_Big Data Analyst/E1403_DuongBinhAn/Final Assignment_Big Data Analytics C2.pdf")
print("exists", pdf.exists())

if not pdf.exists():
    raise SystemExit(0)

text = None

try:
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    print("method", "pypdf", "pages", len(reader.pages))
except Exception as exc:
    print("pypdf_error", type(exc).__name__, str(exc))

if not text:
    try:
        import fitz
        doc = fitz.open(str(pdf))
        text = "\n".join(page.get_text() for page in doc)
        print("method", "fitz", "pages", doc.page_count)
    except Exception as exc:
        print("fitz_error", type(exc).__name__, str(exc))

if text:
    print(text[:15000])
