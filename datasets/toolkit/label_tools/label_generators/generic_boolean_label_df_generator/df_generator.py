from pandas import DataFrame


def generate_empty_label_df(label_list: list[tuple[str, str]], columns: tuple | list) -> DataFrame:
    """
    A helper function to generate a label `DataFrame` of purely boolean labels with arbitrary columns.

    :param label_list: The list of files to label - note it expects a list with each element containing
    the full file label_path (which is never used), and *then* the file name

    :param columns: The names of columns to use for the `DataFrame`
    (Passed directly to `DataFrame` columns in constructor)

    :return: A new `DataFrame` with each row containing a single sample, and a set of empty labels
    """

    # Each row begins as the sample file name, and each label set to `False`
    row_list = ((dataset_sample[1], *(None for _ in range(len(columns) - 1))) for dataset_sample in label_list)
    label_dataframe = DataFrame(data=row_list, columns=columns)

    return label_dataframe
