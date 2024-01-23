from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from model_library.models import UserInformation

class CreateMTRequest(BaseModel):
    user: UserInformation
    deployment_name: str

class DeleteDeployment(BaseModel):
    user_id: str
    namespace: str
    deployment_name: str

class ListDeployment(BaseModel):
    user_id: str
    namespace: str

class ServiceRequest(BaseModel):
    mt_service_url: str
    mt_api_key: Optional[str] = None

class AddAPIToolRequest(ServiceRequest):
    tool_url: str
    tool_routes: Optional[List[str]] = None
    tool_api_key: Optional[str] = None  

class EditToolRequest(BaseModel):
    tool_id: str
    new_description: str


class DeployKalavaiToolRequest(BaseModel):
    tool_id: str
    config: dict

