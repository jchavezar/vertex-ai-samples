# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN pip install --upgrade pip

# Copy the requirements file and install the dependencies for the main application
# This ensures the primary Python 3.11 environment has all original requirements,
# including the real watchdog, as per the "code works with versions exposed locally" constraint.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install git, which is required by Flet build process
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Configure Git to allow working in the Flutter directory as root
RUN git config --global --add safe.directory /root/flutter/3.29.2

# Copy the rest of the application code
# This includes main.py, agent.py, and the original requirements.txt.
COPY . .

# --- FORCE INSTALL SOLUTION: Provide a local, dummy watchdog package via a local PyPI index ---
# This addresses the transitive dependency of flet-cli on 'watchdog' that is
# incompatible with the Pyodide environment used for 'flet build web'.
# We create a dummy 'watchdog' package, build its wheel, and make it available
# via a local file-based PyPI index that 'flet build web's internal pip can use
# to satisfy the dependency without fetching the incompatible real package.

# 1. Create a temporary directory for the dummy watchdog source code.
# The content creates a minimal setup.py and an __init__.py for a package named 'watchdog'
# with the version '4.0.2' to match the requirement.
RUN mkdir -p /tmp/fake_watchdog_src && \
    echo "from setuptools import setup, find_packages\n\nsetup(name='watchdog', version='4.0.2', description='Dummy watchdog for Flet web build workaround', packages=find_packages())" > /tmp/fake_watchdog_src/setup.py && \
    mkdir -p /tmp/fake_watchdog_src/watchdog && \
    touch /tmp/fake_watchdog_src/watchdog/__init__.py

# 2. Build the wheel distribution for the dummy watchdog package.
# 'wheel' package needs to be installed to use 'bdist_wheel'.
RUN pip install wheel && \
    cd /tmp/fake_watchdog_src && \
    python setup.py bdist_wheel && \
    cd /app

# 3. Create a local PyPI index directory and copy the generated dummy watchdog wheel into it.
RUN mkdir -p /app/local_pypi_index && \
    cp /tmp/fake_watchdog_src/dist/watchdog-4.0.2-py3-none-any.whl /app/local_pypi_index/

# 4. Set the FLET_PIP_EXTRA_INDEX_URL environment variable.
# This instructs 'flet build web' (and its underlying 'serious_python' pip) to
# look for packages in our local file-based index before checking other sources.
ENV FLET_PIP_EXTRA_INDEX_URL=file:///app/local_pypi_index

# Build the Flet web app
# With FLET_PIP_EXTRA_INDEX_URL set, flet's internal pip will find and install
# our dummy watchdog wheel from the local index, satisfying the dependency.
RUN flet build web

# Expose the port the app runs on, as expected by Cloud Run
EXPOSE 8080

# Run the web server to serve the built Flet app
CMD ["python", "-m", "http.server", "8080", "--directory", "build/web"]