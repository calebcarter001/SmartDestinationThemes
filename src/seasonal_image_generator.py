#!/usr/bin/env python3
"""
Seasonal Image Generator
AI-powered seasonal image generation for travel destinations using DALL-E
"""

import os
import requests
import logging
import time
import asyncio
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
        
        # Rate limiting settings for DALL-E 3
        self.rate_limit_enabled = self.seasonal_config.get('rate_limit_enabled', True)
        self.rate_limit_images_per_minute = self.seasonal_config.get('rate_limit_images_per_minute', 5)  # Conservative Tier 1 limit
        self.rate_limit_delay = 60 / self.rate_limit_images_per_minute  # 12 seconds between images
        self.last_generation_time = 0  # Track last generation time for rate limiting
        
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
        if self.rate_limit_enabled:
            logger.info(f"   ⚡ Rate limiting: {self.rate_limit_images_per_minute} images/minute ({self.rate_limit_delay:.1f}s delay)")
    
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
        
        # Generate images for each season with rate limiting
        for i, (season, details) in enumerate(self.season_prompts.items()):
            try:
                # Apply rate limiting delay (except for first image)
                if self.rate_limit_enabled and i > 0:
                    self._apply_rate_limit()
                
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
                
                # Update last generation time for rate limiting
                if self.rate_limit_enabled:
                    self.last_generation_time = time.time()
                
            except Exception as e:
                logger.error(f"❌ Failed to generate {season} image for {destination}: {e}")
                seasonal_results[season] = {
                    'error': str(e),
                    'prompt': prompt if 'prompt' in locals() else None
                }
        
        logger.info(f"🎨 Seasonal image generation complete for {destination}: {len(seasonal_results)} items")
        return seasonal_results
    
    def _apply_rate_limit(self):
        """Apply rate limiting delay if needed"""
        if not self.rate_limit_enabled:
            return
            
        current_time = time.time()
        time_since_last = current_time - self.last_generation_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.info(f"⏳ Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
    
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
    
    def _sanitize_destination_name(self, destination: str) -> str:
        """Convert destination name to filesystem-safe format"""
        # Replace problematic characters
        sanitized = destination.lower()
        sanitized = sanitized.replace(', ', '_')
        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.replace(',', '')
        
        # Remove any remaining problematic characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789_-')
        sanitized = ''.join(c for c in sanitized if c in allowed_chars)
        
        return sanitized
    
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