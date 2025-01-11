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

# Create Celery tasks
celery_tasks = create_celery_tasks(celery_app)

def load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.yaml')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def main():
    try:
        # Load configuration
        config = load_config()
        
        # Initialize task manager
        task_manager = TaskManager(celery_app)
        
        # Initialize AI provider
        ai_provider = OpenAIProvider(
            api_key=config['ai_providers']['openai']['api_key'],
            model=config['ai_providers']['openai'].get('model', 'gpt-4')
        )
        
        # Initialize agents
        agents = {
            "builder": CodeBuilder(ai_provider, config['prompts']),
            "reviewer": CodeReviewer(ai_provider, config['prompts']),
            "tester": CodeTester(ai_provider, config['prompts'])
        }
        
        # Initialize pipeline
        pipeline = CodeGenerationPipeline(task_manager, agents)
        
        # Get user input
        user_request = input("Enter your coding request: ")
        
        # Execute pipeline
        result = await pipeline.execute({"user_request": user_request})
        
        # Handle result
        if result["status"] == "success":
            print("\nGenerated Code:")
            print(result["code"])
            print("\nTests:")
            print(result["tests"])
            print("\nCode Review:")
            print(result["review"])
        else:
            print(f"\nError: {result['message']}")
            if 'code' in result:
                print("\nPartial Code:")
                print(result["code"])
                
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
