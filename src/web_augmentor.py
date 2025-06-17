import logging
import asyncio
from typing import Dict, List
from tools.web_discovery_tools import DiscoverAndFetchContentTool
from src.schemas import PageContent

class WebAugmentor:
    """
    Augments destination data by using a comprehensive tool to discover,
    fetch, and process web content.
    """
    def __init__(self, config: dict):
        self.config = config
        api_key = self.config.get("api_keys", {}).get("brave_search")
        
        # Initialize the high-level tool that orchestrates the whole process
        self.discovery_tool = DiscoverAndFetchContentTool(
            brave_api_key=api_key, 
            config=self.config
        )

    async def enrich(self, destination_name: str) -> Dict[str, List[PageContent]]:
        """
        Uses the DiscoverAndFetchContentTool to get validated, content-rich pages.
        """
        logging.info(f"Starting web augmentation for {destination_name} using DiscoverAndFetchContentTool...")
        
        # The tool handles the entire workflow: discovery, fetching, fallback, and priority
        pages = await self.discovery_tool._arun(destination_name=destination_name)
        
        logging.info(f"Web augmentation complete for {destination_name}. Found {len(pages)} pages.")
        
        return {"pages": pages} 