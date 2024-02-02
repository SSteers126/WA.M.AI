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


def false_default_boolean_labels_to_none(df: DataFrame) -> DataFrame:
    """
    Converts a label file created when the default label was `False`, and removes the default labels to keep
    compatability with the new system. This function assumes that labelling has stopped when
    no more True labels are present, and removes all labels in rows after that point.

    :param df: The `DataFrame` to remove default labels from
    :return: The `DataFrame` without default `False` labels
    """
    last_row = 0
    for count, row in enumerate(df.itertuples()):
        if True in row:
            last_row = count

    df.iloc[last_row + 1:, 1:-1] = None

    return df

