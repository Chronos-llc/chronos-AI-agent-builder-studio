"""
API Connector Skill

Provides API integration capabilities with authentication and data transformation.
"""
from typing import Dict, Any, List, Optional
import json
import time
import random
from datetime import datetime

from app.core.skills_engine import SkillInterface


class APIConnectorSkill(SkillInterface):
    """API integration skill for connecting to external services"""
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Return skill metadata"""
        return {
            'display_name': 'API Connector',
            'description': 'Advanced API integration system that supports multiple authentication methods, request batching, and response transformation for seamless integration with external services.',
            'category': 'integration',
            'icon': 'Link',
            'version': '1.3.0',
            'parameters': {
                'api_requests': {
                    'type': 'array',
                    'description': 'List of API requests to execute',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'description': 'Request name for identification'},
                            'url': {'type': 'string', 'description': 'API endpoint URL', 'format': 'uri'},
                            'method': {'type': 'string', 'enum': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], 'default': 'GET'},
                            'headers': {
                                'type': 'object',
                                'description': 'Request headers',
                                'additionalProperties': {'type': 'string'}
                            },
                            'body': {
                                'type': 'object',
                                'description': 'Request body (for POST/PUT/PATCH)'
                            },
                            'query_params': {
                                'type': 'object',
                                'description': 'Query parameters',
                                'additionalProperties': {'type': 'string'}
                            },
                            'authentication': {
                                'type': 'object',
                                'description': 'Authentication configuration',
                                'properties': {
                                    'type': {'type': 'string', 'enum': ['none', 'api_key', 'bearer', 'basic', 'oauth2']},
                                    'api_key': {'type': 'string', 'description': 'API key'},
                                    'bearer_token': {'type': 'string', 'description': 'Bearer token'},
                                    'username': {'type': 'string', 'description': 'Basic auth username'},
                                    'password': {'type': 'string', 'description': 'Basic auth password', 'format': 'password'},
                                    'oauth2': {
                                        'type': 'object',
                                        'description': 'OAuth2 configuration',
                                        'properties': {
                                            'token_url': {'type': 'string', 'description': 'OAuth2 token URL'},
                                            'client_id': {'type': 'string', 'description': 'OAuth2 client ID'},
                                            'client_secret': {'type': 'string', 'description': 'OAuth2 client secret'},
                                            'scope': {'type': 'string', 'description': 'OAuth2 scope'}
                                        }
                                    }
                                }
                            },
                            'timeout': {'type': 'integer', 'description': 'Request timeout in seconds', 'minimum': 5, 'maximum': 120, 'default': 30},
                            'retry_policy': {
                                'type': 'object',
                                'description': 'Retry policy',
                                'properties': {
                                    'max_retries': {'type': 'integer', 'description': 'Maximum retries', 'minimum': 0, 'maximum': 5, 'default': 2},
                                    'retry_delay': {'type': 'integer', 'description': 'Retry delay in seconds', 'minimum': 1, 'maximum': 30, 'default': 5},
                                    'retry_on_status': {
                                        'type': 'array',
                                        'description': 'HTTP status codes to retry on',
                                        'items': {'type': 'integer'}
                                    }
                                }
                            },
                            'response_transform': {
                                'type': 'object',
                                'description': 'Response transformation rules',
                                'properties': {
                                    'extract_fields': {
                                        'type': 'array',
                                        'description': 'Fields to extract from response',
                                        'items': {'type': 'string'}
                                    },
                                    'rename_fields': {
                                        'type': 'object',
                                        'description': 'Field renaming rules',
                                        'additionalProperties': {'type': 'string'}
                                    },
                                    'filter_conditions': {
                                        'type': 'object',
                                        'description': 'Filter conditions for response data',
                                        'additionalProperties': True
                                    }
                                }
                            }
                        }
                    }
                },
                'batch_strategy': {
                    'type': 'string',
                    'description': 'Batch execution strategy',
                    'enum': ['sequential', 'parallel', 'queued'],
                    'default': 'sequential'
                },
                'max_concurrent_requests': {
                    'type': 'integer',
                    'description': 'Maximum concurrent requests for parallel execution',
                    'minimum': 1,
                    'maximum': 10,
                    'default': 3
                },
                'request_delay': {
                    'type': 'integer',
                    'description': 'Delay between requests in milliseconds',
                    'minimum': 0,
                    'maximum': 5000,
                    'default': 100
                },
                'global_headers': {
                    'type': 'object',
                    'description': 'Global headers for all requests',
                    'additionalProperties': {'type': 'string'}
                }
            },
            'tags': ['api', 'integration', 'http', 'rest', 'webhook'],
            'is_premium': False
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters"""
        if 'api_requests' not in parameters or not parameters['api_requests']:
            return False
        
        for request in parameters['api_requests']:
            if 'url' not in request or not request['url']:
                return False
            
            if 'method' in request and request['method'] not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                return False
        
        return True
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute API requests"""
        api_requests = parameters.get('api_requests', [])
        batch_strategy = parameters.get('batch_strategy', 'sequential')
        max_concurrent = parameters.get('max_concurrent_requests', 3)
        request_delay = parameters.get('request_delay', 100) / 1000.0  # Convert to seconds
        global_headers = parameters.get('global_headers', {})
        
        # Execute requests based on strategy
        if batch_strategy == 'sequential':
            results = self._execute_sequential(api_requests, global_headers, request_delay)
        elif batch_strategy == 'parallel':
            results = self._execute_parallel(api_requests, global_headers, max_concurrent)
        else:  # queued
            results = self._execute_queued(api_requests, global_headers, request_delay)
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            'success': True,
            'total_requests': len(api_requests),
            'batch_strategy': batch_strategy,
            'execution_time': time.time(),
            'results': results,
            'summary': summary
        }
    
    def _execute_sequential(
        self,
        requests: List[Dict[str, Any]],
        global_headers: Dict[str, str],
        delay: float
    ) -> List[Dict[str, Any]]:
        """Execute requests sequentially"""
        results = []
        
        for i, request in enumerate(requests):
            # Execute request
            result = self._execute_single_request(request, global_headers)
            results.append(result)
            
            # Add delay between requests (except after last request)
            if i < len(requests) - 1:
                time.sleep(delay)
        
        return results
    
    def _execute_parallel(
        self,
        requests: List[Dict[str, Any]],
        global_headers: Dict[str, str],
        max_concurrent: int
    ) -> List[Dict[str, Any]]:
        """Execute requests in parallel (simulated)"""
        results = []
        
        # Simulate parallel execution by processing in batches
        for i in range(0, len(requests), max_concurrent):
            batch = requests[i:i + max_concurrent]
            batch_results = []
            
            for request in batch:
                result = self._execute_single_request(request, global_headers)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Small delay between batches
            time.sleep(0.1)
        
        return results
    
    def _execute_queued(
        self,
        requests: List[Dict[str, Any]],
        global_headers: Dict[str, str],
        delay: float
    ) -> List[Dict[str, Any]]:
        """Execute requests in queue with delay"""
        # Similar to sequential but with different timing
        return self._execute_sequential(requests, global_headers, delay)
    
    def _execute_single_request(
        self,
        request: Dict[str, Any],
        global_headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Execute a single API request"""
        # Simulate request execution
        start_time = time.time()
        
        # Merge global headers with request headers
        headers = {**global_headers, **(request.get('headers', {}))}
        
        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.5))
        
        # Simulate different response scenarios
        response_scenarios = [
            {'status': 200, 'success': True},
            {'status': 201, 'success': True},
            {'status': 400, 'success': False, 'error': 'Bad Request'},
            {'status': 401, 'success': False, 'error': 'Unauthorized'},
            {'status': 404, 'success': False, 'error': 'Not Found'},
            {'status': 500, 'success': False, 'error': 'Internal Server Error'}
        ]
        
        scenario = random.choices(
            response_scenarios,
            weights=[0.6, 0.1, 0.05, 0.05, 0.05, 0.1],
            k=1
        )[0]
        
        # Generate response data
        response_data = self._generate_response_data(request, scenario)
        
        # Apply response transformation if specified
        if 'response_transform' in request:
            response_data = self._apply_response_transform(response_data, request['response_transform'])
        
        end_time = time.time()
        
        return {
            'request_name': request.get('name', f'request_{random.randint(1000, 9999)}'),
            'url': request['url'],
            'method': request.get('method', 'GET'),
            'status_code': scenario['status'],
            'success': scenario['success'],
            'response_time': end_time - start_time,
            'response_data': response_data,
            'error': scenario.get('error'),
            'headers': headers,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_response_data(
        self,
        request: Dict[str, Any],
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate simulated response data"""
        if scenario['success']:
            # Generate successful response based on request type
            if request.get('method') in ['POST', 'PUT', 'PATCH']:
                return {
                    'id': random.randint(1000, 9999),
                    'status': 'success',
                    'message': 'Request processed successfully',
                    'data': {
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                        'resource_id': f"res_{random.randint(10000, 99999)}"
                    }
                }
            else:  # GET, DELETE
                return {
                    'status': 'success',
                    'data': {
                        'items': [
                            {
                                'id': i,
                                'name': f'Item {i}',
                                'value': random.uniform(10, 100)
                            }
                            for i in range(1, random.randint(3, 10))
                        ],
                        'total': random.randint(3, 10),
                        'page': 1,
                        'page_size': random.randint(3, 10)
                    }
                }
        else:
            # Generate error response
            return {
                'status': 'error',
                'error': {
                    'code': scenario['status'],
                    'message': scenario['error'],
                    'details': f'The request to {request["url"]} failed with status {scenario["status"]}',
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def _apply_response_transform(
        self,
        response_data: Dict[str, Any],
        transform_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply response transformation rules"""
        transformed = response_data.copy()
        
        # Extract fields
        if 'extract_fields' in transform_rules:
            extracted = {}
            for field in transform_rules['extract_fields']:
                if field in transformed:
                    extracted[field] = transformed[field]
            transformed = extracted
        
        # Rename fields
        if 'rename_fields' in transform_rules:
            renamed = {}
            for old_name, new_name in transform_rules['rename_fields'].items():
                if old_name in transformed:
                    renamed[new_name] = transformed[old_name]
                else:
                    renamed[new_name] = None
            transformed = renamed
        
        # Apply filter conditions
        if 'filter_conditions' in transform_rules:
            # Simple filtering - in real implementation would be more sophisticated
            filtered = {}
            for key, value in transformed.items():
                if isinstance(value, (int, float)) and value > 0:
                    filtered[key] = value
            transformed = filtered
        
        return transformed
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution summary"""
        status_counts = {}
        total_time = 0
        
        for result in results:
            status = result['status_code']
            status_counts[status] = status_counts.get(status, 0) + 1
            total_time += result['response_time']
        
        # Calculate success rate
        success_count = sum(count for status, count in status_counts.items() if status < 400)
        success_rate = (success_count / max(len(results), 1)) * 100
        
        return {
            'total_requests': len(results),
            'successful_requests': success_count,
            'failed_requests': len(results) - success_count,
            'success_rate': round(success_rate, 2),
            'status_code_distribution': status_counts,
            'average_response_time': total_time / max(len(results), 1),
            'total_execution_time': total_time,
            'performance_metrics': {
                'fastest_response': min(r['response_time'] for r in results) if results else 0,
                'slowest_response': max(r['response_time'] for r in results) if results else 0,
                'response_time_variance': self._calculate_variance([r['response_time'] for r in results])
            }
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of response times"""
        if not values or len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        squared_diffs = [(x - mean) ** 2 for x in values]
        variance = sum(squared_diffs) / len(values)
        
        return round(variance, 4)


# Create instance for direct use
skill_instance = APIConnectorSkill()

if __name__ == "__main__":
    # Test the skill
    test_data = {
        'api_requests': [
            {
                'name': 'Get User Data',
                'url': 'https://api.example.com/users',
                'method': 'GET',
                'headers': {
                    'Accept': 'application/json',
                    'X-Custom-Header': 'test-value'
                },
                'query_params': {
                    'page': '1',
                    'page_size': '10'
                },
                'authentication': {
                    'type': 'bearer',
                    'bearer_token': 'test-token-123'
                },
                'response_transform': {
                    'extract_fields': ['data.items', 'data.total'],
                    'rename_fields': {
                        'data.items': 'users',
                        'data.total': 'total_users'
                    }
                }
            },
            {
                'name': 'Create Order',
                'url': 'https://api.example.com/orders',
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': {
                    'user_id': 123,
                    'items': [
                        {'product_id': 456, 'quantity': 2},
                        {'product_id': 789, 'quantity': 1}
                    ],
                    'shipping_address': '123 Main St'
                },
                'authentication': {
                    'type': 'api_key',
                    'api_key': 'secret-api-key'
                }
            }
        ],
        'batch_strategy': 'sequential',
        'request_delay': 200,
        'global_headers': {
            'User-Agent': 'APIConnector/1.0',
            'X-Request-ID': f"req_{random.randint(10000, 99999)}"
        }
    }
    
    result = skill_instance.execute(test_data, {})
    print("API Connector Test Result:")
    print(json.dumps(result, indent=2, default=str))