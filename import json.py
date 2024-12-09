import json
import requests

# Configuration for the server
server_config = {
    "server_ip": "http://167.71.237.12",
    "server_port": "80",
    "post_url": "/api/receive"
}

# Switch state data
switch_states = {
    "1": {"switch_state": "off"},
    "2": {"switch_state": "off"},
    "3": {"switch_state": "off"}
}

# HTML representation for the index page in JSON
html_template = {
    "index_page": {
        "template_path": "/var/www/html/iotswitch/templates/index.html",
        "state": {switch_id: state["switch_state"] for switch_id, state in switch_states.items()}
    }
}

# Mock endpoint for data reception (JSON representation)
api_receive_endpoint = {
    "endpoint": "/api/receive",
    "method": "POST",
    "response": {
        "status": "success",
        "message": "Data received"
    }
}

# Toggle switch functionality (logic encapsulated in JSON)
def toggle_switch(switch_id, state):
    """
    Toggle the switch state and return the result in JSON.
    """
    if switch_id not in switch_states:
        return json.dumps({
            "status": "error",
            "message": "Invalid switch_id"
        })
    
    if state not in ["on", "off"]:
        return json.dumps({
            "status": "error",
            "message": "Invalid state"
        })

    # Update the switch state
    switch_states[switch_id]["switch_state"] = state

    # Prepare payload for the external server
    payload = {
        "switch_id": switch_id,
        "switch_state": state
    }

    try:
        # Send a POST request to the external server (simulate sending data)
        server_url = f"{server_config['server_ip']}:{server_config['server_port']}{server_config['post_url']}"
        response = requests.post(server_url, json=payload)
        
        if response.status_code == 200:
            server_response = response.json()
            return json.dumps({
                "status": "success",
                "response": server_response,
                "switch_state": switch_states[switch_id]["switch_state"]
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Server returned status code {response.status_code}"
            })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

# Get current switch states as JSON
def get_state():
    """
    Return the current state of all switches in JSON format.
    """
    return json.dumps({
        switch_id: state["switch_state"] for switch_id, state in switch_states.items()
    })

# Main JSON structure for application
application_json = {
    "server_config": server_config,
    "switch_states": switch_states,
    "html_template": html_template,
    "endpoints": {
        "api_receive": api_receive_endpoint,
        "toggle_switch": toggle_switch,
        "get_state": get_state
    }
}

# Simulate API calls (example usage)
if __name__== "__main__":
    # Example: Toggle switch 1 to "on"
    print(toggle_switch("1", "on"))

    # Example: Get the current state of all switches
    print(get_state())