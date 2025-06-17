import asyncio
import logging
import hashlib
from typing import List, Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.schemas import PageContent, ProcessedPageChunk

logger = logging.getLogger(__name__)

# Placeholder configuration, actual Vectorize MCP server details would be needed
VECTORIZE_API_ENDPOINT = "YOUR_VECTORIZE_API_ENDPOINT_HERE" # Load from config eventually
VECTORIZE_API_KEY = "YOUR_VECTORIZE_API_KEY_HERE" # Load from config eventually

class VectorizeToolInput(BaseModel):
    page_content_list: List[PageContent] = Field(description="A list of PageContent objects to process and chunk.")
    chunk_size: int = Field(default=1000, description="Target size for text chunks.")
    chunk_overlap: int = Field(default=100, description="Overlap between chunks.")

class ProcessContentWithVectorizeTool(StructuredTool):
    name: str = "process_content_with_vectorize"
    description: str = "Chunks raw page content using a text splitter."
    args_schema: Type[BaseModel] = VectorizeToolInput
    config: Dict[str, Any]
    text_splitter: Any # Declare the field for Pydantic

    def __init__(self, config: Dict[str, Any]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 1000),
            chunk_overlap=config.get("chunk_overlap", 100),
            length_function=len,
        )
        super().__init__(config=config, text_splitter=text_splitter)

    async def _arun(self, page_content_list: List[PageContent], chunk_size: int = 1000, chunk_overlap: int = 100) -> Dict[str, Any]:
        logger.info(f"Received {len(page_content_list)} PageContent objects for chunking.")
        all_processed_chunks: List[ProcessedPageChunk] = []

        for page in page_content_list:
            if not page.content or not page.content.strip():
                logger.warning(f"Skipping page {page.url} due to empty content.")
                continue
            
            chunks = self.text_splitter.split_text(page.content)
            
            for i, chunk_text in enumerate(chunks):
                url_hash = hashlib.md5(page.url.encode()).hexdigest()
                chunk_id = f"{url_hash}_{i}"
                
                processed_chunk = ProcessedPageChunk(
                    chunk_id=chunk_id,
                    url=page.url,
                    title=page.title,
                    text_chunk=chunk_text,
                    chunk_order=i,
                    metadata={"original_content_length": page.content_length}
                )
                all_processed_chunks.append(processed_chunk)
            logger.info(f"Processed {len(chunks)} chunks from {page.url}")

        logger.info(f"Total processed chunks: {len(all_processed_chunks)}")
        
        return {
            "total_chunks": len(all_processed_chunks),
            "chunks": all_processed_chunks,
            "pages_processed": len(page_content_list),
            "processing_method": "RecursiveCharacterTextSplitter"
        }

    def _run(self, page_content_list: List[PageContent], chunk_size: int = 1000, chunk_overlap: int = 100) -> Dict[str, Any]:
        # This tool is not IO-bound, so a sync wrapper is less of an issue.
        # However, it's better to call _arun from an async context.
        return asyncio.run(self._arun(page_content_list, chunk_size, chunk_overlap)) 