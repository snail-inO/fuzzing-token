import Web3 from "web3";
import dotenv from "dotenv";
import { promises as fs } from "fs";

dotenv.config()
const ETHEREUM_MAINNET_RPC = process.env.ETHEREUM_MAINNET_RPC

const l1Source = new Web3(ETHEREUM_MAINNET_RPC);

const decodeArgs = (inputs, args) => {
  return l1Source.eth.abi.decodeParameters(inputs, "0x" + args);
};

const getAbi = async (filePath) => {
  const file = await fs.readFile(filePath);
  const abis = JSON.parse(file);
  for (const abi of abis) {
    if (abi.type == "constructor") {
      return abi;
    }
  }

  return null;
};

const writeJson = async (data, filename) => {
  await fs.writeFile(
    filename,
    JSON.stringify(data, undefined, 2),
    (e) => console.log
  );
};

const main = async () => {
  const filePath = process.argv[2];
  const argFilePath = "./tests/token/tmp/args.txt";
  const abi = await getAbi(filePath);
  const file = await fs.readFile(argFilePath);
  const args = decodeArgs(abi.inputs, file.toString());
  await writeJson(args, "./tests/token/tmp/args.json");
};

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
