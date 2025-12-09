"""
Process banking transactions files.
"""

import logging
import os
import json

import pandas as pd


from log_config.logging_config import setup_root_logger
from utils.data_handling import (
    transform_data,
    categorise_contractor,
    categorise_title,
    start_with_no_category,
    no_category_dict,
)
from utils.file_handling import (
    get_transaction_file,
    read_csv_file,
    verify_csv_file,
    InvalidCSVFileError,
)
from config import (
    TASK_NAME,
    LOGS_FOLDER,
    FILES_FOLDER,
    CATEGORIES_MAPPING,
    FIELD_MAPPING,
    UNCATEGORISED,
    OUTPUT_FOLDER,
)


def process_transaction_file(file_path, logger: logging.Logger) -> None:
    """
    Process banking transactions.

    Parameters
    ---------
    file_path: str
        Transaction file path.

    Returns
    -------
    None
    """

    # Fields mapping
    with open(FIELD_MAPPING, "r", encoding="utf-8") as file:
        fields_mapping = json.load(file)

    fields_mapping = fields_mapping["ing"]
    title_field = fields_mapping["title"]
    contractor_field = fields_mapping["contractor"]
    category_field = fields_mapping["category"]
    transaction_date_field = fields_mapping["transaction_date"]
    amount_field = fields_mapping["amount"]
    account_field = fields_mapping["account"]

    mandatory_columns = [
        transaction_date_field,
        contractor_field,
        title_field,
        amount_field,
        account_field,
    ]

    csv_generator = read_csv_file(file_path, custom_separator=";", custom_chunksize=10)
    verify_csv_file(csv_generator, mandatory_columns)

    # Create 2nd generator. The 1st one exhausted 1 element for fiel verification
    csv_generator = read_csv_file(file_path, custom_separator=";", custom_chunksize=10)

    all_data = pd.DataFrame()
    for chunk in csv_generator:
        data = transform_data(chunk, mandatory_columns)
        all_data = pd.concat([all_data, data], ignore_index=True)

    # Categorise
    with open(CATEGORIES_MAPPING, "r", encoding="utf-8") as file:
        categories = json.load(file)

    all_data = categorise_contractor(
        all_data, categories["Contractor"], contractor_field
    )
    all_data = categorise_title(all_data, categories["Title"], title_field)
    all_data = start_with_no_category(all_data, category_field, "NO CATEGORY")

    no_category_rows = all_data[all_data[category_field] == "NO CATEGORY"].shape[0]
    logger.info("Number of uncategorised rows: %s", no_category_rows)

    # Save outputs
    output_file = os.path.join(OUTPUT_FOLDER, "output.xlsx")
    all_data.to_excel(output_file)
    logger.info("Output file saved in: %s", output_file)

    no_category = no_category_dict(all_data, title_field)
    no_catregory_title_file = os.path.join(UNCATEGORISED, "title.json")
    with open(no_catregory_title_file, "w", encoding="utf-8") as f:
        json.dump(no_category, f, indent=True)
    logger.info("Uncategorised title saved in: %s", no_catregory_title_file)

    no_category = no_category_dict(all_data, contractor_field)
    no_catregory_contractor_file = os.path.join(UNCATEGORISED, "contractor.json")
    with open(no_catregory_contractor_file, "w", encoding="utf-8") as f:
        json.dump(no_category, f, indent=True)
    logger.info("Uncategorised contractors saved in: %s", no_catregory_contractor_file)


#  Main code
log_file = os.path.join(LOGS_FOLDER, f"{TASK_NAME}.log")
setup_root_logger(log_file)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Add two empty log to mark the beggining
    # Usefull when logs are saved in the same file
    logger.info("")
    logger.info("")
    logger.info("Execution started.")

    file_pattern = "Lista_transakcji_nr_"
    file_extension = ".csv"

    transaction_file_path = get_transaction_file(
        folder_path=FILES_FOLDER, pattern=file_pattern, extension=file_extension
    )
    items = []
    items.append(transaction_file_path)
    num_items = len(items)
    if not num_items:
        logger.info("No items to process")

    for item_index, item in enumerate(items):
        try:
            logger.info("#" * 100)  # Mark start point for item. Easy to see in log
            logger.info("Started processing item: %s/%s", item_index + 1, num_items)
            # main function
            process_transaction_file(item, logger)
            logger.info("Status: Success for %s", item)

        except (FileNotFoundError, InvalidCSVFileError) as e:
            logger.error("Known error: %s", e)
            logger.info("Status: Failed for %s", item)
        # Catch all unexpected errors
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unknown error: %s", e)
            logger.info("Status: Failed for %s", item)
        logger.info("Finished processing file: %s/%s", item_index + 1, num_items)
        logger.info("#" * 100)  # Mark end point for item. Easy to see in log
    logger.info("Execution finished.")
