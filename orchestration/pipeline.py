from typing import Dict, Any, List
from agents.base import Agent
from .task_manager import TaskManager
import logging

class Pipeline:
    """Base class for orchestration pipelines."""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline with the given context."""
        pass

class CodeGenerationPipeline(Pipeline):
    def __init__(self, task_manager: TaskManager, agents: Dict[str, Agent]):
        super().__init__(task_manager)
        self.agents = agents

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Generate code
        builder_result = await self.task_manager.execute_task(
            self.agents["builder"].execute,
            context["user_request"]
        )
        
        if builder_result["status"] != "success":
            return builder_result
            
        generated_code = builder_result["result"]["code"]
        
        # Review code
        reviewer_result = await self.task_manager.execute_task(
            self.agents["reviewer"].execute,
            generated_code,
            context["user_request"]
        )
        
        if reviewer_result["status"] != "success":
            return reviewer_result
            
        review_feedback = reviewer_result["result"]
        
        # Test code
        test_result = await self.task_manager.execute_task(
            self.agents["tester"].execute,
            generated_code
        )
        
        if test_result["status"] == "success":
            return {
                "status": "success", 
                "code": generated_code,
                "tests": test_result["result"]["details"],
                "review": review_feedback
            }
        else:
            return {
                "status": "error",
                "message": f"Tests failed: {test_result.get('message', 'Unknown error')}",
                "code": generated_code,
                "review": review_feedback,
                "test_details": test_result.get('details', '')
            }