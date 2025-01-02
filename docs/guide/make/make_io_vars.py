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
        return np.where(df.required, '**_Required Input Variable_**  \n', '')

    def description(df):
        return '_Description_: ' + df.desc + '  \n'

    def datatype(df):
        return '_Datatype_: ' + df.type + '  \n'

    def availability(df):
        return '_Availability_: ' + df.availability + '  \n'

    def form_one(row):
        txt = '_IRS Form Location:_  \n'
        formdict = row.form
        for yrange in sorted(formdict.keys()):
            txt += '{}: {}  \n'.format(yrange, formdict[yrange])
        return txt

    def form(df):
        return df.apply(form_one, axis=1)

    # Create DataFrame with one record per variable.
    df = create_io_df(path, iotype)
    # Create txt, a pandas Series.
    txt = title(df)
    if iotype == 'read':
        txt += required(df)
    txt += description(df) + datatype(df)
    if iotype == 'read':
        txt += availability(df)
    txt += form(df)
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
