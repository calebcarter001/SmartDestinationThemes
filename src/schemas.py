from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PageContent(BaseModel):
    """Represents the raw content scraped from a single web page."""
    url: str = Field(description="The URL of the scraped page.")
    title: str = Field(description="The title of the page.")
    content: str = Field(description="The main text content of the page.")
    content_length: int = Field(description="The length of the content in characters.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source, access time, etc.")

class ProcessedPageChunk(BaseModel):
    """Represents a single chunk of processed text, ready for embedding."""
    chunk_id: str = Field(description="A unique identifier for this chunk (e.g., hash of URL + chunk index).")
    url: str = Field(description="The source URL of the content.")
    title: str = Field(description="The title of the source page.")
    text_chunk: str = Field(description="The text content of this specific chunk.")
    chunk_order: int = Field(description="The sequential order of this chunk within the page.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata from processing.")

class FetchPageInput(BaseModel):
    """Input schema for fetching a single web page."""
    url: str = Field(description="The URL of the web page to fetch.") 