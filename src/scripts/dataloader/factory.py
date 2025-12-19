# datasets/factory.py
import pandas as pd
from typing import List, Optional

# Import loaders from each dataset
from .loaders import *

from .config import COL_FORMAT

# Registry pattern for extensibility
DATASET_LOADERS = {
    "DummyDataset": load_dataset_DummyDataset,
}


def load_datasets(
    dataset_names: List[str],
    resample_freq: Optional[str] = None,
    resample_agg: str = "max",
    ds_col: str = "ds",
    station_col: str = "station",
) -> pd.DataFrame:
    """
    Load, standardize datetime, normalize timezone, and optionally resample datasets.

    - dataset_names: list of dataset keys from DATASET_LOADERS
    - resample_freq: pandas offset alias (e.g. 'H', 'D', '15T') to resample each station series
      If None, no resampling is performed.
    - resample_agg: aggregation function for resampling (e.g. 'mean', 'sum')
    """

    if not dataset_names:
        raise ValueError("Must provide at least one dataset name")

    dataframes = []
    for name in dataset_names:
        if name not in DATASET_LOADERS:
            raise ValueError(
                f"Unknown dataset: {name}. Available: {list(DATASET_LOADERS.keys())}"
            )

        loader_func = DATASET_LOADERS[name]
        df = loader_func(col_format=COL_FORMAT)

        # Keep only mandatory columns
        df = _validate_and_keep_mandatory_columns(df, name)

        # Convert ds to datetime64[ns] (ensure_datetime_utc should do this, but be defensive)
        df = ensure_datetime_utc(df, ds_col=ds_col, drop_tz=True)
        df[ds_col] = pd.to_datetime(df[ds_col])

        # Resample this dataset before concatenating
        if resample_freq:
            # Use MultiIndex (station, ds) to avoid reset_index name conflicts
            df = df.set_index([station_col, ds_col])

            df = (
                df.groupby(level=0)  # group by station (index level 0)
                .resample(resample_freq, level=1)  # resample on ds (index level 1)
                .agg(resample_agg)
                .reset_index()  # brings back station and ds columns
            )

        dataframes.append(df)

    # Concatenate all (now-resampled) dataframes
    combined_df = pd.concat(dataframes, axis=0, ignore_index=True, sort=False)
    return combined_df


def _validate_and_keep_mandatory_columns(
    df: pd.DataFrame, dataset_name: str
) -> pd.DataFrame:
    """Validate that mandatory columns exist and keep only them."""
    mandatory_columns = [COL_FORMAT[i] for i in COL_FORMAT]
    missing = [col for col in mandatory_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"Dataset '{dataset_name}' is missing mandatory columns: {missing}"
        )

    return df[mandatory_columns].copy()


def ensure_datetime_utc(
    df: pd.DataFrame,
    ds_col: str = "ds",
    source_tz: str = "Asia/Bangkok",
    drop_tz: bool = False,
    as_string: bool = False,
    fmt: str = "%Y-%m-%d %H:%M:%S",
) -> pd.DataFrame:
    """
    Parse and normalize a datetime column to UTC (GMT+0).

    Behavior:
      - If a value is tz-aware, convert it to UTC.
      - If a value is tz-naive, assume it is in `source_tz`, localize to `source_tz`
        then convert to UTC.
      - NaT values remain NaT.
      - Return column as tz-aware UTC (default). If `drop_tz=True`:
        - if `as_string=True` -> return formatted strings in UTC using `fmt`
        - else -> return tz-naive datetimes representing UTC wall time (dtype datetime64[ns])

    Notes:
      - We intentionally avoid pandas `.dt.tz_localize(None)` on tz-aware series for portability;
        instead we format and reparse when dropping tz, which is safe and explicit.
    """
    df = df.copy()
    parsed = pd.to_datetime(df[ds_col], errors="coerce")

    def _to_utc(ts):
        if pd.isna(ts):
            return pd.NaT
        # if pandas Timestamp with tzinfo set
        if getattr(ts, "tzinfo", None) is not None:
            # tz-aware -> convert to UTC
            return ts.tz_convert("UTC")
        # tz-naive -> localize to source_tz then convert
        return pd.Timestamp(ts).tz_localize(source_tz).tz_convert("UTC")

    # Vectorized-ish construction (keeps original index)
    converted = pd.Series((_to_utc(ts) for ts in parsed), index=df.index, name=ds_col)

    if drop_tz:
        if as_string:
            result = converted.dt.strftime(fmt)
        else:
            # Convert to strings in UTC wall time then parse back to tz-naive datetimes
            result = pd.to_datetime(
                converted.dt.strftime(fmt), format=fmt, errors="coerce"
            )
    else:
        # Keep tz-aware UTC timestamps
        result = converted

    df[ds_col] = result
    return df
