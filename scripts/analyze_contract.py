import json


def get_constructor(abi):
    constructor = [interface["inputs"] for interface in abi if interface["type"] == "constructor"]
    if len(constructor) == 0:
        return []
    return constructor[0]


def generate_arg(arg):
    match arg:
        case "string":
            return '"Test"'
        case "address":
            return "msg.sender"
        case _:
            return None


def compare_solc_version(version, target):
    versions = version.split('.')
    targets = target.split('.')
    for v, t in zip(versions, targets):
        if int(v) > int(t):
            return True
        elif int(v) == int(t):
            continue
        else:
            return False

    return True


def function_params(func):
    args = []
    for arg in func:
        args.append(arg["type"])

    return args


if __name__ == '__main__':
    with open("./sc_source/abi/ERC20.json") as file:
        abi = json.load(file)
    construct = get_constructor(abi)
    print(function_params(construct))
