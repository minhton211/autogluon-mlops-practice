import sys
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent.parent.resolve()

COL_FORMAT = {"date": "ds", "EC[g/l]": "EC[g/l]", "station_name": "station"}

DATA_PATHS = {
    "DummyDataset": ROOT / "src" / "tests" / "dummy_data.csv",
}
