import streamlit as st
from magic_toolbox.client import MagicToolboxClient 

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state['responses'] = []


# Initialize the API with default values
st.header("Magic Toolbox Client")

api_url = st.text_input("API URL", value="http://0.0.0.0:8000")
api_key = st.text_input("API Key", value="adam")

api = MagicToolboxClient(api_url=api_url, api_key=api_key)

# Function to display the response
def display_response():
    if st.session_state['responses']:
        st.write("Response")
        st.write(st.session_state['responses'][-1])


st.subheader("Magic Toolbox Management")

st.subheader("Magic Toolbox API")

with st.expander("Check Health"):
    with st.form("Check Health"):
        mt_service_url = st.text_input("MT Service URL", value="http://127.0.0.1:8000")
        mt_service_api_key = st.text_input("MT API Key", value="adam")
        if mt_service_api_key == "":
            mt_api_key = None
    
        submit_add_api_tool = st.form_submit_button("Check Health")
        if submit_add_api_tool:
            st.session_state['responses'].append(
                api.health_magic_toolbox()
            )

            display_response()

with st.expander("List Magic Toolboxes"):
    # Create form for 'list_magic_toolboxes'
    with st.form("List Magic Toolboxes"):
        namespace_list = st.text_input("Namespace", value="adam")
        submit_list = st.form_submit_button("List Magic Toolboxes")
        if submit_list:
            st.session_state['responses'].append(api.list_magic_toolboxes(namespace=namespace_list))
            display_response()

with st.expander("Create Magic Toolbox"):
    # Create form for 'create_magic_toolbox'
    with st.form("Create Magic Toolbox"):
        deployment_name_create = st.text_input("Deployment Name", value="test")
        user_id_create = st.text_input("User ID", value="adam")
        namespace_create = st.text_input("Namespace", value="adam")
        api_key_create = st.text_input("API Key", value="adam_test")
        submit_create = st.form_submit_button("Create Magic Toolbox")
        if submit_create:
            st.session_state['responses'].append(api.create_magic_toolbox(deployment_name=deployment_name_create, user_id=user_id_create, namespace=namespace_create, API_key=api_key_create))
            display_response()

# Create form for 'delete_magic_toolbox'
with st.expander("Delete Magic Toolbox"):
    with st.form("Delete Magic Toolbox"):
        user_id_delete = st.text_input("User ID", value="adam")
        namespace_delete = st.text_input("Namespace", value="namespace")
        deployment_name_delete = st.text_input("Deployment Name", value="test")
        submit_delete = st.form_submit_button("Delete Magic Toolbox")
        if submit_delete:
            st.session_state['responses'].append(
                api.delete_magic_toolbox(user_id=user_id_delete, namespace=namespace_delete, deployment_name=deployment_name_delete)
            )

            display_response()

st.subheader("Magic Toolbox API")

with st.expander("Check Toolbox Health"):
    with st.form("Check Toolbox Health"):
        mt_service_url = st.text_input("MT Service URL", value="http://127.0.0.1:8000")
        mt_api_key = st.text_input("MT API Key", value="adam")
        if mt_api_key == "":
            mt_api_key = None
    
        submit_add_api_tool = st.form_submit_button("Check Health")
        if submit_add_api_tool:
            st.session_state['responses'].append(
                api.toolbox_health(
                    mt_service_url=mt_service_url,
                    mt_api_key=mt_api_key,
                )
            )

            display_response()

# Create form for 'add_api_tool'
with st.expander("Add API Tool"):
    with st.form("Add API Tool"):
        mt_service_url = st.text_input("MT Service URL", value="http://127.0.0.1:8000")
        mt_api_key = st.text_input("MT API Key", value="adam")
        if mt_api_key == "":
            mt_api_key = None

        tool_url = st.text_input("Tool URL", value="http://127.0.0.1:8000")
        tool_routes = st.text_input("Tool Routes", value="")
        if tool_routes == "":
            tool_routes = None
        else:
            tool_routes = tool_routes.split(",")
            if tool_routes == []:
                tool_routes = None
        st.write(tool_routes)
        
        tool_api_key = st.text_input("Tool API Key", value="adam")
        if tool_api_key == "":
            tool_api_key = None

        submit_add_api_tool = st.form_submit_button("Add API Tool")
        if submit_add_api_tool:
            st.session_state['responses'].append(
                api.add_api_tool(
                    mt_service_url=mt_service_url,
                    mt_api_key=mt_api_key,
                    tool_url=tool_url,
                    tool_routes=tool_routes,
                    tool_api_key=tool_api_key
                )
            )

            display_response()



st.header("History")
try:
    for response in st.session_state['responses']:
        st.write(response)
except:
    st.info("No History")