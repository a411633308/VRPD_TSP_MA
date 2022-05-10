import random
import gurobipy as gp

def nofly_generator(_dist, _points):
    _nofly_factor = gp.tupledict(
        [(i, 1) for i in _dist]
    )
    a = [random.randint(0, len(_nofly_factor.keys())) for i in range(random.randint(0, int(len(_points) / 2)))]
    i = 0
    for j in _nofly_factor:
        if i in a:
            _nofly_factor[j] = 0
        i += 1
    return _nofly_factor


# input: relevant dictionary to search for; the location of the node;
# output: the role of the node
def nodes_role(_nodes_list, _node):
    if _node in _nodes_list['depot']:
        return 'depot'
    elif _node in _nodes_list['docking hubs']:
        return 'docking hubs'
    elif _node in _nodes_list['customer']:
        return 'customer'
    else:
        return 0


# input: relevant dictionary to search for; the location of the node;
# output: the index of the node
def nodes_index(_nodes_list, _node):
    return [k for k in _nodes_list if _nodes_list[k] == _node]


def routes_role(_distance: dict, _role_list: dict, _index_list: dict, _role: str):
    return  [i for i in _distance.keys() if nodes_role(_role_list, _index_list[i[0]]) == _role or \
                                           nodes_role(_role_list, _index_list[i[1]]) == _role]