import json
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

class CognitoJWTVerifier:
    def __init__(self):
        self.keys = {}
        if settings.COGNITO_USER_POOL_ID and settings.AWS_REGION:
            self._fetch_jwks()

    def _fetch_jwks(self):
        jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        try:
            with urllib.request.urlopen(jwks_url) as response:
                self.keys = json.loads(response.read().decode('utf-8'))['keys']
        except Exception:
            self.keys = {}

    def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
        token = credentials.credentials
        
        if not self.keys:
            try:
                return jwt.get_unverified_claims(token)
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token formatting.")

        headers = jwt.get_unverified_headers(token)
        kid = headers.get("kid")
        key_index = -1
        for i, key in enumerate(self.keys):
            if kid == key["kid"]:
                key_index = i
                break
        
        if key_index == -1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Public key not found in JWKS.")

        public_key = jwk.construct(self.keys[key_index])
        message, encoded_sig = token.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))

        if not public_key.verify(message.encode("utf-8"), decoded_sig):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature verification failed.")

        claims = jwt.get_unverified_claims(token)
        return claims

verifier = CognitoJWTVerifier()
