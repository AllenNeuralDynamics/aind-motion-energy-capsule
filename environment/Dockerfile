# hash:sha256:6ceefde681fb5ad2ca41bca5b1ebdfc35ce9ce0f7acc50dc183706cc463f5d61
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/jupyterlab:3.6.1-miniconda4.12.0-python3.9-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive


RUN conda install -y python=3.11 \
    && conda clean -ya

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# aind-motion-energy pulls PyAV (bundles its own ffmpeg) transitively;
# [viz] extra adds matplotlib for the synced motion-energy video
RUN pip install "aind-motion-energy[viz] @ git+https://github.com/AllenNeuralDynamics/aind-motion-energy.git@main"  # 2026-06-11 viz
