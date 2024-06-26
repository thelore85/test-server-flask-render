def filter_unique_dicts(dict_list):
    def dict_to_tuple(d):
        return tuple(sorted(d.items()))
    
    unique_dicts = set()
    
    for d in dict_list:
        dict_tuple = dict_to_tuple(d)
        unique_dicts.add(dict_tuple)
    
    return [dict(t) for t in unique_dicts]