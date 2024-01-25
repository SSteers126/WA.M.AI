from pathlib import Path

from pandas import DataFrame


def save_label_df(df: DataFrame, path: Path | str):
    """
    A simple helper function to ensure all label files are consistently saved.
    Saves a dataframe without an index, ensuring the file is only open as long as needed.

    :param df: The `DataFrame` to save
    :param path: The label_path of the file to save the `DataFrame` to.
    :return: `None`
    """
    with open(path, "w") as label_file:
        df.to_csv(label_file, index=False)
