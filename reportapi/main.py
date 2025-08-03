import logging
from fastapi import FastAPI, Request, HTTPException
from jwcrypto.common import JWException
from keycloak import KeycloakOpenID
from fastapi.middleware.cors import CORSMiddleware

#  Конфигурация
KEYCLOAK_SERVER_URL="http://keycloak:8080"
KEYCLOAK_CLIENT_ID="reports-frontend"
KEYCLOAK_REALM_NAME="reports-realm"
KEYCLOAK_CLIENT_SECRET_KEY="oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq"

ROLE_HAS_ACCESS = "prothetic_user"


keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 realm_name=KEYCLOAK_REALM_NAME,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY)

app = FastAPI()

# Настройка CORS политик
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/reports")
async def reports_endpoint(request: Request):
    
    # Разбор токена
    try:
        token = request.headers.get('Authorization').replace('Bearer ', '')
        tokenInfo = keycloak_openid.decode_token(token)
    except Exception as e:
        logging.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получение списка ролей
    try:
        roles = tokenInfo.get("realm_access", {}).get("roles", [])      
    except Exception as e:
        logging.warning(f"Role handling failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Role handling failed")
    
    # Проверка роли
    if ROLE_HAS_ACCESS not in roles:
        raise HTTPException(status_code=403, detail="Access denied")  
    
    return {"report": "User '" + tokenInfo.get('name') + "' got access to reports"}