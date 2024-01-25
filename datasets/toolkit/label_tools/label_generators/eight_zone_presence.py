from . import generic_boolean_label_df_generator
from .generic_boolean_label_df_generator.boolean_labels import generate_boolean_dtype_dict

DF_COLUMNS = ("file_name",
              "b1", "b2", "b3", "b4",
              "b5", "b6", "b7", "b8")

DF_DTYPES = generate_boolean_dtype_dict(DF_COLUMNS[1:])


def generate_eight_zone_label_df(label_list: list[tuple[str, str]]):
    return generic_boolean_label_df_generator.generate_empty_label_df(label_list, DF_COLUMNS)
