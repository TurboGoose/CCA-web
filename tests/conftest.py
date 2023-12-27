import os

import pandas as pd
import pytest

DATASET_NAME = "dataset.csv"


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {"username": "dude", "sent": ["2023-09-01T12:00:00Z"], "text": ["Hello there!"]}
    )


@pytest.fixture
def sample_dataset_path(sample_dataframe, tmpdir):
    csv_path = os.path.join(tmpdir, DATASET_NAME)
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path
