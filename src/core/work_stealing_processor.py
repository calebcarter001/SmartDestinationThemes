"""
Work Stealing Processor
Implements work-stealing algorithm for enhanced parallel processing.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
import time
from collections import deque
import random

logger = logging.getLogger(__name__)

class WorkItem:
    """Represents a work item in the work stealing queue"""
    
    def __init__(self, item_id: str, data: Any, priority: int = 0):
        self.item_id = item_id
        self.data = data
        self.priority = priority
        self.created_at = datetime.now()
        self.attempts = 0
        self.max_attempts = 3
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first

class WorkerStats:
    """Statistics for individual workers"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.items_processed = 0
        self.items_stolen = 0
        self.items_failed = 0
        self.total_processing_time = 0.0
        self.avg_processing_time = 0.0
        self.last_activity = datetime.now()
    
    def update_processing_time(self, processing_time: float):
        """Update processing time statistics"""
        self.total_processing_time += processing_time
        self.items_processed += 1
        self.avg_processing_time = self.total_processing_time / self.items_processed
        self.last_activity = datetime.now()

class WorkStealingProcessor:
    """Work-stealing processor for enhanced parallel processing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        perf_config = config.get('performance_optimization', {})
        self.num_workers = perf_config.get('worker_pool_size', 12)
        self.steal_threshold = perf_config.get('work_steal_threshold', 2)
        self.max_steal_attempts = perf_config.get('max_steal_attempts', 3)
        self.enable_work_stealing = perf_config.get('enable_work_stealing', True)
        
        # Work queues - one per worker
        self.work_queues: List[deque] = [deque() for _ in range(self.num_workers)]
        self.queue_locks: List[asyncio.Lock] = [asyncio.Lock() for _ in range(self.num_workers)]
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.worker_stats: List[WorkerStats] = [
            WorkerStats(f"worker_{i}") for i in range(self.num_workers)
        ]
        
        # Global state
        self.is_running = False
        self.total_items_processed = 0
        self.total_items_failed = 0
        self.start_time = None
        
        # Results storage
        self.results: Dict[str, Any] = {}
        self.result_lock = asyncio.Lock()
        
    async def process_items(
        self, 
        items: List[Any], 
        processor_func: Callable[[Any], Awaitable[Any]], 
        item_id_func: Callable[[Any], str] = None,
        timeout_seconds: float = 30.0
    ) -> Dict[str, Any]:
        """Process items using work-stealing algorithm"""
        
        if not items:
            return {}
        
        logger.info(f"Starting work-stealing processing of {len(items)} items with {self.num_workers} workers")
        
        # Prepare work items
        work_items = []
        for i, item in enumerate(items):
            item_id = item_id_func(item) if item_id_func else f"item_{i}"
            work_item = WorkItem(item_id, item, priority=random.randint(1, 10))
            work_items.append(work_item)
        
        # Distribute work items across queues using round-robin
        for i, work_item in enumerate(work_items):
            queue_index = i % self.num_workers
            self.work_queues[queue_index].append(work_item)
        
        # Start processing
        self.is_running = True
        self.start_time = time.time()
        self.results.clear()
        
        # Start worker tasks
        self.workers = [
            asyncio.create_task(self._worker(i, processor_func))
            for i in range(self.num_workers)
        ]
        
        # Wait for all workers to complete with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.workers, return_exceptions=True),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning(f"Work-stealing processing timed out after {timeout_seconds}s")
            # Force shutdown
            self.is_running = False
            for worker in self.workers:
                if not worker.done():
                    worker.cancel()
            # Wait a bit more for cleanup
            await asyncio.gather(*self.workers, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in work-stealing processing: {e}")
        finally:
            self.is_running = False
        
        # Log final statistics
        total_time = time.time() - self.start_time
        logger.info(f"Work-stealing processing completed in {total_time:.2f}s")
        logger.info(f"Items processed: {self.total_items_processed}, Failed: {self.total_items_failed}")
        
        # Log worker statistics
        for stats in self.worker_stats:
            if stats.items_processed > 0:
                logger.debug(f"{stats.worker_id}: {stats.items_processed} items, "
                           f"{stats.items_stolen} stolen, avg time: {stats.avg_processing_time:.2f}s")
        
        return self.results.copy()
    
    async def _worker(self, worker_id: int, processor_func: Callable[[Any], Awaitable[Any]]):
        """Individual worker that processes items and steals work when needed"""
        stats = self.worker_stats[worker_id]
        consecutive_empty_checks = 0
        max_empty_checks = 100  # Prevent infinite loops
        
        while self.is_running or (not self._all_queues_empty() and consecutive_empty_checks < max_empty_checks):
            work_item = await self._get_work_item(worker_id)
            
            if work_item is None:
                consecutive_empty_checks += 1
                # If we're not running and no work available, break
                if not self.is_running and consecutive_empty_checks > 10:
                    break
                # No work available, wait a bit
                await asyncio.sleep(0.01)
                continue
            
            # Reset counter when we find work
            consecutive_empty_checks = 0
            
            # Process the work item
            start_time = time.time()
            try:
                result = await processor_func(work_item.data)
                processing_time = time.time() - start_time
                
                # Store result
                async with self.result_lock:
                    self.results[work_item.item_id] = result
                    self.total_items_processed += 1
                
                # Update statistics
                stats.update_processing_time(processing_time)
                
                logger.debug(f"Worker {worker_id} processed {work_item.item_id} in {processing_time:.2f}s")
                
            except Exception as e:
                processing_time = time.time() - start_time
                work_item.attempts += 1
                
                logger.error(f"Worker {worker_id} failed to process {work_item.item_id}: {e}")
                
                # Retry if under max attempts
                if work_item.attempts < work_item.max_attempts:
                    # Put back in a random queue for retry
                    retry_queue = random.randint(0, self.num_workers - 1)
                    async with self.queue_locks[retry_queue]:
                        self.work_queues[retry_queue].append(work_item)
                    logger.debug(f"Retrying {work_item.item_id} (attempt {work_item.attempts})")
                else:
                    # Max attempts reached, mark as failed
                    async with self.result_lock:
                        self.results[work_item.item_id] = None
                        self.total_items_failed += 1
                    
                    stats.items_failed += 1
                    logger.warning(f"Work item {work_item.item_id} failed after {work_item.attempts} attempts")
        
        logger.debug(f"Worker {worker_id} terminating (processed {stats.items_processed} items)")
    
    async def _get_work_item(self, worker_id: int) -> Optional[WorkItem]:
        """Get work item from own queue or steal from others"""
        
        # First, try to get work from own queue
        async with self.queue_locks[worker_id]:
            if self.work_queues[worker_id]:
                return self.work_queues[worker_id].popleft()
        
        # If no work in own queue and work stealing is enabled, try to steal
        if self.enable_work_stealing:
            return await self._steal_work(worker_id)
        
        return None
    
    async def _steal_work(self, worker_id: int) -> Optional[WorkItem]:
        """Attempt to steal work from other workers"""
        
        # Find queues with work available
        potential_victims = []
        for i in range(self.num_workers):
            if i != worker_id and len(self.work_queues[i]) > self.steal_threshold:
                potential_victims.append(i)
        
        if not potential_victims:
            return None
        
        # Try to steal from random victims
        random.shuffle(potential_victims)
        
        for attempt in range(min(self.max_steal_attempts, len(potential_victims))):
            victim_id = potential_victims[attempt]
            
            # Try to acquire lock without blocking too long
            try:
                async with asyncio.wait_for(self.queue_locks[victim_id].acquire(), timeout=0.001):
                    if self.work_queues[victim_id]:
                        # Steal from the end (LIFO for better locality)
                        stolen_item = self.work_queues[victim_id].pop()
                        self.worker_stats[worker_id].items_stolen += 1
                        
                        logger.debug(f"Worker {worker_id} stole work from worker {victim_id}")
                        return stolen_item
                    
                    self.queue_locks[victim_id].release()
                    
            except asyncio.TimeoutError:
                # Couldn't acquire lock quickly, try next victim
                continue
        
        return None
    
    def _all_queues_empty(self) -> bool:
        """Check if all work queues are empty"""
        return all(len(queue) == 0 for queue in self.work_queues)
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        total_time = (time.time() - self.start_time) if self.start_time else 0
        
        worker_stats_data = []
        total_stolen = 0
        
        for stats in self.worker_stats:
            worker_data = {
                'worker_id': stats.worker_id,
                'items_processed': stats.items_processed,
                'items_stolen': stats.items_stolen,
                'items_failed': stats.items_failed,
                'avg_processing_time': stats.avg_processing_time,
                'total_processing_time': stats.total_processing_time
            }
            worker_stats_data.append(worker_data)
            total_stolen += stats.items_stolen
        
        return {
            'total_processing_time': total_time,
            'total_items_processed': self.total_items_processed,
            'total_items_failed': self.total_items_failed,
            'total_items_stolen': total_stolen,
            'num_workers': self.num_workers,
            'work_stealing_enabled': self.enable_work_stealing,
            'worker_stats': worker_stats_data,
            'avg_items_per_worker': self.total_items_processed / self.num_workers if self.num_workers > 0 else 0,
            'steal_efficiency': total_stolen / self.total_items_processed if self.total_items_processed > 0 else 0
        }
    
    async def shutdown(self):
        """Shutdown the work stealing processor"""
        self.is_running = False
        
        # Cancel all worker tasks
        for worker in self.workers:
            if not worker.done():
                worker.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        
        # Clear queues
        for queue in self.work_queues:
            queue.clear()
        
        logger.info("Work stealing processor shutdown complete")
