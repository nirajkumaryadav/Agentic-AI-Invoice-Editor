# Agentic AI Invoice Editor

An end-to-end Agentic AI system that processes multilingual invoices from PDFs and images.

The platform extracts invoice fields, translates non-English content, validates records against enterprise data, and produces audit-ready reports.

## Technology Stack

- Python
- LangGraph
- Retrieval Augmented Generation (RAG)
- Tesseract OCR
- Streamlit
- LangFuse

## Core Responsibilities and Contributions

- Designed and developed a full invoice auditing workflow with multiple specialized agents.
- Built multilingual invoice processing with OCR plus translation for cross-language document handling.
- Implemented validation logic against mock ERP purchase order records to reduce processing errors.
- Developed automated audit report generation for business and compliance review.
- Created a RAG-based pipeline with vector search to improve retrieval quality and context grounding.
- Integrated human-in-the-loop feedback to improve reliability, decision quality, and continuous accuracy.

## End-to-End Workflow

1. Invoice intake from the incoming folder.
2. OCR and data extraction from invoice PDFs/images.
3. Translation of extracted fields when source language is not English.
4. Validation of invoice data against enterprise PO/ERP records.
5. Report generation with validation outcomes and discrepancy details.
6. Feedback loop for reviewer corrections and quality improvements.

## Project Structure

- main.py: Entry point to run the invoice auditor workflow.
- agents/: Agent modules for extraction, translation, validation, monitoring, and reporting.
- agents/rag_agents/: RAG indexing, retrieval, generation, reflection, and graph pipeline components.
- workflow/: Workflow orchestration for invoice processing.
- langgraph_workflows/: LangGraph workflow configuration.
- configs/: Personas and rule configurations.
- data/: Input invoices and ERP mock datasets.
- ui/: Streamlit application for interactive usage.
- mock_erp/: Mock ERP service/app for validation support.

## Getting Started

### 1. Prerequisites

- Python 3.10+
- Tesseract OCR installed and available in PATH

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Workflow

```bash
python main.py
```

### 4. Run the Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

## Sample Data

- Input invoices: data/incoming/
- Mock ERP purchase records: data/erp_mock_data/PO_Records.json

## Use Cases

- Automated accounts payable pre-audit
- Multilingual invoice normalization and validation
- Exception detection and audit trail generation
- Human-reviewed AI invoice processing pipeline

## Future Enhancements

- Direct ERP integration beyond mock data
- Additional language coverage and OCR tuning
- Confidence scoring dashboards in Streamlit
- Expanded LangFuse observability and tracing

## License

For educational and demonstration purposes. Add a formal license if needed for production or open-source distribution.
