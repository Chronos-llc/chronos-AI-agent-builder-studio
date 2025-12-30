import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import traceback
import re

logger = logging.getLogger(__name__)

class Debugger:
    """Comprehensive debugging and logging system for actions and hooks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_directory = Path(config.get('log_directory', 'logs'))
        self.log_directory.mkdir(exist_ok=True)
        self.max_log_size = config.get('max_log_size_mb', 10)
        self.max_log_files = config.get('max_log_files', 100)
        
    def log_execution(self, execution_id: str, action_name: str, 
                     code: str, inputs: Dict[str, Any], 
                     result: Any, error: Optional[str] = None) -> Dict[str, Any]:
        """Log an execution with comprehensive details"""
        
        log_entry = {
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action_name": action_name,
            "inputs": inputs,
            "code": code,
            "result": result,
            "error": error,
            "success": error is None
        }
        
        # Write to file
        log_file = self._get_log_file()
        self._write_log_entry(log_file, log_entry)
        
        # Clean up old logs
        self._rotate_logs()
        
        return log_entry
    
    def _get_log_file(self) -> Path:
        """Get the current log file path"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_directory / f"execution_{today}.log"
    
    def _write_log_entry(self, log_file: Path, entry: Dict[str, Any]):
        """Write a log entry to file"""
        try:
            with log_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(entry, indent=2, ensure_ascii=False))
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to write log entry: {str(e)}")
    
    def _rotate_logs(self):
        """Rotate logs to prevent excessive disk usage"""
        try:
            # Get all log files sorted by modification time
            log_files = sorted(self.log_directory.glob("*.log"), 
                              key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Delete oldest files if we exceed the limit
            if len(log_files) > self.max_log_files:
                for log_file in log_files[self.max_log_files:]:
                    log_file.unlink()
            
            # Check current log file size
            current_log = self._get_log_file()
            if current_log.exists() and current_log.stat().st_size > self.max_log_size * 1024 * 1024:
                # Rotate current log
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_file = self.log_directory / f"execution_{timestamp}.log"
                current_log.rename(rotated_file)
                
        except Exception as e:
            logger.error(f"Log rotation failed: {str(e)}")
    
    def get_execution_logs(self, execution_id: Optional[str] = None, 
                          action_name: Optional[str] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve execution logs with filtering options"""
        
        logs = []
        
        # Read all log files
        log_files = sorted(self.log_directory.glob("*.log"), reverse=True)
        
        for log_file in log_files:
            try:
                with log_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                
                                # Apply filters
                                if execution_id and entry.get('execution_id') != execution_id:
                                    continue
                                if action_name and entry.get('action_name') != action_name:
                                    continue
                                
                                logs.append(entry)
                                
                                if len(logs) >= limit:
                                    return logs
                                    
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {str(e)}")
                continue
        
        return logs
    
    def get_execution_by_id(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific execution by ID"""
        
        log_files = sorted(self.log_directory.glob("*.log"), reverse=True)
        
        for log_file in log_files:
            try:
                with log_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                if entry.get('execution_id') == execution_id:
                                    return entry
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {str(e)}")
                continue
        
        return None
    
    def analyze_execution(self, execution_id: str) -> Dict[str, Any]:
        """Analyze an execution and provide debugging insights"""
        
        execution = self.get_execution_by_id(execution_id)
        if not execution:
            return {"error": "Execution not found"}
        
        analysis = {
            "execution_id": execution_id,
            "timestamp": execution.get("timestamp"),
            "action_name": execution.get("action_name"),
            "success": execution.get("success", False),
            "performance": self._analyze_performance(execution),
            "code_quality": self._analyze_code_quality(execution.get("code", "")),
            "error_analysis": None,
            "recommendations": []
        }
        
        if not analysis["success"]:
            analysis["error_analysis"] = self._analyze_error(execution.get("error", ""))
            analysis["recommendations"] = self._generate_recommendations(execution)
        
        return analysis
    
    def _analyze_performance(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze execution performance"""
        
        # This would be enhanced with actual timing data in a real implementation
        return {
            "execution_time_ms": "N/A",  # Would be captured in actual execution
            "memory_usage_mb": "N/A",    # Would be captured in actual execution
            "cpu_usage_percent": "N/A"    # Would be captured in actual execution
        }
    
    def _analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality and potential issues"""
        
        issues = []
        
        # Check for common code quality issues
        if len(code.split('\n')) > 200:
            issues.append("Code is very long - consider breaking into smaller functions")
        
        if len(code) > 5000:
            issues.append("Code size exceeds recommended limit")
        
        # Check for hardcoded credentials (simple pattern)
        credential_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Potential hardcoded credential detected: {pattern}")
        
        # Check for excessive nesting
        if code.count('    ') > 50:  # More than 50 indentations
            issues.append("Code has excessive nesting - consider refactoring")
        
        return {
            "issues_found": len(issues),
            "issues": issues,
            "code_length": len(code),
            "line_count": len(code.split('\n'))
        }
    
    def _analyze_error(self, error: str) -> Dict[str, Any]:
        """Analyze error details"""
        
        if not error:
            return {"error": "No error information available"}
        
        error_type = "unknown"
        error_message = error
        
        # Try to extract more detailed error information
        if "SyntaxError" in error:
            error_type = "syntax_error"
        elif "NameError" in error:
            error_type = "name_error"
        elif "TypeError" in error:
            error_type = "type_error"
        elif "ValueError" in error:
            error_type = "value_error"
        elif "ImportError" in error:
            error_type = "import_error"
        elif "ModuleNotFoundError" in error:
            error_type = "module_not_found"
        elif "RuntimeError" in error:
            error_type = "runtime_error"
        elif "MemoryError" in error:
            error_type = "memory_error"
        elif "TimeoutError" in error:
            error_type = "timeout_error"
        
        # Extract line numbers if available
        line_match = re.search(r"line\s+(\d+)", error)
        line_number = int(line_match.group(1)) if line_match else None
        
        return {
            "error_type": error_type,
            "error_message": error_message,
            "line_number": line_number,
            "suggested_fix": self._suggest_fix(error_type, error_message)
        }
    
    def _suggest_fix(self, error_type: str, error_message: str) -> str:
        """Suggest fixes for common error types"""
        
        suggestions = {
            "syntax_error": "Check your code syntax and fix any indentation, missing brackets, or typos.",
            "name_error": "Check that all variables and functions are properly defined before use.",
            "type_error": "Verify that you're passing the correct data types to functions and operations.",
            "value_error": "Check that your input values are valid for the expected operations.",
            "import_error": "Verify that the module you're trying to import exists and is installed.",
            "module_not_found": "Install the required module using pip or your package manager.",
            "runtime_error": "Check for logical errors in your code execution flow.",
            "memory_error": "Optimize your code to use less memory or increase memory limits.",
            "timeout_error": "Optimize your code for better performance or increase timeout limits."
        }
        
        return suggestions.get(error_type, "Check the error message and your code logic carefully.")
    
    def _generate_recommendations(self, execution: Dict[str, Any]) -> List[str]:
        """Generate debugging recommendations"""
        
        recommendations = []
        
        # Basic recommendations
        recommendations.append("Review the error message and stack trace carefully")
        recommendations.append("Check your input parameters and data types")
        recommendations.append("Validate that all required dependencies are available")
        
        # Code-specific recommendations
        code = execution.get("code", "")
        if "import" in code and "ImportError" in str(execution.get("error", "")):
            recommendations.append("Verify that all imported modules are installed in the execution environment")
        
        if len(code.split('\n')) > 100:
            recommendations.append("Consider breaking down complex code into smaller, testable functions")
        
        # Add language-specific recommendations
        language = self._detect_language(code)
        if language == "python":
            recommendations.append("Use Python's built-in debugging tools like pdb or logging module")
        elif language == "javascript":
            recommendations.append("Use console.log() for debugging or Node.js debugger")
        
        return recommendations
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        
        if code.startswith("#!/usr/bin/env python") or "import " in code and "def " in code:
            return "python"
        elif code.startswith("#!/usr/bin/env node") or "require(" in code or "const " in code:
            return "javascript"
        elif "public class " in code or "System.out.println" in code:
            return "java"
        elif "using System;" in code or "Console.WriteLine" in code:
            return "csharp"
        elif "<?php" in code:
            return "php"
        elif "package main" in code or "import (" in code:
            return "go"
        
        return "unknown"
    
    def create_debug_session(self, action_name: str, code: str) -> Dict[str, Any]:
        """Create a new debug session"""
        
        session_id = str(uuid.uuid4())
        
        debug_session = {
            "session_id": session_id,
            "action_name": action_name,
            "code": code,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "breakpoints": [],
            "watch_expressions": [],
            "variables": {}
        }
        
        # Store debug session
        session_file = self.log_directory / f"debug_{session_id}.json"
        with session_file.open('w', encoding='utf-8') as f:
            json.dump(debug_session, f, indent=2)
        
        return debug_session
    
    def update_debug_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update a debug session"""
        
        session_file = self.log_directory / f"debug_{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            with session_file.open('r', encoding='utf-8') as f:
                session = json.load(f)
            
            session.update(updates)
            
            with session_file.open('w', encoding='utf-8') as f:
                json.dump(session, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update debug session: {str(e)}")
            return False
    
    def get_debug_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a debug session by ID"""
        
        session_file = self.log_directory / f"debug_{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with session_file.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read debug session: {str(e)}")
            return None
    
    def search_logs(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search logs using a query string"""
        
        results = []
        
        # Simple text search implementation
        log_files = sorted(self.log_directory.glob("*.log"), reverse=True)
        
        for log_file in log_files:
            try:
                with log_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip() and query.lower() in line.lower():
                            try:
                                entry = json.loads(line)
                                results.append(entry)
                                
                                if len(results) >= limit:
                                    return results
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Failed to search log file {log_file}: {str(e)}")
                continue
        
        return results
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about logging activity"""
        
        stats = {
            "total_log_files": 0,
            "total_executions": 0,
            "success_rate": 0.0,
            "error_count": 0,
            "first_execution": None,
            "last_execution": None
        }
        
        log_files = sorted(self.log_directory.glob("*.log"), reverse=True)
        stats["total_log_files"] = len(log_files)
        
        if not log_files:
            return stats
        
        total_executions = 0
        error_count = 0
        first_timestamp = None
        last_timestamp = None
        
        for log_file in log_files:
            try:
                with log_file.open('r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                total_executions += 1
                                
                                if not entry.get("success", True):
                                    error_count += 1
                                
                                timestamp = entry.get("timestamp")
                                if timestamp:
                                    if not first_timestamp or timestamp < first_timestamp:
                                        first_timestamp = timestamp
                                    if not last_timestamp or timestamp > last_timestamp:
                                        last_timestamp = timestamp
                                        
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {str(e)}")
                continue
        
        stats["total_executions"] = total_executions
        stats["error_count"] = error_count
        stats["first_execution"] = first_timestamp
        stats["last_execution"] = last_timestamp
        
        if total_executions > 0:
            stats["success_rate"] = (total_executions - error_count) / total_executions
        
        return stats

# Singleton instance for easy access
debugger_instance = None

def get_debugger(config: Dict[str, Any] = None):
    global debugger_instance
    if debugger_instance is None:
        if config is None:
            config = {
                "log_directory": "logs",
                "max_log_size_mb": 10,
                "max_log_files": 100
            }
        debugger_instance = Debugger(config)
    return debugger_instance