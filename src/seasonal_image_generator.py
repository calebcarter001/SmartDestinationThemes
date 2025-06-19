#!/usr/bin/env python3
"""
Seasonal Image Generator
AI-powered seasonal image generation for travel destinations using DALL-E
"""

import os
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class SeasonalImageGenerator:
    """Generate seasonal images for travel destinations using DALL-E"""
    
    def __init__(self, config: Dict = None):
        """Initialize the seasonal image generator"""
        self.config = config or {}
        self.seasonal_config = self.config.get('seasonal_imagery', {})
        
        # Load OpenAI API key
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Configuration
        self.enabled = self.seasonal_config.get('enabled', True)
        self.model = self.seasonal_config.get('model', 'dall-e-3')
        self.image_size = self.seasonal_config.get('image_size', '1024x1024')
        self.quality = self.seasonal_config.get('quality', 'standard')
        self.timeout = self.seasonal_config.get('timeout_seconds', 60)
        
        # Seasonal prompts
        self.season_prompts = self.seasonal_config.get('season_prompts', {
            "spring": "soft cherry blossoms, pastel light, fresh blooms, gentle morning light",
            "summer": "vibrant colors, lively festivals, sunny skies, bright daylight",
            "autumn": "golden leaves, warm evening glow, harvest colors, amber light", 
            "winter": "snow-covered streets, twinkling lights, cozy atmosphere, crisp air"
        })
        
        # Prompt template
        self.prompt_template = self.seasonal_config.get('prompt_template',
            "High-resolution professional travel photography of {destination} in {season}, {details}. "
            "Stunning composition, vibrant colors, iconic landmarks visible, {season} atmosphere."
        )
        
        logger.info(f"🎨 Seasonal Image Generator initialized - Model: {self.model}, Size: {self.image_size}")
    
    def generate_seasonal_images(self, destination: str, output_dir: Path) -> Dict[str, Dict]:
        """
        Generate seasonal images for a destination
        
        Args:
            destination: Destination name (e.g., "Tokyo, Japan")
            output_dir: Directory to save images
            
        Returns:
            Dict with seasonal image metadata
        """
        
        if not self.enabled:
            logger.info("🎨 Seasonal image generation disabled")
            return {}
        
        logger.info(f"🎨 Generating seasonal images for {destination}")
        
        # Create destination-specific directory
        dest_dir = output_dir / self._sanitize_destination_name(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        seasonal_results = {}
        seasonal_image_paths = []
        
        # Generate images for each season
        for season, details in self.season_prompts.items():
            try:
                logger.info(f"🌸 Generating {season} image for {destination}")
                
                # Create prompt
                prompt = self.prompt_template.format(
                    destination=destination,
                    season=season,
                    details=details
                )
                
                # Generate image
                image_url = self._generate_image_with_dalle(prompt)
                
                # Download and save image
                image_path = dest_dir / f"{season}.jpg"
                downloaded_path = self._download_image(image_url, image_path)
                seasonal_image_paths.append(downloaded_path)
                
                # Store metadata
                seasonal_results[season] = {
                    'url': str(image_url),
                    'local_path': str(downloaded_path.relative_to(output_dir.parent)),
                    'prompt': prompt,
                    'size': self.image_size,
                    'model': self.model
                }
                
                logger.info(f"✅ {season.capitalize()} image saved: {downloaded_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to generate {season} image for {destination}: {e}")
                seasonal_results[season] = {
                    'error': str(e),
                    'prompt': prompt if 'prompt' in locals() else None
                }
        
        # Create collage if we have multiple images
        if len(seasonal_image_paths) >= 2:
            try:
                collage_path = self._create_seasonal_collage(seasonal_image_paths, dest_dir)
                seasonal_results['collage'] = {
                    'local_path': str(collage_path.relative_to(output_dir.parent)),
                    'images_used': len(seasonal_image_paths)
                }
                logger.info(f"✅ Seasonal collage created: {collage_path}")
            except Exception as e:
                logger.error(f"❌ Failed to create collage for {destination}: {e}")
                seasonal_results['collage'] = {'error': str(e)}
        
        logger.info(f"🎨 Seasonal image generation complete for {destination}: {len(seasonal_results)} items")
        return seasonal_results
    
    def _generate_image_with_dalle(self, prompt: str) -> str:
        """Generate image using DALL-E API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": self.image_size,
            "quality": self.quality
        }
        
        logger.debug(f"🎨 DALL-E request: {prompt[:100]}...")
        
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            logger.debug(f"✅ DALL-E image generated: {image_url[:50]}...")
            return image_url
        else:
            error_msg = f"DALL-E API failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _download_image(self, url: str, save_path: Path) -> Path:
        """Download image from URL and save locally"""
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            save_path.write_bytes(response.content)
            logger.debug(f"📥 Image downloaded: {save_path}")
            return save_path
            
        except Exception as e:
            error_msg = f"Failed to download image from {url}: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _create_seasonal_collage(self, image_paths: List[Path], output_dir: Path) -> Path:
        """Create a 2x2 collage from seasonal images"""
        
        collage_path = output_dir / "seasonal_collage.jpg"
        
        try:
            # Load images
            images = []
            for path in image_paths[:4]:  # Max 4 images for 2x2 grid
                if path.exists():
                    img = Image.open(path).convert("RGB")
                    images.append(img)
            
            if len(images) < 2:
                raise ValueError("Need at least 2 images for collage")
            
            # Get dimensions (assuming all images are same size)
            w, h = images[0].size
            
            # Create canvas
            if len(images) == 2:
                # 1x2 layout
                canvas = Image.new("RGB", (2*w, h))
                canvas.paste(images[0], (0, 0))
                canvas.paste(images[1], (w, 0))
            elif len(images) == 3:
                # 2x2 with one empty spot
                canvas = Image.new("RGB", (2*w, 2*h))
                canvas.paste(images[0], (0, 0))
                canvas.paste(images[1], (w, 0))
                canvas.paste(images[2], (0, h))
            else:
                # 2x2 full grid
                canvas = Image.new("RGB", (2*w, 2*h))
                canvas.paste(images[0], (0, 0))  # top-left
                canvas.paste(images[1], (w, 0))  # top-right
                canvas.paste(images[2], (0, h))  # bottom-left
                canvas.paste(images[3], (w, h))  # bottom-right
            
            # Save collage
            canvas.save(collage_path, "JPEG", quality=90)
            logger.debug(f"🖼️  Collage created: {collage_path}")
            return collage_path
            
        except Exception as e:
            error_msg = f"Failed to create collage: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _sanitize_destination_name(self, destination: str) -> str:
        """Convert destination name to filesystem-safe directory name"""
        return destination.lower().replace(', ', '_').replace(' ', '_').replace(',', '')
    
    def get_seasonal_metadata(self, destination: str, session_dir: Path) -> Dict:
        """Get metadata for existing seasonal images"""
        
        dest_dir = session_dir / "images" / self._sanitize_destination_name(destination)
        
        if not dest_dir.exists():
            return {}
        
        metadata = {}
        
        # Check for individual seasonal images
        for season in self.season_prompts.keys():
            image_path = dest_dir / f"{season}.jpg"
            if image_path.exists():
                metadata[season] = {
                    'local_path': str(image_path.relative_to(session_dir.parent)),
                    'exists': True,
                    'size_bytes': image_path.stat().st_size
                }
        
        # Check for collage
        collage_path = dest_dir / "seasonal_collage.jpg"
        if collage_path.exists():
            metadata['collage'] = {
                'local_path': str(collage_path.relative_to(session_dir.parent)),
                'exists': True,
                'size_bytes': collage_path.stat().st_size
            }
        
        return metadata 