
import logging
import polars as pl

try:
    from utils import load_balance_sheet_json, get_all_child_values, validate_balance_sheet_json_schema, validate_balance_sheet_equation
except ImportError:
    from .utils import load_balance_sheet_json, get_all_child_values, validate_balance_sheet_json_schema, validate_balance_sheet_equation


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting balance sheet validation")

    # Load the balance sheet json file
    logger.info("Loading balance sheet json into memory")
    balance_sheet_data = load_balance_sheet_json('balance_sheet_payload.json')

    logger.info("Validating the json schema")
    validate_balance_sheet_json_schema(balance_sheet_data)

    logger.info("Validating the values of the balance sheet")
    validate_balance_sheet_equation(balance_sheet_data)

    logger.info("Convert balance sheet to tabular format for ingestion by the data warehouse")
    df = get_all_child_values(balance_sheet_data)
    df.write_csv('json_to_tabular.csv')

