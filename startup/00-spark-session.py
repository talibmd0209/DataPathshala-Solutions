"""
Runs automatically at kernel startup (IPython startup folder).
Creates a `spark` SparkSession pre-configured with Delta Lake,
mirroring what's already available in a Databricks notebook.
"""
import os
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = (
    SparkSession.builder
    .appName("local-databricks-like")
    .master(os.environ.get("SPARK_MASTER", "local[*]"))
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.driver.memory", os.environ.get("SPARK_DRIVER_MEMORY", "2g"))
    .config("spark.executor.memory", os.environ.get("SPARK_EXECUTOR_MEMORY", "2g"))
    .config("spark.sql.warehouse.dir", "/home/jovyan/work/spark-warehouse")
    .config("spark.ui.showConsoleProgress", "false")
)

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

sc = spark.sparkContext

print(f"Spark {spark.version} session ready as `spark` (Delta Lake enabled).")
