import subprocess
import tempfile
import os
import shutil
import uuid
import docker
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SandboxManager:
    """Secure sandboxed execution environment for actions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.docker_client = docker.from_env() if config.get('use_docker', True) else None
        self.sandbox_timeout = config.get('timeout_seconds', 30)
        self.max_memory = config.get('max_memory_mb', 512)
        
    def execute_in_sandbox(self, code: str, language: str, inputs: Dict[str, Any] = None) -> Tuple[bool, Any]:
        """Execute code in a secure sandboxed environment"""
        
        if inputs is None:
            inputs = {}
        
        try:
            if self.config.get('use_docker', True):
                return self._execute_in_docker_container(code, language, inputs)
            else:
                return self._execute_in_process(code, language, inputs)
                
        except Exception as e:
            logger.error(f"Sandbox execution failed: {str(e)}")
            return False, {"error": str(e), "type": "sandbox_error"}
    
    def _execute_in_docker_container(self, code: str, language: str, inputs: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute code in a Docker container for maximum isolation"""
        
        container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
        
        try:
            # Create a temporary directory for the execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write the code to a file
                code_file = temp_path / f"execution.{self._get_file_extension(language)}"
                code_file.write_text(code)
                
                # Write inputs to a JSON file
                input_file = temp_path / "inputs.json"
                input_file.write_text(self._serialize_inputs(inputs))
                
                # Create output directory
                output_dir = temp_path / "output"
                output_dir.mkdir()
                
                # Determine the appropriate Docker image based on language
                image_name = self._get_docker_image(language)
                
                # Run the container with strict resource limits
                container = self.docker_client.containers.run(
                    image=image_name,
                    command=self._get_execution_command(language, code_file.name, input_file.name),
                    working_dir="/app",
                    volumes={str(temp_path): {"bind": "/app", "mode": "rw"}},
                    detach=True,
                    name=container_name,
                    mem_limit=f"{self.max_memory}m",
                    cpu_period=100000,
                    cpu_quota=50000,
                    network_mode="none",
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges"],
                    read_only=True,
                    tmpfs={"/tmp": "exec,size=65536k"},
                    auto_remove=False
                )
                
                # Wait for execution with timeout
                exit_code = container.wait(timeout=self.sandbox_timeout)
                
                # Get logs
                logs = container.logs().decode('utf-8', errors='replace')
                
                # Read output
                output_file = output_dir / "output.json"
                if output_file.exists():
                    output = output_file.read_text()
                    result = self._parse_output(output)
                else:
                    result = {"stdout": logs, "stderr": ""}
                
                # Clean up
                container.remove(force=True)
                
                success = exit_code == 0
                return success, {
                    "success": success,
                    "result": result,
                    "logs": logs,
                    "exit_code": exit_code
                }
                
        except Exception as e:
            logger.error(f"Docker execution failed: {str(e)}")
            # Clean up container if it exists
            try:
                container = self.docker_client.containers.get(container_name)
                container.remove(force=True)
            except:
                pass
            return False, {"error": str(e), "type": "docker_error"}
    
    def _execute_in_process(self, code: str, language: str, inputs: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute code in a subprocess with resource limits"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write the code to a file
            code_file = temp_path / f"execution.{self._get_file_extension(language)}"
            code_file.write_text(code)
            
            # Write inputs to a JSON file
            input_file = temp_path / "inputs.json"
            input_file.write_text(self._serialize_inputs(inputs))
            
            # Create output directory
            output_dir = temp_path / "output"
            output_dir.mkdir()
            
            try:
                # Build the command based on language
                command = self._get_execution_command(language, code_file.name, input_file.name)
                
                # Execute with timeout
                result = subprocess.run(
                    command,
                    cwd=str(temp_path),
                    capture_output=True,
                    text=True,
                    timeout=self.sandbox_timeout,
                    shell=True
                )
                
                # Read output
                output_file = output_dir / "output.json"
                if output_file.exists():
                    output = output_file.read_text()
                    parsed_output = self._parse_output(output)
                else:
                    parsed_output = {"stdout": result.stdout, "stderr": result.stderr}
                
                success = result.returncode == 0
                return success, {
                    "success": success,
                    "result": parsed_output,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.returncode
                }
                
            except subprocess.TimeoutExpired:
                return False, {"error": "Execution timed out", "type": "timeout"}
            except Exception as e:
                return False, {"error": str(e), "type": "execution_error"}
    
    def _get_file_extension(self, language: str) -> str:
        """Get appropriate file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "csharp": "cs",
            "ruby": "rb",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "bash": "sh"
        }
        return extensions.get(language.lower(), "txt")
    
    def _get_docker_image(self, language: str) -> str:
        """Get appropriate Docker image for language"""
        images = {
            "python": "python:3.9-slim",
            "javascript": "node:18-alpine",
            "typescript": "node:18-alpine",
            "java": "openjdk:17-slim",
            "csharp": "mcr.microsoft.com/dotnet/sdk:6.0",
            "ruby": "ruby:3.2-slim",
            "go": "golang:1.20-alpine",
            "rust": "rust:1.70-slim",
            "php": "php:8.2-cli",
            "bash": "alpine:latest"
        }
        return images.get(language.lower(), "python:3.9-slim")
    
    def _get_execution_command(self, language: str, code_file: str, input_file: str) -> str:
        """Get execution command for specific language"""
        commands = {
            "python": f"python {code_file}",
            "javascript": f"node {code_file}",
            "typescript": f"npx ts-node {code_file}",
            "java": f"javac {code_file} && java {Path(code_file).stem}",
            "csharp": f"dotnet run {code_file}",
            "ruby": f"ruby {code_file}",
            "go": f"go run {code_file}",
            "rust": f"rustc {code_file} && ./{Path(code_file).stem}",
            "php": f"php {code_file}",
            "bash": f"bash {code_file}"
        }
        
        base_command = commands.get(language.lower(), f"python {code_file}")
        
        # Add input file environment variable
        return f"INPUT_FILE={input_file} OUTPUT_DIR=output {base_command}"
    
    def _serialize_inputs(self, inputs: Dict[str, Any]) -> str:
        """Serialize inputs to JSON"""
        import json
        return json.dumps(inputs, indent=2)
    
    def _parse_output(self, output: str) -> Any:
        """Parse output from execution"""
        import json
        try:
            return json.loads(output)
        except:
            return {"raw_output": output}
    
    def validate_code_safety(self, code: str) -> Tuple[bool, str]:
        """Validate code for potentially dangerous operations"""
        
        dangerous_patterns = [
            r"import\s+os",
            r"require\('os'\)",
            r"import\s+subprocess",
            r"require\('subprocess'\)",
            r"import\s+sys",
            r"require\('sys'\)",
            r"import\s+shutil",
            r"require\('shutil'\)",
            r"import\s+socket",
            r"require\('socket'\)",
            r"import\s+http",
            r"require\('http'\)",
            r"import\s+requests",
            r"require\('requests'\)",
            r"import\s+urllib",
            r"require\('urllib'\)",
            r"import\s+ftplib",
            r"require\('ftplib'\)",
            r"import\s+poplib",
            r"require\('poplib'\)",
            r"import\s+smtplib",
            r"require\('smtplib'\)",
            r"import\s+telnetlib",
            r"require\('telnetlib'\)",
            r"import\s+platform",
            r"require\('platform'\)",
            r"import\s+ctypes",
            r"require\('ctypes'\)",
            r"import\s+multiprocessing",
            r"require\('multiprocessing'\)",
            r"import\s+threading",
            r"require\('threading'\)",
            r"import\s+asyncio",
            r"require\('asyncio'\)",
            r"import\s+inspect",
            r"require\('inspect'\)",
            r"import\s+gc",
            r"require\('gc'\)",
            r"import\s+__import__",
            r"require\('__import__'\)",
            r"eval\(",
            r"exec\(",
            r"compile\(",
            r"open\(",
            r"file\.",
            r"\.to_file",
            r"\.write_file",
            r"\.save",
            r"\.dump",
            r"\.load",
            r"\.read",
            r"\.write",
            r"\.append",
            r"\.delete",
            r"\.remove",
            r"\.unlink",
            r"\.rmdir",
            r"\.mkdir",
            r"\.chmod",
            r"\.chown",
            r"\.rename",
            r"\.replace",
            r"\.symlink",
            r"\.copy",
            r"\.move",
            r"\.execute",
            r"\.run",
            r"\.system",
            r"\.popen",
            r"\.call",
            r"\.check_call",
            r"\.check_output"
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Potentially dangerous pattern detected: {pattern}"
        
        return True, "Code appears safe"
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        return {
            "max_memory_mb": self.max_memory,
            "timeout_seconds": self.sandbox_timeout,
            "execution_mode": "docker" if self.config.get('use_docker', True) else "process"
        }

# Singleton instance for easy access
sandbox_manager = None

def get_sandbox_manager(config: Dict[str, Any] = None):
    global sandbox_manager
    if sandbox_manager is None:
        if config is None:
            config = {
                "use_docker": True,
                "timeout_seconds": 30,
                "max_memory_mb": 512
            }
        sandbox_manager = SandboxManager(config)
    return sandbox_manager
