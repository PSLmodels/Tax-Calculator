import taxcalc as tc
import pandas as pd
import numpy as np


def make_io_vars(path):
    """ Create string of information for input or output variables.

    Args:
        path: Path to records_variables.json.

    Returns:
        String with all information for all input and output variables.
    """
    def title(df):
        return '###  `' + df.index + '`  \n'

    def required(df):
        return np.where(df.required, '**_Required Input Variable_**  \n', '')

    def description(df):
        return '_Description_: ' + df.desc + '  \n'

    def datatype(df):
        return '_Datatype_: ' + df.type + '  \n'

    def availability:
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
    df = create_io_df(path)
    # Create content.
    df['content'] = (title(df) + required(df) + description(df) + datatype(df) +
        availability(df) + form(df))
    # Add section headers when section changes.
    df['new_section'] = ~df.section.eq(df.section.shift()) & (df.section > '')
    df.content = np.where(df.new_section, '## ' + df.section + '  \n' + df.content,
        df.content)
    # Return single string.
    return '\n\n'.join(df.content)


def create_io_df(path):
    """ Read variables for iotype ('read' for input or 'calc' for output) from
        path, integrate them into text, and return the integrated text.

    Args:
        path: Path to records_variables.json.

    Returns:
        DataFrame including input and output variables.
    """
    # Read json file and convert to a dict.
    with open(path) as vfile:
        json_text = vfile.read()
    variables = tc.json_to_dict(json_text)
    assert isinstance(variables, dict)
    # Create DataFrames for input and output variables.
    indf = pd.DataFrame(iovars['read']).transpose()
    outdf = pd.DataFrame(iovars['calc']).transpose()
    # Add a section title.
    indf['section'] = 'Input Variables'
    outdf['section'] = 'Output Variables'
    # Return both.
    return pd.concat([indf, outdf])
