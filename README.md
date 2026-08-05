# Spark + Jupyter, Databricks-flavored

A local Docker environment that gives you a Jupyter Lab + PySpark setup with
the Databricks notebook conveniences layered on top:

| Databricks feature      | Available here as |
|--------------------------|--------------------|
| pre-created `spark`      | ✅ auto-created SparkSession (Delta Lake enabled) |
| `display(df)`            | ✅ rich HTML table, capped at 1000 rows like Databricks |
| `dbutils.fs.*`           | ✅ ls / mkdirs / rm / cp / mv / put / head, backed by local disk |
| `dbutils.widgets.*`      | ✅ text / dropdown parameter widgets |
| `dbutils.notebook.exit`/`.run` | ✅ run another notebook and get its return value |
| `%run ./other_notebook`  | ✅ via `%run_notebook ./other_notebook` line magic |
| Delta Lake tables         | ✅ `delta-spark` pre-installed and wired into Spark config |

## Usage

```bash
docker compose up --build
```

Then open http://localhost:8888 (token: `databricks`, set in `docker-compose.yml`).

- Notebooks live in `./notebooks` (mounted to `/home/jovyan/work`).
- Data files live in `./data` (mounted to `/home/jovyan/data`) — use this as
  your "DBFS" root with `dbutils.fs`.
- Spark UI: http://localhost:4040 while a job is running.

A starter notebook is included at `notebooks/00_getting_started.ipynb`.

## Customizing

- Add Python packages: edit `Dockerfile`'s `pip install` list.
- Change Spark resources: edit `SPARK_DRIVER_MEMORY` / `SPARK_EXECUTOR_MEMORY`
  in `docker-compose.yml`.
- The `display()` / `dbutils` shims live in `startup/01-databricks-utils.py` —
  edit freely, they're plain Python, loaded automatically as an IPython
  startup script on every kernel launch.

## Notes / limitations

- `dbutils.fs` operates on the local filesystem, not real DBFS/cloud storage
  — good enough for local dev, not a drop-in for cloud paths (`s3://`,
  `abfss://`) unless you mount/configure those separately.
- `%run_notebook` is a custom magic (Jupyter doesn't allow overriding `%run`'s
  behavior for `.ipynb` files) — use it instead of Databricks' bare `%run`.
- Single-node Spark (`local[*]`) — fine for development; for a real cluster
  swap the `master` in `startup/00-spark-session.py` for a Spark
  standalone/YARN/K8s master URL.
