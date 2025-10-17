import dagster as dg
from pathlib import Path
import duckdb
from dagster_dbt import DbtCliResource, DbtProject


# DuckDB database Resource
class DuckDBResource:
    """Simple resource to manage a DuckDB connection."""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        return duckdb.connect(self.db_path)


duckdb_resource = dg.ResourceDefinition.hardcoded_resource(
    DuckDBResource("../loan_data.duckdb")
)

#  DBT models Resource
dbt_project = DbtProject(
    project_dir=Path(__file__).joinpath("../../..", "dbt_data").resolve()
)
dbt_project.prepare_if_dev()
dbt_resource = DbtCliResource(
    project_dir=dbt_project,
)
