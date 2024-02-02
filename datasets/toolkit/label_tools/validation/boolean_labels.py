from pandas import DataFrame


def find_empty_labels(label_frame: DataFrame) -> list[str]:
    """
    Iterates through a boolean label `DataFrame`, and lists any samples that do not have all labels in the row filled
    with a boolean value.

    :param label_frame: The label `DataFrame` to search for samples without labels
    :return: A list of the `file_name` of samples that do not have all labels filled.
    """
    unlabelled_samples = []

    for row in label_frame.itertuples():
        # Remove index and file name, and check if any of the labels are not boolean.
        if any(not isinstance(val, bool) for val in row[2:]):
            # Add the filename if any labels are not added
            unlabelled_samples.append(row[1])

    return unlabelled_samples

# print(find_empty_labels(read_csv("8_zone_presence_labels.csv")))
