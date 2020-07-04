def assumption_param_text(pname, ptype, param):
    """
    Extract info from param for pname of ptype and return as HTML string.
    """
    sec1 = param.get('section_1', '')
    if sec1:
        txt = '### {}'.format(param.get('section_2', ''))
    else:
        txt = '### {}'.format(ptype.capitalize())
    txt += '#### `{}`  \n'.format(pname)
    if sec1:
        txt += '_TB Name:_ {}  \n'.format(param['title'])
    else:
        txt += '_Long Name:_ {}  \n'.format(param['title'])
    txt += '_Description:_ {}  \n'.format(param['description'])
    if param.get('notes', ''):
        txt += '_Notes:_ {}  \n'.format(param['notes'])
    txt += '_Default Value:_  \n'
    if param.get('vi_vals', []):
        cols = ', '.join(param['vi_vals'])
        txt += ' for: [{}]  \n'.format(cols)
    for vo in param["value"]:
        labels = " ".join(
            f"{label}={value}" for label, value in vo.items()
            if label not in ("year", "value")
        )
        txt += f"{vo['year']}: {vo['value']} {labels}  "
    txt += '_Valid Range:_'
    validators = param.get("validators", None)
    if validators:
        minval = validators['range']['min']
        maxval = validators['range']['max']
        txt += ' min = {} and max = {}  \n'.format(minval, maxval)
        invalid_action = validators["range"].get('level', 'error')
        txt += '_Out-of-Range Action:_ {}  \n'.format(invalid_action)
    return txt


def assumption_params(ptype, path, text):
    """
    Read assumption parameters of ptype from path, integrate them into text,
    and return the integrated text.
    """
    with open(path) as pfile:
        json_text = pfile.read()
    params = tc.json_to_dict(json_text)
    assert isinstance(params, OrderedDict)
    # construct parameter text for each param
    ptext = ''
    for pname in params:
        if pname == "schema":
            continue
        param = params[pname]
        ptext += assumption_param_text(pname, ptype, param)
    # integrate parameter text into text
    old = '<!-- {}@parameters -->'.format(ptype)
    text = text.replace(old, ptext)
    return text
