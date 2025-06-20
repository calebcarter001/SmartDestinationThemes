"""
Export System
Handles export of consolidated destination data in various formats.
"""

import logging
import json
import shutil
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import zipfile

logger = logging.getLogger(__name__)

class DestinationDataExporter:
    """Exports consolidated destination data in various formats"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.export_config = config.get('export_system', {})
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
        
        # Schema version for export compatibility
        self.schema_version = self.export_config.get('schema_version', '2024.1')
        self.export_version = self.export_config.get('version', '1.0.0')
    
    async def export_destination(self, destination: str, consolidated_data: Dict[str, Any], 
                                export_format: str = None) -> Dict[str, Any]:
        """Main export method for a destination"""
        
        export_format = export_format or self.export_config.get('default_format', 'structured')
        
        logger.info(f"Exporting {destination} in {export_format} format")
        
        # Validate data quality
        if not await self._validate_export_data(destination, consolidated_data):
            raise ValueError(f"Data quality insufficient for export: {destination}")
        
        # Create export directory structure
        export_path = await self._create_export_structure(destination)
        
        # Export data based on format
        if export_format == 'structured':
            export_result = await self._export_structured_format(destination, consolidated_data, export_path)
        elif export_format == 'json':
            export_result = await self._export_json_format(destination, consolidated_data, export_path)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Copy images if enabled
        if self.export_config.get('copy_images_to_export', True):
            await self._copy_images_to_export(destination, consolidated_data, export_path)
        
        # Create manifest and metadata
        await self._create_export_manifest(destination, export_path, export_result)
        
        # Validate export integrity
        if self.export_config.get('validate_export_integrity', True):
            await self._validate_export_integrity(export_path)
        
        logger.info(f"Export complete for {destination}: {export_path}")
        
        return {
            'destination': destination,
            'export_format': export_format,
            'export_path': str(export_path),
            'export_timestamp': datetime.now().isoformat(),
            'export_result': export_result
        }
    
    async def _create_export_structure(self, destination: str) -> Path:
        """Create directory structure for destination export"""
        
        safe_name = destination.lower().replace(', ', '_').replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.export_config.get('organize_by_destination', True):
            export_path = self.export_dir / safe_name / f"export_{timestamp}"
        else:
            export_path = self.export_dir / f"{safe_name}_export_{timestamp}"
        
        # Create directory structure
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['data', 'images', 'metadata', 'schemas']
        for subdir in subdirs:
            (export_path / subdir).mkdir(exist_ok=True)
        
        return export_path
    
    async def _export_structured_format(self, destination: str, consolidated_data: Dict[str, Any], 
                                       export_path: Path) -> Dict[str, Any]:
        """Export in structured format with separate files for each data type"""
        
        export_result = {
            'format': 'structured',
            'files_created': [],
            'data_summary': {}
        }
        
        # Export themes
        if consolidated_data.get('themes'):
            themes_file = export_path / "data" / "themes.json"
            await self._write_json_file(themes_file, {
                'destination': destination,
                'export_metadata': self._create_export_metadata('themes'),
                'themes_data': consolidated_data['themes']
            })
            export_result['files_created'].append(str(themes_file))
            export_result['data_summary']['themes'] = {
                'theme_count': len(consolidated_data['themes'].get('affinities', [])),
                'categories': list(set(theme.get('category', 'unknown') 
                                     for theme in consolidated_data['themes'].get('affinities', [])))
            }
        
        # Export nuances
        if consolidated_data.get('nuances'):
            nuances_file = export_path / "data" / "nuances.json"
            await self._write_json_file(nuances_file, {
                'destination': destination,
                'export_metadata': self._create_export_metadata('nuances'),
                'nuances_data': consolidated_data['nuances']
            })
            export_result['files_created'].append(str(nuances_file))
            export_result['data_summary']['nuances'] = {
                'destination_nuances': len(consolidated_data['nuances'].get('destination_nuances', [])),
                'hotel_expectations': len(consolidated_data['nuances'].get('hotel_expectations', [])),
                'vacation_rental_expectations': len(consolidated_data['nuances'].get('vacation_rental_expectations', []))
            }
        
        # Export evidence
        if consolidated_data.get('evidence'):
            evidence_file = export_path / "data" / "evidence.json"
            await self._write_json_file(evidence_file, {
                'destination': destination,
                'export_metadata': self._create_export_metadata('evidence'),
                'evidence_data': consolidated_data['evidence']
            })
            export_result['files_created'].append(str(evidence_file))
            export_result['data_summary']['evidence'] = {
                'evidence_count': len(consolidated_data['evidence'].get('evidence', []))
            }
        
        # Export consolidated metadata
        if consolidated_data.get('metadata'):
            metadata_file = export_path / "metadata" / "processing_metadata.json"
            await self._write_json_file(metadata_file, {
                'destination': destination,
                'export_metadata': self._create_export_metadata('metadata'),
                'processing_metadata': consolidated_data['metadata']
            })
            export_result['files_created'].append(str(metadata_file))
        
        return export_result
    
    async def _export_json_format(self, destination: str, consolidated_data: Dict[str, Any], 
                                 export_path: Path) -> Dict[str, Any]:
        """Export in single JSON format with all data"""
        
        export_file = export_path / "data" / f"{destination.lower().replace(', ', '_').replace(' ', '_')}_complete.json"
        
        complete_export = {
            'destination': destination,
            'export_metadata': self._create_export_metadata('complete'),
            'consolidated_data': consolidated_data
        }
        
        await self._write_json_file(export_file, complete_export)
        
        # Calculate summary
        data_summary = {
            'themes': len(consolidated_data.get('themes', {}).get('affinities', [])),
            'destination_nuances': len(consolidated_data.get('nuances', {}).get('destination_nuances', [])),
            'hotel_expectations': len(consolidated_data.get('nuances', {}).get('hotel_expectations', [])),
            'vacation_rental_expectations': len(consolidated_data.get('nuances', {}).get('vacation_rental_expectations', [])),
            'evidence_count': len(consolidated_data.get('evidence', {}).get('evidence', []))
        }
        
        return {
            'format': 'json',
            'files_created': [str(export_file)],
            'data_summary': data_summary
        }
    
    async def _copy_images_to_export(self, destination: str, consolidated_data: Dict[str, Any], 
                                    export_path: Path):
        """Copy images to export directory"""
        
        images_data = consolidated_data.get('images', {})
        if not images_data:
            return
        
        images_dir = export_path / "images"
        copied_images = []
        
        for season, image_path in images_data.items():
            if os.path.exists(image_path):
                dest_file = images_dir / f"{season}.jpg"
                try:
                    shutil.copy2(image_path, dest_file)
                    copied_images.append(str(dest_file))
                    logger.debug(f"Copied image: {season} -> {dest_file}")
                except Exception as e:
                    logger.warning(f"Failed to copy image {image_path}: {e}")
        
        # Create image manifest if enabled
        if self.export_config.get('create_image_manifest', True):
            manifest = {
                'destination': destination,
                'images': {
                    season: {
                        'original_path': image_path,
                        'export_path': str(images_dir / f"{season}.jpg"),
                        'exists': os.path.exists(image_path)
                    }
                    for season, image_path in images_data.items()
                },
                'copied_images': copied_images,
                'export_timestamp': datetime.now().isoformat()
            }
            
            manifest_file = images_dir / "image_manifest.json"
            await self._write_json_file(manifest_file, manifest)
    
    async def _create_export_manifest(self, destination: str, export_path: Path, 
                                     export_result: Dict[str, Any]):
        """Create comprehensive export manifest"""
        
        # Calculate export size
        export_size = sum(f.stat().st_size for f in export_path.rglob('*') if f.is_file())
        
        manifest = {
            'export_manifest': {
                'destination': destination,
                'export_version': self.export_version,
                'schema_version': self.schema_version,
                'export_timestamp': datetime.now().isoformat(),
                'export_format': export_result.get('format'),
                'export_size_bytes': export_size,
                'export_size_mb': round(export_size / (1024 * 1024), 2)
            },
            'data_summary': export_result.get('data_summary', {}),
            'files': {
                'data_files': [],
                'image_files': [],
                'metadata_files': [],
                'schema_files': []
            },
            'quality_information': self._extract_quality_info(destination),
            'processing_history': self._get_processing_history(destination) if self.export_config.get('include_processing_history', True) else None
        }
        
        # Categorize files
        for file_path in export_path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(export_path))
                
                if file_path.parent.name == 'data':
                    manifest['files']['data_files'].append(relative_path)
                elif file_path.parent.name == 'images':
                    manifest['files']['image_files'].append(relative_path)
                elif file_path.parent.name == 'metadata':
                    manifest['files']['metadata_files'].append(relative_path)
                elif file_path.parent.name == 'schemas':
                    manifest['files']['schema_files'].append(relative_path)
        
        # Save manifest
        manifest_file = export_path / "EXPORT_MANIFEST.json"
        await self._write_json_file(manifest_file, manifest)
        
        # Create schema files if enabled
        if self.export_config.get('include_schema_metadata', True):
            await self._create_schema_files(export_path)
    
    def _create_export_metadata(self, data_type: str) -> Dict[str, Any]:
        """Create metadata for exported data"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'export_version': self.export_version,
            'schema_version': self.schema_version,
            'data_type': data_type,
            'exporter_system': 'SmartDestinationThemes'
        }
    
    def _extract_quality_info(self, destination: str) -> Dict[str, Any]:
        """Extract quality information for export"""
        # This would typically be passed from consolidated_data
        return {
            'note': 'Quality information should be passed from consolidated data',
            'destination': destination
        }
    
    def _get_processing_history(self, destination: str) -> Dict[str, Any]:
        """Get processing history for destination"""
        # This would typically track session history
        return {
            'note': 'Processing history tracking would be implemented here',
            'destination': destination
        }
    
    async def _create_schema_files(self, export_path: Path):
        """Create schema definition files"""
        
        schemas_dir = export_path / "schemas"
        
        # Theme schema
        theme_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Destination Theme Data",
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "affinities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string"},
                            "category": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "required": ["theme", "category", "confidence"]
                    }
                }
            },
            "required": ["destination", "affinities"]
        }
        
        # Nuance schema
        nuance_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Destination Nuance Data",
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "destination_nuances": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phrase": {"type": "string"},
                            "quality_score": {"type": "number"},
                            "search_validated": {"type": "boolean"}
                        }
                    }
                },
                "hotel_expectations": {"type": "array"},
                "vacation_rental_expectations": {"type": "array"}
            },
            "required": ["destination"]
        }
        
        # Save schemas
        await self._write_json_file(schemas_dir / "theme_schema.json", theme_schema)
        await self._write_json_file(schemas_dir / "nuance_schema.json", nuance_schema)
    
    async def _write_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Write JSON data to file with proper formatting"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise
    
    async def _validate_export_data(self, destination: str, consolidated_data: Dict[str, Any]) -> bool:
        """Validate data quality before export"""
        
        min_quality = self.export_config.get('min_quality_for_export', 0.6)
        require_both = self.export_config.get('require_both_themes_and_nuances', False)
        
        has_themes = bool(consolidated_data.get('themes', {}).get('affinities'))
        has_nuances = bool(any(consolidated_data.get('nuances', {}).get(cat, []) 
                              for cat in ['destination_nuances', 'hotel_expectations', 'vacation_rental_expectations']))
        
        if require_both and not (has_themes and has_nuances):
            logger.warning(f"Export validation failed for {destination}: requires both themes and nuances")
            return False
        
        if not has_themes and not has_nuances:
            logger.warning(f"Export validation failed for {destination}: no themes or nuances data")
            return False
        
        # Check quality scores if available
        quality_scores = consolidated_data.get('metadata', {}).get('quality_scores', {})
        
        for data_type, quality in quality_scores.items():
            if quality < min_quality:
                logger.warning(f"Export validation failed for {destination}: {data_type} quality ({quality:.3f}) below threshold ({min_quality})")
                return False
        
        logger.debug(f"Export validation passed for {destination}")
        return True
    
    async def _validate_export_integrity(self, export_path: Path):
        """Validate the integrity of the exported data"""
        
        required_files = []
        
        # Check for data files
        data_dir = export_path / "data"
        if data_dir.exists():
            required_files.extend(data_dir.glob("*.json"))
        
        # Check for manifest
        manifest_file = export_path / "EXPORT_MANIFEST.json"
        if not manifest_file.exists():
            raise ValueError(f"Export manifest missing: {manifest_file}")
        
        # Validate JSON files
        for json_file in export_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in export file {json_file}: {e}")
        
        logger.debug(f"Export integrity validation passed: {export_path}")
    
    async def create_export_archive(self, export_path: Path) -> Path:
        """Create a ZIP archive of the export"""
        
        archive_path = export_path.parent / f"{export_path.name}.zip"
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in export_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(export_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Created export archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create export archive: {e}")
            raise
    
    async def get_export_statistics(self) -> Dict[str, Any]:
        """Get statistics about exports"""
        
        try:
            export_dirs = [d for d in self.export_dir.iterdir() if d.is_dir()]
            
            stats = {
                'total_exports': len(export_dirs),
                'export_directory': str(self.export_dir),
                'destinations_exported': [],
                'total_export_size_mb': 0
            }
            
            for export_dir in export_dirs:
                destination_name = export_dir.name
                stats['destinations_exported'].append(destination_name)
                
                # Calculate size
                size = sum(f.stat().st_size for f in export_dir.rglob('*') if f.is_file())
                stats['total_export_size_mb'] += size / (1024 * 1024)
            
            stats['total_export_size_mb'] = round(stats['total_export_size_mb'], 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get export statistics: {e}")
            return {'error': str(e)}
    
    async def cleanup_old_exports(self, days_old: int = 30):
        """Clean up exports older than specified days"""
        
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
        cleaned_count = 0
        
        try:
            for export_path in self.export_dir.rglob('export_*'):
                if export_path.is_dir() and export_path.stat().st_ctime < cutoff_time:
                    shutil.rmtree(export_path)
                    cleaned_count += 1
                    logger.debug(f"Cleaned up old export: {export_path}")
            
            logger.info(f"Cleaned up {cleaned_count} old exports")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old exports: {e}")
            return 0
