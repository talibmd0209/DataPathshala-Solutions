FROM jupyter/pyspark-notebook:spark-3.5.0

USER root

# Extra OS deps (useful for reading/writing common formats, JDBC, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Python packages: Delta Lake (Databricks' table format), plotting, misc utils
RUN pip install --no-cache-dir \
    delta-spark==3.1.0 \
    pandas \
    matplotlib \
    seaborn \
    plotly \
    pyarrow \
    ipywidgets \
    faker

# Make sure the startup folder exists (mounted via docker-compose volume too,
# but this keeps the image usable standalone)
RUN mkdir -p /home/jovyan/.ipython/profile_default/startup

WORKDIR /home/jovyan/work
