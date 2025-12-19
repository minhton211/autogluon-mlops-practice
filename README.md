# AutoGluon MLOps Practice – Salinity Prediction in the Mekong Delta

---

## 📌 Project Overview

This repository is part of my work on **applying AutoGluon to predict river salinity levels in the Mekong River Delta (Vietnam)**, as well as my **hands-on practice with MLOps principles and tooling**.

The project structure and workflow are strongly inspired and guided by:
- https://mlops-guide.github.io/Structure/starting/
- https://github.com/graviraja/MLOps-Basics

This repository serves both as:
- A **research / experimentation workspace**
- A **learning-oriented MLOps practice project**

---

## Components

The following tools and technologies are used:

- **Git** – Code version control  
- **DVC** – Data and model version control  
- **AutoGluon** – Automated machine learning for tabular data  
- **Docker** – Containerization of trained models  
- **S3 (LocalStack)** – Remote storage backend for DVC  
- **Pytest & pre-commit hooks** – Testing and code quality checks  

---

## Project Workflow

**Notebook ➜ Model Files ➜ DVC to S3 ➜ Docker Image**

1️⃣ **Develop** in a Jupyter notebook.  
2️⃣ **Convert** notebook logic into reusable model/training scripts.  
3️⃣ **Version & push** artifacts with DVC to S3 (LocalStack for local use).  
4️⃣ **Build Docker image** that pulls artifacts from S3 and packages the app.

---

## Replication steps

### 1. Project initialization
The repository was bootstrapped from the MLOps cookiecutter template:

```bash
cookiecutter https://github.com/mlops-guide/mlops-template.git
```

After initialization, I removed unused files and initialized project metadata and create pyproject.toml by running:

```bash
uv init
```
**Dependency policy:** this project uses pyproject.toml (with uv.lock) rather than requirements.txt to support optional dependency groups (extras) for separating test / ml / aws dependencies.

### 2. Virtual environment initialization

Create two isolated virtual environments to enforce separation of concerns:

- `.venv-ml` — Python 3.10, primary environment for ML development (modeling, experiments).  
- `.venv-aws` — Python 3.12, environment to run LocalStack and AWS-related tooling.

This split keeps ML dependencies (Autogluon, data libraries) separate from AWS/infra tooling and avoids cross-contamination of packages. 

**Note 1**: Autogluon and related ML tooling are best used on Python 3.10; LocalStack and AWS tools can run on newer runtimes (3.12).

**Note 2**: You can list all available python version by running `py -0`. 

#### Create the ML environment 
```bash
py -3.10 -m venv .venv-ml
source .venv-ml/bin/activate
pip install -e ".[ml]"
```

#### Create the AWS environment 
```bash
py -3.12 -m venv .venv-aws
source .venv-ml/bin/activate
pip install -e ".[aws]"
```

#### Managing dependencies with uv

When adding libraries, update pyproject.toml and the lockfile using uv so optional groups stay consistent:

```bash
uv add <package> --optional <ml|aws|test> --active
```

```--optional <group>``` places the package into the named optional dependency group (e.g., ml, aws, test).

```--active``` prevents uv from creating a default .venv when you use a custom virtual environment name.

### 3. Pre-commit hook configuration

In the pre-commit, we will do 3 things:
- Detect potentially leaked passwords using `detect-secrets`
- Correct formatting mistakes in python code using `black`
- Run `pytest`

#### Configure detect-secrets
1. Create secret baseline
    ```bash
    detect-secrets scan > .secrets.baseline
    ```
    Run the command above to produce a `.secrets.baseline` file that lists all secrets detected in the repository’s current state. Add and commit this file so you can track newly detected secrets against that baseline. Note that `detect-secrets` only compares the current findings to the baseline, it does not search the repository’s commit history for previously leaked secrets. For details on managing the baseline, see the project docs: [link](https://github.com/Yelp/detect-secrets).

1. Pytest

    I’ll add more tests over time to improve code quality. One **note**: if the repository contains no tests, running pytest in CI can produce a non-zero exit (i.e., a failing run), which will cause a `GitHub Actions` job that runs `pytest` on push to be marked as failed.

---

## Current limitations
- No Docker registry: images are built locally; no push to a central registry is configured.

- No CI/CD: the workflow is manual and local; automated pipelines are out of scope for now.

- No serving or monitoring: the scope covers data/model versioning and reproducible builds only — production serving, logging, and monitoring are not implemented.

---

## References
- MLOps guide: https://mlops-guide.github.io/Structure/starting/

- MLOps basics repo: https://github.com/graviraja/MLOps-Basics