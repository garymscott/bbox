import os
import yaml
import logging
from celery import Celery
from ai import OpenAIProvider
from agents import CodeBuilder, CodeReviewer, CodeTester
from orchestration import TaskManager, create_celery_tasks, CodeGenerationPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Celery
celery_app = Celery(
    "code_generation",
    broker="pyamqp://guest:guest@localhost//",
    backend="rpc://"
)

# Configure Celery
celery_app.conf.update(
    worker_pool='solo',  # For Windows compatibility
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
