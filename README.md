# AutoDocker

AutoDocker is a CLI tool that simplifies the process of creating Dockerfiles, building Docker images, and running them in containers. It allows you to quickly set up your applications with Docker by filling out a series of prompts. The tool even includes an option to run the containers automatically and opens the default browser on port `8080` to view your application.

---

## Features
- Automatically generates **Dockerfiles** for multiple services (e.g., frontend, backend).
- Builds Docker images based on user input.
- Creates and runs containers.
- Optionally opens the application in the browser on port `8080`.

---

## Installation and Usage

### Step 1: Clone the Repository
To get started, clone the repository to your local machine:
```bash
git clone https://github.com/devinbowler/AutoDocker.git
```
## Navigate into the cloned directory:

```bash
cd AutoDocker
```

### Step 2: Run the Tool
Run the CLI tool to initialize the process:

```bash
python main/cli.py init
```

### Step 3: Fill Out the Prompts
The tool will guide you through a series of prompts:

- Number of Docker Images: Specify how many Docker images you want to generate.
- Base Image: Select the base image (e.g., nginx:alpine, python:3.9-slim, etc.).
- Files to Include: Use the CLI to select the files and directories you want to copy into each image.
- Exposed Port: Specify which port should be exposed for each container.
- Run Command: Provide the command to start the application inside the container.

### Step 4: Automatic Build and Deployment
After completing the prompts:

- The tool will generate the required Dockerfiles.
- It will build the Docker images and create containers.
- If selected, the tool will automatically run the containers and open your default browser to http://localhost:8080.

## Example Workflow
Clone the repository:

```bash
git clone https://github.com/devinbowler/AutoDocker.git
cd AutoDocker
```
Run the tool:

```bash
python main/cli.py init
```
Follow the prompts to configure and generate Dockerfiles, build images, and deploy containers.

Visit http://localhost:8080 in your browser to view the running application.

## Requirements
- Python 3.9 or later
- Docker installed and running on your machine
- An active internet connection for downloading base images

## Contribution
Contributions are welcome! Feel free to fork the repository, create a feature branch, and submit a pull request.
