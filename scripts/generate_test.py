import json
import os
import retrieve_code

TOKEN_TEST_TEMPLATE = "./test_template/token_test.sol"


def add_imports(template, source_file, contract_name):
    template[5] = template[5].replace("Testee", contract_name)
    template.insert(0, f'import "{source_file}";\n')


def set_constructor(content, contract_name, params, args):
    if len(params) == 0 or args is None:
        return

    elements = content[11].split()
    new_args = preprocess_args(params, args)
    elements.insert(1, f'{contract_name}({", ".join(new_args)})')
    elements.insert(0, "   ")
    elements.append("\n")
    content[11] = " ".join(elements)


def remove_constructor(content):
    del content[11]
    del content[12]
    del content[13]


def preprocess_args(params, args):
    new_args = []
    for param, arg in zip(params, args):
        if param == "string":
            arg = f'"{arg}"'
        new_args.append(arg)

    return new_args


def check_result(path):
    with open(path) as file:
        lines = file.readlines()
        result = json.loads(lines[-1])
    if result["tests"][0]["status"] == "passed":
        return None
    else:
        return result["tests"][0]


def generate_edge_from_result(filepath):
    result = check_result(filepath)
    if result is None:
        return None
    else:
        return get_edge(result)


def get_edge(result):
    return [transaction for transaction in result["transactions"]]


def generate_edge_str(edge):
    return [generate_path(node) for node in edge]


def generate_path(transaction):
    args_str = generate_args_str(transaction["arguments"])
    return f'\tTokenTest.{transaction["function"]}({args_str})'


def generate_args_str(args):
    return ", ".join(args)


def form_edge_str(edge):
    edge_str = ",\n".join(edge)
    return f'[\n{edge_str}\n]\n'


def save_edge(path, edge):
    edge_str = generate_edge_str(edge)
    if not os.path.exists(path):
        with open(path, "x") as file:
            pass
    with open(path, "a") as file:
        file.write(form_edge_str(edge_str))


def add_func_filter(config_file, edge, abi):
    func_name = edge[-1]["function"]
    arg_count = len(edge[-1]["arguments"])
    signature = [generate_func_signature(func) for func in abi if
                 "name" in func and func["name"] == func_name and func["type"] == "function" and arg_count == len(func["inputs"])]
    with open(config_file, "r") as file:
        lines = file.readlines()
        append_func(lines, signature[0])

    with open(config_file, "w") as file:
        file.writelines(lines)


def append_func(lines, signature):
    index = None
    for i in range(len(lines)):
        if lines[i].startswith(']'):
            index = i
            break
    print(f'\t"TokenTest.{signature}",\n')
    lines.insert(index, f'\t"TokenTest.{signature}",\n')


def generate_func_signature(abi):
    params = [param["type"] for param in abi["inputs"]]
    params_str = ",".join(params)
    return f'{abi["name"]}({params_str})'


def filter_params_from_file(path):
    params = retrieve_code.get_constructor_params_from_file(path)
    last = params["__length__"]
    params = [param for i, param in enumerate(params.values()) if i < last]
    return params


def save_test(path, content):
    with open(path, "w") as file:
        file.writelines(content)


if __name__ == '__main__':
    # with open(TOKEN_TEST_TEMPLATE) as file:
    #     test = file.readlines()
    # add_imports(test, './tmp/ERC20.sol', "ERC20")
    # set_constructor(test, "ERC20", ['"Test"', '"Test"'])
    # save_test('./tests/token/ERC20_test.sol', test)
    params = filter_params_from_file("./tests/token/tmp/args.json")