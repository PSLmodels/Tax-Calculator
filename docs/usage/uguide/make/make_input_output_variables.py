

def var_text(vname, iotype, variable):
    """
    Extract info from variable for vname of iotype
    and return info as HTML string.
    """
    if iotype == 'read':
        txt = '## `{}`'.format(vname)
        if 'required' in variable:
            txt += '*'
    else:
        txt = '## `{}`'.format(vname)
    txt += '_Description:_ {}  \n'.format(variable['desc'])
    if variable['type'] == 'float':
        vtype = 'real'
    elif variable['type'] == 'int':
        vtype = 'integer'
    else:
        msg = ('{} variable {} has '
               'unknown type={}  \n'.format(iotype, vname, variable['type']))
        raise ValueError(msg)
    txt += '_Datatype:_ {}  \n'.format(vtype)
    if iotype == 'read':
        txt += '_Availability:_ {}  \n'.format(variable['availability'])
    txt += '_IRS Form Location:_'
    formdict = variable['form']
    for yrange in sorted(formdict.keys()):
        txt += '{}: {}  \n'.format(yrange, formdict[yrange])
    return txt


def io_variables(iotype, path, text):
    """
    Read variables for iotype ('read' for input or 'calc' for output)
    from path, integrate them into text, and return the integrated text.
    """
    with open(path) as vfile:
        json_text = vfile.read()
    variables = tc.json_to_dict(json_text)
    assert isinstance(variables, dict)
    # construct variable text
    vtext = ''
    for vname in sorted(variables[iotype].keys()):
        vtext += var_text(vname, iotype, variables[iotype][vname])
    # integrate variable text into text
    old = '<!-- {}@variables -->'.format(iotype)
    text = text.replace(old, vtext)
    return text
