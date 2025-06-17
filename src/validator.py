import logging
import asyncio
from typing import Dict, List
from sentence_transformers import SentenceTransformer, util
from tools.vectorize_processing_tool import ProcessContentWithVectorizeTool

class AffinityValidator:
    """
    Handles the validation and reconciliation of affinities from different sources.
    Performs semantic clustering and evidence-based validation against web content.
    """
    def __init__(self, config: dict, vectorizer: ProcessContentWithVectorizeTool):
        self.config = config
        self.vectorizer = vectorizer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def validate_and_reconcile(self, llm_affinities: dict, web_signals: dict) -> dict:
        """
        Reconciles LLM-generated affinities with signals from web augmentation.
        """
        logging.info("Performing validation and reconciliation...")
        
        if not llm_affinities.get("affinities"):
            logging.warning("No affinities from LLM to validate.")
            return llm_affinities

        # --- Stage 1: Chunk Web Content ---
        web_pages = web_signals.get("pages", [])
        if not web_pages:
            logging.warning("No web pages found to validate against. Skipping evidence check.")
            chunked_content = []
        else:
            vectorize_result = await self.vectorizer._arun(page_content_list=web_pages)
            chunked_content = vectorize_result.get("chunks", [])

        # --- Stage 2: Evidence-based Score Adjustment ---
        affinities = llm_affinities["affinities"]
        if chunked_content:
            affinities = self._find_evidence_and_adjust_scores(affinities, chunked_content)
        
        # --- Stage 3: Semantic Clustering on adjusted affinities ---
        final_affinities = self._semantic_clustering(affinities)

        llm_affinities["affinities"] = final_affinities
        return llm_affinities

    def _find_evidence_and_adjust_scores(self, affinities: List[Dict], chunks: List) -> List[Dict]:
        """
        Adjusts affinity confidence based on evidence found in web content.
        A simple implementation for now.
        """
        logging.info("Adjusting scores based on web evidence...")
        for affinity in affinities:
            theme = affinity.get("theme", "").lower()
            sub_themes = [st.lower() for st in affinity.get("sub_themes", [])]
            found_evidence = False
            for chunk in chunks:
                chunk_text = chunk.text_chunk.lower()
                if theme in chunk_text:
                    found_evidence = True
                    break
                if any(sub_theme in chunk_text for sub_theme in sub_themes):
                    found_evidence = True
                    break
            
            if found_evidence:
                affinity['confidence'] = min(1.0, affinity.get('confidence', 0.5) + 0.1)
                affinity['validation'] = "Evidence found in web content"
            else:
                affinity['confidence'] = max(0.0, affinity.get('confidence', 0.5) - 0.1)
                affinity['validation'] = "No evidence found in web content"
        
        return affinities

    def _semantic_clustering(self, affinities: List[Dict]) -> List[Dict]:
        """
        Groups affinities based on the semantic similarity of their themes.
        Merges less confident affinities into more confident ones.
        """
        if len(affinities) < 2:
            return affinities

        themes = [affinity['theme'] for affinity in affinities]
        logging.info(f"Clustering themes: {themes}")

        embeddings = self.model.encode(themes, convert_to_tensor=True)
        similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)
        
        clusters = []
        visited = [False] * len(affinities)
        similarity_threshold = 0.8

        for i in range(len(affinities)):
            if visited[i]:
                continue
            
            current_cluster = [i]
            for j in range(i + 1, len(affinities)):
                if not visited[j] and similarity_matrix[i][j] > similarity_threshold:
                    visited[j] = True
                    current_cluster.append(j)
            
            clusters.append(current_cluster)
            visited[i] = True

        logging.info(f"Found {len(clusters)} semantic clusters.")

        merged_affinities = []
        for cluster in clusters:
            if not cluster: continue
            
            best_affinity_in_cluster = max([affinities[i] for i in cluster], key=lambda x: x.get('confidence', 0.0))
            merged_affinities.append(best_affinity_in_cluster)
            
            logging.info(f"From cluster with themes {[affinities[i]['theme'] for i in cluster]}, selected '{best_affinity_in_cluster['theme']}' based on confidence.")

        return merged_affinities 