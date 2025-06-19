"""
Base Agent Framework

Provides the foundational agent functionality for the SmartDestinationThemes system.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Agent lifecycle states"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1=highest, 10=lowest
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    requires_response: bool = False
    timeout_seconds: Optional[float] = None

@dataclass
class AgentPerformanceMetrics:
    """Performance tracking for agents"""
    messages_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_processing_time: float = 0.0
    total_processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    error_count: int = 0
    last_activity: Optional[datetime] = None

class BaseAgent(ABC):
    """
    Base agent class providing core functionality for all agents in the system.
    
    Features:
    - Async message handling and communication
    - Performance monitoring and metrics
    - Lifecycle management
    - Error handling and recovery
    - Health monitoring
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.state = AgentState.INITIALIZING
        
        # Communication setup
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.message_handlers: Dict[str, Callable] = {}
        self.orchestrator_channel: Optional[asyncio.Queue] = None
        
        # Performance monitoring
        self.metrics = AgentPerformanceMetrics()
        self.start_time = time.time()
        
        # Task management
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, Any] = {}
        
        # Error handling
        self.max_retries = config.get('agent_max_retries', 3)
        self.retry_delay = config.get('agent_retry_delay', 1.0)
        
        # Health monitoring
        self.health_check_interval = config.get('agent_health_check_interval', 30.0)
        self.last_health_check = time.time()
        
        # Logging
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
    async def initialize(self) -> bool:
        """Initialize the agent and prepare for operation"""
        try:
            self.logger.info(f"Initializing agent {self.agent_id}")
            
            # Register default message handlers
            self._register_default_handlers()
            
            # Agent-specific initialization
            await self._initialize_agent_specific()
            
            # Start message processing loop
            asyncio.create_task(self._message_processing_loop())
            
            # Start health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            self.state = AgentState.READY
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            self.state = AgentState.ERROR
            return False
    
    @abstractmethod
    async def _initialize_agent_specific(self):
        """Agent-specific initialization logic - must be implemented by subclasses"""
        pass
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to another agent or the orchestrator"""
        try:
            if message.recipient_id == "orchestrator" and self.orchestrator_channel:
                await self.orchestrator_channel.put(message)
            else:
                # For inter-agent communication, route through orchestrator
                message.sender_id = self.agent_id
                if self.orchestrator_channel:
                    await self.orchestrator_channel.put(message)
                else:
                    self.logger.warning(f"No orchestrator channel available to send message {message.message_id}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message {message.message_id}: {e}")
            return False
    
    async def receive_message(self, message: AgentMessage):
        """Receive a message from another agent or orchestrator"""
        try:
            await self.message_queue.put(message)
        except asyncio.QueueFull:
            self.logger.error(f"Message queue full, dropping message {message.message_id}")
    
    async def execute_task(self, task_id: str, task_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with proper error handling and monitoring"""
        self.state = AgentState.PROCESSING
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting task {task_id}")
            
            # Agent-specific task execution
            result = await self._execute_task_specific(task_id, task_definition)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_task_metrics(processing_time, success=True)
            
            self.logger.info(f"Completed task {task_id} in {processing_time:.2f}s")
            self.state = AgentState.READY
            
            return {
                'status': 'success',
                'result': result,
                'processing_time': processing_time,
                'agent_id': self.agent_id
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_task_metrics(processing_time, success=False)
            
            self.logger.error(f"Task {task_id} failed: {e}")
            self.state = AgentState.ERROR
            
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': processing_time,
                'agent_id': self.agent_id
            }
    
    @abstractmethod
    async def _execute_task_specific(self, task_id: str, task_definition: Dict[str, Any]) -> Any:
        """Agent-specific task execution - must be implemented by subclasses"""
        pass
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def set_orchestrator_channel(self, channel: asyncio.Queue):
        """Set the communication channel to the orchestrator"""
        self.orchestrator_channel = channel
        self.logger.debug("Orchestrator channel set")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        uptime = time.time() - self.start_time
        
        return {
            'agent_id': self.agent_id,
            'state': self.state.value,
            'uptime_seconds': uptime,
            'messages_processed': self.metrics.messages_processed,
            'tasks_completed': self.metrics.tasks_completed,
            'tasks_failed': self.metrics.tasks_failed,
            'success_rate': (
                self.metrics.tasks_completed / (self.metrics.tasks_completed + self.metrics.tasks_failed)
                if (self.metrics.tasks_completed + self.metrics.tasks_failed) > 0 else 0.0
            ),
            'average_processing_time': self.metrics.average_processing_time,
            'total_processing_time': self.metrics.total_processing_time,
            'memory_usage_mb': self.metrics.memory_usage_mb,
            'error_count': self.metrics.error_count,
            'last_activity': self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        self.logger.info(f"Shutting down agent {self.agent_id}")
        self.state = AgentState.SHUTTING_DOWN
        
        try:
            # Cancel active tasks
            for task_id, task in self.active_tasks.items():
                if not task.done():
                    task.cancel()
                    self.logger.debug(f"Cancelled task {task_id}")
            
            # Wait a bit for tasks to clean up
            await asyncio.sleep(0.1)
            
            # Agent-specific cleanup
            await self._cleanup_agent_specific()
            
            self.state = AgentState.TERMINATED
            self.logger.info(f"Agent {self.agent_id} shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def _cleanup_agent_specific(self):
        """Agent-specific cleanup - can be overridden by subclasses"""
        pass
    
    # Private methods
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("health_check", self._handle_health_check)
        self.register_message_handler("get_metrics", self._handle_get_metrics)
        self.register_message_handler("shutdown", self._handle_shutdown)
    
    async def _message_processing_loop(self):
        """Main message processing loop"""
        self.logger.debug("Starting message processing loop")
        
        while self.state not in [AgentState.SHUTTING_DOWN, AgentState.TERMINATED]:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                await self._process_message(message)
                self.metrics.messages_processed += 1
                self.metrics.last_activity = datetime.now()
                
            except asyncio.TimeoutError:
                # No message received, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                self.metrics.error_count += 1
    
    async def _process_message(self, message: AgentMessage):
        """Process a received message"""
        handler = self.message_handlers.get(message.message_type)
        
        if handler:
            try:
                await handler(message)
            except Exception as e:
                self.logger.error(f"Error handling message {message.message_id}: {e}")
                
                if message.requires_response:
                    # Send error response
                    error_response = AgentMessage(
                        sender_id=self.agent_id,
                        recipient_id=message.sender_id,
                        message_type="error_response",
                        payload={'error': str(e), 'original_message_id': message.message_id},
                        correlation_id=message.message_id
                    )
                    await self.send_message(error_response)
        else:
            self.logger.warning(f"No handler for message type: {message.message_type}")
    
    async def _health_monitoring_loop(self):
        """Health monitoring loop"""
        while self.state not in [AgentState.SHUTTING_DOWN, AgentState.TERMINATED]:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Perform health check
                is_healthy = await self._perform_health_check()
                
                if not is_healthy:
                    self.logger.warning(f"Health check failed for agent {self.agent_id}")
                    # Could trigger recovery actions here
                
                self.last_health_check = time.time()
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
    
    async def _perform_health_check(self) -> bool:
        """Perform agent health check - can be overridden by subclasses"""
        # Basic health check - agent is responsive
        return self.state in [AgentState.READY, AgentState.PROCESSING, AgentState.WAITING]
    
    def _update_task_metrics(self, processing_time: float, success: bool):
        """Update task processing metrics"""
        if success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1
        
        # Update average processing time
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        self.metrics.total_processing_time += processing_time
        self.metrics.average_processing_time = self.metrics.total_processing_time / total_tasks
    
    # Default message handlers
    
    async def _handle_ping(self, message: AgentMessage):
        """Handle ping message"""
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="pong",
            payload={'timestamp': datetime.now().isoformat()},
            correlation_id=message.message_id
        )
        await self.send_message(response)
    
    async def _handle_health_check(self, message: AgentMessage):
        """Handle health check message"""
        is_healthy = await self._perform_health_check()
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="health_response",
            payload={
                'healthy': is_healthy,
                'state': self.state.value,
                'metrics': self.get_performance_metrics()
            },
            correlation_id=message.message_id
        )
        await self.send_message(response)
    
    async def _handle_get_metrics(self, message: AgentMessage):
        """Handle get metrics message"""
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="metrics_response",
            payload=self.get_performance_metrics(),
            correlation_id=message.message_id
        )
        await self.send_message(response)
    
    async def _handle_shutdown(self, message: AgentMessage):
        """Handle shutdown message"""
        await self.shutdown() 