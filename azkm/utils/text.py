def flatten_dict(d: dict):
    f_d = {}
    def __(d: dict, key_prefix: str = ''):
        if isinstance(d, dict):
            for k in d:
                if isinstance(d[k], dict):
                    __(d[k], key_prefix + k + '/')
                elif not isinstance(d[k], str) and isinstance(d[k], list):
                    for idx, val in enumerate(d[k]):
                        suffix = '/' + str(idx) + '/'
                        if len(d[k]) == 1:
                            suffix = '/'
                        __(val, key_prefix + k + suffix)
                else:
                    f_d[key_prefix + k] = d[k]   
        elif isinstance(d, str):  # if you got here from a list of str
            f_d[key_prefix] = d

    __(d) 
    return f_d

def replace_tokens(txt: str, ref_dict: dict):
    # flatten dict
    f_d = flatten_dict(ref_dict)
    
    txt_out = txt
    for k in f_d:
        if f_d[k]:
            txt_out = txt_out.replace('{{'+k+'}}', str(f_d[k]))
    return txt_out

