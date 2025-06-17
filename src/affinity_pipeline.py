import logging
from src.llm_generator import LLMGenerator
from src.web_augmentor import WebAugmentor
from src.validator import AffinityValidator
from src.knowledge_graph import TopBraidIntegration
from src.caching import AffinityCache
from tools.vectorize_processing_tool import ProcessContentWithVectorizeTool

class AffinityPipeline:
    """
    Orchestrates the end-to-end process of generating destination affinities.
    1. Baseline Generation (LLM) → 2. Dynamic Enrichment (Web) → 
    3. Validation & Reconciliation → 4. Knowledge Graph Integration
    """
    def __init__(self, config: dict):
        self.config = config
        self.llm_generator = LLMGenerator(config=config)
        self.web_augmentor = WebAugmentor(config=config)
        self.vectorize_tool = ProcessContentWithVectorizeTool(config=config)
        self.validator = AffinityValidator(config=config, vectorizer=self.vectorize_tool)
        self.kg_integration = TopBraidIntegration(config=config)
        self.cache = AffinityCache(config=config)

    async def process_destination(self, destination_name: str):
        """
        Runs a single destination through the full affinity generation pipeline.
        Includes caching logic to avoid redundant processing.
        """
        # First, try to get the result from the cache
        # Note: Caching for web-augmented data will need to be more sophisticated.
        # For now, we cache the final validated affinities.
        cached_data = self.cache.get(destination_name)
        if cached_data:
            return cached_data

        # 1. Baseline Generation (LLM)
        llm_affinities = self.llm_generator.generate_baseline(destination_name)
        if "error" in llm_affinities:
            logging.error(f"Halting pipeline for {destination_name} due to LLM generation error.")
            return llm_affinities

        # 2. Dynamic Enrichment (Web) - Now an async call
        web_signals = await self.web_augmentor.enrich(destination_name)

        # 3. Validation & Reconciliation
        # This will eventually take both llm_affinities and web_signals
        validated_affinities = await self.validator.validate_and_reconcile(
            llm_affinities, 
            web_signals
        )
        
        # For now, let's add the web content to the output for inspection
        # validated_affinities['web_augmentation_results'] = web_signals # This is now handled inside validator

        # 4. Knowledge Graph Integration
        self.kg_integration.materialize_to_kg(validated_affinities)

        # Store the final result in the cache before returning
        self.cache.set(destination_name, validated_affinities)

        return validated_affinities 