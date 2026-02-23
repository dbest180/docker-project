# Docker Learning Project: Initial Setup

## Context for LLM
Act as a Senior DevOps Engineer. The goal of this repository is to learn Docker from scratch, incorporating cloud CI/CD best practices using GitHub Actions. Read the requirements below and generate the necessary files to bootstrap the project.

## Tech Stack
* **Containerization:** Docker, Docker Compose
* **Hosting & CI/CD:** GitHub, GitHub Actions
* **Application:** [Specify your preferred language here, e.g., Python/Node.js/Go]

## Requirements to Generate
1.  **Base Application:** Create a minimal "Hello World" web server.
2.  **Dockerfile:** Write a production-ready, multi-stage `Dockerfile`.
3.  **Docker Ignore:** Create a `.dockerignore` file to exclude unnecessary assets.
4.  **Local Dev:** Create a `docker-compose.yml` file to spin up the service locally.
5.  **GitHub Actions Workflow:** Create `.github/workflows/docker-ci.yml`.

## CI/CD Pipeline Specifications
The GitHub Action must:
* Trigger on `push` and `pull_request` to the `main` branch.
* Checkout the repository.
* Set up Docker Buildx.
* Build the Docker image.
* Run a simple test (e.g., verify the container starts or run a linter).
