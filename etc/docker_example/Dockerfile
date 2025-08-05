# 1. Base OS
FROM ubuntu:20.04


# 2. Install C libraries and system dependencies
# 2.1 Set environment variable to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
# 2.2 Install necessary packages
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    zlib1g-dev \
    ca-certificates \
    g++ \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Miniconda (non-interactively)
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py310_24.1.2-0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    conda clean -afy

# 4. Create a Conda environment with Python 3.10.0 and install packages
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy

# 5. Activate the environment for subsequent commands
SHELL ["conda", "run", "-n", "phewas_docker", "/bin/bash", "-c"]

# 6. Pip install from GitHub
RUN pip install --use-pep517 git+https://github.com/wayne-monical/pheweb.git@adding_samples

# 7. Copy your application code
COPY . /app

# 7.1 Change working directory to where your site lives
WORKDIR /app/my-new-pheweb

# 8. Expose the port pheweb will run on
EXPOSE 55000

# 9. Start the web server 
CMD ["conda", "run", "--no-capture-output", "-n", "phewas_docker", "pheweb", "serve", "--port", "55000", "--host", "0.0.0.0"]


