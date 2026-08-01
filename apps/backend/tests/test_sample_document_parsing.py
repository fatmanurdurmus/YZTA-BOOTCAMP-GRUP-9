import os

from carbonpilot.ingestion.documents import extract_document_text


def test_sample_docs_directory_exists():
    """Ensure the sample documents directory is present."""
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    samples_dir = os.path.join(base_dir, "docs", "samples")
    assert os.path.exists(samples_dir), "docs/samples directory must exist"


def test_parse_docx_sample_if_present():
    """Test extracting text from DOCX sample if file is provided."""
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    docx_path = os.path.join(base_dir, "docs", "samples", "sample_invoice.docx")

    if os.path.exists(docx_path):
        with open(docx_path, "rb") as f:
            content = f.read()

        # extract_document_text takes (content, content_type, filename) and
        # returns a list of (page_number, text) tuples, not a plain string.
        extracted = extract_document_text(
            content,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "sample_invoice.docx",
        )
        assert len(extracted) > 0

        combined_text = "\n".join(text for _, text in extracted)
        assert "kWh" in combined_text or "Fatura" in combined_text