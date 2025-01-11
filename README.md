# bbox

A modular AI-powered code generation and testing pipeline.

## Overview

This project provides a flexible framework for generating, reviewing, and testing code using various AI providers (OpenAI, Gemini, Claude).

## Features

- Modular AI provider integration
- Code generation
- Automated code review
- Test generation and execution
- Docker-based test isolation
- Async task processing with Celery

## Installation

```bash
pip install -r requirements.txt
```

## Getting Started

1. Configure your AI provider credentials in `config/config.yaml`
2. Start the RabbitMQ server
3. Start the Celery worker
4. Run the main application

## Project Structure

```
project/
├── config/           # Configuration files
├── ai/              # AI provider implementations
├── agents/          # Agent implementations
├── orchestration/   # Task management and pipeline
└── utils/           # Utility functions
```