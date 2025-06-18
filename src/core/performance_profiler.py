"""
Performance Profiler
Comprehensive performance monitoring and profiling for the SmartDestinationThemes application.
"""

import asyncio
import logging
import time
import psutil
import gc
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import tracemalloc
import sys

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProfileSession:
    """Performance profiling session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: List[PerformanceMetric] = field(default_factory=list)
    memory_snapshots: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

class PerformanceProfiler:
    """Comprehensive performance profiler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configuration
        perf_config = config.get('performance_optimization', {})
        self.enable_profiling = perf_config.get('enable_performance_profiling', False)
        self.memory_tracking = perf_config.get('enable_memory_tracking', True)
        self.detailed_profiling = perf_config.get('enable_detailed_profiling', False)
        self.profile_interval = perf_config.get('profile_interval_seconds', 1.0)
        
        # Profiling state
        self.active_sessions: Dict[str, ProfileSession] = {}
        self.global_metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # System baseline
        self.baseline_metrics = self._capture_baseline_metrics()
        
        # Memory tracking
        if self.memory_tracking:
            tracemalloc.start()
    
    def _capture_baseline_metrics(self) -> Dict[str, Any]:
        """Capture baseline system metrics"""
        try:
            process = psutil.Process()
            system_info = {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'process_memory_baseline': process.memory_info().rss,
                'process_cpu_baseline': process.cpu_percent(),
                'python_version': sys.version,
                'platform': sys.platform
            }
            return system_info
        except Exception as e:
            logger.warning(f"Failed to capture baseline metrics: {e}")
            return {}
    
    async def start_session(self, session_id: str) -> ProfileSession:
        """Start a new profiling session"""
        if not self.enable_profiling:
            return None
        
        if session_id in self.active_sessions:
            logger.warning(f"Profiling session {session_id} already exists")
            return self.active_sessions[session_id]
        
        session = ProfileSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        # Start monitoring if not already running
        if not self.is_monitoring:
            await self.start_monitoring()
        
        logger.info(f"Started profiling session: {session_id}")
        return session
    
    async def end_session(self, session_id: str) -> Optional[ProfileSession]:
        """End a profiling session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Profiling session {session_id} not found")
            return None
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        
        # Capture final metrics
        await self._capture_session_metrics(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Stop monitoring if no active sessions
        if not self.active_sessions and self.is_monitoring:
            await self.stop_monitoring()
        
        logger.info(f"Ended profiling session: {session_id} (duration: {session.duration:.2f}s)")
        return session
    
    @asynccontextmanager
    async def profile_operation(self, operation_name: str, category: str = "operation"):
        """Context manager for profiling individual operations"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            # Record metrics
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            metric = PerformanceMetric(
                name=f"{operation_name}_duration",
                value=duration,
                unit="seconds",
                timestamp=datetime.now(),
                category=category,
                metadata={
                    'operation': operation_name,
                    'memory_delta': memory_delta,
                    'start_memory': start_memory,
                    'end_memory': end_memory
                }
            )
            
            self.global_metrics.append(metric)
            
            # Add to active sessions
            for session in self.active_sessions.values():
                session.metrics.append(metric)
            
            logger.debug(f"Operation {operation_name} completed in {duration:.3f}s (memory delta: {memory_delta:+.1f}MB)")
    
    async def record_metric(self, name: str, value: float, unit: str, category: str = "custom", **metadata):
        """Record a custom metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            category=category,
            metadata=metadata
        )
        
        self.global_metrics.append(metric)
        
        # Add to active sessions
        for session in self.active_sessions.values():
            session.metrics.append(metric)
    
    async def start_monitoring(self):
        """Start continuous system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started performance monitoring")
    
    async def stop_monitoring(self):
        """Stop continuous system monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped performance monitoring")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.is_monitoring:
            try:
                await self._capture_system_metrics()
                await asyncio.sleep(self.profile_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.profile_interval)
    
    async def _capture_system_metrics(self):
        """Capture current system metrics"""
        try:
            process = psutil.Process()
            
            # CPU metrics
            cpu_percent = process.cpu_percent()
            system_cpu = psutil.cpu_percent()
            
            # Memory metrics
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            # Create metrics
            metrics = [
                PerformanceMetric("process_cpu_percent", cpu_percent, "percent", datetime.now(), "system"),
                PerformanceMetric("system_cpu_percent", system_cpu, "percent", datetime.now(), "system"),
                PerformanceMetric("process_memory_rss", memory_info.rss / 1024 / 1024, "MB", datetime.now(), "memory"),
                PerformanceMetric("process_memory_vms", memory_info.vms / 1024 / 1024, "MB", datetime.now(), "memory"),
                PerformanceMetric("system_memory_percent", system_memory.percent, "percent", datetime.now(), "memory"),
                PerformanceMetric("system_memory_available", system_memory.available / 1024 / 1024, "MB", datetime.now(), "memory"),
            ]
            
            # Memory tracking metrics
            if self.memory_tracking and tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                metrics.extend([
                    PerformanceMetric("traced_memory_current", current / 1024 / 1024, "MB", datetime.now(), "memory"),
                    PerformanceMetric("traced_memory_peak", peak / 1024 / 1024, "MB", datetime.now(), "memory"),
                ])
            
            # Add to global metrics
            self.global_metrics.extend(metrics)
            
            # Add to active sessions
            for session in self.active_sessions.values():
                session.metrics.extend(metrics)
                
                # Capture memory snapshots for detailed profiling
                if self.detailed_profiling:
                    snapshot = {
                        'timestamp': datetime.now().isoformat(),
                        'memory_rss': memory_info.rss / 1024 / 1024,
                        'cpu_percent': cpu_percent,
                        'gc_counts': gc.get_count()
                    }
                    session.memory_snapshots.append(snapshot)
                    
        except Exception as e:
            logger.error(f"Failed to capture system metrics: {e}")
    
    async def _capture_session_metrics(self, session: ProfileSession):
        """Capture final metrics for a session"""
        try:
            # Capture final memory snapshot
            if self.detailed_profiling:
                process = psutil.Process()
                memory_info = process.memory_info()
                
                final_snapshot = {
                    'timestamp': datetime.now().isoformat(),
                    'memory_rss': memory_info.rss / 1024 / 1024,
                    'cpu_percent': process.cpu_percent(),
                    'gc_counts': gc.get_count(),
                    'session_duration': session.duration
                }
                session.memory_snapshots.append(final_snapshot)
                
        except Exception as e:
            logger.error(f"Failed to capture session metrics: {e}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    async def get_performance_report(self, session_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            metrics = session.metrics
            memory_snapshots = session.memory_snapshots
        else:
            metrics = self.global_metrics
            memory_snapshots = []
        
        # Analyze metrics by category
        categories = {}
        for metric in metrics:
            if metric.category not in categories:
                categories[metric.category] = []
            categories[metric.category].append(metric)
        
        # Generate summary statistics
        summary = {}
        for category, cat_metrics in categories.items():
            if not cat_metrics:
                continue
                
            # Group by metric name
            metric_groups = {}
            for metric in cat_metrics:
                if metric.name not in metric_groups:
                    metric_groups[metric.name] = []
                metric_groups[metric.name].append(metric.value)
            
            # Calculate statistics
            category_stats = {}
            for name, values in metric_groups.items():
                if values:
                    category_stats[name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'latest': values[-1] if values else 0
                    }
            
            summary[category] = category_stats
        
        # System information
        system_info = self.baseline_metrics.copy()
        if self.is_monitoring:
            try:
                process = psutil.Process()
                system_info.update({
                    'current_memory_mb': process.memory_info().rss / 1024 / 1024,
                    'current_cpu_percent': process.cpu_percent(),
                    'uptime_seconds': (datetime.now() - process.create_time()).total_seconds() if hasattr(process, 'create_time') else 0
                })
            except:
                pass
        
        report = {
            'session_id': session_id,
            'report_generated_at': datetime.now().isoformat(),
            'profiling_enabled': self.enable_profiling,
            'monitoring_active': self.is_monitoring,
            'total_metrics': len(metrics),
            'active_sessions': len(self.active_sessions),
            'system_info': system_info,
            'performance_summary': summary,
            'memory_snapshots': memory_snapshots[-10:] if memory_snapshots else []  # Last 10 snapshots
        }
        
        return report
    
    async def cleanup(self):
        """Cleanup profiler resources"""
        await self.stop_monitoring()
        
        # End all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            await self.end_session(session_id)
        
        # Stop memory tracking
        if self.memory_tracking and tracemalloc.is_tracing():
            tracemalloc.stop()
        
        logger.info("Performance profiler cleanup complete")
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick performance statistics"""
        try:
            process = psutil.Process()
            return {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'active_sessions': len(self.active_sessions),
                'total_metrics': len(self.global_metrics),
                'monitoring_active': self.is_monitoring,
                'profiling_enabled': self.enable_profiling
            }
        except Exception as e:
            logger.error(f"Failed to get quick stats: {e}")
            return {'error': str(e)}
