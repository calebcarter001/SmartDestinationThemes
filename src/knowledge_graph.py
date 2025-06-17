import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import requests
import time

class TopBraidIntegration:
    """
    Knowledge Graph integration component that handles the transformation and loading 
    of validated affinities into a knowledge graph using SPARQL endpoints.
    Supports RDF triple generation, graph management, and querying capabilities.
    """
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("app.kg_integration")
        
        # Connection configuration
        kg_config = self.config.get("kg_connection", {})
        self.sparql_endpoint = kg_config.get("sparql_endpoint", "")
        self.graph_uri = kg_config.get("graph_uri", "http://smartdestinations.ai/graph/affinities")
        self.username = kg_config.get("username", "")
        self.password = kg_config.get("password", "")
        self.timeout = kg_config.get("timeout", 30)
        
        # Namespace configuration
        self.namespaces = {
            'sdt': 'http://smartdestinations.ai/ontology/',
            'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'skos': 'http://www.w3.org/2004/02/skos/core#'
        }
        
        # Performance tracking
        self.performance_metrics = {
            'triples_inserted': 0,
            'total_operations': 0,
            'avg_operation_time': 0.0,
            'last_materialization': None
        }
        
        # Initialize connection if endpoint is configured
        if self.sparql_endpoint:
            self._test_connection()
        else:
            self.logger.warning("No SPARQL endpoint configured. Knowledge graph integration disabled.")

    def materialize_to_kg(self, validated_affinities: dict) -> Dict[str, Any]:
        """
        Transforms validated affinity data into RDF triples and loads them into the knowledge graph.

        Args:
            validated_affinities: The validated affinity data for a destination
            
        Returns:
            Dictionary containing materialization results and metadata
        """
        if not validated_affinities or "affinities" not in validated_affinities:
            self.logger.warning("KG Integration: No valid affinities to materialize.")
            return self._empty_result("No affinities provided")

        if not self.sparql_endpoint:
            self.logger.warning("KG Integration: No SPARQL endpoint configured.")
            return self._empty_result("No SPARQL endpoint configured")
        
        start_time = time.time()
        destination_id = validated_affinities.get("destination_id", "unknown_destination")
        
        self.logger.info(f"Materializing {len(validated_affinities['affinities'])} affinities for {destination_id} to knowledge graph")
        
        try:
            # Generate RDF triples
            triples = self._generate_rdf_triples(validated_affinities)
            
            # Clear existing data for this destination
            self._clear_destination_data(destination_id)
            
            # Insert new triples
            insert_result = self._insert_triples(triples)
            
            # Update performance metrics
            operation_time = time.time() - start_time
            self._update_performance_metrics(len(triples), operation_time)
            
            result = {
                "status": "success",
                "destination_id": destination_id,
                "triples_generated": len(triples),
                "triples_inserted": insert_result.get("inserted_count", 0),
                "operation_time_seconds": round(operation_time, 3),
                "graph_uri": self.graph_uri,
                "materialization_timestamp": datetime.now().isoformat(),
                "sparql_endpoint": self.sparql_endpoint
            }
            
            self.logger.info(f"Successfully materialized {len(triples)} triples for {destination_id} in {operation_time:.3f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to materialize affinities for {destination_id}: {e}", exc_info=True)
            return self._error_result(destination_id, str(e))

    def query_destination_affinities(self, destination_id: str) -> Dict[str, Any]:
        """
        Query existing affinities for a destination from the knowledge graph.
        
        Args:
            destination_id: The destination identifier
            
        Returns:
            Dictionary containing query results
        """
        if not self.sparql_endpoint:
            return self._empty_result("No SPARQL endpoint configured")
        
        query = f"""
        PREFIX sdt: <{self.namespaces['sdt']}>
        PREFIX rdfs: <{self.namespaces['rdfs']}>
        
        SELECT ?affinity ?theme ?category ?confidence ?travelerType ?pricePoint ?rationale
        WHERE {{
            GRAPH <{self.graph_uri}> {{
                ?destination sdt:hasAffinity ?affinity .
                ?destination sdt:destinationId "{destination_id}" .
                ?affinity sdt:theme ?theme ;
                         sdt:category ?category ;
                         sdt:confidence ?confidence .
                OPTIONAL {{ ?affinity sdt:travelerType ?travelerType }}
                OPTIONAL {{ ?affinity sdt:pricePoint ?pricePoint }}
                OPTIONAL {{ ?affinity sdt:rationale ?rationale }}
            }}
        }}
        ORDER BY DESC(?confidence)
        """
        
        try:
            results = self._execute_sparql_query(query)
            return {
                "status": "success",
                "destination_id": destination_id,
                "affinities": results.get("results", {}).get("bindings", []),
                "query_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to query affinities for {destination_id}: {e}")
            return self._error_result(destination_id, str(e))

    def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current state of the knowledge graph.
        
        Returns:
            Dictionary containing graph statistics
        """
        if not self.sparql_endpoint:
            return self._empty_result("No SPARQL endpoint configured")
        
        stats_query = f"""
        PREFIX sdt: <{self.namespaces['sdt']}>
        
        SELECT 
            (COUNT(DISTINCT ?destination) AS ?totalDestinations)
            (COUNT(DISTINCT ?affinity) AS ?totalAffinities)
            (AVG(?confidence) AS ?avgConfidence)
        WHERE {{
            GRAPH <{self.graph_uri}> {{
                ?destination sdt:hasAffinity ?affinity .
                ?affinity sdt:confidence ?confidence .
            }}
        }}
        """
        
        try:
            results = self._execute_sparql_query(stats_query)
            bindings = results.get("results", {}).get("bindings", [])
            
            if bindings:
                stats = bindings[0]
                return {
                    "status": "success",
                    "total_destinations": int(stats.get("totalDestinations", {}).get("value", 0)),
                    "total_affinities": int(stats.get("totalAffinities", {}).get("value", 0)),
                    "average_confidence": float(stats.get("avgConfidence", {}).get("value", 0)),
                    "graph_uri": self.graph_uri,
                    "performance_metrics": self.performance_metrics,
                    "query_timestamp": datetime.now().isoformat()
                }
            else:
                return self._empty_result("No data found in knowledge graph")
                
        except Exception as e:
            self.logger.error(f"Failed to get knowledge graph stats: {e}")
            return self._error_result("stats", str(e))

    def _generate_rdf_triples(self, validated_affinities: dict) -> List[str]:
        """
        Generate RDF triples from validated affinity data.
        
        Args:
            validated_affinities: Affinity data to convert
            
        Returns:
            List of RDF triple strings in Turtle format
        """
        destination_id = validated_affinities.get("destination_id")
        affinities = validated_affinities.get("affinities", [])
        meta = validated_affinities.get("meta", {})
        
        # Create destination URI
        destination_uri = f"sdt:destination_{self._sanitize_uri(destination_id)}"
        
        triples = []
        
        # Add destination metadata
        triples.extend([
            f"{destination_uri} rdf:type sdt:Destination .",
            f"{destination_uri} sdt:destinationId \"{destination_id}\" .",
            f"{destination_uri} sdt:lastUpdated \"{datetime.now().isoformat()}\"^^xsd:dateTime .",
        ])
        
        if meta.get("generated_at"):
            triples.append(f"{destination_uri} sdt:generatedAt \"{meta['generated_at']}\"^^xsd:dateTime .")
        
        if meta.get("model_consensus"):
            triples.append(f"{destination_uri} sdt:modelConsensus {meta['model_consensus']} .")
        
        # Add affinity triples
        for i, affinity in enumerate(affinities):
            affinity_uri = f"sdt:affinity_{self._sanitize_uri(destination_id)}_{i}"
            
            # Core affinity properties
            triples.extend([
                f"{destination_uri} sdt:hasAffinity {affinity_uri} .",
                f"{affinity_uri} rdf:type sdt:Affinity .",
                f"{affinity_uri} sdt:theme \"{self._escape_literal(affinity.get('theme', ''))}\" .",
                f"{affinity_uri} sdt:category sdt:{affinity.get('category', 'unknown')} .",
                f"{affinity_uri} sdt:confidence {affinity.get('confidence', 0.0)} .",
                f"{affinity_uri} sdt:pricePoint sdt:{affinity.get('price_point', 'unknown')} .",
            ])
            
            # Optional properties
            if affinity.get('rationale'):
                triples.append(f"{affinity_uri} sdt:rationale \"{self._escape_literal(affinity['rationale'])}\" .")
            
            if affinity.get('validation'):
                triples.append(f"{affinity_uri} sdt:validation \"{self._escape_literal(affinity['validation'])}\" .")
            
            # Sub-themes
            for j, sub_theme in enumerate(affinity.get('sub_themes', [])):
                sub_theme_uri = f"sdt:subtheme_{self._sanitize_uri(destination_id)}_{i}_{j}"
                triples.extend([
                    f"{affinity_uri} sdt:hasSubTheme {sub_theme_uri} .",
                    f"{sub_theme_uri} rdf:type sdt:SubTheme .",
                    f"{sub_theme_uri} rdfs:label \"{self._escape_literal(sub_theme)}\" .",
                ])
            
            # Traveler types
            for traveler_type in affinity.get('traveler_types', []):
                triples.append(f"{affinity_uri} sdt:travelerType sdt:{traveler_type} .")
            
            # Unique selling points
            for j, usp in enumerate(affinity.get('unique_selling_points', [])):
                usp_uri = f"sdt:usp_{self._sanitize_uri(destination_id)}_{i}_{j}"
                triples.extend([
                    f"{affinity_uri} sdt:hasUSP {usp_uri} .",
                    f"{usp_uri} rdf:type sdt:UniqueSellingPoint .",
                    f"{usp_uri} rdfs:label \"{self._escape_literal(usp)}\" .",
                ])
            
            # Seasonality information
            seasonality = affinity.get('seasonality', {})
            if seasonality.get('peak'):
                for month in seasonality['peak']:
                    triples.append(f"{affinity_uri} sdt:peakMonth sdt:{month} .")
            
            if seasonality.get('avoid'):
                for month in seasonality['avoid']:
                    triples.append(f"{affinity_uri} sdt:avoidMonth sdt:{month} .")
        
        return triples

    def _clear_destination_data(self, destination_id: str) -> bool:
        """
        Clear existing data for a destination from the knowledge graph.
        
        Args:
            destination_id: The destination identifier
            
        Returns:
            Boolean indicating success
        """
        destination_uri = f"<{self.namespaces['sdt']}destination_{self._sanitize_uri(destination_id)}>"
        
        delete_query = f"""
        PREFIX sdt: <{self.namespaces['sdt']}>
        
        DELETE {{
            GRAPH <{self.graph_uri}> {{
                ?s ?p ?o .
            }}
        }}
        WHERE {{
            GRAPH <{self.graph_uri}> {{
                {{
                    {destination_uri} ?p ?o .
                    BIND({destination_uri} as ?s)
                }} UNION {{
                    {destination_uri} sdt:hasAffinity ?affinity .
                    ?affinity ?p ?o .
                    BIND(?affinity as ?s)
                }} UNION {{
                    {destination_uri} sdt:hasAffinity ?affinity .
                    ?affinity sdt:hasSubTheme ?subtheme .
                    ?subtheme ?p ?o .
                    BIND(?subtheme as ?s)
                }} UNION {{
                    {destination_uri} sdt:hasAffinity ?affinity .
                    ?affinity sdt:hasUSP ?usp .
                    ?usp ?p ?o .
                    BIND(?usp as ?s)
                }}
            }}
        }}
        """
        
        try:
            self._execute_sparql_update(delete_query)
            self.logger.debug(f"Cleared existing data for destination {destination_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear data for destination {destination_id}: {e}")
            return False

    def _insert_triples(self, triples: List[str]) -> Dict[str, Any]:
        """
        Insert RDF triples into the knowledge graph.
        
        Args:
            triples: List of RDF triple strings
            
        Returns:
            Dictionary with insertion results
        """
        if not triples:
            return {"inserted_count": 0}
        
        # Build SPARQL INSERT query
        prefixes = "\n".join([f"PREFIX {prefix}: <{uri}>" for prefix, uri in self.namespaces.items()])
        triples_block = "\n    ".join(triples)
        
        insert_query = f"""
        {prefixes}
        
        INSERT DATA {{
            GRAPH <{self.graph_uri}> {{
                {triples_block}
            }}
        }}
        """
        
        try:
            self._execute_sparql_update(insert_query)
            self.logger.debug(f"Successfully inserted {len(triples)} triples")
            return {"inserted_count": len(triples)}
        except Exception as e:
            self.logger.error(f"Failed to insert triples: {e}")
            raise

    def _execute_sparql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SPARQL SELECT query against the endpoint.
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results
        """
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query'
        }
        
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)
        
        response = requests.post(
            self.sparql_endpoint,
            data=query,
            headers=headers,
            auth=auth,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()

    def _execute_sparql_update(self, update: str) -> None:
        """
        Execute a SPARQL UPDATE operation against the endpoint.
        
        Args:
            update: SPARQL update string
        """
        headers = {
            'Content-Type': 'application/sparql-update'
        }
        
        auth = None
        if self.username and self.password:
            auth = (self.username, self.password)
        
        # Use update endpoint if configured separately
        update_endpoint = self.config.get("kg_connection", {}).get("sparql_update_endpoint", self.sparql_endpoint)
        
        response = requests.post(
            update_endpoint,
            data=update,
            headers=headers,
            auth=auth,
            timeout=self.timeout
        )
        
        response.raise_for_status()

    def _test_connection(self) -> bool:
        """
        Test the connection to the SPARQL endpoint.
        
        Returns:
            Boolean indicating if connection is successful
        """
        test_query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
        
        try:
            self._execute_sparql_query(test_query)
            self.logger.info(f"Successfully connected to SPARQL endpoint: {self.sparql_endpoint}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to SPARQL endpoint {self.sparql_endpoint}: {e}")
            return False

    def _sanitize_uri(self, text: str) -> str:
        """
        Sanitize text for use in URIs.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text suitable for URIs
        """
        if not text:
            return "unknown"
        
        # Replace spaces and special characters
        sanitized = text.lower().replace(" ", "_").replace(",", "").replace(".", "")
        # Remove any remaining non-alphanumeric characters except underscores
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        return sanitized

    def _escape_literal(self, text: str) -> str:
        """
        Escape special characters in RDF literals.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        if not text:
            return ""
        
        # Escape quotes and backslashes
        escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        return escaped

    def _update_performance_metrics(self, triples_count: int, operation_time: float) -> None:
        """
        Update performance metrics.
        
        Args:
            triples_count: Number of triples processed
            operation_time: Time taken for the operation
        """
        self.performance_metrics['triples_inserted'] += triples_count
        self.performance_metrics['total_operations'] += 1
        
        # Calculate rolling average
        current_avg = self.performance_metrics['avg_operation_time']
        total_ops = self.performance_metrics['total_operations']
        new_avg = ((current_avg * (total_ops - 1)) + operation_time) / total_ops
        self.performance_metrics['avg_operation_time'] = new_avg
        
        self.performance_metrics['last_materialization'] = datetime.now().isoformat()

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """
        Return empty result structure.
        
        Args:
            reason: Reason for empty result
            
        Returns:
            Empty result dictionary
        """
        return {
            "status": "skipped",
            "reason": reason,
            "triples_generated": 0,
            "triples_inserted": 0,
            "operation_time_seconds": 0.0,
            "materialization_timestamp": datetime.now().isoformat()
        }

    def _error_result(self, destination_id: str, error_message: str) -> Dict[str, Any]:
        """
        Return error result structure.
        
        Args:
            destination_id: Destination identifier
            error_message: Error message
            
        Returns:
            Error result dictionary
        """
        return {
            "status": "error",
            "destination_id": destination_id,
            "error_message": error_message,
            "triples_generated": 0,
            "triples_inserted": 0,
            "operation_time_seconds": 0.0,
            "materialization_timestamp": datetime.now().isoformat()
        } 