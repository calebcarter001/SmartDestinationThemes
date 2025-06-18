"""
Streaming Processor
Implements streaming results for progressive feedback and better user experience.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from datetime import datetime
import time
import json

logger = logging.getLogger(__name__)

class StreamingChunk:
    """Represents a chunk of streaming data"""
    
    def __init__(self, chunk_id: str, data: Any, chunk_type: str = "data", progress: float = 0.0):
        self.chunk_id = chunk_id
        self.data = data
        self.chunk_type = chunk_type  # data, progress, status, error, complete
        self.progress = progress
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for serialization"""
        return {
            'chunk_id': self.chunk_id,
            'data': self.data,
            'chunk_type': self.chunk_type,
            'progress': self.progress,
            'timestamp': self.timestamp.isoformat()
        }

class StreamingProcessor:
    """Streaming processor for progressive results"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        perf_config = config.get('performance_optimization', {})
        self.enable_streaming = perf_config.get('enable_streaming_results', False)
        self.feedback_interval = perf_config.get('progressive_feedback_interval', 2.0)
        self.max_chunk_size = perf_config.get('max_streaming_chunk_size', 1024 * 1024)  # 1MB
        
        # Streaming state
        self.active_streams: Dict[str, asyncio.Queue] = {}
        self.stream_stats: Dict[str, Dict] = {}
        self.global_stats = {
            'total_streams': 0,
            'active_streams': 0,
            'chunks_sent': 0,
            'total_data_streamed': 0
        }
    
    async def create_stream(self, stream_id: str) -> asyncio.Queue:
        """Create a new streaming queue"""
        if stream_id in self.active_streams:
            raise ValueError(f"Stream {stream_id} already exists")
        
        stream_queue = asyncio.Queue(maxsize=100)  # Buffer up to 100 chunks
        self.active_streams[stream_id] = stream_queue
        self.stream_stats[stream_id] = {
            'created_at': datetime.now(),
            'chunks_sent': 0,
            'data_sent': 0,
            'last_activity': datetime.now()
        }
        
        self.global_stats['total_streams'] += 1
        self.global_stats['active_streams'] += 1
        
        logger.debug(f"Created streaming queue for {stream_id}")
        return stream_queue
    
    async def send_chunk(self, stream_id: str, chunk: StreamingChunk):
        """Send a chunk to the specified stream"""
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found, ignoring chunk")
            return
        
        try:
            # Add chunk to queue (non-blocking)
            self.active_streams[stream_id].put_nowait(chunk)
            
            # Update statistics
            stats = self.stream_stats[stream_id]
            stats['chunks_sent'] += 1
            stats['last_activity'] = datetime.now()
            
            # Estimate data size
            if hasattr(chunk.data, '__len__'):
                data_size = len(str(chunk.data))
                stats['data_sent'] += data_size
                self.global_stats['total_data_streamed'] += data_size
            
            self.global_stats['chunks_sent'] += 1
            
            logger.debug(f"Sent chunk {chunk.chunk_id} to stream {stream_id}")
            
        except asyncio.QueueFull:
            logger.warning(f"Stream {stream_id} queue is full, dropping chunk {chunk.chunk_id}")
    
    async def send_progress(self, stream_id: str, progress: float, message: str = ""):
        """Send progress update to stream"""
        chunk = StreamingChunk(
            chunk_id=f"progress_{int(time.time() * 1000)}",
            data={'message': message, 'progress': progress},
            chunk_type="progress",
            progress=progress
        )
        await self.send_chunk(stream_id, chunk)
    
    async def send_status(self, stream_id: str, status: str, details: Dict[str, Any] = None):
        """Send status update to stream"""
        chunk = StreamingChunk(
            chunk_id=f"status_{int(time.time() * 1000)}",
            data={'status': status, 'details': details or {}},
            chunk_type="status"
        )
        await self.send_chunk(stream_id, chunk)
    
    async def send_error(self, stream_id: str, error: str, error_details: Dict[str, Any] = None):
        """Send error to stream"""
        chunk = StreamingChunk(
            chunk_id=f"error_{int(time.time() * 1000)}",
            data={'error': error, 'details': error_details or {}},
            chunk_type="error"
        )
        await self.send_chunk(stream_id, chunk)
    
    async def send_completion(self, stream_id: str, final_result: Any = None):
        """Send completion signal to stream"""
        chunk = StreamingChunk(
            chunk_id=f"complete_{int(time.time() * 1000)}",
            data={'result': final_result},
            chunk_type="complete"
        )
        await self.send_chunk(stream_id, chunk)
    
    async def get_stream(self, stream_id: str) -> AsyncGenerator[StreamingChunk, None]:
        """Get streaming chunks from the specified stream"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        stream_queue = self.active_streams[stream_id]
        
        try:
            while True:
                try:
                    # Wait for next chunk with timeout
                    chunk = await asyncio.wait_for(stream_queue.get(), timeout=self.feedback_interval)
                    yield chunk
                    
                    # Check if this is a completion chunk
                    if chunk.chunk_type == "complete":
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive/heartbeat
                    heartbeat = StreamingChunk(
                        chunk_id=f"heartbeat_{int(time.time() * 1000)}",
                        data={'timestamp': datetime.now().isoformat()},
                        chunk_type="heartbeat"
                    )
                    yield heartbeat
                    
        except Exception as e:
            logger.error(f"Error in stream {stream_id}: {e}")
            # Send error chunk
            error_chunk = StreamingChunk(
                chunk_id=f"stream_error_{int(time.time() * 1000)}",
                data={'error': str(e)},
                chunk_type="error"
            )
            yield error_chunk
        finally:
            # Clean up stream
            await self.close_stream(stream_id)
    
    async def close_stream(self, stream_id: str):
        """Close and clean up a stream"""
        if stream_id in self.active_streams:
            # Clear remaining items in queue
            queue = self.active_streams[stream_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Remove from active streams
            del self.active_streams[stream_id]
            self.global_stats['active_streams'] -= 1
            
            logger.debug(f"Closed stream {stream_id}")
    
    async def stream_destination_processing(
        self, 
        stream_id: str, 
        destinations: List[str], 
        processor_func: Callable[[str], AsyncGenerator[Dict[str, Any], None]]
    ):
        """Stream destination processing with progressive results"""
        
        if not self.enable_streaming:
            logger.info("Streaming disabled, using batch processing")
            return
        
        await self.create_stream(stream_id)
        
        try:
            total_destinations = len(destinations)
            processed_count = 0
            
            await self.send_status(stream_id, "started", {
                'total_destinations': total_destinations,
                'streaming_enabled': True
            })
            
            for dest in destinations:
                await self.send_status(stream_id, "processing", {
                    'current_destination': dest,
                    'progress': processed_count / total_destinations
                })
                
                try:
                    # Stream results for this destination
                    async for result_chunk in processor_func(dest):
                        chunk = StreamingChunk(
                            chunk_id=f"{dest}_{int(time.time() * 1000)}",
                            data={
                                'destination': dest,
                                'result': result_chunk,
                                'partial': True
                            },
                            chunk_type="data",
                            progress=processed_count / total_destinations
                        )
                        await self.send_chunk(stream_id, chunk)
                    
                    processed_count += 1
                    await self.send_progress(
                        stream_id, 
                        processed_count / total_destinations,
                        f"Completed {dest} ({processed_count}/{total_destinations})"
                    )
                    
                except Exception as e:
                    await self.send_error(stream_id, f"Failed to process {dest}", {
                        'destination': dest,
                        'error': str(e)
                    })
                    processed_count += 1  # Still count as processed
            
            # Send final completion
            await self.send_completion(stream_id, {
                'total_processed': processed_count,
                'success_rate': processed_count / total_destinations if total_destinations > 0 else 0
            })
            
        except Exception as e:
            await self.send_error(stream_id, "Stream processing failed", {
                'error': str(e),
                'processed_count': processed_count
            })
        finally:
            await self.close_stream(stream_id)
    
    async def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming performance statistics"""
        active_stream_details = []
        
        for stream_id, stats in self.stream_stats.items():
            if stream_id in self.active_streams:
                queue_size = self.active_streams[stream_id].qsize()
                active_stream_details.append({
                    'stream_id': stream_id,
                    'chunks_sent': stats['chunks_sent'],
                    'data_sent': stats['data_sent'],
                    'queue_size': queue_size,
                    'created_at': stats['created_at'].isoformat(),
                    'last_activity': stats['last_activity'].isoformat()
                })
        
        return {
            'global_stats': self.global_stats.copy(),
            'active_streams': active_stream_details,
            'streaming_enabled': self.enable_streaming,
            'feedback_interval': self.feedback_interval,
            'max_chunk_size': self.max_chunk_size
        }
    
    async def cleanup_inactive_streams(self, max_inactive_minutes: int = 30):
        """Clean up streams that have been inactive for too long"""
        cutoff_time = datetime.now() - timedelta(minutes=max_inactive_minutes)
        
        inactive_streams = []
        for stream_id, stats in self.stream_stats.items():
            if stats['last_activity'] < cutoff_time and stream_id in self.active_streams:
                inactive_streams.append(stream_id)
        
        for stream_id in inactive_streams:
            logger.info(f"Cleaning up inactive stream: {stream_id}")
            await self.close_stream(stream_id)
        
        return len(inactive_streams)
    
    async def shutdown(self):
        """Shutdown streaming processor and clean up all streams"""
        stream_ids = list(self.active_streams.keys())
        
        for stream_id in stream_ids:
            await self.close_stream(stream_id)
        
        self.stream_stats.clear()
        logger.info("Streaming processor shutdown complete")
