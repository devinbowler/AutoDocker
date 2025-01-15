import click
import inquirer
import os
import webbrowser
import subprocess
from inquirer import List, Checkbox, Text, Confirm

# ASCII Art Banner
DOCKER_BANNER = r"""
    _         _        ____             _             
   / \  _   _| |_ ___ |  _ \  ___   ___| | _____ _ __ 
  / _ \| | | | __/ _ \| | | |/ _ \ / __| |/ / _ \ '__|
 / ___ \ |_| | || (_) | |_| | (_) | (__|   <  __/ |   
/_/   \_\__,_|\__\___/|____/ \___/ \___|_|\_\___|_|   
------------------------------------------------------
   AutoDocker - Automatically Generate Docker Images
"""

@click.group()
def cli():
    """Root command for Docker Generation Tool."""
    pass


def list_files_in_chunks(directory=".", chunk_size=10, max_files_per_folder=15, exclude_folders=None):
    """
    Recursively list all files in a directory, skipping specific folders and folders with too many files,
    and display files in chunks of a given size.
    """
    # Set default excluded folders if none are provided
    if exclude_folders is None:
        exclude_folders = ["node_modules", ".git", "__pycache__"]

    # Recursively collect all files with their relative paths
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Skip excluded folders
        dirs[:] = [d for d in dirs if d not in exclude_folders]

        # Skip folders with too many files
        if len(files) > max_files_per_folder:
            continue

        for file in files:
            full_path = os.path.relpath(os.path.join(root, file), directory)
            all_files.append(full_path)

    selected_files = []
    chunk_start = 0

    # Display files in chunks
    while chunk_start < len(all_files):
        chunk_end = min(chunk_start + chunk_size, len(all_files))
        chunk = all_files[chunk_start:chunk_end]

        # Prompt the user to select files from the current chunk
        question = [
            Checkbox(
                "selection",
                message="Select files to include (or load more):",
                choices=chunk + ["[Load more]"] if chunk_end < len(all_files) else chunk,
            )
        ]
        answer = inquirer.prompt(question)

        # Handle selection
        if "[Load more]" in answer["selection"]:
            selected_files.extend([f for f in answer["selection"] if f != "[Load more]"])
            chunk_start += chunk_size  # Load the next chunk
        else:
            selected_files.extend(answer["selection"])
            break  # User finished selecting

    return selected_files


@cli.command()
def init():
    """
    Interactive command that asks questions and generates Dockerfiles.
    """
    # Display ASCII art
    click.echo(DOCKER_BANNER)

    # Get current directory
    current_directory = os.getcwd()

    # Ask for the number of images
    base_questions = [
        Text('image_count', message="How many images do you want to generate?", default="1")
    ]
    base_answers = inquirer.prompt(base_questions)
    image_count = int(base_answers['image_count'])

    # Define default commands for each base image
    base_image_commands = {
        "python:3.9-slim": '["python3", "app.py"]',
        "node:16-alpine": '["node", "server.js"]',
        "nginx:alpine": '["nginx", "-g", "daemon off;"]',
        "golang:1.17-alpine": '["go", "run", "main.go"]',
        "openjdk:17-slim": '["java", "-jar", "app.jar"]',
        "ruby:3.1-alpine": '["ruby", "app.rb"]',
        "ubuntu:20.04": '["/bin/bash"]',
        "alpine:latest": '["/bin/sh"]',
    }

    # Loop through the number of images
    all_image_details = []
    for index in range(image_count):
        click.echo(f"\n--- Configuring Image {index + 1} ---")

        # Ask for base image first to determine the default run command
        base_image_question = [
            List(
                f'base_image_{index}',
                message=f"Select the base image for Image {index + 1}",
                choices=[
                    "python:3.9-slim",
                    "node:16-alpine",
                    "nginx:alpine",
                    "golang:1.17-alpine",
                    "openjdk:17-slim",
                    "ruby:3.1-alpine",
                    "ubuntu:20.04",
                    "alpine:latest"
                ],
                default="python:3.9-slim",
            )
        ]
        base_image_answer = inquirer.prompt(base_image_question)
        selected_base_image = base_image_answer[f'base_image_{index}']

        # Use the selected base image to determine the default run command
        default_run_cmd = base_image_commands.get(selected_base_image, "/bin/sh")

        # Ask the user to select files and folders using the recursive function
        selected_files = list_files_in_chunks(
            current_directory,
            chunk_size=10,
            max_files_per_folder=15,
            exclude_folders=["node_modules", ".git", "__pycache__"]
        )

        # Ask for additional details
        image_questions = [
            Text(f'image_name_{index}', message=f"Name for Image {index + 1}", default=f"image_{index + 1}"),
            Text(f'exposed_port_{index}', message=f"Port to expose for Image {index + 1}", default="8000"),
            Text(f'run_cmd_{index}', message=f"Command to run Image {index + 1}", default=default_run_cmd),
        ]
        other_image_details = inquirer.prompt(image_questions)

        # Combine all details into a single dictionary, including selected files
        image_details = {
            **base_image_answer,
            **other_image_details,
            f'files_{index}': selected_files
        }
        all_image_details.append(image_details)

    # Optionally, ask if the user wants to automatically build and run
    auto_questions = [
        Confirm('auto_build', message="Do you want to automatically build and run the Docker containers now?", default=True)
    ]
    auto_answers = inquirer.prompt(auto_questions)

    print(all_image_details)

    base_image_files = {
        "python:3.9-slim": "/app/",
        "node:16-alpine": "/usr/src/app/",
        "nginx:alpine": "/usr/share/nginx/html/",
        "golang:1.17-alpine": "/go/src/app/",
        "openjdk:17-slim": "/usr/src/app/",
        "ruby:3.1-alpine": "/usr/src/app/",
        "ubuntu:20.04": "/app/",
        "alpine:latest": "/app/",
    }

    # Generate Dockerfiles for each image
    for index, details in enumerate(all_image_details):
        dockerfile_name = f"Dockerfile.{details[f'image_name_{index}']}"
        with open(dockerfile_name, 'w', newline='\n') as dockerfile:
            dockerfile.write(f"FROM {details[f'base_image_{index}']}\n")
            for file in details[f'files_{index}']:
                # Normalize the file path and replace backslashes with forward slashes
                normalized_file = os.path.normpath(file).replace("\\", "/")
                
                # Get the directory path (excluding the file)
                directory_path = os.path.dirname(normalized_file).replace("\\", "/")
                
                # Build the destination path
                destination_pre_path = base_image_files.get(details[f'base_image_{index}'], "")
                
                # If the file has a directory, add it; otherwise, just use the base path
                if directory_path:
                    dockerfile.write(f"COPY {normalized_file} {destination_pre_path}{directory_path}/\n")
                else:
                    dockerfile.write(f"COPY {normalized_file} {destination_pre_path}\n")

            dockerfile.write(f"EXPOSE {details[f'exposed_port_{index}']}\n")
            dockerfile.write(f"CMD {details[f'run_cmd_{index}']}\n")

        click.echo(f"Dockerfile for {details[f'image_name_{index}']} created: {dockerfile_name}")

    # Build and run Docker containers
    for index, details in enumerate(all_image_details):
        # Command to build a Docker image
        dockerfile_name = f"Dockerfile.{details[f'image_name_{index}']}"
        build_command = f"docker build -t {details[f'image_name_{index}']} -f {dockerfile_name} ."

        try:
            # Run the build command
            build_result = subprocess.run(build_command, shell=True, check=True, text=True, capture_output=True)
            print("Build Output:\n", build_result.stdout)
        except subprocess.CalledProcessError as e:
            print("Build Error:\n", e.stderr)
        
        exposed_port = details[f'exposed_port_{index}']
        # Command to run the Docker container
        run_command = f"docker run -d -p 8080:{exposed_port} --name container_{index} {details[f'image_name_{index}']}"
        
        try:
            # Run the container command
            run_result = subprocess.run(run_command, shell=True, check=True, text=True, capture_output=True)
            print("Container Run Output:\n", run_result.stdout)

            # Open the container in the browser
            url = f"http://localhost:{8080}"
            print(f"Opening browser to {url}...")
            webbrowser.open(url)  # This will open the default browser to the container URL
        except subprocess.CalledProcessError as e:
            print("Container Run Error:\n", e.stderr)


if __name__ == "__main__":
    cli()

