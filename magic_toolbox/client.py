import os
import requests
from typing import Dict, Any, Optional

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ.get("MAGIC_TOOLBOX_LOG_LEVEL", "INFO")))

class MagicToolboxClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {'X-API-KEY': api_key}

    def _request(self, method: str, endpoint: str, data: Dict = None):
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}

    #########################################
    # Management API
    #########################################
        
    def health_magic_toolbox(self):
        return self._request('GET', 'health')
    
    def delete_magic_toolbox(self, user_id: str, namespace:str, deployment_name: str) -> Dict[str, Any]:
        data = {'user_id': user_id, 'namespace':namespace, 'deployment_name': deployment_name}
        return self._request('DELETE', 'management/delete', data)

    def list_magic_toolboxes(self, namespace: str) -> Dict[str, Any]:
        data = {'namespace': namespace,"user_id":namespace}
        return self._request('GET', 'management/list', data)

    def create_magic_toolbox(self, deployment_name: str, user_id:str, namespace:str, API_key:str) -> Dict[str, Any]:
        data = {'deployment_name': deployment_name, 'user': {'id': user_id, 'namespace': namespace, 'API_key': API_key}}
        return self._request('POST', 'management/create', data)
    
    #########################################
    # Magic Toolbox API
    #########################################

    def toolbox_health(self, mt_service_url: str, mt_api_key: Optional[str] =None) -> Dict[str, Any]:
        data = {
            'mt_service_url': mt_service_url,
            'mt_api_key': mt_api_key
        }

        logger.info("Toolbox Health")
        logger.info(data)

        return self._request('POST', 'magic_toolbox/health', data)

    def add_api_tool(self, mt_service_url: str, mt_api_key: str, tool_url: str, tool_routes: str = None, tool_api_key: str = None) -> Dict[str, Any]:
        data = {
            'mt_service_url': mt_service_url,
            'mt_api_key': mt_api_key,
            'tool_url': tool_url,
            'tool_routes': tool_routes,
            'tool_api_key': tool_api_key
        }
        logger.info("Adding API Tools")
        logger.info(data)

        return self._request('POST', 'magic_toolbox/add_api_tool', data)

    # do the get route
    def get_tools(self, mt_service_url: str, mt_api_key: str):
        data = {
            'mt_service_url': mt_service_url,
            'mt_api_key': mt_api_key
        }

        logger.info("Getting Tools from Toolbox Instance")
        logger.info(data)

        return self._request('POST', 'magic_toolbox/get_tools', data)




if __name__ == "__main__":
    # Example usage

    api = MagicToolboxClient(api_url="http://0.0.0.0:8000", api_key="adam")   

    print("Listing Magic Toolbox\n\n")
    response = api.list_magic_toolboxes(namespace="adam")

    print("Deploy Magic Toolbox\n\n")
    response = api.create_magic_toolbox(
        deployment_name="test",
        user_id = "adam",
        namespace = "adam",
        API_key = "adam_test"
    )
    print(response)

    print("Delete Magic Toolbox\n\n")
    response = api.delete_magic_toolbox(user_id="adam", namespace="namespace", deployment_name="test")
    print(response)

