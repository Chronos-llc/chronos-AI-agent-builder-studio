from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from app.core.integration_monitoring import (
    integration_monitor,
    IntegrationTestResult
)
from app.core.security import get_current_user
from app.models.user import User as UserModel


router = APIRouter()


@router.post("/monitoring/test/{config_id}", response_model=IntegrationTestResult)
async def test_integration(
    config_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Test an integration configuration"""
    try:
        result = await integration_monitor.test_integration(config_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration test failed: {str(e)}")


@router.get("/monitoring/history/{config_id}", response_model=List[IntegrationTestResult])
async def get_test_history(
    config_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get test history for an integration"""
    try:
        history = integration_monitor.get_test_history(config_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get test history: {str(e)}")


@router.get("/monitoring/metrics/{config_id}", response_model=Dict[str, Any])
async def get_performance_metrics(
    config_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get performance metrics for an integration"""
    try:
        metrics = integration_monitor.get_performance_metrics(config_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/monitoring/health/", response_model=Dict[str, Any])
async def get_monitoring_health(
    current_user: UserModel = Depends(get_current_user)
):
    """Get overall monitoring system health"""
    try:
        return {
            "status": "healthy",
            "monitored_integrations": len(integration_monitor.test_history),
            "total_tests": sum(len(tests) for tests in integration_monitor.test_history.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring health: {str(e)}")


@router.post("/monitoring/test-all/", response_model=Dict[str, Any])
async def test_all_integrations(
    current_user: UserModel = Depends(get_current_user)
):
    """Test all configured integrations"""
    try:
        # In a real implementation, this would fetch all integration configs
        # and test each one
        results = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "details": {}
        }
        
        # Mock implementation - test a few sample config IDs
        sample_configs = [1, 2, 3]  # Would be fetched from database
        
        for config_id in sample_configs:
            try:
                result = await integration_monitor.test_integration(config_id)
                results["total_tests"] += 1
                
                if result.success:
                    results["successful_tests"] += 1
                else:
                    results["failed_tests"] += 1
                
                results["details"][str(config_id)] = {
                    "success": result.success,
                    "message": result.message,
                    "response_time": result.response_time
                }
            except Exception as e:
                results["total_tests"] += 1
                results["failed_tests"] += 1
                results["details"][str(config_id)] = {
                    "success": False,
                    "message": str(e),
                    "response_time": 0.0
                }
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test all integrations: {str(e)}")