from typing import Dict, Any, List
from .base import Agent
import os
import logging
import subprocess
import json

class CodeTester(Agent):
    def __init__(self, ai_provider: 'AIProvider', prompts: Dict[str, Any], docker_image: str = "python:3.9-slim"):
        super().__init__(ai_provider, prompts)
        self.docker_image = docker_image

    async def execute(self, code: str) -> Dict[str, Any]:
        """Generate and run tests for the provided code."""
        try:
            # Generate test cases
            test_code = await self._generate_tests(code)
            
            # Run the tests
            test_result = await self._run_tests(code, test_code)
            return test_result
            
        except Exception as e:
            logging.error(f"Testing error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _generate_tests(self, code: str) -> str:
        """Generate test cases for the provided code."""
        prompt = self._construct_test_prompt(code)
        
        try:
            test_code = await self.ai.complete(
                prompt=prompt,
                system_prompt="You are a Python testing expert."
            )
            return test_code
        except Exception as e:
            logging.error(f"Test generation error: {e}")
            raise

    async def _run_tests(self, code: str, test_code: str) -> Dict[str, Any]:
        """Run the provided tests in a Docker container."""
        try:
            # Define absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.join(base_dir, "app")
            
            # Create app directory if it doesn't exist
            os.makedirs(app_dir, exist_ok=True)
            
            # Save code and tests to files in the app directory
            code_path = os.path.join(app_dir, "generated_code.py")
            test_path = os.path.join(app_dir, "test_generated_code.py")
            
            with open(code_path, "w") as f:
                f.write(code)

            with open(test_path, "w") as f:
                f.write(test_code)

            # Generate requirements.txt in app directory
            libraries = self._extract_imports(code)
            req_path = os.path.join(app_dir, "requirements.txt")
            self._generate_requirements(libraries)

            # Run the Docker container
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{app_dir}:/app",
                    self.docker_image,
                    "pytest",
                    "-vv",
                    "--maxfail=0",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            logging.info("STDOUT:\n" + result.stdout)
            logging.info("STDERR:\n" + result.stderr)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "details": result.stdout
                }
            else:
                failures = self._parse_test_failures(result.stdout)
                return {
                    "status": "failed",
                    "failures": failures,
                    "details": result.stdout
                }
                
        except subprocess.SubprocessError as e:
            logging.error(f"Docker subprocess error: {e}")
            return {
                "status": "error",
                "message": f"Docker execution failed: {str(e)}"
            }
        except Exception as e:
            logging.error(f"Test execution error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _construct_test_prompt(self, code: str) -> str:
        return (
            f"{self.prompts['generate_tests']['description']}\n\n"
            f"{code}\n\n"
            f"{self.prompts['generate_tests']['instructions']}"
        )

    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from the code."""
        import_lines = []
        for line in code.split('\n'):
            if line.startswith('import ') or line.startswith('from '):
                package = line.split()[1].split('.')[0]
                if package not in ['pytest', 'unittest']:
                    import_lines.append(package)
        return list(set(import_lines))

    def _generate_requirements(self, libraries: List[str]) -> None:
        """Generate requirements.txt file from extracted imports."""
        requirements = ['pytest'] + libraries  # Always include pytest
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "requirements.txt"), "w") as f:
            f.write('\n'.join(requirements))

    def _parse_test_failures(self, output: str) -> List[Dict[str, str]]:
        """Parse pytest output to extract test failures."""
        failures = []
        current_failure = None
        
        for line in output.split('\n'):
            if line.startswith('FAILED '):
                if current_failure:
                    failures.append(current_failure)
                current_failure = {'test': line.split(' ')[1], 'message': ''}
            elif current_failure and line.strip():
                current_failure['message'] += line + '\n'
                
        if current_failure:
            failures.append(current_failure)
            
        return failures
