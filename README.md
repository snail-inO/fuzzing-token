# Fuzzing-token
## Description
This project is for testing ERC20 tokens' reliability using Echidna.
## Prerequisites
- Python
- Node Js
## Usage
1. Install js dependcy packages `npm install`
2. Install python depency packages `pip install py-solc-x python-dotenv-vault`
3. Config .env (Please refer to example.env)
4. Run `./clean.sh` to cleanup enviorment
5. Run `./start.sh` to start testing tokens provided in candidate_list.txt
## Output
All the test results are stored in `tests/token/result/` directory seperately for each token.  
Each path is presented in the form of the following example:  
``
[
    contract.func1(params...),
    contract.func2(params...),
    ...
    contract.funcN(params...)
]
...
[
    another path
]
``

## Limitations
- Do not support solidity version older thant 0.4.25 (limited by Echidna)
- 