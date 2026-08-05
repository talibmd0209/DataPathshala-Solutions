# DataPathshala PySpark Solutions

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-4.0-E25A1C?logo=apachespark&logoColor=white)
![Spark SQL](https://img.shields.io/badge/Spark-SQL-E25A1C?logo=apachespark&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Lab-F37626?logo=jupyter&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta-Lake-00ADD8)

Practice PySpark and Spark SQL by solving DataPathshala problems on a fully Dockerized local Apache Spark environment.


This repository contains my solutions to the **DataPathshala** PySpark and Spark SQL practice problems.

All solutions are developed and tested on a **local Apache Spark environment running inside Docker**, providing a reproducible setup without requiring Databricks or any cloud platform.

The repository also includes all Docker, Spark, and Jupyter configuration files needed to run the environment locally.

---

## Repository Goals

* Solve DataPathshala practice problems using **PySpark**
* Provide equivalent **Spark SQL** solutions where applicable
* Practice production-style Spark development
* Learn and experiment with Spark in a local environment
* Share a fully reproducible Spark development setup

---

## Local Spark Environment

The project uses a **Docker-based Spark + Jupyter Lab** environment with several Databricks-inspired utilities to make local development easier.

| Databricks Feature          | Available Locally                                   |
| --------------------------- | --------------------------------------------------- |
| Pre-created `spark` session | ✅ Auto-created SparkSession with Delta Lake enabled |
| `display(df)`               | ✅ Rich HTML table (up to 1000 rows)                 |
| `dbutils.fs.*`              | ✅ Local filesystem implementation                   |
| `dbutils.widgets.*`         | ✅ Text and dropdown widgets                         |
| `dbutils.notebook.run()`    | ✅ Execute notebooks and return values               |
| `%run_notebook`             | ✅ Notebook execution magic                          |
| Delta Lake                  | ✅ Fully configured                                  |

---

## Project Structure

```text
.
├── data/                  # Practice datasets
├── notebooks/             # PySpark & Spark SQL solutions
├── startup/               # Databricks utility shims
├── configs/               # Spark configuration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Docker
- Docker Compose
- Git


## Getting Started

Clone the repository.

```bash
git clone https://github.com/talibmd0209/DataPathshala-Solutions.git
cd DataPathshala-Solutions
```

Build and start the environment.

```bash
docker compose up --build
```

Open Jupyter Lab:

```
http://localhost:8888
```

(Default token is configured in `docker-compose.yml`.)

---

## Folder Mapping

| Local Folder  | Container Path      |
| ------------- | ------------------- |
| `./notebooks` | `/home/jovyan/work` |
| `./data`      | `/home/jovyan/data` |

Spark UI is available at:

```
http://localhost:4040
```

while a Spark job is running.

---

## Customization

* Add Python packages by editing the `Dockerfile`.
* Modify Spark memory settings in `docker-compose.yml`.
* Customize the Databricks helper utilities in:

```text
startup/
├── 00-spark-session.py
└── 01-databricks-utils.py
```

---

## Limitations

* Runs in **single-node (`local[*]`) Spark mode**.
* `dbutils.fs` works on the local filesystem rather than cloud storage.
* `%run_notebook` replaces Databricks' `%run` for Jupyter compatibility.

---

## Acknowledgement

A special thanks to **Manish Kumar**, the creator of **DataPathshala**, for building an outstanding platform for learning Data Engineering through practical, hands-on problems.

His educational content on **PySpark**, **Spark SQL**, **SQL**, and Data Engineering has helped many learners develop strong problem-solving skills and a deeper understanding of distributed data processing.

This repository contains **my own implementations** of the practice problems available on DataPathshala. It is created for educational purposes and is **not affiliated with or endorsed by DataPathshala or Manish Kumar**.

---

## Future Work

This repository will continue to grow with additional solutions covering:

* DataFrame Transformations
* Aggregations
* Window Functions
* Joins
* Spark SQL
* Optimization Techniques
* Interview Problems
* Delta Lake
* Data Engineering Patterns

---

## License

This repository is intended solely for educational and learning purposes.
