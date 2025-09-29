from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

class EmergencyEventCreate(BaseModel):
    event_type: str
    location: str
    severity: str
    description: str
    affected_population: int
    coordinates: Dict[str, float]

class ResourceAllocationRequest(BaseModel):
    event_id: str
    resource_type: str
    quantity: int
    priority: str
    destination: str

@router.post("/events")
async def create_emergency_event(event: EmergencyEventCreate):
    """Create a new emergency event"""
    try:
        # In a real implementation, this would integrate with emergency management systems
        return {
            "success": True,
            "event_id": f"event_{hash(event.location + event.event_type)}",
            "message": "Emergency event created successfully",
            "event": {
                "type": event.event_type,
                "location": event.location,
                "severity": event.severity,
                "affected_population": event.affected_population
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating emergency event: {str(e)}")

@router.get("/events/active")
async def get_active_emergency_events():
    """Get all active emergency events"""
    try:
        # Mock data - in real implementation, fetch from database
        active_events = [
            {
                "event_id": "event_123",
                "type": "flood",
                "location": "Houston, TX",
                "severity": "high",
                "start_time": "2024-01-01T12:00:00Z",
                "affected_population": 50000,
                "status": "active"
            }
        ]
        
        return {
            "success": True,
            "total_events": len(active_events),
            "events": active_events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emergency events: {str(e)}")

@router.post("/resources/allocate")
async def allocate_emergency_resources(allocation: ResourceAllocationRequest):
    """Allocate emergency resources"""
    try:
        return {
            "success": True,
            "allocation_id": f"alloc_{hash(allocation.event_id + allocation.resource_type)}",
            "message": "Resources allocated successfully",
            "allocation": {
                "event_id": allocation.event_id,
                "resource_type": allocation.resource_type,
                "quantity": allocation.quantity,
                "priority": allocation.priority,
                "destination": allocation.destination
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error allocating resources: {str(e)}")

@router.get("/resources/status")
async def get_resource_status():
    """Get current resource allocation status"""
    try:
        # Mock data - in real implementation, fetch from blockchain and database
        resource_status = {
            "total_resources": {
                "food": 10000,
                "water": 50000,
                "medical": 5000,
                "shelter": 1000
            },
            "allocated_resources": {
                "food": 2000,
                "water": 15000,
                "medical": 1000,
                "shelter": 200
            },
            "available_resources": {
                "food": 8000,
                "water": 35000,
                "medical": 4000,
                "shelter": 800
            }
        }
        
        return {
            "success": True,
            "resource_status": resource_status,
            "last_updated": "2024-01-01T12:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resource status: {str(e)}")

@router.get("/coordination/teams")
async def get_emergency_teams():
    """Get emergency response teams and their status"""
    try:
        teams = [
            {
                "team_id": "team_001",
                "name": "Houston Emergency Response",
                "type": "flood_response",
                "status": "deployed",
                "location": "Houston, TX",
                "members": 25,
                "equipment": ["boats", "rescue_gear", "medical_supplies"]
            },
            {
                "team_id": "team_002", 
                "name": "Weather Monitoring Unit",
                "type": "monitoring",
                "status": "standby",
                "location": "Austin, TX",
                "members": 10,
                "equipment": ["weather_stations", "drones", "communication"]
            }
        ]
        
        return {
            "success": True,
            "total_teams": len(teams),
            "teams": teams
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emergency teams: {str(e)}")

@router.get("/alerts/emergency")
async def get_emergency_alerts():
    """Get current emergency alerts"""
    try:
        alerts = [
            {
                "alert_id": "alert_001",
                "type": "flood_warning",
                "severity": "critical",
                "location": "Houston Metro Area",
                "message": "Severe flooding expected in the next 6 hours. Evacuate low-lying areas immediately.",
                "issued_at": "2024-01-01T10:00:00Z",
                "expires_at": "2024-01-01T22:00:00Z",
                "affected_areas": ["Downtown Houston", "Bayou Area", "Memorial Park"]
            }
        ]
        
        return {
            "success": True,
            "total_alerts": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emergency alerts: {str(e)}")

@router.post("/communication/broadcast")
async def broadcast_emergency_message(message: str, channels: List[str]):
    """Broadcast emergency message through multiple channels"""
    try:
        # In real implementation, integrate with SMS, email, social media APIs
        return {
            "success": True,
            "message_id": f"msg_{hash(message)}",
            "message": "Emergency message broadcasted successfully",
            "channels": channels,
            "estimated_reach": len(channels) * 1000  # Mock reach calculation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error broadcasting message: {str(e)}")
