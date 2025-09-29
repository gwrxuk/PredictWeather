from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..services.blockchain_service import blockchain_service

router = APIRouter()

# Pydantic models
class WeatherDataSubmission(BaseModel):
    location: str
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    precipitation: float
    weather_type: str
    ipfs_hash: Optional[str] = ""

class InsurancePolicyCreate(BaseModel):
    location: str
    event_type: int  # 0=FLOOD, 1=DROUGHT, 2=STORM, 3=EXTREME_TEMPERATURE, 4=HAIL
    coverage_amount: float  # in ETH
    threshold: float
    duration: int  # in seconds
    premium: float  # in ETH

class ResourceRequest(BaseModel):
    location: str
    resource_type: int  # 0=FOOD, 1=WATER, 2=MEDICAL, 3=SHELTER, 4=EVACUATION, 5=EQUIPMENT
    quantity: int
    priority: int  # 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
    description: str

@router.get("/status")
async def get_blockchain_status():
    """Get blockchain connection status"""
    try:
        is_connected = blockchain_service.is_connected()
        
        if is_connected and blockchain_service.account:
            balance = blockchain_service.get_balance(blockchain_service.account.address)
            return {
                "connected": True,
                "network": blockchain_service.rpc_url,
                "account": blockchain_service.account.address,
                "balance": balance,
                "contracts": {
                    "weather_data_registry": bool(blockchain_service.contracts.get("WeatherDataRegistry")),
                    "weather_insurance": bool(blockchain_service.contracts.get("WeatherInsurance")),
                    "emergency_resource": bool(blockchain_service.contracts.get("EmergencyResourceAllocation"))
                }
            }
        else:
            return {
                "connected": is_connected,
                "network": blockchain_service.rpc_url,
                "account": None,
                "balance": 0,
                "contracts": {}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking blockchain status: {str(e)}")

@router.post("/weather/submit")
async def submit_weather_to_blockchain(data: WeatherDataSubmission):
    """Submit weather data to blockchain"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.submit_weather_data(
            data.location,
            data.temperature,
            data.humidity,
            data.pressure,
            data.wind_speed,
            data.precipitation,
            data.weather_type,
            data.ipfs_hash
        )
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Weather data submitted to blockchain successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit weather data to blockchain")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting weather data: {str(e)}")

@router.get("/weather/{data_id}")
async def get_weather_from_blockchain(data_id: int):
    """Get weather data from blockchain"""
    try:
        weather_data = blockchain_service.get_weather_data(data_id)
        
        if weather_data:
            return {
                "success": True,
                "data": weather_data
            }
        else:
            raise HTTPException(status_code=404, detail="Weather data not found on blockchain")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@router.post("/weather/{data_id}/verify")
async def verify_weather_data(data_id: int):
    """Verify weather data on blockchain"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.verify_weather_data(data_id)
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Weather data verification submitted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to verify weather data")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying weather data: {str(e)}")

@router.get("/weather/recent")
async def get_recent_weather_from_blockchain():
    """Get recent weather data from blockchain"""
    try:
        recent_data_ids = blockchain_service.get_recent_weather_data()
        
        # Fetch detailed data for each ID
        weather_data_list = []
        for data_id in recent_data_ids[:10]:  # Limit to 10 most recent
            weather_data = blockchain_service.get_weather_data(data_id)
            if weather_data:
                weather_data_list.append(weather_data)
        
        return {
            "success": True,
            "total_recent": len(recent_data_ids),
            "data": weather_data_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent weather data: {str(e)}")

@router.post("/insurance/policy")
async def create_insurance_policy(policy: InsurancePolicyCreate):
    """Create a new insurance policy"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.create_insurance_policy(
            policy.location,
            policy.event_type,
            policy.coverage_amount,
            policy.threshold,
            policy.duration,
            policy.premium
        )
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Insurance policy created successfully",
                "policy": {
                    "location": policy.location,
                    "coverage_amount": policy.coverage_amount,
                    "premium": policy.premium
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create insurance policy")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating insurance policy: {str(e)}")

@router.post("/insurance/claim")
async def submit_insurance_claim(policy_id: int, data_id: int):
    """Submit an insurance claim"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.submit_insurance_claim(policy_id, data_id)
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Insurance claim submitted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit insurance claim")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting insurance claim: {str(e)}")

@router.get("/insurance/policies/{user_address}")
async def get_user_policies(user_address: str):
    """Get user's insurance policies"""
    try:
        policy_ids = blockchain_service.get_user_policies(user_address)
        
        return {
            "success": True,
            "user_address": user_address,
            "policy_count": len(policy_ids),
            "policy_ids": policy_ids
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user policies: {str(e)}")

@router.post("/emergency/request")
async def request_emergency_resources(request: ResourceRequest):
    """Request emergency resources"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.request_emergency_resources(
            request.location,
            request.resource_type,
            request.quantity,
            request.priority,
            request.description
        )
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Emergency resource request submitted successfully",
                "request": {
                    "location": request.location,
                    "resource_type": request.resource_type,
                    "quantity": request.quantity,
                    "priority": request.priority
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit resource request")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error requesting emergency resources: {str(e)}")

@router.post("/emergency/approve/{request_id}")
async def approve_resource_request(request_id: int, approved_quantity: int):
    """Approve an emergency resource request"""
    try:
        if not blockchain_service.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain not connected")
        
        tx_hash = blockchain_service.approve_resource_request(request_id, approved_quantity)
        
        if tx_hash:
            return {
                "success": True,
                "transaction_hash": tx_hash,
                "message": "Resource request approved successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to approve resource request")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving resource request: {str(e)}")

@router.get("/emergency/requests/pending")
async def get_pending_emergency_requests(priority: Optional[int] = None):
    """Get pending emergency resource requests"""
    try:
        if priority is not None:
            request_ids = blockchain_service.get_pending_requests_by_priority(priority)
        else:
            # Get all priorities
            all_requests = []
            for p in range(4):  # 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
                requests = blockchain_service.get_pending_requests_by_priority(p)
                all_requests.extend(requests)
            request_ids = all_requests
        
        return {
            "success": True,
            "total_pending": len(request_ids),
            "request_ids": request_ids,
            "priority_filter": priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")

@router.get("/emergency/inventory")
async def get_resource_inventory():
    """Get current emergency resource inventory"""
    try:
        inventory = blockchain_service.get_resource_inventory()
        
        resource_types = ["FOOD", "WATER", "MEDICAL", "SHELTER", "EVACUATION", "EQUIPMENT"]
        
        formatted_inventory = {
            "available": {
                resource_types[i]: inventory["available"][i] if i < len(inventory["available"]) else 0
                for i in range(len(resource_types))
            },
            "reserved": {
                resource_types[i]: inventory["reserved"][i] if i < len(inventory["reserved"]) else 0
                for i in range(len(resource_types))
            }
        }
        
        return {
            "success": True,
            "inventory": formatted_inventory,
            "last_updated": "blockchain"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resource inventory: {str(e)}")

@router.get("/contracts/addresses")
async def get_contract_addresses():
    """Get deployed contract addresses"""
    return {
        "weather_data_registry": blockchain_service.weather_data_registry_address,
        "weather_insurance": blockchain_service.weather_insurance_address,
        "emergency_resource_allocation": blockchain_service.emergency_resource_address,
        "network": blockchain_service.rpc_url
    }
