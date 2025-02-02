import jsonschema
import json
import polars as pl
import logging

logger = logging.getLogger(__name__)

def get_all_child_values(balance_sheet_data: dict) -> pl.DataFrame:
    """
    Extracts root child node values from the balance sheet data along with their paths.

    Args:
        balance_sheet_data (dict): Dictionary containing the balance sheet data with nested structure

    Returns:
        pl.DataFrame: DataFrame with columns 'path', 'name', 'value', and 'account_id'.
                     Only includes nodes where account_id is not null.

    Example:
        >>> df = get_all_child_values(balance_sheet_data)
        >>> print(df.columns)
        ['path', 'name', 'value', 'account_id']
    """
    rows = []
    
    def traverse_node(node: dict, current_path: str = ""):
        # Add current node if it has account_id and it's not null
        if "value" in node and "account_id" in node and node["account_id"] is not None:
            rows.append({
                "account_id": node["account_id"],
                "path": current_path,
                "name": node["name"],
                "value": float(node["value"])
            })
            
        # Recursively process child nodes
        if "items" in node:
            for child in node["items"]:
                # Build path by appending child name
                child_path = f"{current_path}/{node['name']}" if current_path else node['name']
                traverse_node(child, child_path)
    
    # Process each main section
    for section in ["assets", "liabilities", "equity"]:
        if section in balance_sheet_data:
            traverse_node(balance_sheet_data[section], section)
            
    # Create DataFrame from collected rows
    return pl.DataFrame(rows)



def load_balance_sheet_json(path: str) -> dict:
    """
    Loads and parses a balance sheet JSON file.

    Args:
        path (str): Path to the JSON file containing balance sheet data

    Returns:
        dict: Parsed JSON data as a dictionary

    Raises:
        FileNotFoundError: If the specified file does not exist
    """
    try:
        with open('balance_sheet_payload.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Balance sheet json file not found")
        raise FileNotFoundError(f"Balance sheet json file not found at {path}")



def validate_balance_sheet_json_schema(balance_sheet_data: dict) -> None:
    """
    Validates that the balance sheet data conforms to the expected JSON schema.

    Args:
        balance_sheet_data (dict): Dictionary containing the balance sheet data

    Raises:
        jsonschema.exceptions.ValidationError: If the data does not conform to the schema

    Note:
        Currently only validates the top level structure. In a production environment,
        you would want to validate the complete nested structure.
    """
    # In the interest of time, we'll just validate the top level of the json
    # You would want to validate the entire json schema in a real world scenario
    schema = {
        "type": "object",
        "properties": {
            "assets": {"type": "object"},
            "liabilities": {"type": "object"},
            "equity": {"type": "object"},
        },
        "required": ["assets", "liabilities", "equity"],
    }

    jsonschema.validate(balance_sheet_data, schema)
    logger.info("Balance sheet json schema validation passed")


def validate_balance_sheet_equation(balance_sheet_data: dict) -> None:
    """
    Validates that the balance sheet equation (Assets = Liabilities + Equity) holds true
    and that all parent node values equal the sum of their children.

    Args:
        balance_sheet_data (dict): Dictionary containing the balance sheet data

    Returns:
        float: Total assets value

    Raises:
        ValueError: If any parent node's value does not equal the sum of its children
        AssertionError: If assets do not equal liabilities plus equity

    Note:
        Allows for small floating point rounding differences (up to 0.01)
    """
    def validate_node_sum(node: dict) -> float:
        """Validates that a node's value equals the sum of its children's values."""
        # Convert node value to float
        node_value = float(node["value"])
        
        # If node has no children, return its value
        if "items" not in node:
            return node_value
            
        # Calculate sum of children
        children_sum = sum(validate_node_sum(child) for child in node["items"])
        
        # Check if node value matches children sum (allowing for small float rounding differences)
        if abs(node_value - children_sum) > 0.01:
            logger.error(f"Value mismatch for {node['name']}: node value = {node_value}, sum of children = {children_sum}")
            raise ValueError(f"Balance sheet validation failed: {node['name']} value does not match sum of its children")
            
        return node_value

    # Validate each major section
    assets_value = validate_node_sum(balance_sheet_data["assets"])
    liabilities_value = validate_node_sum(balance_sheet_data["liabilities"]) 
    equity_value = validate_node_sum(balance_sheet_data["equity"])

    assert assets_value == liabilities_value + equity_value, "Assets do not equal liabilities plus equity"

    logger.info("All parent-child sums validated successfully")
    
    # Return total assets for potential further validation
    return assets_value
