import time
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import json

class AffinityMonitoring:
    """
    Comprehensive Monitoring & Continuous Improvement system for tracking system health,
    data quality, performance metrics, and user feedback. Provides real-time monitoring
    with configurable alerting and quality assessment.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("app.monitoring")
        
        # Initialize metrics storage
        self.metrics = {
            'system_health': defaultdict(list),
            'data_quality': defaultdict(list),
            'performance': defaultdict(list),
            'user_feedback': defaultdict(list),
            'errors': defaultdict(list)
        }
        
        # Time series data (keep last 1000 entries per metric)
        self.time_series = {
            'affinity_generation_time': deque(maxlen=1000),
            'web_discovery_time': deque(maxlen=1000),
            'validation_time': deque(maxlen=1000),
            'quality_scores': deque(maxlen=1000),
            'cache_hit_rates': deque(maxlen=1000),
            'error_rates': deque(maxlen=1000)
        }
        
        # Alert thresholds
        self.thresholds = {
            'quality_score_min': self.config.get('monitoring', {}).get('quality_threshold', 0.6),
            'response_time_max': self.config.get('monitoring', {}).get('response_time_threshold', 30.0),
            'error_rate_max': self.config.get('monitoring', {}).get('error_rate_threshold', 0.1),
            'cache_hit_rate_min': self.config.get('monitoring', {}).get('cache_hit_threshold', 0.4)
        }
        
        # System state tracking
        self.system_state = {
            'status': 'healthy',
            'last_check': None,
            'active_alerts': [],
            'total_destinations_processed': 0,
            'total_affinities_generated': 0,
            'uptime_start': datetime.now()
        }
        
        self.logger.info("AffinityMonitoring system initialized")

    def track_system_health(self) -> Dict[str, Any]:
        """
        Tracks and exposes key system health metrics including performance,
        quality, and operational status.
        """
        self.logger.info("Tracking system health metrics")
        
        current_time = datetime.now()
        
        # Calculate system health metrics
        health_metrics = self._calculate_health_metrics()
        
        # Store metrics
        self.metrics['system_health']['timestamp'].append(current_time.isoformat())
        for metric_name, value in health_metrics.items():
            self.metrics['system_health'][metric_name].append(value)
        
        # Update system state
        self.system_state['last_check'] = current_time.isoformat()
        self.system_state['status'] = self._assess_overall_health(health_metrics)
        
        # Log key metrics
        self.logger.info(f"System Status: {self.system_state['status']}")
        self.logger.info(f"Quality Score: {health_metrics.get('avg_quality_score', 0):.3f}")
        self.logger.info(f"Response Time: {health_metrics.get('avg_response_time', 0):.2f}s")
        self.logger.info(f"Error Rate: {health_metrics.get('error_rate', 0):.3f}")
        
        return {
            'system_state': self.system_state,
            'health_metrics': health_metrics,
            'timestamp': current_time.isoformat()
        }

    def track_destination_processing(self, destination: str, processing_time: float, 
                                   quality_score: float, affinity_count: int,
                                   errors: List[str] = None) -> None:
        """
        Track metrics for a single destination processing operation.
        """
        timestamp = datetime.now()
        errors = errors or []
        
        # Update counters
        self.system_state['total_destinations_processed'] += 1
        self.system_state['total_affinities_generated'] += affinity_count
        
        # Track time series data
        self.time_series['affinity_generation_time'].append({
            'timestamp': timestamp.isoformat(),
            'destination': destination,
            'processing_time': processing_time,
            'affinity_count': affinity_count
        })
        
        self.time_series['quality_scores'].append({
            'timestamp': timestamp.isoformat(),
            'destination': destination,
            'quality_score': quality_score,
            'affinity_count': affinity_count
        })
        
        # Track errors
        if errors:
            self.time_series['error_rates'].append({
                'timestamp': timestamp.isoformat(),
                'destination': destination,
                'error_count': len(errors),
                'errors': errors
            })
        
        self.logger.info(f"Tracked processing for {destination}: "
                        f"{processing_time:.2f}s, quality: {quality_score:.3f}, "
                        f"affinities: {affinity_count}, errors: {len(errors)}")

    def track_web_discovery_performance(self, destination: str, discovery_time: float,
                                      urls_found: int, urls_processed: int,
                                      cache_hits: int, cache_misses: int) -> None:
        """
        Track web discovery and caching performance metrics.
        """
        timestamp = datetime.now()
        cache_hit_rate = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
        
        self.time_series['web_discovery_time'].append({
            'timestamp': timestamp.isoformat(),
            'destination': destination,
            'discovery_time': discovery_time,
            'urls_found': urls_found,
            'urls_processed': urls_processed,
            'success_rate': urls_processed / urls_found if urls_found > 0 else 0
        })
        
        self.time_series['cache_hit_rates'].append({
            'timestamp': timestamp.isoformat(),
            'destination': destination,
            'cache_hit_rate': cache_hit_rate,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses
        })
        
        self.logger.debug(f"Web discovery for {destination}: {discovery_time:.2f}s, "
                         f"cache hit rate: {cache_hit_rate:.3f}")

    def track_validation_performance(self, destination: str, validation_time: float,
                                   themes_before: int, themes_after: int,
                                   confidence_improvement: float) -> None:
        """
        Track validation and reconciliation performance.
        """
        timestamp = datetime.now()
        
        self.time_series['validation_time'].append({
            'timestamp': timestamp.isoformat(),
            'destination': destination,
            'validation_time': validation_time,
            'themes_before': themes_before,
            'themes_after': themes_after,
            'reduction_rate': (themes_before - themes_after) / themes_before if themes_before > 0 else 0,
            'confidence_improvement': confidence_improvement
        })
        
        self.logger.debug(f"Validation for {destination}: {validation_time:.2f}s, "
                         f"themes: {themes_before}→{themes_after}, "
                         f"confidence boost: {confidence_improvement:.3f}")

    def check_for_alerts(self) -> List[Dict[str, Any]]:
        """
        Checks metric thresholds and generates alerts for anomalies or threshold breaches.
        """
        alerts = []
        current_time = datetime.now()
        
        # Check quality score alerts
        recent_quality_scores = self._get_recent_values('quality_scores', hours=1)
        if recent_quality_scores:
            avg_quality = statistics.mean([score['quality_score'] for score in recent_quality_scores])
            if avg_quality < self.thresholds['quality_score_min']:
                alerts.append({
                    'type': 'quality_degradation',
                    'severity': 'high',
                    'message': f"Average quality score ({avg_quality:.3f}) below threshold ({self.thresholds['quality_score_min']})",
                    'timestamp': current_time.isoformat(),
                    'metric': 'quality_score',
                    'value': avg_quality,
                    'threshold': self.thresholds['quality_score_min']
                })
        
        # Check response time alerts
        recent_processing_times = self._get_recent_values('affinity_generation_time', hours=1)
        if recent_processing_times:
            avg_time = statistics.mean([pt['processing_time'] for pt in recent_processing_times])
            if avg_time > self.thresholds['response_time_max']:
                alerts.append({
                    'type': 'performance_degradation',
                    'severity': 'medium',
                    'message': f"Average response time ({avg_time:.2f}s) above threshold ({self.thresholds['response_time_max']}s)",
                    'timestamp': current_time.isoformat(),
                    'metric': 'response_time',
                    'value': avg_time,
                    'threshold': self.thresholds['response_time_max']
                })
        
        # Check error rate alerts
        recent_errors = self._get_recent_values('error_rates', hours=1)
        total_recent_operations = len(self._get_recent_values('affinity_generation_time', hours=1))
        if total_recent_operations > 0:
            error_rate = len(recent_errors) / total_recent_operations
            if error_rate > self.thresholds['error_rate_max']:
                alerts.append({
                    'type': 'error_rate_high',
                    'severity': 'high',
                    'message': f"Error rate ({error_rate:.3f}) above threshold ({self.thresholds['error_rate_max']})",
                    'timestamp': current_time.isoformat(),
                    'metric': 'error_rate',
                    'value': error_rate,
                    'threshold': self.thresholds['error_rate_max']
                })
        
        # Check cache performance alerts
        recent_cache_rates = self._get_recent_values('cache_hit_rates', hours=1)
        if recent_cache_rates:
            avg_cache_hit = statistics.mean([chr['cache_hit_rate'] for chr in recent_cache_rates])
            if avg_cache_hit < self.thresholds['cache_hit_rate_min']:
                alerts.append({
                    'type': 'cache_performance_low',
                    'severity': 'low',
                    'message': f"Cache hit rate ({avg_cache_hit:.3f}) below threshold ({self.thresholds['cache_hit_rate_min']})",
                    'timestamp': current_time.isoformat(),
                    'metric': 'cache_hit_rate',
                    'value': avg_cache_hit,
                    'threshold': self.thresholds['cache_hit_rate_min']
                })
        
        # Update active alerts
        self.system_state['active_alerts'] = alerts
        
        # Log alerts
        for alert in alerts:
            severity = alert['severity']
            message = alert['message']
            if severity == 'high':
                self.logger.error(f"HIGH SEVERITY ALERT: {message}")
            elif severity == 'medium':
                self.logger.warning(f"MEDIUM SEVERITY ALERT: {message}")
            else:
                self.logger.info(f"LOW SEVERITY ALERT: {message}")
        
        return alerts

    def get_system_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive system metrics for the specified time period.
        """
        # Get recent data
        recent_quality = self._get_recent_values('quality_scores', hours)
        recent_processing = self._get_recent_values('affinity_generation_time', hours)
        recent_cache = self._get_recent_values('cache_hit_rates', hours)
        recent_errors = self._get_recent_values('error_rates', hours)
        
        # Calculate aggregate metrics
        metrics = {
            'time_period_hours': hours,
            'total_destinations_processed': len(recent_processing),
            'total_affinities_generated': sum(p['affinity_count'] for p in recent_processing),
            'avg_quality_score': statistics.mean([q['quality_score'] for q in recent_quality]) if recent_quality else 0,
            'avg_processing_time': statistics.mean([p['processing_time'] for p in recent_processing]) if recent_processing else 0,
            'avg_cache_hit_rate': statistics.mean([c['cache_hit_rate'] for c in recent_cache]) if recent_cache else 0,
            'error_count': len(recent_errors),
            'error_rate': len(recent_errors) / len(recent_processing) if recent_processing else 0,
            'uptime_hours': (datetime.now() - self.system_state['uptime_start']).total_seconds() / 3600,
            'system_status': self.system_state['status'],
            'active_alerts_count': len(self.system_state['active_alerts'])
        }
        
        # Add quality distribution
        if recent_quality:
            quality_scores = [q['quality_score'] for q in recent_quality]
            metrics['quality_distribution'] = {
                'min': min(quality_scores),
                'max': max(quality_scores),
                'median': statistics.median(quality_scores),
                'std_dev': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            }
        
        # Add performance distribution
        if recent_processing:
            processing_times = [p['processing_time'] for p in recent_processing]
            metrics['performance_distribution'] = {
                'min': min(processing_times),
                'max': max(processing_times),
                'median': statistics.median(processing_times),
                'p95': self._percentile(processing_times, 95)
            }
        
        return metrics

    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics in specified format for external monitoring systems.
        """
        metrics_data = {
            'system_state': self.system_state,
            'current_metrics': self.get_system_metrics(hours=1),
            'daily_metrics': self.get_system_metrics(hours=24),
            'active_alerts': self.system_state['active_alerts'],
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format.lower() == 'json':
            return json.dumps(metrics_data, indent=2)
        else:
            # Could add support for other formats (Prometheus, CSV, etc.)
            return str(metrics_data)

    def _calculate_health_metrics(self) -> Dict[str, float]:
        """Calculate current system health metrics."""
        # Get recent data (last hour)
        recent_quality = self._get_recent_values('quality_scores', hours=1)
        recent_processing = self._get_recent_values('affinity_generation_time', hours=1)
        recent_cache = self._get_recent_values('cache_hit_rates', hours=1)
        recent_errors = self._get_recent_values('error_rates', hours=1)
        
        metrics = {}
        
        # Quality metrics
        if recent_quality:
            quality_scores = [q['quality_score'] for q in recent_quality]
            metrics['avg_quality_score'] = statistics.mean(quality_scores)
            metrics['min_quality_score'] = min(quality_scores)
        else:
            metrics['avg_quality_score'] = 0
            metrics['min_quality_score'] = 0
        
        # Performance metrics
        if recent_processing:
            processing_times = [p['processing_time'] for p in recent_processing]
            metrics['avg_response_time'] = statistics.mean(processing_times)
            metrics['max_response_time'] = max(processing_times)
            metrics['throughput'] = len(recent_processing)  # Operations per hour
        else:
            metrics['avg_response_time'] = 0
            metrics['max_response_time'] = 0
            metrics['throughput'] = 0
        
        # Cache performance
        if recent_cache:
            cache_rates = [c['cache_hit_rate'] for c in recent_cache]
            metrics['avg_cache_hit_rate'] = statistics.mean(cache_rates)
        else:
            metrics['avg_cache_hit_rate'] = 0
        
        # Error metrics
        total_operations = len(recent_processing)
        error_count = len(recent_errors)
        metrics['error_rate'] = error_count / total_operations if total_operations > 0 else 0
        metrics['error_count'] = error_count
        
        return metrics

    def _assess_overall_health(self, health_metrics: Dict[str, float]) -> str:
        """Assess overall system health based on metrics."""
        issues = 0
        
        # Check each metric against thresholds
        if health_metrics.get('avg_quality_score', 1) < self.thresholds['quality_score_min']:
            issues += 2  # Quality issues are critical
        
        if health_metrics.get('avg_response_time', 0) > self.thresholds['response_time_max']:
            issues += 1
        
        if health_metrics.get('error_rate', 0) > self.thresholds['error_rate_max']:
            issues += 2  # Error rate issues are critical
        
        if health_metrics.get('avg_cache_hit_rate', 1) < self.thresholds['cache_hit_rate_min']:
            issues += 1
        
        # Determine status
        if issues == 0:
            return 'healthy'
        elif issues <= 2:
            return 'degraded'
        else:
            return 'unhealthy'

    def _get_recent_values(self, metric_name: str, hours: int) -> List[Dict]:
        """Get metric values from the last N hours."""
        if metric_name not in self.time_series:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_values = []
        
        for entry in self.time_series[metric_name]:
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if entry_time >= cutoff_time:
                recent_values.append(entry)
        
        return recent_values

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)] 