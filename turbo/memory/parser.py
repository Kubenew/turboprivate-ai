from pathlib import Path


class DocumentParser:
    def __init__(self):
        self.parsers = {
            ".pdf": self._parse_pdf,
            ".docx": self._parse_docx,
            ".html": self._parse_html,
            ".htm": self._parse_html,
            ".md": self._parse_markdown,
            ".txt": self._parse_text,
            ".csv": self._parse_csv,
            ".json": self._parse_json,
            ".xml": self._parse_xml,
            ".yaml": self._parse_yaml,
            ".yml": self._parse_yaml,
        }

    async def parse(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = file_path.suffix.lower()
        parser = self.parsers.get(ext)
        if parser is None:
            raise ValueError(f"Unsupported file type: {ext}")
        return await parser(file_path)

    async def _parse_pdf(self, path: Path) -> str:
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
        text_parts = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        text_parts.append(" | ".join(cell or "" for cell in row))
        return "\n\n".join(text_parts)

    async def _parse_docx(self, path: Path) -> str:
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    async def _parse_html(self, path: Path) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("beautifulsoup4 not installed. Run: pip install beautifulsoup4")
        with open(path, encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    async def _parse_markdown(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    async def _parse_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    async def _parse_csv(self, path: Path) -> str:
        import csv
        import io
        text = path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(text))
        lines = [" | ".join(row) for row in reader]
        return "\n".join(lines)

    async def _parse_json(self, path: Path) -> str:
        import json
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2)

    async def _parse_xml(self, path: Path) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("beautifulsoup4 not installed")
        with open(path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "xml")
        return soup.get_text(separator="\n")

    async def _parse_yaml(self, path: Path) -> str:
        import json

        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2)
