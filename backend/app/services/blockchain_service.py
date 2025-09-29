from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

class BlockchainService:
    def __init__(self):
        # Initialize Web3 connection
        self.rpc_url = os.getenv("ETHEREUM_RPC_URL", "http://localhost:8545")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add PoA middleware for testnets
        if "goerli" in self.rpc_url.lower() or "sepolia" in self.rpc_url.lower():
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Account configuration
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            self.account = None
        
        # Contract addresses
        self.weather_data_registry_address = os.getenv("WEATHER_DATA_REGISTRY_ADDRESS")
        self.weather_insurance_address = os.getenv("WEATHER_INSURANCE_ADDRESS")
        self.emergency_resource_address = os.getenv("EMERGENCY_RESOURCE_ADDRESS")
        
        # Load contract ABIs
        self.contracts = {}
        self._load_contracts()
    
    def _load_contracts(self):
        """Load contract ABIs and create contract instances"""
        contract_files = {
            "WeatherDataRegistry": "WeatherDataRegistry.json",
            "WeatherInsurance": "WeatherInsurance.json", 
            "EmergencyResourceAllocation": "EmergencyResourceAllocation.json"
        }
        
        for contract_name, filename in contract_files.items():
            try:
                # Load ABI from compiled contract
                abi_path = f"../blockchain/artifacts/contracts/{filename}"
                if os.path.exists(abi_path):
                    with open(abi_path, 'r') as f:
                        contract_json = json.load(f)
                        abi = contract_json.get('abi', [])
                        
                        # Create contract instance if address is available
                        address_key = f"{contract_name.upper()}_ADDRESS"
                        contract_address = os.getenv(address_key)
                        
                        if contract_address and abi:
                            self.contracts[contract_name] = self.w3.eth.contract(
                                address=contract_address,
                                abi=abi
                            )
            except Exception as e:
                print(f"Failed to load contract {contract_name}: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_balance(self, address: str) -> float:
        """Get ETH balance for an address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    def send_transaction(self, contract_function, *args, **kwargs) -> Optional[str]:
        """Send a transaction to a smart contract"""
        if not self.account:
            raise ValueError("No account configured for transactions")
        
        try:
            # Build transaction
            transaction = contract_function(*args, **kwargs).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
        
        except Exception as e:
            print(f"Transaction failed: {e}")
            return None
    
    # Weather Data Registry Functions
    def submit_weather_data(self, location: str, temperature: float, humidity: float,
                          pressure: float, wind_speed: float, precipitation: float,
                          weather_type: str, ipfs_hash: str = "") -> Optional[str]:
        """Submit weather data to blockchain"""
        if "WeatherDataRegistry" not in self.contracts:
            raise ValueError("WeatherDataRegistry contract not loaded")
        
        contract = self.contracts["WeatherDataRegistry"]
        
        # Convert float values to integers (multiply by 100 for precision)
        temp_int = int(temperature * 100)
        humidity_int = int(humidity)
        pressure_int = int(pressure)
        wind_int = int(wind_speed * 100)
        precip_int = int(precipitation * 100)
        
        return self.send_transaction(
            contract.functions.submitWeatherData,
            location, temp_int, humidity_int, pressure_int,
            wind_int, precip_int, weather_type, ipfs_hash
        )
    
    def verify_weather_data(self, data_id: int) -> Optional[str]:
        """Verify weather data on blockchain"""
        if "WeatherDataRegistry" not in self.contracts:
            raise ValueError("WeatherDataRegistry contract not loaded")
        
        contract = self.contracts["WeatherDataRegistry"]
        return self.send_transaction(contract.functions.verifyWeatherData, data_id)
    
    def get_weather_data(self, data_id: int) -> Optional[Dict]:
        """Get weather data from blockchain"""
        if "WeatherDataRegistry" not in self.contracts:
            return None
        
        try:
            contract = self.contracts["WeatherDataRegistry"]
            result = contract.functions.getWeatherData(data_id).call()
            
            return {
                "id": result[0],
                "location": result[1],
                "temperature": result[2] / 100.0,  # Convert back from integer
                "humidity": result[3],
                "pressure": result[4],
                "wind_speed": result[5] / 100.0,
                "precipitation": result[6] / 100.0,
                "weather_type": result[7],
                "timestamp": result[8],
                "reporter": result[9],
                "verified": result[10],
                "verification_count": result[11],
                "ipfs_hash": result[12]
            }
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None
    
    def get_recent_weather_data(self) -> List[int]:
        """Get recent weather data IDs"""
        if "WeatherDataRegistry" not in self.contracts:
            return []
        
        try:
            contract = self.contracts["WeatherDataRegistry"]
            return contract.functions.getRecentWeatherData().call()
        except Exception as e:
            print(f"Error getting recent weather data: {e}")
            return []
    
    # Weather Insurance Functions
    def create_insurance_policy(self, location: str, event_type: int, coverage_amount: float,
                              threshold: float, duration: int, premium: float) -> Optional[str]:
        """Create a new insurance policy"""
        if "WeatherInsurance" not in self.contracts:
            raise ValueError("WeatherInsurance contract not loaded")
        
        contract = self.contracts["WeatherInsurance"]
        
        # Convert values
        coverage_wei = self.w3.to_wei(coverage_amount, 'ether')
        premium_wei = self.w3.to_wei(premium, 'ether')
        threshold_int = int(threshold * 100)
        
        return self.send_transaction(
            contract.functions.createPolicy,
            location, event_type, coverage_wei, threshold_int, duration,
            value=premium_wei
        )
    
    def submit_insurance_claim(self, policy_id: int, data_id: int) -> Optional[str]:
        """Submit an insurance claim"""
        if "WeatherInsurance" not in self.contracts:
            raise ValueError("WeatherInsurance contract not loaded")
        
        contract = self.contracts["WeatherInsurance"]
        return self.send_transaction(contract.functions.submitClaim, policy_id, data_id)
    
    def get_user_policies(self, user_address: str) -> List[int]:
        """Get user's insurance policies"""
        if "WeatherInsurance" not in self.contracts:
            return []
        
        try:
            contract = self.contracts["WeatherInsurance"]
            return contract.functions.getUserPolicies(user_address).call()
        except Exception as e:
            print(f"Error getting user policies: {e}")
            return []
    
    # Emergency Resource Allocation Functions
    def request_emergency_resources(self, location: str, resource_type: int, quantity: int,
                                  priority: int, description: str) -> Optional[str]:
        """Request emergency resources"""
        if "EmergencyResourceAllocation" not in self.contracts:
            raise ValueError("EmergencyResourceAllocation contract not loaded")
        
        contract = self.contracts["EmergencyResourceAllocation"]
        return self.send_transaction(
            contract.functions.requestResources,
            location, resource_type, quantity, priority, description
        )
    
    def approve_resource_request(self, request_id: int, approved_quantity: int) -> Optional[str]:
        """Approve a resource request"""
        if "EmergencyResourceAllocation" not in self.contracts:
            raise ValueError("EmergencyResourceAllocation contract not loaded")
        
        contract = self.contracts["EmergencyResourceAllocation"]
        return self.send_transaction(
            contract.functions.approveRequest,
            request_id, approved_quantity
        )
    
    def get_pending_requests_by_priority(self, priority: int) -> List[int]:
        """Get pending resource requests by priority"""
        if "EmergencyResourceAllocation" not in self.contracts:
            return []
        
        try:
            contract = self.contracts["EmergencyResourceAllocation"]
            return contract.functions.getPendingRequestsByPriority(priority).call()
        except Exception as e:
            print(f"Error getting pending requests: {e}")
            return []
    
    def get_resource_inventory(self) -> Dict[str, List[int]]:
        """Get current resource inventory"""
        if "EmergencyResourceAllocation" not in self.contracts:
            return {"available": [], "reserved": []}
        
        try:
            contract = self.contracts["EmergencyResourceAllocation"]
            available, reserved = contract.functions.getResourceInventory().call()
            return {
                "available": list(available),
                "reserved": list(reserved)
            }
        except Exception as e:
            print(f"Error getting resource inventory: {e}")
            return {"available": [], "reserved": []}

# Global blockchain service instance
blockchain_service = BlockchainService()
