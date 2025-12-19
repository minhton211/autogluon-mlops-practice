import pytest
from scripts.dataloader.factory import load_datasets


@pytest.mark.parametrize(
    "dataset_name",
    [
        "DummyDataset",
    ],
)
def test_dataset_loader(dataset_name):
    df = load_datasets([dataset_name])
    assert not df.empty, f"Dataset '{dataset_name}' could not be loaded properly."
