import logging
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
from enum import Enum
import uuid

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"
    IN_PROGRESS = "in_progress"

class ReviewerRole(Enum):
    SUBJECT_EXPERT = "subject_expert"
    EDITORIAL_REVIEWER = "editorial_reviewer"
    QUALITY_ASSURANCE = "quality_assurance"
    LOCAL_EXPERT = "local_expert"

class QualityAssuranceFlow:
    """
    Comprehensive Quality Assurance and Human Feedback Loop system that manages
    the review process for generated affinities, collects expert feedback,
    and implements continuous improvement through iterative refinement.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logging.getLogger("app.qa_flow")
        
        # Review configuration
        qa_config = self.config.get('quality_assurance', {})
        self.auto_approve_threshold = qa_config.get('auto_approve_threshold', 0.85)
        self.require_review_threshold = qa_config.get('require_review_threshold', 0.6)
        self.multi_reviewer_threshold = qa_config.get('multi_reviewer_threshold', 0.7)
        self.feedback_collection_enabled = qa_config.get('feedback_collection_enabled', True)
        
        # Review storage (in production, this would be a database)
        self.review_queue = {}  # review_id -> review_data
        self.feedback_history = defaultdict(list)  # destination_id -> feedback_list
        self.reviewer_performance = defaultdict(lambda: {
            'reviews_completed': 0,
            'avg_review_time': 0.0,
            'accuracy_score': 0.0,
            'specializations': []
        })
        
        # Quality metrics tracking
        self.quality_metrics = {
            'total_reviews': 0,
            'auto_approved': 0,
            'human_reviewed': 0,
            'rejected': 0,
            'avg_review_time': 0.0,
            'inter_reviewer_agreement': 0.0,
            'improvement_rate': 0.0
        }
        
        # Active learning patterns
        self.learning_patterns = {
            'common_issues': defaultdict(int),
            'reviewer_preferences': defaultdict(dict),
            'quality_improvement_trends': deque(maxlen=100)
        }
        
        self.logger.info("QualityAssuranceFlow system initialized")

    def submit_for_review(self, affinities: dict, quality_score: float, 
                         destination: str, priority: str = "normal") -> Dict[str, Any]:
        """
        Submits generated affinities for human review based on quality score and configuration.
        
        Args:
            affinities: Generated affinity data
            quality_score: Computed quality score from AffinityQualityScorer
            destination: Destination name
            priority: Review priority (low, normal, high, urgent)
            
        Returns:
            Dictionary containing review submission results
        """
        self.logger.info(f"Submitting affinities for review: {destination} (quality: {quality_score:.3f})")
        
        if not affinities or 'affinities' not in affinities:
            return self._error_result("No affinities to review")
        
        # Determine review path based on quality score
        review_decision = self._determine_review_path(quality_score, destination)
        
        if review_decision['action'] == 'auto_approve':
            self._track_auto_approval(destination, quality_score)
            return {
                'status': 'auto_approved',
                'destination': destination,
                'quality_score': quality_score,
                'review_decision': review_decision,
                'approved_at': datetime.now().isoformat(),
                'review_path': 'automatic'
            }
        
        # Create review record
        review_id = str(uuid.uuid4())
        review_data = {
            'review_id': review_id,
            'destination': destination,
            'affinities': affinities,
            'quality_score': quality_score,
            'priority': priority,
            'status': ReviewStatus.PENDING.value,
            'submitted_at': datetime.now().isoformat(),
            'required_reviewers': review_decision['required_reviewers'],
            'review_criteria': review_decision['review_criteria'],
            'reviews': [],
            'metadata': {
                'affinity_count': len(affinities['affinities']),
                'categories_covered': len(set(aff.get('category', '') for aff in affinities['affinities'])),
                'avg_confidence': statistics.mean([aff.get('confidence', 0) for aff in affinities['affinities']])
            }
        }
        
        # Store in review queue
        self.review_queue[review_id] = review_data
        
        # Assign reviewers
        assigned_reviewers = self._assign_reviewers(review_data)
        review_data['assigned_reviewers'] = assigned_reviewers
        
        self.logger.info(f"Created review {review_id} for {destination} with {len(assigned_reviewers)} reviewers")
        
        return {
            'status': 'submitted_for_review',
            'review_id': review_id,
            'destination': destination,
            'quality_score': quality_score,
            'assigned_reviewers': assigned_reviewers,
            'review_decision': review_decision,
            'submitted_at': review_data['submitted_at'],
            'review_path': 'human_review'
        }

    def submit_reviewer_feedback(self, review_id: str, reviewer_id: str, 
                                feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes feedback from human reviewers and updates review status.
        
        Args:
            review_id: Unique review identifier
            reviewer_id: Reviewer identifier
            feedback: Structured feedback from reviewer
            
        Returns:
            Dictionary containing feedback processing results
        """
        if review_id not in self.review_queue:
            return self._error_result(f"Review {review_id} not found")
        
        review_data = self.review_queue[review_id]
        
        # Validate reviewer assignment
        if reviewer_id not in review_data.get('assigned_reviewers', []):
            return self._error_result(f"Reviewer {reviewer_id} not assigned to review {review_id}")
        
        # Process feedback
        processed_feedback = self._process_reviewer_feedback(feedback, reviewer_id)
        
        # Add to review record
        review_entry = {
            'reviewer_id': reviewer_id,
            'reviewer_role': processed_feedback.get('reviewer_role', ReviewerRole.QUALITY_ASSURANCE.value),
            'submitted_at': datetime.now().isoformat(),
            'decision': processed_feedback.get('decision', ReviewStatus.APPROVED.value),
            'feedback': processed_feedback,
            'review_time_minutes': processed_feedback.get('review_time_minutes', 0)
        }
        
        review_data['reviews'].append(review_entry)
        
        # Update reviewer performance metrics
        self._update_reviewer_performance(reviewer_id, review_entry)
        
        # Check if review is complete
        review_complete = self._check_review_completion(review_data)
        
        if review_complete:
            final_decision = self._make_final_decision(review_data)
            review_data['status'] = final_decision['status']
            review_data['final_decision'] = final_decision
            review_data['completed_at'] = datetime.now().isoformat()
            
            # Store feedback for learning
            self._store_feedback_for_learning(review_data)
            
            self.logger.info(f"Review {review_id} completed with decision: {final_decision['status']}")
            
            return {
                'status': 'review_completed',
                'review_id': review_id,
                'final_decision': final_decision,
                'total_reviewers': len(review_data['reviews']),
                'review_duration_hours': self._calculate_review_duration(review_data),
                'destination': review_data['destination']
            }
        else:
            self.logger.info(f"Review {review_id} updated, awaiting additional feedback")
            return {
                'status': 'feedback_recorded',
                'review_id': review_id,
                'reviews_completed': len(review_data['reviews']),
                'reviews_pending': len(review_data['assigned_reviewers']) - len(review_data['reviews']),
                'destination': review_data['destination']
            }

    def get_review_queue(self, reviewer_id: Optional[str] = None, 
                        status: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves pending reviews from the queue, optionally filtered by reviewer or status.

        Args:
            reviewer_id: Optional reviewer filter
            status: Optional status filter
            
        Returns:
            Dictionary containing filtered review queue
        """
        filtered_reviews = []
        
        for review_id, review_data in self.review_queue.items():
            # Apply filters
            if status and review_data.get('status') != status:
                continue
                
            if reviewer_id and reviewer_id not in review_data.get('assigned_reviewers', []):
                continue
            
            # Create summary for queue display
            review_summary = {
                'review_id': review_id,
                'destination': review_data['destination'],
                'quality_score': review_data['quality_score'],
                'priority': review_data['priority'],
                'status': review_data['status'],
                'submitted_at': review_data['submitted_at'],
                'affinity_count': review_data['metadata']['affinity_count'],
                'assigned_reviewers': review_data['assigned_reviewers'],
                'reviews_completed': len(review_data.get('reviews', [])),
                'estimated_review_time': self._estimate_review_time(review_data)
            }
            
            filtered_reviews.append(review_summary)
        
        # Sort by priority and submission time
        priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
        filtered_reviews.sort(key=lambda x: (
            priority_order.get(x['priority'], 2),
            x['submitted_at']
        ))
        
        return {
            'reviews': filtered_reviews,
            'total_count': len(filtered_reviews),
            'queue_timestamp': datetime.now().isoformat()
        }

    def get_feedback_analytics(self, destination: Optional[str] = None, 
                             days: int = 30) -> Dict[str, Any]:
        """
        Analyzes feedback patterns and quality improvement trends.

        Args:
            destination: Optional destination filter
            days: Number of days to analyze
            
        Returns:
            Dictionary containing feedback analytics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter reviews by date and destination
        filtered_reviews = []
        for review_data in self.review_queue.values():
            submitted_date = datetime.fromisoformat(review_data['submitted_at'])
            if submitted_date >= cutoff_date:
                if not destination or review_data['destination'] == destination:
                    if review_data.get('status') != ReviewStatus.PENDING.value:
                        filtered_reviews.append(review_data)
        
        if not filtered_reviews:
            return {'message': 'No completed reviews found for the specified criteria'}
        
        # Calculate analytics
        analytics = {
            'period_days': days,
            'destination_filter': destination,
            'analytics_generated_at': datetime.now().isoformat(),
            
            # Volume metrics
            'total_reviews': len(filtered_reviews),
            'auto_approved': sum(1 for r in filtered_reviews if r.get('final_decision', {}).get('status') == ReviewStatus.APPROVED.value),
            'human_reviewed': sum(1 for r in filtered_reviews if len(r.get('reviews', [])) > 0),
            'rejected': sum(1 for r in filtered_reviews if r.get('final_decision', {}).get('status') == ReviewStatus.REJECTED.value),
            
            # Quality metrics
            'avg_quality_score': statistics.mean([r['quality_score'] for r in filtered_reviews]),
            'quality_improvement': self._calculate_quality_improvement(filtered_reviews),
            
            # Review process metrics
            'avg_review_time_hours': statistics.mean([self._calculate_review_duration(r) for r in filtered_reviews if self._calculate_review_duration(r) > 0]),
            'reviewer_agreement_rate': self._calculate_reviewer_agreement(filtered_reviews),
            
            # Issue analysis
            'common_issues': self._analyze_common_issues(filtered_reviews),
            'improvement_suggestions': self._generate_improvement_suggestions(filtered_reviews),
            
            # Reviewer performance
            'reviewer_stats': self._analyze_reviewer_performance(filtered_reviews)
        }
        
        return analytics

    def _determine_review_path(self, quality_score: float, destination: str) -> Dict[str, Any]:
        """
        Determines the appropriate review path based on quality score and destination characteristics.
        """
        if quality_score >= self.auto_approve_threshold:
            return {
                'action': 'auto_approve',
                'reason': f'Quality score {quality_score:.3f} exceeds auto-approval threshold',
                'required_reviewers': 0,
                'review_criteria': []
            }
        
        if quality_score < self.require_review_threshold:
            # Low quality requires multiple reviewers
            return {
                'action': 'human_review',
                'reason': f'Quality score {quality_score:.3f} below review threshold',
                'required_reviewers': 2,
                'review_criteria': ['factual_accuracy', 'completeness', 'actionability', 'local_relevance']
            }
        
        # Medium quality requires single reviewer
        return {
            'action': 'human_review',
            'reason': f'Quality score {quality_score:.3f} requires validation',
            'required_reviewers': 1,
            'review_criteria': ['factual_accuracy', 'actionability']
        }

    def _assign_reviewers(self, review_data: dict) -> List[str]:
        """
        Assigns appropriate reviewers based on destination and review requirements.
        """
        required_count = review_data['required_reviewers']
        
        # In a real implementation, this would query a reviewer database
        # For now, simulate reviewer assignment
        available_reviewers = [
            'reviewer_subject_expert_001',
            'reviewer_editorial_002',
            'reviewer_local_expert_003',
            'reviewer_qa_004'
        ]
        
        # Simple assignment logic (in production, would consider expertise, availability, etc.)
        assigned = available_reviewers[:required_count]
        
        return assigned

    def _process_reviewer_feedback(self, feedback: Dict[str, Any], reviewer_id: str) -> Dict[str, Any]:
        """
        Processes and validates reviewer feedback.
        """
        processed = feedback.copy()
        
        # Ensure required fields
        processed.setdefault('decision', ReviewStatus.APPROVED.value)
        processed.setdefault('reviewer_role', ReviewerRole.QUALITY_ASSURANCE.value)
        processed.setdefault('review_time_minutes', 30)
        
        # Validate decision
        valid_decisions = [s.value for s in ReviewStatus]
        if processed['decision'] not in valid_decisions:
            processed['decision'] = ReviewStatus.APPROVED.value
        
        # Process specific feedback categories
        if 'category_scores' not in processed:
            processed['category_scores'] = {
                'factual_accuracy': feedback.get('factual_accuracy_score', 0.8),
                'completeness': feedback.get('completeness_score', 0.8),
                'actionability': feedback.get('actionability_score', 0.8),
                'local_relevance': feedback.get('local_relevance_score', 0.8)
            }
        
        return processed

    def _check_review_completion(self, review_data: dict) -> bool:
        """
        Checks if a review has received sufficient feedback to make a final decision.
        """
        required_reviewers = review_data['required_reviewers']
        completed_reviews = len(review_data.get('reviews', []))
        
        return completed_reviews >= required_reviewers

    def _make_final_decision(self, review_data: dict) -> Dict[str, Any]:
        """
        Makes final decision based on all reviewer feedback.
        """
        reviews = review_data.get('reviews', [])
        
        if not reviews:
            return {
                'status': ReviewStatus.REJECTED.value,
                'reason': 'No reviewer feedback received',
                'confidence': 0.0
            }
        
        # Count decisions
        decisions = [r['decision'] for r in reviews]
        decision_counts = defaultdict(int)
        for decision in decisions:
            decision_counts[decision] += 1
        
        # Simple majority rule
        majority_decision = max(decision_counts.items(), key=lambda x: x[1])
        
        # Calculate confidence based on agreement
        total_reviews = len(reviews)
        agreement_rate = majority_decision[1] / total_reviews
        
        # Calculate average category scores
        category_scores = defaultdict(list)
        for review in reviews:
            for category, score in review.get('feedback', {}).get('category_scores', {}).items():
                category_scores[category].append(score)
        
        avg_category_scores = {
            category: statistics.mean(scores) 
            for category, scores in category_scores.items()
        }
        
        return {
            'status': majority_decision[0],
            'reason': f'Majority decision from {total_reviews} reviewers',
            'confidence': agreement_rate,
            'reviewer_agreement': agreement_rate,
            'category_scores': avg_category_scores,
            'total_reviewers': total_reviews
        }

    def _store_feedback_for_learning(self, review_data: dict) -> None:
        """
        Stores feedback data for machine learning and pattern analysis.
        """
        destination = review_data['destination']
        
        # Store in feedback history
        feedback_entry = {
            'review_id': review_data['review_id'],
            'destination': destination,
            'quality_score': review_data['quality_score'],
            'final_decision': review_data.get('final_decision', {}),
            'reviews': review_data.get('reviews', []),
            'completed_at': review_data.get('completed_at'),
            'metadata': review_data.get('metadata', {})
        }
        
        self.feedback_history[destination].append(feedback_entry)
        
        # Update learning patterns
        final_status = review_data.get('final_decision', {}).get('status')
        if final_status == ReviewStatus.REJECTED.value:
            # Analyze common rejection reasons
            for review in review_data.get('reviews', []):
                comments = review.get('feedback', {}).get('comments', '')
                if comments:
                    # Simple keyword extraction (in production, would use NLP)
                    for issue in ['factual error', 'incomplete', 'not actionable', 'irrelevant']:
                        if issue in comments.lower():
                            self.learning_patterns['common_issues'][issue] += 1

    def _track_auto_approval(self, destination: str, quality_score: float) -> None:
        """
        Tracks auto-approval metrics.
        """
        self.quality_metrics['auto_approved'] += 1
        self.quality_metrics['total_reviews'] += 1

    def _update_reviewer_performance(self, reviewer_id: str, review_entry: dict) -> None:
        """
        Updates performance metrics for a reviewer.
        """
        perf = self.reviewer_performance[reviewer_id]
        perf['reviews_completed'] += 1
        
        # Update average review time
        review_time = review_entry.get('review_time_minutes', 30)
        current_avg = perf['avg_review_time']
        completed = perf['reviews_completed']
        perf['avg_review_time'] = ((current_avg * (completed - 1)) + review_time) / completed

    def _calculate_review_duration(self, review_data: dict) -> float:
        """
        Calculates total review duration in hours.
        """
        submitted_at = datetime.fromisoformat(review_data['submitted_at'])
        completed_at_str = review_data.get('completed_at')
        
        if not completed_at_str:
            return 0.0
        
        completed_at = datetime.fromisoformat(completed_at_str)
        duration = completed_at - submitted_at
        return duration.total_seconds() / 3600

    def _estimate_review_time(self, review_data: dict) -> int:
        """
        Estimates review time in minutes based on complexity.
        """
        base_time = 20  # Base review time in minutes
        affinity_count = review_data['metadata']['affinity_count']
        
        # Add time based on affinity count
        estimated_time = base_time + (affinity_count * 2)
        
        # Adjust for quality score (lower quality takes longer)
        quality_factor = 1.0 + (0.8 - review_data['quality_score'])
        estimated_time *= quality_factor
        
        return int(estimated_time)

    def _calculate_quality_improvement(self, reviews: List[dict]) -> float:
        """
        Calculates quality improvement over time.
        """
        if len(reviews) < 2:
            return 0.0
        
        # Sort by submission date
        sorted_reviews = sorted(reviews, key=lambda x: x['submitted_at'])
        
        # Compare first and last quartile
        n = len(sorted_reviews)
        first_quartile = sorted_reviews[:n//4] if n >= 4 else sorted_reviews[:1]
        last_quartile = sorted_reviews[-n//4:] if n >= 4 else sorted_reviews[-1:]
        
        avg_early = statistics.mean([r['quality_score'] for r in first_quartile])
        avg_recent = statistics.mean([r['quality_score'] for r in last_quartile])
        
        return avg_recent - avg_early

    def _calculate_reviewer_agreement(self, reviews: List[dict]) -> float:
        """
        Calculates inter-reviewer agreement rate.
        """
        multi_reviewer_cases = [r for r in reviews if len(r.get('reviews', [])) >= 2]
        
        if not multi_reviewer_cases:
            return 1.0  # No disagreement if no multi-reviewer cases
        
        agreement_scores = []
        for case in multi_reviewer_cases:
            decisions = [r['decision'] for r in case['reviews']]
            # Calculate agreement as percentage of reviewers with majority decision
            decision_counts = defaultdict(int)
            for decision in decisions:
                decision_counts[decision] += 1
            majority_count = max(decision_counts.values())
            agreement_rate = majority_count / len(decisions)
            agreement_scores.append(agreement_rate)
        
        return statistics.mean(agreement_scores)

    def _analyze_common_issues(self, reviews: List[dict]) -> Dict[str, int]:
        """
        Analyzes common issues from reviewer feedback.
        """
        # This is a simplified version - in production would use NLP
        return dict(self.learning_patterns['common_issues'])

    def _generate_improvement_suggestions(self, reviews: List[dict]) -> List[str]:
        """
        Generates improvement suggestions based on feedback patterns.
        """
        suggestions = []
        
        # Analyze rejection reasons
        rejected_reviews = [r for r in reviews if r.get('final_decision', {}).get('status') == ReviewStatus.REJECTED.value]
        
        if len(rejected_reviews) / len(reviews) > 0.2:
            suggestions.append("High rejection rate detected - consider improving initial quality thresholds")
        
        # Analyze quality score distribution
        quality_scores = [r['quality_score'] for r in reviews]
        if statistics.mean(quality_scores) < 0.7:
            suggestions.append("Average quality scores are low - consider enhancing LLM prompts or web discovery")
        
        # Analyze review time
        long_reviews = [r for r in reviews if self._calculate_review_duration(r) > 24]
        if len(long_reviews) / len(reviews) > 0.3:
            suggestions.append("Many reviews take over 24 hours - consider reviewer workload balancing")
        
        return suggestions

    def _analyze_reviewer_performance(self, reviews: List[dict]) -> Dict[str, Any]:
        """
        Analyzes reviewer performance statistics.
        """
        # Collect reviewer data from reviews
        reviewer_data = defaultdict(lambda: {
            'reviews_count': 0,
            'avg_review_time': 0,
            'decisions': defaultdict(int)
        })
        
        for review in reviews:
            for reviewer_feedback in review.get('reviews', []):
                reviewer_id = reviewer_feedback['reviewer_id']
                reviewer_data[reviewer_id]['reviews_count'] += 1
                reviewer_data[reviewer_id]['decisions'][reviewer_feedback['decision']] += 1
        
        return {
            'total_active_reviewers': len(reviewer_data),
            'avg_reviews_per_reviewer': statistics.mean([data['reviews_count'] for data in reviewer_data.values()]) if reviewer_data else 0,
            'reviewer_details': dict(reviewer_data)
        }

    def _error_result(self, message: str) -> Dict[str, Any]:
        """
        Returns error result structure.
        """
        return {
            'status': 'error',
            'error_message': message,
            'timestamp': datetime.now().isoformat()
        } 