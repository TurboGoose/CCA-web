import os
import shutil

import pytest

from app import config
from app.indexer import init_index_storage, create_index, delete_index, rename_index
from conftest import DATASET_NAME


@pytest.fixture
def temp_index_folder(monkeypatch, tmpdir):
    temporary_folder = str(tmpdir / "index")
    monkeypatch.setattr(config, "INDEX_FOLDER", temporary_folder)
    os.mkdir(temporary_folder)
    yield temporary_folder


def test_init_index_storage(temp_index_folder):
    init_index_storage()
    assert os.path.exists(temp_index_folder)


def test_create_index(temp_index_folder, sample_dataset_path):
    expected_index_folder = os.path.join(temp_index_folder, DATASET_NAME)
    assert not os.path.exists(expected_index_folder)
    create_index(sample_dataset_path)
    assert os.path.exists(expected_index_folder)
    assert len(os.listdir(expected_index_folder)) > 0


def test_delete_index(temp_index_folder, sample_dataset_path):
    create_index(sample_dataset_path)
    expected_index_folder = os.path.join(temp_index_folder, DATASET_NAME)
    assert os.path.exists(expected_index_folder)
    delete_index(sample_dataset_path)
    assert not os.path.exists(expected_index_folder)


def test_rename_index(temp_index_folder, sample_dataset_path):
    create_index(sample_dataset_path)
    new_name = "renamed_index"
    rename_index(sample_dataset_path, new_name)
    assert not os.path.exists(os.path.join(temp_index_folder, DATASET_NAME))
    assert os.path.exists(os.path.join(temp_index_folder, new_name))


def test_rename_index_error_if_new_exists(temp_index_folder, sample_dataset_path):
    create_index(sample_dataset_path)
    new_name = "already_exists"
    another_sample_dataset_path = os.path.join(os.path.dirname(sample_dataset_path), new_name)
    shutil.copy(sample_dataset_path, another_sample_dataset_path)
    create_index(another_sample_dataset_path)

    with pytest.raises(ValueError):
        rename_index(sample_dataset_path, new_name)


def test_rename_index_error_if_old_does_not_exist(temp_index_folder, sample_dataset_path):
    with pytest.raises(ValueError):
        rename_index(sample_dataset_path, "should_fail")
