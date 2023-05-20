import requests
import json
import os
import solcx

from dotenv_vault import load_dotenv

load_dotenv()

ETHSCAN_API_KEY = os.getenv("ETHSCAN_API_KEY")
SOURCE_PATH = "./sc_source"

BALANCER_V2_POOL = "0xddce7b2c3f7Fbc4F1eAb24970c3fd26fEe1FF80F"

MATIC_TOKEN = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"
UFRAGMENT_TOKEN = "0x27C70Cd1946795B66be9d954418546998b546634"
VISR_TOKEN = "0xF938424F7210f31dF2Aee3011291b658f872e91e"
PSI_TOKEN = "0xD4Cb461eACe80708078450e465881599d2235f1A"
FVT_TOKEN = "0x45080a6531d671DDFf20DB42f93792a489685e32"

UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
ONEINCH_ROUTER = "0x1111111254fb6c44bAC0beD2854e76F90643097d"
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"


def retrieve_code(addr):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": addr,
        "apikey": ETHSCAN_API_KEY
    }

    resp = requests.request('GET', 'https://api.etherscan.io/api', params=params)

    return resp.json()['result'][0]


def get_abi(content):
    abi = json.loads(content["ABI"])
    return abi


def get_constructor_params_from_file(path):
    with open(path) as file:
        return json.load(file)


def write_json(path, content):
    with open(path, "w") as file:
        file.write(json.dumps(content, indent=4))


def get_sc_library(sc):
    start = sc.find("\nlibrary ")
    if start == -1:
        return sc
    end = sc.find("\ncontract ", start)
    end2 = sc.find("\ninterface ", start)
    if end == -1 or (end2 < end and end2 != -1):
        end = end2
    end3 = sc.find("\nabstract contract ", start)
    if end == -1 or (end3 < end and end3 != -1):
        end = end3
    library = sc[start:end]
    library = library.replace(" public ", " internal ")
    return sc[:start] + library + sc[end:]


def write_sol(path, addr, content):
    if not os.path.exists(f"{path}/{content['ContractName']}_{addr}"):
        os.mkdir(f"{path}/{content['ContractName']}_{addr}")
    try:
        scs = content["SourceCode"]
        if type(scs) is str and scs.startswith("{{"):
            scs = scs[1:-1]
        sc_list = get_sc(scs)
        for sc in sc_list:
            file_path = f"{path}/{content['ContractName']}_{addr}/{os.path.basename(sc[0])}"
            with open(file_path, "w") as file:
                code = change_imports(sc[1])
                code = get_sc_library(code)
                file.write(code)
            if f"contract {content['ContractName']} " in sc[1]:
                contract_path = os.path.basename(sc[0])
    except Exception:
        sc = content["SourceCode"]
        file_path = f"{path}/{content['ContractName']}_{addr}/{content['ContractName']}.sol"
        sc = get_sc_library(sc)
        with open(file_path, "w") as file:
            file.write(sc)
        contract_path = f"{content['ContractName']}.sol"

    return contract_path


def change_imports(sc):
    lines = sc.split("\n")
    new_lines = [change_import(line) for line in lines]
    return "\n".join(new_lines)


def change_import(line):
    if line.startswith("import"):
        elements = line.split()
        prefix = " ".join(elements[:-1])
        return f'{prefix} {elements[-1][-2]}./{os.path.basename(elements[-1])}'
    return line


def get_sc(scs):
    scs = json.loads(scs)
    if "sources" in scs:
        scs = scs["sources"]
    return [(sc_name, sc["content"]) for sc_name, sc in scs.items()]


def save_to_file(filepath, content):
    with open(filepath, "w") as file:
        file.write(content)


def get_version(content):
    return content["CompilerVersion"].split("+")[0][1:]


def compile_sol(path, content):
    version = get_version(content)
    contract = content['ContractName']
    solcx.install_solc(version)
    result = solcx.compile_files([f"{path}/{contract}/{contract}.sol"], solc_version=version,
                                 output_values=["bin-runtime"])
    print(result)


if __name__ == '__main__':
    addr = "0xb5fe099475d3030dde498c3bb6f3854f762a48ad"
    res = retrieve_code(addr)
    write_json(f"{SOURCE_PATH}/json/{res['ContractName']}_{addr}.json", res)
    write_sol(f"{SOURCE_PATH}/sol", addr, res)
    # compile_sol(f"{SOURCE_PATH}/sol", res)
    # abi = get_abi(res)
    # write_json(f"{SOURCE_PATH}/abi/{res['ContractName']}.json", abi)
    # args = get_constructor_params_from_file(res)
    # write_json("./tests/token/tmp/args.txt", args)
    # save_to_file("./tests/token/tmp/args.txt", args)
