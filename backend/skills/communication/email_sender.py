"""
Email Sender Skill

Provides email sending capabilities with templates and attachments.
"""
from typing import Dict, Any, List, Optional
import json
import time
import re
from datetime import datetime

from app.core.skills_engine import SkillInterface


class EmailSenderSkill(SkillInterface):
    """Email sending skill for communication"""
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Return skill metadata"""
        return {
            'display_name': 'Email Sender',
            'description': 'Advanced email sending system that supports HTML templates, attachments, and batch sending with delivery tracking.',
            'category': 'communication',
            'icon': 'Mail',
            'version': '1.5.0',
            'parameters': {
                'emails': {
                    'type': 'array',
                    'description': 'List of email messages to send',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'to': {
                                'type': 'array',
                                'description': 'Recipient email addresses',
                                'items': {'type': 'string', 'format': 'email'}
                            },
                            'cc': {
                                'type': 'array',
                                'description': 'CC email addresses',
                                'items': {'type': 'string', 'format': 'email'}
                            },
                            'bcc': {
                                'type': 'array',
                                'description': 'BCC email addresses',
                                'items': {'type': 'string', 'format': 'email'}
                            },
                            'subject': {'type': 'string', 'description': 'Email subject'},
                            'body': {'type': 'string', 'description': 'Email body (plain text or HTML)'},
                            'is_html': {'type': 'boolean', 'description': 'Is body HTML?', 'default': False},
                            'template': {'type': 'string', 'description': 'Email template name (optional)'},
                            'template_variables': {
                                'type': 'object',
                                'description': 'Variables for template',
                                'additionalProperties': {'type': 'string'}
                            },
                            'attachments': {
                                'type': 'array',
                                'description': 'File attachments',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string', 'description': 'Attachment name'},
                                        'content': {'type': 'string', 'description': 'Base64 encoded content'},
                                        'mime_type': {'type': 'string', 'description': 'MIME type'}
                                    }
                                }
                            },
                            'priority': {'type': 'string', 'enum': ['low', 'normal', 'high'], 'default': 'normal'}
                        }
                    }
                },
                'sender': {
                    'type': 'object',
                    'description': 'Sender information',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Sender name'},
                        'email': {'type': 'string', 'format': 'email', 'description': 'Sender email'}
                    }
                },
                'smtp_config': {
                    'type': 'object',
                    'description': 'SMTP configuration',
                    'properties': {
                        'host': {'type': 'string', 'description': 'SMTP host'},
                        'port': {'type': 'integer', 'description': 'SMTP port', 'default': 587},
                        'username': {'type': 'string', 'description': 'SMTP username'},
                        'password': {'type': 'string', 'description': 'SMTP password', 'format': 'password'},
                        'use_ssl': {'type': 'boolean', 'description': 'Use SSL', 'default': False},
                        'use_tls': {'type': 'boolean', 'description': 'Use TLS', 'default': True}
                    }
                },
                'batch_size': {
                    'type': 'integer',
                    'description': 'Batch size for sending',
                    'minimum': 1,
                    'maximum': 100,
                    'default': 10
                },
                'delay_between_batches': {
                    'type': 'integer',
                    'description': 'Delay between batches in seconds',
                    'minimum': 0,
                    'maximum': 300,
                    'default': 5
                }
            },
            'tags': ['email', 'communication', 'messaging', 'smtp'],
            'is_premium': False
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters"""
        if 'emails' not in parameters or not parameters['emails']:
            return False
        
        if 'sender' not in parameters or 'email' not in parameters['sender']:
            return False
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Check sender email
        if not re.match(email_pattern, parameters['sender']['email']):
            return False
        
        # Check recipient emails
        for email in parameters['emails']:
            if 'to' in email:
                for recipient in email['to']:
                    if not re.match(email_pattern, recipient):
                        return False
            
            if 'cc' in email:
                for recipient in email['cc']:
                    if not re.match(email_pattern, recipient):
                        return False
            
            if 'bcc' in email:
                for recipient in email['bcc']:
                    if not re.match(email_pattern, recipient):
                        return False
        
        return True
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute email sending"""
        emails = parameters.get('emails', [])
        sender = parameters.get('sender', {})
        smtp_config = parameters.get('smtp_config', {})
        batch_size = parameters.get('batch_size', 10)
        delay_between_batches = parameters.get('delay_between_batches', 5)
        
        # Simulate email sending process
        results = []
        total_emails = 0
        
        # Process each email
        for i, email in enumerate(emails):
            # Apply template if specified
            processed_email = self._apply_template(email)
            
            # Validate email
            validation = self._validate_email(processed_email)
            if not validation['valid']:
                results.append({
                    'email_index': i,
                    'status': 'failed',
                    'error': validation['error'],
                    'recipients': processed_email.get('to', [])
                })
                continue
            
            # Simulate sending
            time.sleep(0.1)  # Simulate network delay
            
            # Generate delivery result
            delivery_result = self._simulate_delivery(processed_email, smtp_config)
            results.append(delivery_result)
            
            total_emails += len(processed_email.get('to', []))
            
            # Simulate batch processing
            if (i + 1) % batch_size == 0 and (i + 1) < len(emails):
                time.sleep(delay_between_batches)
        
        # Generate summary
        summary = self._generate_summary(results, total_emails)
        
        return {
            'success': True,
            'total_emails_sent': total_emails,
            'total_recipients': len(results),
            'batch_size': batch_size,
            'processing_time': time.time(),
            'results': results,
            'summary': summary
        }
    
    def _apply_template(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Apply email template if specified"""
        if 'template' in email and email['template']:
            # In a real implementation, this would load and apply a template
            # For simulation, we'll just add a template header
            template_name = email['template']
            template_vars = email.get('template_variables', {})
            
            # Simulate template application
            if 'body' in email:
                email['body'] = f"<!-- Template: {template_name} -->\n{email['body']}"
                
                # Replace template variables
                for var_name, var_value in template_vars.items():
                    email['body'] = email['body'].replace(f'{{{{{var_name}}}}}', str(var_value))
        
        return email
    
    def _validate_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email structure"""
        if 'to' not in email or not email['to']:
            return {'valid': False, 'error': 'No recipients specified'}
        
        if 'subject' not in email or not email['subject']:
            return {'valid': False, 'error': 'No subject specified'}
        
        if 'body' not in email or not email['body']:
            return {'valid': False, 'error': 'No body content specified'}
        
        return {'valid': True}
    
    def _simulate_delivery(self, email: Dict[str, Any], smtp_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate email delivery"""
        # Simulate different delivery outcomes
        outcomes = ['delivered', 'delivered', 'delivered', 'bounced', 'deferred']
        outcome = random.choice(outcomes)
        
        delivery_time = time.time() + random.uniform(0.5, 5.0)
        
        result = {
            'email_index': email.get('index', 0),
            'status': outcome,
            'recipients': email['to'],
            'subject': email['subject'],
            'delivery_time': delivery_time,
            'message_id': f"<{int(time.time())}.{random.randint(1000, 9999)}@email-sender>"
        }
        
        if outcome == 'bounced':
            result['error'] = random.choice(['Mailbox full', 'Invalid recipient', 'Domain not found'])
        elif outcome == 'deferred':
            result['retry_attempts'] = random.randint(1, 3)
            result['next_retry'] = delivery_time + 3600
        
        return result
    
    def _generate_summary(self, results: List[Dict[str, Any]], total_emails: int) -> Dict[str, Any]:
        """Generate delivery summary"""
        status_counts = {}
        for result in results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate success rate
        delivered = status_counts.get('delivered', 0)
        success_rate = (delivered / max(len(results), 1)) * 100
        
        return {
            'total_emails': total_emails,
            'total_recipients': len(results),
            'status_distribution': status_counts,
            'success_rate': round(success_rate, 2),
            'delivery_time_range': {
                'min': min(r['delivery_time'] for r in results),
                'max': max(r['delivery_time'] for r in results),
                'average': sum(r['delivery_time'] for r in results) / len(results)
            },
            'recommendations': self._generate_recommendations(status_counts)
        }
    
    def _generate_recommendations(self, status_counts: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on delivery results"""
        recommendations = []
        
        bounced = status_counts.get('bounced', 0)
        deferred = status_counts.get('deferred', 0)
        
        if bounced > 0:
            recommendations.append(f"Review {bounced} bounced emails and update recipient lists")
        
        if deferred > 0:
            recommendations.append(f"Monitor {deferred} deferred emails for final delivery status")
        
        if bounced > 5 or (bounced / max(len(status_counts), 1)) > 0.2:
            recommendations.append("Consider implementing email validation before sending")
        
        return recommendations


# Create instance for direct use
skill_instance = EmailSenderSkill()

if __name__ == "__main__":
    # Test the skill
    test_data = {
        'emails': [
            {
                'to': ['user1@example.com', 'user2@example.com'],
                'cc': ['manager@example.com'],
                'subject': 'Important Update',
                'body': 'Hello {name},\n\nThis is an important update regarding your account.\n\nBest regards',
                'is_html': False,
                'template': 'notification',
                'template_variables': {
                    'name': 'John Doe'
                },
                'priority': 'high'
            },
            {
                'to': ['support@example.com'],
                'subject': 'System Alert',
                'body': '<h1>System Alert</h1><p>This is an automated system alert.</p>',
                'is_html': True,
                'priority': 'high'
            }
        ],
        'sender': {
            'name': 'System Administrator',
            'email': 'admin@company.com'
        },
        'smtp_config': {
            'host': 'smtp.company.com',
            'port': 587,
            'use_tls': True
        },
        'batch_size': 5,
        'delay_between_batches': 2
    }
    
    result = skill_instance.execute(test_data, {})
    print("Email Sender Test Result:")
    print(json.dumps(result, indent=2, default=str))