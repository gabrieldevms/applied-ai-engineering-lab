# Local Development Environment

## Context

This document records the local development environment used for the Applied AI Engineering Lab.

The goal is to keep track of the tools installed, their versions and the purpose of each tool in the project.

## Environment Status

The local environment was validated successfully.

## Installed Tools

### Git

Version:

```
git version 2.52.0.windows.1
```

Purpose:

Git is used for source code versioning, branch management, commits and collaboration through GitHub.

### Python

Version:

```
Python 3.12.10
```

Purpose:

Python is the main programming language for the Applied AI Engineering Lab.

It will be used to build APIs, LLM integrations, RAG services, agents, evaluation pipelines and automation scripts.

### py launcher

Version:

```
Python 3.12.10
```

Purpose:

The Python launcher is used on Windows to execute and manage Python versions.

### pip

Version:

```
pip 25.0.1
```

Purpose:

pip is the default Python package installer.

Although the project will prioritize uv for dependency and project management, pip remains useful for compatibility and quick checks.

### uv

Version:

```
uv 0.11.25
```

Purpose:

uv is the main Python project and dependency management tool for this project.

It will be used to create environments, install dependencies, manage packages and run Python commands efficiently.

### Docker

Version:

```
Docker version 29.5.3
```

Purpose:

Docker is used to containerize services and create reproducible development environments.

It will be important for running the API, databases, vector databases, observability tools and future production-like environments.

### Docker Compose

Version:

```
Docker Compose version v5.1.4
```

Purpose:

Docker Compose is used to orchestrate multiple local services.

It will be used later to run components such as:

* API service
* PostgreSQL
* Vector database
* Observability tools
* Agent services
* MCP services

### Visual Studio Code

Version:

```
1.120.0
```

Purpose:

Visual Studio Code is the main code editor for the project.

It will be used for development, documentation, debugging and Git integration.

## Validation Commands

The following commands were used to validate the environment:

```
git --version
python --version
py --version
pip --version
uv --version
docker --version
docker compose version
code --version
```

Additional Docker runtime validation:

```
docker run hello-world
```

## Current Status

The local environment is ready for the next phase of the project.

Next phase:

```
M1 — AI API Base
```

In the next module, the project will start implementing the first FastAPI application with uv, Pydantic, pytest, Docker and GitHub Actions.
