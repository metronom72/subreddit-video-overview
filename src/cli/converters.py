import pandas as pd


def convert_data_to_dataframe(data):
    print(f"Original data: {data}")

    # Check if the first element of the tuple is a DataFrame
    if isinstance(data, tuple):
        if isinstance(data[0], pd.DataFrame):
            data = data[0]
        else:
            raise TypeError("The first element of the tuple must be a pandas DataFrame.")
    elif not isinstance(data, pd.DataFrame):
        raise TypeError("The 'data' parameter must be a pandas DataFrame or a tuple containing a DataFrame.")

    print(f"Converted data: {data}")

    return data
