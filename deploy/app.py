import argparse
import sys
from pathlib import Path
import pandas as pd
from autogluon.timeseries import TimeSeriesPredictor

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR_TEMPLATE = BASE_DIR / "models" / "autogluonTS" / "{}"


def main(csv_path: str, output_path: str | None = None, model_name: str | None = None):
    if model_name is None:
        raise ValueError("model_name is required")
    model_path = str(BASE_DIR / "models" / "autogluonTS" / model_name)

    predictor = TimeSeriesPredictor.load(model_path)
    predictor.persist(models="all")

    df = pd.read_csv(csv_path)
    predictions = predictor.predict(df)

    if output_path:
        predictions.to_csv(output_path, index=True)
    else:
        predictions.to_csv(sys.stdout, index=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AutoGluon TimeSeries prediction")
    parser.add_argument("--input-csv", required=True, help="Path to input CSV file")
    parser.add_argument(
        "--output-csv", required=False, help="Path to save predictions CSV (optional)"
    )
    parser.add_argument(
        "--model-name", required=True, help="Name of the trained AutoGluon model"
    )
    args = parser.parse_args()
    main(args.input_csv, args.output_csv, args.model_name)
