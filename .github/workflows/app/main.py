from fastapi import FastAPI, Depends, status
from mangum import Mangum
from app.models import KYCSubmissionRequest, KYCSubmissionResponse
from app.auth import verifier
from app.services import kyc_service

app = FastAPI(
    title="Enterprise Serverless Financial eKYC API",
    description="Identity verification microservice integrated with AWS Lambda, Cognito, and DynamoDB.",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "HEALTHY", "service": "ekyc-identity-processor"}

@app.post("/v1/kyc/verify", response_model=KYCSubmissionResponse, status_code=status.HTTP_201_CREATED)
def initiate_kyc_verification(
    payload: KYCSubmissionRequest,
    user_claims: dict = Depends(verifier.verify_token)
):
    user_id = user_claims.get("sub", "anonymous_user")
    return kyc_service.create_verification_record(request=payload, user_id=user_id)

@app.get("/v1/kyc/verify/{verification_id}", status_code=status.HTTP_200_OK)
def get_kyc_verification_status(
    verification_id: str,
    user_claims: dict = Depends(verifier.verify_token)
):
    return kyc_service.get_verification_status(verification_id=verification_id)

handler = Mangum(app)
