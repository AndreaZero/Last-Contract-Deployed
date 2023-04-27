from web3 import Web3
import requests
from eth_abi import decode_abi
from web3.exceptions import ContractLogicError, BadFunctionCallOutput

# Inserisci il tuo endpoint API Ethereum (Infura, QuickNode, Alchemy, ecc.)
eth_api_url = "https://mainnet.infura.io/v3/IL-TUO-ID-PROJECT"
w3 = Web3(Web3.HTTPProvider(eth_api_url))

# URL per accedere al servizio di Etherscan per la decodifica del bytecode
etherscan_api_url = "https://api.etherscan.io/api"

# La tua chiave API di Etherscan
etherscan_api_key = "LA-TUA-API-ETHERSCAN"

# Numero di blocchi da analizzare (ad esempio, ultimi 1000 blocchi)
num_blocks = 1000
latest_block_number = w3.eth.blockNumber

# Definisci l'interfaccia del contratto per il token ERC20
# Puoi trovare l'interfaccia in formato ABI nella documentazione del token ERC20
# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
contract_interface = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

# Crea un oggetto ContractFactory utilizzando l'interfaccia del contratto
contract_factory = w3.eth.contract(abi=contract_interface)

for i in range(latest_block_number - num_blocks, latest_block_number):
    block = w3.eth.getBlock(i, full_transactions=True)
    for tx in block.transactions:
        if tx['to'] is None:
            contract_address = w3.eth.getTransactionReceipt(tx['hash'])['contractAddress']
            print(f"Contract deployed at block {i}: {contract_address}")
            
            # Recupera il bytecode del contratto
            bytecode = w3.eth.getCode(contract_address).hex()

            # Decodifica il bytecode del contratto utilizzando il servizio di Etherscan
            # Assicurati di aver ottenuto una chiave API valida da Etherscan
            payload = {
                "module": "contract",
                "action": "getsourcecode",
                "address": contract_address,
                "apikey": etherscan_api_key,
            }
            response = requests.get(etherscan_api_url, params=payload).json()

            # Controlla se la risposta è una stringa vuota
            if response:
                contract_name = response['result'][0]['ContractName']
                print(f"Contract Name: {contract_name}")

                try:
                    # Recupera la massima fornitura totale di token
                    contract_instance = contract_factory(address=contract_address)
                    total_supply_wei = contract_instance.functions.totalSupply().call()
                    if total_supply_wei > 0:
                        total_supply_eth = total_supply_wei / 10**18
                        total_supply_formatted = "{:,.0f}".format(total_supply_eth)
                        print(f"Total Supply: {total_supply_formatted}")
                        print("\n")
                    else:
                     print("Total Supply: N/A")
                     print("\n")

                except ContractLogicError:
                    print("Error retrieving total supply")
                    print("\n")
                except BadFunctionCallOutput:
                    print("Unable to decode output from totalSupply")
                    print("\n")
            else:
                print("Cannot decode bytecode")
                print("\n")

