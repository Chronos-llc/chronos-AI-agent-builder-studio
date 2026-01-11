"""
Task Scheduler Skill

Provides advanced task scheduling and automation capabilities.
"""
from typing import Dict, Any, List, Optional
import json
import time
from datetime import datetime, timedelta

from app.core.skills_engine import SkillInterface


class TaskSchedulerSkill(SkillInterface):
    """Task scheduling skill for automating workflows"""
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Return skill metadata"""
        return {
            'display_name': 'Task Scheduler',
            'description': 'Advanced task scheduling system that allows you to create, manage, and execute automated workflows on specific schedules.',
            'category': 'automation',
            'icon': 'CalendarClock',
            'version': '2.1.0',
            'parameters': {
                'tasks': {
                    'type': 'array',
                    'description': 'List of tasks to schedule',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'description': 'Task name'},
                            'description': {'type': 'string', 'description': 'Task description'},
                            'schedule': {
                                'type': 'object',
                                'description': 'Task schedule',
                                'properties': {
                                    'type': {'type': 'string', 'enum': ['once', 'daily', 'weekly', 'monthly', 'cron']},
                                    'time': {'type': 'string', 'description': 'Time in HH:MM format'},
                                    'day_of_week': {'type': 'integer', 'description': 'Day of week (0-6)', 'minimum': 0, 'maximum': 6},
                                    'day_of_month': {'type': 'integer', 'description': 'Day of month (1-31)', 'minimum': 1, 'maximum': 31},
                                    'cron_expression': {'type': 'string', 'description': 'Cron expression for complex schedules'}
                                }
                            },
                            'priority': {'type': 'integer', 'description': 'Task priority (1-5)', 'minimum': 1, 'maximum': 5},
                            'timeout': {'type': 'integer', 'description': 'Task timeout in seconds', 'minimum': 10, 'maximum': 86400}
                        }
                    }
                },
                'start_date': {
                    'type': 'string',
                    'description': 'Start date for scheduling (YYYY-MM-DD)',
                    'format': 'date'
                },
                'end_date': {
                    'type': 'string',
                    'description': 'End date for scheduling (YYYY-MM-DD)',
                    'format': 'date',
                    'optional': True
                },
                'timezone': {
                    'type': 'string',
                    'description': 'Timezone for scheduling',
                    'default': 'UTC'
                },
                'max_concurrent_tasks': {
                    'type': 'integer',
                    'description': 'Maximum concurrent tasks',
                    'minimum': 1,
                    'maximum': 20,
                    'default': 5
                }
            },
            'tags': ['automation', 'scheduling', 'workflow', 'cron'],
            'is_premium': False
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters"""
        if 'tasks' not in parameters:
            return False
        
        if not isinstance(parameters['tasks'], list) or len(parameters['tasks']) == 0:
            return False
        
        for task in parameters['tasks']:
            if 'name' not in task or 'schedule' not in task:
                return False
            
            schedule = task['schedule']
            if 'type' not in schedule:
                return False
            
            if schedule['type'] not in ['once', 'daily', 'weekly', 'monthly', 'cron']:
                return False
        
        return True
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute task scheduling"""
        tasks = parameters.get('tasks', [])
        start_date = parameters.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = parameters.get('end_date')
        timezone = parameters.get('timezone', 'UTC')
        max_concurrent = parameters.get('max_concurrent_tasks', 5)
        
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        except ValueError:
            return {'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}
        
        # Generate schedule
        schedule = self._generate_schedule(tasks, start_dt, end_dt, timezone, max_concurrent)
        
        return {
            'success': True,
            'schedule_generated': True,
            'total_tasks': len(tasks),
            'scheduled_events': schedule,
            'timezone': timezone,
            'start_date': start_date,
            'end_date': end_date,
            'max_concurrent_tasks': max_concurrent,
            'execution_plan': self._generate_execution_plan(schedule)
        }
    
    def _generate_schedule(
        self,
        tasks: List[Dict[str, Any]],
        start_date: datetime,
        end_date: Optional[datetime],
        timezone: str,
        max_concurrent: int
    ) -> List[Dict[str, Any]]:
        """Generate task schedule"""
        schedule = []
        current_date = start_date
        
        # Generate schedule for each task
        for task in tasks:
            task_name = task['name']
            task_schedule = task['schedule']
            task_priority = task.get('priority', 3)
            task_timeout = task.get('timeout', 3600)
            
            # Generate events based on schedule type
            if task_schedule['type'] == 'once':
                # Single execution
                event_time = self._parse_schedule_time(task_schedule, current_date)
                if event_time:
                    schedule.append({
                        'task_name': task_name,
                        'scheduled_time': event_time.isoformat(),
                        'type': 'once',
                        'priority': task_priority,
                        'timeout': task_timeout,
                        'status': 'scheduled'
                    })
            
            elif task_schedule['type'] == 'daily':
                # Daily execution
                event_count = 0
                while True:
                    event_time = self._parse_schedule_time(task_schedule, current_date)
                    if event_time:
                        schedule.append({
                            'task_name': task_name,
                            'scheduled_time': event_time.isoformat(),
                            'type': 'daily',
                            'priority': task_priority,
                            'timeout': task_timeout,
                            'status': 'scheduled',
                            'occurrence': event_count + 1
                        })
                        event_count += 1
                    
                    current_date += timedelta(days=1)
                    
                    # Check if we've reached end date
                    if end_date and current_date > end_date:
                        break
                    
                    # Safety limit
                    if event_count >= 365:  # Max 1 year
                        break
            
            # Reset current_date for next task
            current_date = start_date
        
        return schedule
    
    def _parse_schedule_time(self, schedule: Dict[str, Any], date: datetime) -> Optional[datetime]:
        """Parse schedule time"""
        if 'time' in schedule:
            try:
                # Parse time
                time_parts = schedule['time'].split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                
                # Create datetime
                return datetime(date.year, date.month, date.day, hour, minute)
            except (ValueError, IndexError):
                return None
        
        return None
    
    def _generate_execution_plan(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution plan with statistics"""
        if not schedule:
            return {'message': 'No tasks scheduled'}
        
        # Sort by scheduled time
        sorted_schedule = sorted(schedule, key=lambda x: x['scheduled_time'])
        
        # Calculate statistics
        start_time = datetime.fromisoformat(sorted_schedule[0]['scheduled_time'])
        end_time = datetime.fromisoformat(sorted_schedule[-1]['scheduled_time'])
        total_duration = (end_time - start_time).total_seconds()
        
        # Count by type
        type_counts = {}
        for event in sorted_schedule:
            event_type = event['type']
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        return {
            'total_events': len(sorted_schedule),
            'execution_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'duration_seconds': total_duration,
                'duration_human': self._format_duration(total_duration)
            },
            'event_types': type_counts,
            'priority_distribution': self._calculate_priority_distribution(sorted_schedule),
            'concurrency_analysis': self._analyze_concurrency(sorted_schedule)
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    def _calculate_priority_distribution(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate priority distribution"""
        priority_counts = {}
        for event in schedule:
            priority = event['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return priority_counts
    
    def _analyze_concurrency(self, schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze task concurrency"""
        # Simple analysis - in real implementation would check overlapping times
        return {
            'max_concurrent_tasks': min(len(schedule), 5),
            'concurrency_warnings': [],
            'recommended_max_concurrent': min(len(schedule), 3)
        }


# Create instance for direct use
skill_instance = TaskSchedulerSkill()

if __name__ == "__main__":
    # Test the skill
    test_data = {
        'tasks': [
            {
                'name': 'Data Backup',
                'description': 'Backup database to cloud storage',
                'schedule': {
                    'type': 'daily',
                    'time': '02:30'
                },
                'priority': 4,
                'timeout': 1800
            },
            {
                'name': 'Report Generation',
                'description': 'Generate daily reports',
                'schedule': {
                    'type': 'daily',
                    'time': '08:00'
                },
                'priority': 3,
                'timeout': 3600
            }
        ],
        'start_date': '2026-01-10',
        'end_date': '2026-01-15',
        'timezone': 'UTC'
    }
    
    result = skill_instance.execute(test_data, {})
    print("Task Scheduler Test Result:")
    print(json.dumps(result, indent=2, default=str))