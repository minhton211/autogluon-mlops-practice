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
.venv-ml\Scripts\Activate.ps1 
pip install -e ".[ml]"
```

#### Create the AWS environment 
```bash
py -3.12 -m venv .venv-aws
.venv-aws\Scripts\Activate.ps1 
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

Run `pre-commit install` to set up the git hook scripts.

#### Configure detect-secrets
```bash
detect-secrets scan > .secrets.baseline
```
Run the command above to produce a `.secrets.baseline` file that lists all secrets detected in the repository’s current state. Add and commit this file so you can track newly detected secrets against that baseline. Note that `detect-secrets` only compares the current findings to the baseline, it does not search the repository’s commit history for previously leaked secrets. For details on managing the baseline, see the project [official documentation](https://github.com/Yelp/detect-secrets).

**Note 1**: `.secrets.baseline` may be saved under incorrect format (e.g. UTF16 LE) leading to error 'Unable to read baseline'. Always make sure it is saved as `UTF-8` format.

**Note 2**: `detect-secrets` may flag image outputs in notebooks as leaked passwords. --> You may clear cell outputs from notebooks to avoid errors.  

#### Pytest

I’ll add more tests over time to improve code quality. One **note**: if the repository contains no tests, running pytest in CI can produce a non-zero exit (i.e., a failing run), which will cause a `GitHub Actions` job that runs `pytest` on push to be marked as failed.

### Autogluon development

There are four main directories to be aware of:

1. **`./data`**  
   Contains all datasets used in the project.  
   The data format must include the required columns defined in `./src/dataloader`.

2. **`./models`**  
   Holds all trained model artifacts.

3. **`./notebooks`**  
   Used for experimentation and model training.  
   Models are trained through these notebooks, and training results are logged with **Weights & Biases (wandb)**.

4. **`./src`**  
   Contains the core source code, including data loaders and test scripts.

### S3 Storage with LocalStack

Prior to implementing large-scale data versioning and containerization, it is essential to establish foundational knowledge of S3 and LocalStack.

- **S3** is a cloud storage service provided by Amazon Web Services (AWS)
- **LocalStack** is a cloud service emulator that enables local execution of Amazon Web Services without requiring connection to remote cloud providers

#### Credentials

Shared credentials configuration for all Localstack users:

```bash
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

#### Quick Start

Begin by launching LocalStack:

```bash
localstack start
```

There are two methods available for creating an S3 bucket:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://sample-bucket

awslocal s3api create-bucket --bucket sample-bucket  # requires awslocal-cli library (recommended)
```

The `awslocal` utility serves as a lightweight wrapper that simplifies command syntax.

For comprehensive documentation regarding S3 storage in LocalStack, please consult the [official documentation](https://docs.localstack.cloud/aws/services/s3/).

### Data Versioning with DVC

For detailed information about DVC, please refer to the [official documentation](https://doc.dvc.org/start).

Begin by initializing DVC:

```bash
dvc init
```

Subsequently, add and commit the files created by DVC within the `./.dvc` directory:

```bash
git status
Changes to be committed:
        new file:   .dvc/.gitignore
        new file:   .dvc/config
        ...
git commit -m "Initialize DVC"
```

Next, utilize `dvc add` to track files. Note that tracked files should be listed in `.gitignore`, while their corresponding `<tracked-file-name>.dvc` files must remain visible to Git.

Data will be cached locally and can subsequently be pushed to remote storage. To integrate DVC with S3, install the additional `dvc-s3` library:

```bash
dvc remote add -d <storage name> s3://baswap/
```

When working with LocalStack, configure the S3 storage endpoint URL:

```bash
dvc remote modify storage endpointurl http://localhost:4566
```

You can then use `dvc push` and `dvc pull` to synchronize files with remote storage.

### Containerization with Docker

The next phase involves containerizing the AutoGluon inference code. By leveraging remote storage, the containerization process focuses on the environment and libraries, while models are retrieved from S3 storage at runtime using DVC. This section addresses the containerization of code within the `./deploy` directory. Run the below command to start building:
```bash
docker build -t baswap-ts .
```
Remember to have the trailing dot.

To facilitate model loading at runtime, create an entrypoint file named `start.sh`. Note that within the `.env` file, the S3 endpoint URL has been modified from `localhost` to `host.docker.internal`. This adjustment is necessary because `localhost` within a container references the container itself rather than the host machine running LocalStack. Run the below code to run a container created by the image:
```bash
docker run --rm --env-file deploy/.env baswap-ts
```

---

## Current limitations
- No Docker registry: images are built locally; no push to a central registry is configured.

- No CI/CD: the workflow is manual and local; automated pipelines are out of scope for now.

- No serving or monitoring: the scope covers data/model versioning and reproducible builds only — production serving, logging, and monitoring are not implemented.

---

## References
- MLOps guide: https://mlops-guide.github.io/Structure/starting/

- MLOps basics repo: https://github.com/graviraja/MLOps-Basics
