"""Document tree representation with typed blocks and hierarchical links."""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class BlockType(str, Enum):
    """Categorical type for document structural elements."""

    ROOT = "root"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    CODE = "code"
    EQUATION = "equation"
    LIST = "list"
    HEADER_FOOTER = "header_footer"


class DocumentNode(BaseModel):
    """Hierarchical node representing an element in a document AST."""

    id: str
    node_type: BlockType
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_id: str | None = None
    children: list["DocumentNode"] = Field(default_factory=list)
    level: int = 0
    section_path: list[str] = Field(default_factory=list)
    preceding_prose_id: str | None = None
    table_metadata: dict[str, Any] | None = None


class DocumentTree:
    """Manages the hierarchical tree of document nodes and semantic relationships."""

    def __init__(self, doc_id: str = "doc_root", title: str = "Document") -> None:
        """Initialize an empty DocumentTree with a root node.

        Args:
            doc_id: Unique identifier for the document.
            title: Human-readable document title.
        """
        self.doc_id = doc_id
        self.root = DocumentNode(
            id=doc_id,
            node_type=BlockType.ROOT,
            content=title,
            metadata={"title": title},
            level=0,
            section_path=[title],
        )
        self._nodes: dict[str, DocumentNode] = {doc_id: self.root}

    def add_node(self, node: DocumentNode, parent_id: str | None = None) -> None:
        """Add a child node to the tree under a specified parent.

        Args:
            node: DocumentNode instance to add.
            parent_id: Target parent node ID. Defaults to tree root.
        """
        target_parent_id = parent_id or self.root.id
        parent_node = self._nodes.get(target_parent_id, self.root)

        node.parent_id = parent_node.id
        if not node.section_path:
            node.section_path = list(parent_node.section_path)
            if node.node_type == BlockType.SECTION:
                node.section_path.append(node.content.strip())

        parent_node.children.append(node)
        self._nodes[node.id] = node

    def get_node(self, node_id: str) -> DocumentNode | None:
        """Retrieve a node by its identifier.

        Args:
            node_id: Target node ID.

        Returns:
            DocumentNode if found, otherwise None.
        """
        return self._nodes.get(node_id)

    def link_preceding_prose(self) -> None:
        """Link every table node to its immediately preceding paragraph block."""
        all_nodes = self.walk()
        last_paragraph_id: str | None = None
        current_section_id: str | None = None

        for node in all_nodes:
            if node.node_type == BlockType.SECTION:
                current_section_id = node.id
                last_paragraph_id = None
            elif node.node_type == BlockType.PARAGRAPH:
                last_paragraph_id = node.id
            elif node.node_type == BlockType.TABLE:
                if last_paragraph_id:
                    node.preceding_prose_id = last_paragraph_id
                    logger.debug("Linked table %s to preceding prose %s", node.id, last_paragraph_id)

    def walk(self, start_node: DocumentNode | None = None) -> list[DocumentNode]:
        """Perform a pre-order depth-first traversal of the tree.

        Args:
            start_node: Starting node for traversal. Defaults to root.

        Returns:
            Flattened list of DocumentNodes in reading/hierarchy order.
        """
        start = start_node or self.root
        result: list[DocumentNode] = [start]

        def _traverse(node: DocumentNode) -> None:
            for child in node.children:
                result.append(child)
                _traverse(child)

        _traverse(start)
        return result

    def get_nodes_by_type(self, node_type: BlockType) -> list[DocumentNode]:
        """Filter and return all nodes of a specific block type.

        Args:
            node_type: BlockType enum value to filter by.

        Returns:
            List of matching DocumentNode instances.
        """
        return [node for node in self._nodes.values() if node.node_type == node_type]

    @classmethod
    def from_blocks(cls, blocks: list[dict[str, Any]], doc_id: str = "doc_root", title: str = "Document") -> "DocumentTree":
        """Construct a hierarchical DocumentTree from a linear sequence of typed blocks.

        Args:
            blocks: List of raw block dictionaries with keys 'id', 'type', 'content', 'level', etc.
            doc_id: Unique identifier for the document.
            title: Document title.

        Returns:
            Assembled and linked DocumentTree instance.
        """
        tree = cls(doc_id=doc_id, title=title)
        section_stack: list[DocumentNode] = [tree.root]

        for idx, block in enumerate(blocks):
            block_id = block.get("id", f"{doc_id}_block_{idx}")
            block_type = BlockType(block.get("type", BlockType.PARAGRAPH.value))
            content = block.get("content", "")
            level = int(block.get("level", 0))
            metadata = block.get("metadata", {})
            table_metadata = block.get("table_metadata")

            node = DocumentNode(
                id=block_id,
                node_type=block_type,
                content=content,
                level=level,
                metadata=metadata,
                table_metadata=table_metadata,
            )

            if block_type == BlockType.SECTION:
                # Pop sections with level >= current section level
                while len(section_stack) > 1 and section_stack[-1].level >= level:
                    section_stack.pop()

                parent_section = section_stack[-1]
                tree.add_node(node, parent_id=parent_section.id)
                section_stack.append(node)
            else:
                # Attach to current active section
                parent_section = section_stack[-1]
                tree.add_node(node, parent_id=parent_section.id)

        tree.link_preceding_prose()
        return tree
