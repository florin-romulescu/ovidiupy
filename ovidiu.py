#! /opt/homebrew/bin/python3
import os
import subprocess
import sys
import argparse
from typing import Callable, List, Any
from functools import partial

def create_directory(path:str) -> bool:
    try:
        os.makedirs(path)
    except FileExistsError:
        return False
    return True

def init_git_repo(path:str) -> bool:
    try:
        subprocess.run(['git', 'init', path], check=True)
    except subprocess.CalledProcessError:
        return False
    return True

def create_readme(path:str) -> bool:
    readme_content = '''
# Project Title

A short description of the project.

## Installation
Instructions on how to install the project.

## Usage
Instructions on how to use the project.

## Contributing
Instructions on how to contribute to the project.

## License
Information about the license of the project.
'''
    try:
        with open(os.path.join(path, 'README.md'), 'w') as f:
            f.write(readme_content)
    except IOError:
        return False
    return True

def create_gitignore(path:str) -> bool:
    gitignore_content = '''
__pycache__/
*.pyc
*.pyo

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.cache
nosetests.xml
coverage.xml

# dotenv
.env
.venv

# mkdocs documentation
/site

# mypy
.mypy_cache/
'''
    try:
        with open(os.path.join(path, '.gitignore'), 'w') as f:
            f.write(gitignore_content)
    except IOError:
        return False
    return True

def create_docs(path:str) -> bool:
    doc_content = '''
# Project Title
This is where the documentation of the project goes.

## Description
Describe what the project is trying to achieve.

## Installation
Provide instructions on how to install the project.

## Usage
Provide instructions on how to use the project.

## API Reference
Provide information about the API of the project.

## License
Provide information about the license of the project.
'''
    try:
        os.makedirs(os.path.join(path, 'docs'))
        with open(os.path.join(path, 'docs', 'DOCS.md'), 'w') as f:
            f.write(doc_content)
    except IOError:
        return False
    return True

def create_mit_license(path:str) -> bool:
    mit_license_content = '''
    Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
    try:
        with open(os.path.join(path, 'LICENSE'), 'w') as f:
            f.write(mit_license_content)
    except IOError:
        return False
    return True

def create_venv(path:str) -> bool:
    try:
        subprocess.run(['python3', '-m', 'venv', os.path.join(path, '.venv')], check=True)
    except subprocess.CalledProcessError:
        return False
    return True

def create_directory(path:str) -> bool:
    try:
        os.makedirs(path)
    except FileExistsError:
        return False
    return True

def install_dependencies(path:str, dependencies:List[str]) -> bool:
    if dependencies == []:
        return True
    try:
        subprocess.run([os.path.join(path, '.venv', 'bin', 'pip'), 'install'] + dependencies, check=True)
    except Exception:
        return False
    return True

def create_docs(path:str) -> bool:
    doc_content = '''# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "src/app.py"]
'''
    try:
        os.makedirs(os.path.join(path, 'docs'))
        with open(os.path.join(path, 'Dockerfile'), 'w') as f:
            f.write(doc_content)
    except Exception:
        return False

def install_linters(path:str, linters:List[str]) -> bool:
    if linters == []:
        return True
    try:
        subprocess.run([os.path.join(path, '.venv', 'bin', 'pip'), 'install'] + linters, check=True)
    except Exception:
        return False
    return True

def on_failure(path:str) -> bool:
    try:
        subprocess.run(['rm', '-rf', path])
    except FileNotFoundError:
        return False
    return True

def pipeline(functions:list[tuple[Callable, tuple[Any]]], on_failure:Callable) -> bool:
    for function, args in functions:
        if not function(*args):
            on_failure()
            return False
    return True

def main(args) -> None:
    on_failure_func = partial(on_failure, args.path)
    functions = [
        (create_directory, (args.path,)),
        (create_directory, (os.path.join(args.path, 'tests'),)),
        (init_git_repo, (args.path,)),
        (create_readme, (args.path,)),
        (create_gitignore, (args.path,)),
        (create_docs, (args.path,)),
        (create_mit_license, (args.path,)),
        (create_venv, (args.path,)),
        (install_dependencies, (args.path, args.dependencies))
    ]
    if args.use_linters:
        functions.append((install_linters, (args.path, args.linters)))
    if args.use_docker:
        functions.append((create_docs, (args.path,)))
    result = pipeline(functions, on_failure_func)
    if not result:
        print('An error occurred while creating the project.')
        sys.exit(1)
    print('Project created successfully.')
    return

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--path', help='Path to the project directory', required=True)
    args.add_argument('--dependencies', nargs='+', help='List of dependencies to install', default=[])
    args.add_argument('--use-linters', action='store_true', help='Install linters', default=False)
    args.add_argument('--linters', nargs='+', help='List of linters to install', default=['flake8', 'black'])
    args.add_argument('--use-docker', action='store_true', help='Install Docker', default=False)


    args = args.parse_args()
    main(args)