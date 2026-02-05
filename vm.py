class VirtualMachine:
    def __init__(self):
        self.state = {} # Global state storage: {contract_address: {key: value}}
        self.contracts = {
            "0x01": self.staking_contract,
            "0x02": self.homens_contract
        }

    def execute(self, transaction):
        """Executes a transaction. If it sends data using a special protocol, handle it."""
        # Simple protocol: if tx has 'data' with 'action' and 'contract', execute it.
        # Data format: {"contract": "0x01", "action": "stake", "params": {...}}
        if not transaction.data or not isinstance(transaction.data, dict):
            return

        contract_addr = transaction.data.get("contract")
        if contract_addr in self.contracts:
            self.contracts[contract_addr](transaction)

    def staking_contract(self, tx):
        """System contract for Staking (0x01)."""
        action = tx.data.get("action")
        if action == "stake":
            # In a real chain, we would lock the funds here.
            # Ideally the Blockchain class calls this and updates Consensus.
            # For this prototype, we will just record the state change request.
            print(f"[VM] Staking request from {tx.sender} for {tx.amount}")
            current_stake = self.get_state("0x01", tx.sender) or 0
            self.set_state("0x01", tx.sender, current_stake + tx.amount)

    def homens_contract(self, tx):
        """Home Naming Service (0x02). Register names like 'budi.home'."""
        action = tx.data.get("action")
        if action == "register":
            name = tx.data.get("name")
            if name and name.endswith(".home"):
                if self.get_state("0x02", name) is None:
                    self.set_state("0x02", name, tx.sender)
                    print(f"[VM] Registered {name} to {tx.sender}")
                else:
                    print(f"[VM] Name {name} already taken.")

    def get_state(self, contract, key):
        if contract not in self.state:
            return None
        return self.state[contract].get(key)

    def set_state(self, contract, key, value):
        if contract not in self.state:
            self.state[contract] = {}
        self.state[contract][key] = value

    def resolve_name(self, name: str):
        """Resolves a .home name to an address."""
        if not name.endswith(".home"):
            return None
        return self.get_state("0x02", name)
