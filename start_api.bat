@echo off
title Oracle EBS Mock Leave Management API Server
echo =====================================================================
echo Starting Oracle EBS Mock API Gateway on http://localhost:8000
echo Interactive Swagger Documentation: http://localhost:8000/docs
echo OpenAPI JSON: http://localhost:8000/openapi.json
echo =====================================================================
cd /d "D:\copilot_oracle_leave_system"
python -m uvicorn mock_oracle_ebs_api.main:app --host 0.0.0.0 --port 8000 --reload
pause
