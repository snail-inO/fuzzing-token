import retrieve_code
import generate_test
import analyze_contract

import os
import shutil
import sys


SOURCE_PATH = "./sc_source"
TEST_PATH = "./tests/token"


def get_contract(addr, path, dst_path):
    contract = retrieve_code.retrieve_code(addr)
    retrieve_code.write_json(f"{path}/json/{contract['ContractName']}_{addr}.json", contract)
    contract_path = retrieve_code.write_sol(f"{path}/sol", addr, contract)
    abi = retrieve_code.get_abi(contract)
    retrieve_code.write_json(f"{path}/abi/{contract['ContractName']}_{addr}.json", abi)
    retrieve_code.save_to_file(f'{dst_path}/tmp/args.txt', contract["ConstructorArguments"])
    os.system(f'node decode_args.js {path}/abi/{contract["ContractName"]}_{addr}.json')

    return contract, abi, contract_path


def preprocess(contract_name, contract_path, addr, abi, version, dst_path):
    constructor = analyze_contract.get_constructor(abi)
    params = analyze_contract.function_params(constructor)
    args = None

    if len(params) != 0:
        args = generate_test.filter_params_from_file(f'{dst_path}/tmp/args.json')
    file_path = f"./tmp/{contract_name}_{addr}/{contract_path}"
    with open(generate_test.TOKEN_TEST_TEMPLATE) as file:
        template = file.readlines()
    generate_test.add_imports(template, file_path, contract_name)
    if not analyze_contract.compare_solc_version(version, "0.5.0"):
        generate_test.remove_constructor(template)
    else:
        generate_test.set_constructor(template, contract_name, params, args)
    generate_test.save_test(f'{dst_path}/{contract_name}_test.sol', template)


def start_test(source_path, test_path, contract_name, addr, solc_version, abi):
    pass_counter = 0
    config_file = f'{test_path}/config.yaml'
    result_path = f"{test_path}/tmp/result.json"
    source = f'{source_path}/sol/{contract_name}_{addr}'
    dst = f'{test_path}/tmp/{contract_name}_{addr}'
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(source, dst)
    shutil.copyfile('./test_template/token_config.yaml', f'{test_path}/config.yaml')
    os.system(f"solc-select install {solc_version}")
    os.system(f"solc-select use {solc_version}")
    while pass_counter < 3:
        print(pass_counter)
        os.system(f'echidna {test_path}/{contract_name}_test.sol --contract TokenTest --config {config_file} --format json > {result_path}')
        # os.system(f'echidna {test_path}/{contract_name}_test.sol --contract TokenTest --config {config_file}')
        edge = generate_test.generate_edge_from_result(result_path)
        if edge is None:
            pass_counter += 1
            continue
        else:
            generate_test.save_edge(f'{test_path}/result/{contract_name}_{addr}.txt', edge)
            generate_test.add_func_filter(config_file, edge, abi)
            pass_counter = 0
    shutil.rmtree(dst)
    os.remove(f'{test_path}/{contract_name}_test.sol')


if __name__ == '__main__':
    addr = sys.argv[1]
    print(addr)
    contract, abi, contract_path = get_contract(addr, SOURCE_PATH, TEST_PATH)
    version = retrieve_code.get_version(contract)
    if not analyze_contract.compare_solc_version(version, "0.4.25"):
        print("skipped contract version older thant 0.4.25")
        exit()
    contract_name = contract['ContractName']
    preprocess(contract_name, contract_path, addr, abi, version, TEST_PATH)
    start_test(SOURCE_PATH, TEST_PATH, contract_name, addr, version, abi)
