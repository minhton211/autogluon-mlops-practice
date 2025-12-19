import pandas as pd
from .config import DATA_PATHS

def load_dataset_DummyDataset(col_format) -> pd.Series:
    """
    Load and standardize Dummy Dataset.

    Args:
        file_path: Optional custom file path. Uses default if None.

    """

    file_path = DATA_PATHS["DummyDataset"]

    # Read raw data
    df = pd.read_csv(file_path)

    # Rename/transform to standardized format
    df = df.rename(
        columns={
            "timestamp": col_format["date"],
            "item_id": col_format["station_name"],
            "EC[g/l]": col_format["EC[g/l]"],
            # Map other columns as needed
        }
    )

    # Convert date column to datetime
    df[col_format["date"]] = pd.to_datetime(df[col_format["date"]])

    # Select and reorder columns (mandatory first, then others)
    mandatory_cols = [col_format[i] for i in col_format]
    other_cols = [col for col in df.columns if col not in mandatory_cols]
    df = df[mandatory_cols + other_cols]

    return df
