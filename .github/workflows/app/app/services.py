import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from app.config import settings
from app.models import KYCSubmissionRequest, KYCSubmissionResponse, VerificationStatus

dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

class EKYCService:
    def __init__(self):
        self.table = dynamodb.Table(settings.DYNAMODB_TABLE)
        self.bucket = settings.S3_BUCKET

    def create_verification_record(self, request: KYCSubmissionRequest, user_id: str) -> KYCSubmissionResponse:
        verification_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        s3_key = f"documents/{user_id}/{verification_id}.pdf"

        item = {
            "verification_id": verification_id,
            "user_id": user_id,
            "national_id": request.national_id,
            "full_name": request.full_name,
            "email": request.email,
            "document_type": request.document_type.value,
            "status": VerificationStatus.PENDING.value,
            "s3_key": s3_key,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database persistent failure: {e.response['Error']['Message']}"
            )

        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_key,
                    'ContentType': 'application/pdf'
                },
                ExpiresIn=300
            )
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Storage presigned generation failure: {e.response['Error']['Message']}"
            )

        return KYCSubmissionResponse(
            verification_id=verification_id,
            status=VerificationStatus.PENDING,
            presigned_upload_url=presigned_url,
            created_at=timestamp
        )

    def get_verification_status(self, verification_id: str) -> dict:
        try:
            response = self.table.get_item(Key={"verification_id": verification_id})
            if "Item" not in response:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification request not found.")
            return response["Item"]
        except ClientError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.response['Error']['Message'])

kyc_service = EKYCService()
