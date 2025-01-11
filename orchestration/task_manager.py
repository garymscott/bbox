from typing import Any, Callable, Dict, Optional
from celery import Celery
import logging
import asyncio
from functools import partial

class TaskManager:
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app
        logging.info("TaskManager initialized with Celery app")

    async def execute_task(self, 
                          task_func: Callable, 
                          *args, 
                          timeout: int = 300,
                          **kwargs) -> Dict[str, Any]:
        """Execute a task asynchronously and return the result."""
        logging.info(f"Executing task: {task_func.__name__}")
        logging.info(f"Args: {args}")
        logging.info(f"Kwargs: {kwargs}")

        try:
            # Create Celery task
            task = self.celery_app.send_task(
                name=task_func.__name__,
                args=args,
                kwargs=kwargs
            )
            logging.info(f"Task enqueued with ID: {task.id}")

            # Wait for result
            result = await self._wait_for_result(task, timeout)
            
            if result is None:
                return {
                    "status": "error",
                    "message": f"Task timed out after {timeout} seconds"
                }

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            logging.error(f"Task execution error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _wait_for_result(self, 
                              task: 'AsyncResult', 
                              timeout: int) -> Optional[Any]:
        """Wait for task result with timeout."""
        try:
            # Convert the sync get() to async using run_in_executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(task.get, timeout=timeout)
            )
            return result
        except Exception as e:
            logging.error(f"Error waiting for task result: {e}")
            return None

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task."""
        try:
            result = self.celery_app.AsyncResult(task_id)
            return {
                "status": result.status,
                "result": result.result if result.ready() else None,
                "traceback": result.traceback if result.failed() else None,
            }
        except Exception as e:
            logging.error(f"Error getting task status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


def create_celery_tasks(celery_app: Celery):
    """Create Celery task decorators for our agent methods."""
    
    @celery_app.task(name="generate_code")
    def generate_code_task(*args, **kwargs):
        return args[0](*args[1:], **kwargs)

    @celery_app.task(name="review_code")
    def review_code_task(*args, **kwargs):
        return args[0](*args[1:], **kwargs)

    @celery_app.task(name="run_tests")
    def run_tests_task(*args, **kwargs):
        return args[0](*args[1:], **kwargs)

    return {
        "generate_code": generate_code_task,
        "review_code": review_code_task,
        "run_tests": run_tests_task
    }