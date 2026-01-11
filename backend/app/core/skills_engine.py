"""
Skills Engine

Manages loading, execution, and lifecycle of skills from the file system.
Skills are Python files with a standard interface that provide pre-built capabilities.
"""
import os
import sys
import importlib.util
import inspect
import json
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import time
import traceback

from app.core.logging import get_logger

logger = get_logger(__name__)


class SkillInterface:
    """Base interface that all skills must implement"""
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Return skill metadata including name, description, parameters, etc."""
        raise NotImplementedError("Skills must implement metadata property")
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute the skill with given parameters and context"""
        raise NotImplementedError("Skills must implement execute method")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate that parameters meet skill requirements"""
        return True


class SkillsEngine:
    """Engine for managing and executing skills"""
    
    def __init__(self, skills_directory: str = "backend/skills"):
        self.skills_directory = Path(skills_directory)
        self.loaded_skills: Dict[str, Any] = {}
        self.skill_cache: Dict[str, Dict[str, Any]] = {}
        
    def discover_skills(self) -> List[Dict[str, Any]]:
        """
        Discover all skills in the skills directory.
        Returns list of skill metadata.
        """
        skills = []
        
        if not self.skills_directory.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_directory}")
            return skills
        
        # Walk through all subdirectories
        for category_dir in self.skills_directory.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue
            
            category = category_dir.name
            
            # Find all Python files in category
            for skill_file in category_dir.glob("*.py"):
                if skill_file.name.startswith('_'):
                    continue
                
                try:
                    skill_info = self._load_skill_metadata(skill_file, category)
                    if skill_info:
                        skills.append(skill_info)
                except Exception as e:
                    logger.error(f"Error loading skill {skill_file}: {str(e)}")
        
        return skills
    
    def _load_skill_metadata(self, skill_file: Path, category: str) -> Optional[Dict[str, Any]]:
        """Load metadata from a skill file without executing it"""
        try:
            # Read file content
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file stats
            file_stats = skill_file.stat()
            
            # Load the module
            spec = importlib.util.spec_from_file_location(skill_file.stem, skill_file)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find skill class (should inherit from SkillInterface or have required methods)
            skill_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name != 'SkillInterface' and hasattr(obj, 'metadata') and hasattr(obj, 'execute'):
                    skill_class = obj
                    break
            
            if not skill_class:
                logger.warning(f"No valid skill class found in {skill_file}")
                return None
            
            # Instantiate and get metadata
            skill_instance = skill_class()
            metadata = skill_instance.metadata
            
            # Build skill info
            skill_info = {
                'name': skill_file.stem,
                'display_name': metadata.get('display_name', skill_file.stem.replace('_', ' ').title()),
                'description': metadata.get('description', ''),
                'category': category,
                'icon': metadata.get('icon', 'Code'),
                'version': metadata.get('version', '1.0.0'),
                'parameters': metadata.get('parameters', {}),
                'tags': metadata.get('tags', []),
                'file_path': str(skill_file.relative_to(self.skills_directory.parent)),
                'file_size': file_stats.st_size,
                'content_preview': content[:500] if len(content) > 500 else content,
                'is_premium': metadata.get('is_premium', False),
            }
            
            return skill_info
            
        except Exception as e:
            logger.error(f"Error loading skill metadata from {skill_file}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def load_skill(self, skill_path: str) -> Optional[Any]:
        """Load a skill from file path and cache it"""
        if skill_path in self.loaded_skills:
            return self.loaded_skills[skill_path]
        
        try:
            # Convert relative path to absolute
            if not os.path.isabs(skill_path):
                skill_path = os.path.join(os.getcwd(), skill_path)
            
            skill_file = Path(skill_path)
            if not skill_file.exists():
                logger.error(f"Skill file not found: {skill_path}")
                return None
            
            # Load the module
            spec = importlib.util.spec_from_file_location(skill_file.stem, skill_file)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate skill class
            skill_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name != 'SkillInterface' and hasattr(obj, 'metadata') and hasattr(obj, 'execute'):
                    skill_class = obj
                    break
            
            if not skill_class:
                logger.error(f"No valid skill class found in {skill_path}")
                return None
            
            skill_instance = skill_class()
            self.loaded_skills[skill_path] = skill_instance
            
            logger.info(f"Successfully loaded skill: {skill_path}")
            return skill_instance
            
        except Exception as e:
            logger.error(f"Error loading skill {skill_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def execute_skill(
        self,
        skill_path: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a skill with given parameters and context.
        Returns execution result with success status, result data, and timing.
        """
        start_time = time.time()
        
        try:
            # Load skill
            skill = self.load_skill(skill_path)
            if not skill:
                return {
                    'success': False,
                    'error': f'Failed to load skill: {skill_path}',
                    'execution_time': time.time() - start_time
                }
            
            # Validate parameters
            if hasattr(skill, 'validate_parameters'):
                if not skill.validate_parameters(parameters):
                    return {
                        'success': False,
                        'error': 'Invalid parameters provided',
                        'execution_time': time.time() - start_time
                    }
            
            # Execute skill
            context = context or {}
            result = skill.execute(parameters, context)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing skill {skill_path}: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'execution_time': execution_time
            }
    
    def get_skill_metadata(self, skill_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific skill"""
        skill = self.load_skill(skill_path)
        if skill and hasattr(skill, 'metadata'):
            return skill.metadata
        return None
    
    def reload_skill(self, skill_path: str) -> bool:
        """Reload a skill from disk (useful for development)"""
        try:
            # Remove from cache
            if skill_path in self.loaded_skills:
                del self.loaded_skills[skill_path]
            
            # Reload
            skill = self.load_skill(skill_path)
            return skill is not None
            
        except Exception as e:
            logger.error(f"Error reloading skill {skill_path}: {str(e)}")
            return False
    
    def validate_skill_file(self, skill_path: str) -> Dict[str, Any]:
        """
        Validate a skill file for correctness.
        Returns validation result with any errors or warnings.
        """
        errors = []
        warnings = []
        
        try:
            skill_file = Path(skill_path)
            
            # Check file exists
            if not skill_file.exists():
                errors.append(f"File not found: {skill_path}")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Check file extension
            if skill_file.suffix != '.py':
                errors.append("Skill file must be a Python file (.py)")
            
            # Try to load
            skill = self.load_skill(skill_path)
            if not skill:
                errors.append("Failed to load skill class")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
            
            # Check required methods
            if not hasattr(skill, 'metadata'):
                errors.append("Skill must have 'metadata' property")
            
            if not hasattr(skill, 'execute'):
                errors.append("Skill must have 'execute' method")
            
            # Validate metadata structure
            if hasattr(skill, 'metadata'):
                metadata = skill.metadata
                if not isinstance(metadata, dict):
                    errors.append("Metadata must be a dictionary")
                else:
                    # Check recommended fields
                    recommended_fields = ['display_name', 'description', 'version', 'parameters']
                    for field in recommended_fields:
                        if field not in metadata:
                            warnings.append(f"Recommended field '{field}' not found in metadata")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}


# Global skills engine instance
skills_engine = SkillsEngine()
