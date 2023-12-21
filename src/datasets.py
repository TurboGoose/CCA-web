import os
from datetime import datetime
from html import escape

import numpy as np
import pandas as pd
from pandas import DataFrame

from consts import DATETIME_FORMAT


def write_csv_dataset(dataset: DataFrame, dataset_path: str) -> None:
    dataset.to_csv(dataset_path, index=False)


def rename_csv_dataset(dataset_path: str, new_name: str) -> None:
    new_dataset_path = dataset_path.replace(os.path.basename(dataset_path), new_name)
    if not os.path.exists(dataset_path):
        raise ValueError(f"Cannot rename dataset: file '{dataset_path}' does not exist")
    if os.path.exists(new_dataset_path):
        raise ValueError(
            f"Cannot rename dataset: file '{new_dataset_path}' already exists"
        )
    os.rename(dataset_path, new_dataset_path)


def delete_csv_dataset(dataset_path: str) -> None:
    if os.path.exists(dataset_path):
        os.remove(dataset_path)


def read_csv_dataset(dateset_path: str) -> DataFrame:
    if not os.path.exists(dateset_path):
        raise FileNotFoundError(f"File '{dateset_path}' not exists")
    df = pd.read_csv(dateset_path)
    _substitute_nan_labels_to_none(df)
    return df


def _substitute_nan_labels_to_none(df: DataFrame) -> None:
    if "label" in df:
        df["label"].replace({np.nan: None}, inplace=True)


def transform_and_write_csv_dataset(dataset_path: str) -> None:
    df = read_csv_dataset(dataset_path)
    _add_label_column_if_not_present(df)
    _transform(df)
    write_csv_dataset(df, dataset_path)


def _add_label_column_if_not_present(df: DataFrame) -> None:
    if "label" not in df:
        df["label"] = np.nan


def _transform(df: DataFrame) -> None:
    _format_sent_datetime(df)
    _escape_html_in_text(df)


def _format_sent_datetime(df: DataFrame) -> None:
    if not _is_datetime_has_target_format(df.loc[0]["sent"]):
        df["sent"] = df["sent"].apply(
            lambda dt: _format_datetime(_parse_iso_datetime(dt))
        )


def _is_datetime_has_target_format(dt: str) -> bool:
    try:
        datetime.strptime(dt, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


def _parse_iso_datetime(dt: str) -> datetime:
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


def _format_datetime(dt: datetime) -> str:
    return datetime.strftime(dt, DATETIME_FORMAT)


def _escape_html_in_text(df):
    df["text"] = df["text"].apply(lambda t: escape(t))
