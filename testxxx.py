#!/usr/bin/env python
import argparse
import logging
import sys
from typing import Callable, Sequence, Dict
from pyspark.sql import SparkSession

from src.advanced_field_monitoring.data_loader.load.Table import Table
from src.advanced_field_monitoring.data_loader.extract.tables.Vehicle import Vehicle
from src.advanced_field_monitoring.data_loader.extract.tables.BatteryDiag import BatteryDiag
from src.advanced_field_monitoring.data_loader.extract.tables.BatteryDiagCell import (
    BatteryDiagCell,
)
from src.advanced_field_monitoring.data_loader.extract.tables.DTC import DTC
from src.advanced_field_monitoring.data_loader.extract.tables.EngineeringModel import (
    EngineeringModel,
)
from src.advanced_field_monitoring.data_loader.extract.tables.ForecastDiag import (
    ForecastDiag,
)
from src.advanced_field_monitoring.data_loader.extract.tables.Warranty import (
    Warranty,
)
from src.advanced_field_monitoring.data_loader.extract.tables.BatteryType import (
    BatteryType,
)
from src.advanced_field_monitoring.data_loader.extract.tables.ForecastValidation import (
    ForecastValidation,
)
from src.advanced_field_monitoring.data_loader.extract.tables.TableInterface import (
    ArgType,
    TableInterface,
)


def parse_args(args: Sequence[str]) -> ArgType:
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      parsed command line parameters namespace
    """

    parser = argparse.ArgumentParser(description="Advanced Field Monitoring")
    parser.add_argument(
        "--afm-db",
        "-afm",
        required=True,
        dest="afm_db",
        help="Name of afm database",
    )
    parser.add_argument(
        "--afm-forecast-db",
        "-fc",
        required=False,
        dest="afm_forecast_db",
        help="Name of afm forecast database",
    )
    parser.add_argument(
        "--xev-db",
        "-xev",
        required=True,
        dest="xev_db",
        help="Name of xev database",
    )
    parser.add_argument(
        "--table-name",
        "-tn",
        required=True,
        dest="table_name",
        help="Name of target table class which should be loaded",
    )
    parser.add_argument(
        "--afm-home",
        "-home",
        required=True,
        dest="afm_home",
        help="Home directory for afm data",
    )
    parser.add_argument(
        "--output-db-name",
        "-o",
        required=False,
        dest="output_db_name",
        help="Name of output database name (optional)",
    )
    parser.add_argument(
        "--run-mode",
        "-rm",
        required=False,
        dest="run_mode",
        choices=["all", "latest"],
        help="Should the engineering model run for all diagnosis or only on latest?",
    )

    parser_namespace = parser.parse_args(args)

    # Why an extra variable artifacts_home? In the tests, afm_home should point
    # to a different directory of local CSV files. But Table.py needs the
    # unmodified afm_home.
    parser_namespace.artifacts_home = (
        parser_namespace.afm_home + "/afm_backend_artifacts/"
    )
    return parser_namespace


def get_table_class(
    table_name: str,
) -> Callable[[SparkSession, ArgType], TableInterface]:
    """
    Get the class containing the business logic
    for the target table name

    Args:
        table_name: Name of table which should be loaded

    Returns:
        Table's class
    """

    table_name_to_class: Dict[
        str, Callable[[SparkSession, ArgType], TableInterface]
    ] = {
        "battery_diag": BatteryDiag,
        "battery_diag_cell": BatteryDiagCell,
        "dtc": DTC,
        "engineering_model": EngineeringModel,
        "vehicle": Vehicle,
        "forecast_diag": ForecastDiag,
        "warranty": Warranty,
        "battery_type": BatteryType,
        "forecast_validation": ForecastValidation,
    }

    try:
        return table_name_to_class[table_name.lower()]
    except KeyError as e:
        raise RuntimeError("Cannot find specified table") from e