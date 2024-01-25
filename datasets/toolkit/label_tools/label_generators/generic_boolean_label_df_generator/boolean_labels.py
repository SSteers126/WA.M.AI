def generate_boolean_dtype_dict(label_columns: list[str] | tuple[str]) -> dict:
    label_dtype_dict = {"file_name": str}
    for column in label_columns:
        label_dtype_dict[column] = bool

    return label_dtype_dict
