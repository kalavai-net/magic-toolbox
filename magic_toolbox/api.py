from fastapi import FastAPI, HTTPException, Depends
from starlette.requests import Request

import os
import logging
from typing import Dict, List, Any

from tool_library.client import ToolLibraryClient
from kube_watcher.kube_core import KubeAPI
from model_library.library import ModelLibrary 

from model_library.models import UserInformation, ModelDeploymentCard
from model_library.cards.model_deployment_templates import TOOL_LIBRARY_DEPLOYMENT_CARD

from magic_toolbox.models import *

# Configure logging at the application's entry point
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration handling
# Conservatively assume Auth is enabled if anything other than these false values are set.
USE_AUTH = not os.getenv("TL_USE_AUTH", "True").lower() in ("false", "0", "f", "no")
MASTER_KEY = os.getenv("TL_MASTER_KEY")

if USE_AUTH:
    assert MASTER_KEY is not None, "If you are using auth, you must set a master key using the 'TL_MASTER_KEY' environment variable."
else:
    logger.warning("Warning: Authentication is disabled. This should only be used for testing.")

# API Key Management (Consider using a more secure approach for production)
VALID_API_KEYS = {MASTER_KEY}

model_library = ModelLibrary()
kube_watcher = KubeAPI()

tags_metadata = [
    {
        "name": "Magic Toolbox Management",
        "description": "Operations related to managing Magic Toolboxes.",
    },
    {
        "name": "Tool Management",
        "description": "Endpoints for adding, removing, and editing Tools on a Toolbox.",
    },
    {
        "name": "Configuration",
        "description": "Endpoints for generating and deploying configurations.",
    },
    # Add more tags as needed
]

# FastAPI instance
app = FastAPI(openapi_tags=tags_metadata)

# API Key Validation
async def verify_api_key(request: Request):
    if not USE_AUTH:
        return
    api_key = request.headers.get("X-API-KEY")
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Endpoint to check health
@app.get("/health/")
async def health():
    return HTTPException(status_code=200, detail="OK")

# Routes
#1. Delete a MT for a User (KW)
@app.delete("/management/delete", tags=["Magic Toolbox Management"])
async def delete_magic_toolbox(request:DeleteDeployment, api_key: str = Depends(verify_api_key)):
    try:
        # Note, this does not take the user-id into account, only the namespace and deployment name
        # We are assuming only the user who knows the namespace can delete the deployment
        # This seems a little fragile, perhaps not secure. Mayte a check on if the creator of the deployment is the same as the user_id?
        label_value = request.deployment_name
        label_key = "magic_toolbox"
        result = kube_watcher.delete_labeled_resources(namespace=request.namespace, label_key=label_key, label_value=label_value)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#2. List all the MTs of a User (KW)
@app.get("/management/list", tags=["Magic Toolbox Management"])
async def list_magic_toolboxes(request: ListDeployment, api_key: str = Depends(verify_api_key)):
    # Todo, should we actually only be listing deployments of type "tool-library" here somehow?

    label_key = f"magic_toolbox"
    label_value = None

    try:
        logger.warning("Listing Deployments, but user_id isn't implemented yet, and neither is deployment type?")
        result = kube_watcher.find_resources_with_label(request.namespace, label_key=label_key, label_value=label_value)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#3. Create a new MT for a User (ML + KW)
@app.post("/management/create", tags=["Magic Toolbox Management"])
async def create_magic_toolbox(request: CreateMTRequest, api_key: str = Depends(verify_api_key)):

    # First, check that nothing exists with this namespace with the derived label:

    label_value = request.deployment_name
    label_key = f"magic_toolbox"

    current = kube_watcher.find_resources_with_label(
        namespace=request.user.namespace,
        label_key=label_key,
        label_value=label_value
    )
    logger.info("Creating new Magic Toolbox")
    logger.info(current)

    if len(current) > 0:
        # return an error, and return the the current deployments found as data
        raise HTTPException(status_code=409, detail=f"Deployment with name {request.deployment_name} already exists in namespace {request.user.namespace}")

    # Get the Template, create a user, and create a config
    template = ModelDeploymentCard(
        model_deployment_template = TOOL_LIBRARY_DEPLOYMENT_CARD,
        user_information = request.user,
        override_params = {"deployment_name": request.deployment_name}
    )

    config = template.extract_deployment_config()
        
    try:
        result = kube_watcher.deploy_generic_model(config=config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


#4. Add new servive by URL per Instance + User
@app.post("/magic_toolbox/add_api_tool", tags=["Tool Management"])
async def add_service(request: AddAPIToolRequest, api_key: str = Depends(verify_api_key)):
    #try:
    logger.debug(f"Adding service {request}")
    tool_library = ToolLibraryClient(service_url=request.mt_service_url, api_key=request.mt_api_key)
    #except:
    #    raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    result = tool_library.register_api_tool(
        tool_url=request.tool_url,
        tool_routes=request.tool_routes,
        tool_api_key=request.tool_api_key
    )
    return result
    #except ValueError as e:
    #    raise HTTPException(status_code=400, detail=str(e))

# health check on underlying Toolbox API
@app.post("/magic_toolbox/health", tags = ["Tool Management"])
async def health(request: ServiceRequest, api_key: str = Depends(verify_api_key)):
    
    try:
        tool_library = ToolLibraryClient(service_url=request.mt_service_url, api_key=request.mt_api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    return tool_library.health()

@app.post("/magic_toolbox/get_tools", tags = ["Tool Management"])
async def get_tools(request: ServiceRequest, api_key: str = Depends(verify_api_key)):
    
    try:
        tool_library = ToolLibraryClient(service_url=request.mt_service_url, api_key=request.mt_api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    return tool_library.get_tools()





"""
#5. Remove a service by ID
@app.delete("/magic_toolbox/remove", tags=["Tool Management"])
async def remove_service(service_id: str, api_key: str = Depends(verify_api_key)):
    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
        result = tool_library.remove_service(service_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#6. Edit a Tool or set of tools descriptions.
@app.put("/tool/edit")
async def edit_tool(request: EditToolRequest, api_key: str = Depends(verify_api_key)):

    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    try:
        result = tool_library.edit_tool(request.tool_id, request.new_description)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    

#7. Generate ChatGPT Dynamic Config
@app.get("/config/chatgpt/dynamic")
async def generate_dynamic_chatgpt_config(api_key: str = Depends(verify_api_key)):
    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    try:
        result = tool_library.generate_chatgpt_dynamic_config()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

#8. Generate ChatGPT Static Configs
@app.get("/config/chatgpt/static")
async def generate_static_chatgpt_config(api_key: str = Depends(verify_api_key)):
    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    try:
        result = tool_library.generate_chatgpt_static_config()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


#9. Deploy a Kalavai Tool
@app.post("/tool/kalavai/deploy")
async def deploy_kalavai_tool(request: DeployKalavaiToolRequest, api_key: str = Depends(verify_api_key)):
    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    try:
        result = tool_library.deploy_kalavai_tool(request.tool_id, request.config)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


#10. Search for Rapid API Tools.
@app.get("/tools/search")
async def search_rapid_api_tools(query: str, api_key: str = Depends(verify_api_key)):
    try:
        tool_library = ToolLibraryClient(service_url=request.service_url, api_key=request.api_key)
    except:
        raise HTTPException(status_code=400, detail="Unable to connect to the tool library service.")

    try:
        result = tool_library.search_rapid_api_tools(query)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
