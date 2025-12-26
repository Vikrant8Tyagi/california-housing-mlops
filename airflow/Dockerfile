FROM apache/airflow:2.7.0

# -------------------------------------------------
# Switch to root to install system packages
# -------------------------------------------------
USER root

# Install system dependencies required for building python packages
RUN apt-get update && \
    apt-get install -y gcc g++ git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# 🔑 FIX: Git "dubious ownership" issue (Jenkins / CI)
# -------------------------------------------------
# Mark common workspace paths as safe for Git
RUN git config --system --add safe.directory /app && \
    git config --system --add safe.directory /opt/airflow && \
    git config --system --add safe.directory '*'

# -------------------------------------------------
# Switch back to airflow user (BEST PRACTICE)
# -------------------------------------------------
USER airflow

# -------------------------------------------------
# Install Python dependencies
# -------------------------------------------------
RUN pip install --no-cache-dir \
    scikit-learn \
    pandas \
    mlflow \
    skl2onnx \
    onnxruntime
