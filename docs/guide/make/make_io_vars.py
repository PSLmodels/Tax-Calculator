import taxcalc as tc
import pandas as pd
import numpy as np


def make_io_vars(path, iotype):
    """
    Create string of information for input or output variables.

    Args:
        path: Path to records_variables.json.
        iotype: 'read' to create DataFrame for input variables, 'calc' for
            output variables.

    Returns:
        String with all information for input or output variables.
    """
    def title(df):
        return '##  `' + df.index + '`  \n'

    def required(df):
        is_required = df.required.fillna(False).astype(bool)
        return np.where(is_required, '**_Required Input Variable_**  \n', '')

    def description(df):
        return '_Description_: ' + df.desc + '  \n'

    def datatype(df):
        return '_Datatype_: ' + df.type + '  \n'

    def availability(df):
        return '_Availability_: ' + df.availability + '  \n'

    # Create DataFrame with one record per variable.
    df = create_io_df(path, iotype)
    # Create txt, a pandas Series.
    txt = title(df)
    if iotype == 'read':
        txt += required(df)
    txt += description(df) + datatype(df)
    if iotype == 'read':
        txt += availability(df)
    # Return single string.
    return '\n\n'.join(txt)


def create_io_df(path, iotype):
    """ Create a DataFrame from JSON representing input or output variables.

    Args:
        path: Path to records_variables.json.
        iotype: 'read' to create DataFrame for input variables, 'calc' for
            output variables.

    Returns:
        DataFrame including input and output variables.
    """
    # Read json file and convert to a dict.
    with open(path) as vfile:
        json_text = vfile.read()
    variables = tc.json_to_dict(json_text)
    assert isinstance(variables, dict)
    # Create DataFrames for input and output variables.
    return pd.DataFrame(variables[iotype]).transpose()
