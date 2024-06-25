from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List
from pymongo import MongoClient
from datetime import datetime
import os
import secrets
import logging
import hashlib
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production to specific origins (ie- your web domain names as a security measure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

client = MongoClient(os.getenv("DB_URL"))
db = client.error_logs
db.logs.create_index("created_at")
db.analytics.create_index("timestamp")

# Authentication - Please dont use this default sh*t, 
# Itll be painful for me to watch as a cybersecurity professional
VALID_USERNAME = "admin"
VALID_PASSWORD_HASH = hashlib.sha256("password".encode()).hexdigest()

def get_current_time_utc():
    return datetime.utcnow()  # Uses UTC timezone for timestamps

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(hashlib.sha256(credentials.password.encode()).hexdigest(), VALID_PASSWORD_HASH)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Models - Change this if you need more or less info
class ErrorLog(BaseModel):
    project_source: str = Field(..., title="Project Source", max_length=100)
    timestamp: datetime = Field(default_factory=get_current_time_utc, title="Timestamp")
    error_message: str = Field(..., title="Error Message")
    additional_info: str = Field(None, title="Additional Information")

class AnalyticsLog(BaseModel):
    endpoint: str
    method: str
    ip_address: str
    params: dict
    response_status: int
    timestamp: datetime = Field(default_factory=get_current_time_utc)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    ip = request.client.host
    method = request.method
    url = request.url.path
    params = dict(request.query_params)
    
    try:
        response = await call_next(request)
    except Exception as e:
        log_error_to_db("error-logging-api", str(e), {"url": url, "params": params, "ip": ip, "method": method})
        raise e

    response_status = response.status_code
    log_dict = {
        "endpoint": url,
        "method": method,
        "ip_address": ip,
        "params": params,
        "response_status": response_status,
        "timestamp": get_current_time_utc()
    }
    db.analytics.insert_one(log_dict)
    
    return response

def log_error_to_db(project_source, error_message, additional_info=None):
    error_log = {
        "project_source": project_source,
        "timestamp": get_current_time_utc(),
        "error_message": error_message,
        "additional_info": additional_info,
        "created_at": get_current_time_utc()
    }
    db.logs.insert_one(error_log)
    logger.error(f"Error log inserted for project: {project_source} with message: {error_message}")

@app.post("/log", response_model=dict)
async def post_log(log: ErrorLog, username: str = Depends(authenticate)):
    try:
        log_dict = log.dict()
        result = db.logs.insert_one(log_dict)
        logger.info(f"Error log inserted with ID: {result.inserted_id}")
        return {"status": "success", "id": str(result.inserted_id)}
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logs", response_model=List[ErrorLog])
async def get_logs(skip: int = 0, limit: int = 10):
    logs = list(db.logs.find().skip(skip).limit(limit).sort("created_at", -1))
    return logs

@app.get("/current", response_model=List[ErrorLog])
async def get_current_logs():
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = list(db.logs.find({"created_at": {"$gte": start_of_day}}).sort("created_at", -1))
    return logs

@app.get("/analytics", response_model=List[AnalyticsLog])
async def get_analytics(skip: int = 0, limit: int = 10):
    logs = list(db.analytics.find().skip(skip).limit(limit).sort("timestamp", -1))
    return logs

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log_error_to_db("error-logging-api", str(exc), {"url": str(request.url), "method": request.method})
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal Server Error")
