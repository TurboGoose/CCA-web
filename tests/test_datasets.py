import os
import shutil

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from app import config
from app.datasets import (
    init_dataset_storage,
    write_csv_dataset,
    rename_csv_dataset,
    read_csv_dataset,
    delete_csv_dataset,
)


@pytest.fixture
def temp_dataset_folder(monkeypatch, tmpdir):
    temporary_folder = str(tmpdir / "datasets")
    monkeypatch.setattr(config, "DATASET_FOLDER", temporary_folder)
    os.mkdir(temporary_folder)
    yield temporary_folder


def test_init_dataset_storage(temp_dataset_folder):
    init_dataset_storage()
    assert os.path.exists(temp_dataset_folder)


def test_write_csv_dataset(sample_dataframe, temp_dataset_folder):
    file_path = os.path.join(temp_dataset_folder, "temp_dataset.csv")
    write_csv_dataset(sample_dataframe, file_path)
    assert os.path.exists(file_path)

    loaded_df = pd.read_csv(file_path)
    assert_frame_equal(sample_dataframe, loaded_df)


def test_rename_csv_dataset(sample_dataset_path):
    original_path = sample_dataset_path
    new_name = "new_test.csv"
    new_path = os.path.join(os.path.dirname(original_path), new_name)

    rename_csv_dataset(original_path, new_name)
    assert not os.path.exists(original_path)
    assert os.path.exists(new_path)


def test_rename_dataset_error_if_new_exists(sample_dataset_path):
    new_name = "new_test.csv"
    another_sample_dataset_path = os.path.join(
        os.path.dirname(sample_dataset_path), new_name
    )
    shutil.copy(sample_dataset_path, another_sample_dataset_path)

    with pytest.raises(ValueError):
        rename_csv_dataset(sample_dataset_path, new_name)


def test_delete_csv_dataset(sample_dataset_path):
    delete_csv_dataset(sample_dataset_path)
    assert not os.path.exists(sample_dataset_path)


def test_read_csv_dataset(sample_dataset_path, sample_dataframe):
    loaded_df = read_csv_dataset(sample_dataset_path)
    assert_frame_equal(sample_dataframe, loaded_df)
