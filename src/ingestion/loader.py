"""Document loader module supporting multiple file formats."""

from pathlib import Path
from typing import Any
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """Loads text documents from local filesystem across multiple formats."""

    def __init__(self, supported_extensions: list[str] | None = None) -> None:
        """Initialize DocumentLoader with allowed file extensions.

        Args:
            supported_extensions: List of supported file extensions (e.g. ['.txt', '.pdf']).
        """
        self.supported_extensions = supported_extensions or [
            ".txt",
            ".pdf",
            ".csv",
            ".md",
            ".docx",
        ]

    def load_file(self, file_path: str) -> dict[str, Any]:
        """Load single file content and metadata.

        Args:
            file_path: Path to the target document.

        Returns:
            Dictionary containing 'content' and 'metadata'.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is unsupported.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {ext}")

        content = ""
        if ext in [".txt", ".md", ".csv"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext == ".pdf":
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(path))
                content = "\n".join([page.extract_text() or "" for page in reader.pages])
            except ImportError:
                logger.warning("pypdf not installed. Falling back to plain text read.")
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        logger.info(f"Loaded document: {path.name} ({len(content)} characters)")
        return {
            "content": content,
            "metadata": {
                "source": str(path.resolve()),
                "filename": path.name,
                "extension": ext,
                "size_bytes": path.stat().st_size,
            },
        }

    def load_directory(self, dir_path: str) -> list[dict[str, Any]]:
        """Load all supported documents in a directory.

        Args:
            dir_path: Path to the target directory.

        Returns:
            List of document dictionaries with content and metadata.
        """
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Directory not found: {dir_path}")
            return []

        documents = []
        for file in directory.rglob("*"):
            if file.is_file() and file.suffix.lower() in self.supported_extensions:
                try:
                    documents.append(self.load_file(str(file)))
                except Exception as exc:
                    logger.error(f"Failed to load {file}: {exc}")

        logger.info(f"Successfully loaded {len(documents)} documents from {dir_path}")
        return documents
