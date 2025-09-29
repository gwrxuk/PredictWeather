from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()

class PolicyQuoteRequest(BaseModel):
    location: str
    coverage_amount: float
    event_type: str
    duration_days: int
    risk_factors: Dict[str, Any]

class ClaimRequest(BaseModel):
    policy_id: str
    event_type: str
    damage_description: str
    estimated_damage: float
    supporting_data: Dict[str, Any]

@router.post("/quote")
async def get_insurance_quote(request: PolicyQuoteRequest):
    """Get insurance quote for weather protection"""
    try:
        # Calculate premium based on risk factors
        base_rate = 0.05  # 5% base rate
        
        # Risk multipliers
        risk_multipliers = {
            "flood": 1.5,
            "drought": 1.2,
            "storm": 2.0,
            "extreme_temperature": 1.3,
            "hail": 1.8
        }
        
        event_multiplier = risk_multipliers.get(request.event_type.lower(), 1.0)
        duration_multiplier = min(2.0, request.duration_days / 365)  # Max 2x for full year
        
        premium = request.coverage_amount * base_rate * event_multiplier * duration_multiplier
        
        return {
            "success": True,
            "quote": {
                "policy_type": f"{request.event_type}_protection",
                "location": request.location,
                "coverage_amount": request.coverage_amount,
                "premium": round(premium, 2),
                "duration_days": request.duration_days,
                "event_type": request.event_type,
                "risk_assessment": {
                    "base_rate": base_rate,
                    "event_multiplier": event_multiplier,
                    "duration_multiplier": duration_multiplier,
                    "overall_risk": "medium"
                },
                "terms": {
                    "deductible": request.coverage_amount * 0.1,  # 10% deductible
                    "payout_trigger": "verified_weather_event",
                    "max_payout": request.coverage_amount,
                    "claim_processing": "automated_blockchain"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insurance quote: {str(e)}")

@router.post("/policies")
async def create_insurance_policy(policy_data: Dict[str, Any]):
    """Create a new insurance policy"""
    try:
        policy_id = f"policy_{hash(str(policy_data))}"
        
        return {
            "success": True,
            "policy_id": policy_id,
            "message": "Insurance policy created successfully",
            "policy": {
                "id": policy_id,
                "status": "active",
                "created_at": "2024-01-01T12:00:00Z",
                "blockchain_tx": f"0x{hash(policy_id):x}",
                **policy_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating insurance policy: {str(e)}")

@router.get("/policies/{user_address}")
async def get_user_policies(user_address: str):
    """Get all policies for a user"""
    try:
        # Mock data - in real implementation, fetch from blockchain
        policies = [
            {
                "policy_id": "policy_001",
                "type": "flood_protection",
                "location": "Miami, FL",
                "coverage_amount": 100000,
                "premium": 5000,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "expires_at": "2024-12-31T23:59:59Z"
            },
            {
                "policy_id": "policy_002",
                "type": "storm_protection", 
                "location": "Houston, TX",
                "coverage_amount": 75000,
                "premium": 7500,
                "status": "active",
                "created_at": "2024-01-15T00:00:00Z",
                "expires_at": "2025-01-14T23:59:59Z"
            }
        ]
        
        return {
            "success": True,
            "user_address": user_address,
            "total_policies": len(policies),
            "policies": policies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user policies: {str(e)}")

@router.post("/claims")
async def submit_insurance_claim(claim: ClaimRequest):
    """Submit an insurance claim"""
    try:
        claim_id = f"claim_{hash(claim.policy_id + str(claim.estimated_damage))}"
        
        # Automatic claim assessment based on weather data
        auto_approval = claim.estimated_damage < 10000  # Auto-approve small claims
        
        return {
            "success": True,
            "claim_id": claim_id,
            "message": "Insurance claim submitted successfully",
            "claim": {
                "id": claim_id,
                "policy_id": claim.policy_id,
                "status": "approved" if auto_approval else "under_review",
                "estimated_payout": claim.estimated_damage if auto_approval else None,
                "submitted_at": "2024-01-01T12:00:00Z",
                "processing_type": "automated" if auto_approval else "manual_review",
                "blockchain_verification": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting insurance claim: {str(e)}")

@router.get("/claims/{claim_id}")
async def get_claim_status(claim_id: str):
    """Get status of an insurance claim"""
    try:
        # Mock data - in real implementation, fetch from blockchain and database
        claim_status = {
            "claim_id": claim_id,
            "policy_id": "policy_001",
            "status": "approved",
            "payout_amount": 8500,
            "submitted_at": "2024-01-01T12:00:00Z",
            "processed_at": "2024-01-01T14:30:00Z",
            "weather_verification": {
                "verified": True,
                "data_source": "blockchain",
                "verification_count": 3
            },
            "payout_transaction": "0x1234567890abcdef",
            "processing_notes": "Claim automatically approved based on verified weather data"
        }
        
        return {
            "success": True,
            "claim": claim_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching claim status: {str(e)}")

@router.get("/analytics/pool")
async def get_insurance_pool_analytics():
    """Get insurance pool analytics"""
    try:
        analytics = {
            "pool_statistics": {
                "total_pool_value": 1000000,  # $1M
                "total_premiums_collected": 250000,
                "total_claims_paid": 150000,
                "active_policies": 150,
                "pool_utilization": 0.15  # 15%
            },
            "risk_distribution": {
                "flood": 0.35,
                "storm": 0.25,
                "drought": 0.20,
                "extreme_temperature": 0.15,
                "hail": 0.05
            },
            "geographic_distribution": {
                "texas": 0.30,
                "florida": 0.25,
                "california": 0.20,
                "louisiana": 0.15,
                "other": 0.10
            },
            "performance_metrics": {
                "claim_approval_rate": 0.85,
                "average_claim_processing_time": "2.5 hours",
                "customer_satisfaction": 4.2,
                "fraud_detection_rate": 0.02
            }
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "last_updated": "2024-01-01T12:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching insurance analytics: {str(e)}")

@router.get("/risk-assessment/{location}")
async def get_location_risk_assessment(location: str):
    """Get risk assessment for a specific location"""
    try:
        # Mock risk assessment - in real implementation, use AI and historical data
        risk_assessment = {
            "location": location,
            "overall_risk_score": 7.2,  # Out of 10
            "risk_factors": {
                "flood_risk": {
                    "score": 8.5,
                    "factors": ["proximity_to_water", "elevation", "drainage"],
                    "historical_events": 3,
                    "trend": "increasing"
                },
                "storm_risk": {
                    "score": 6.8,
                    "factors": ["wind_patterns", "pressure_systems", "seasonal_patterns"],
                    "historical_events": 5,
                    "trend": "stable"
                },
                "drought_risk": {
                    "score": 4.2,
                    "factors": ["precipitation_patterns", "temperature_trends", "soil_conditions"],
                    "historical_events": 1,
                    "trend": "decreasing"
                },
                "extreme_temperature_risk": {
                    "score": 7.8,
                    "factors": ["climate_change", "urban_heat_island", "seasonal_extremes"],
                    "historical_events": 4,
                    "trend": "increasing"
                }
            },
            "recommendations": {
                "suggested_coverage": 75000,
                "priority_protections": ["flood", "extreme_temperature"],
                "mitigation_strategies": ["flood_barriers", "cooling_systems", "early_warning"]
            }
        }
        
        return {
            "success": True,
            "risk_assessment": risk_assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing risk assessment: {str(e)}")
