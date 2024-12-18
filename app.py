import json
import os
import requests
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

# Server Configuration
SERVER_IP = "http://167.71.237.12"
SERVER_PORT = "9000"
POST_URL = f"{SERVER_IP}:{SERVER_PORT}/api/receive"

# Store switch state globally for simplicity
switch_state = {
    "switch_1": "off",
    "switch_2": "off",
    "switch_3": "off"
}

# Specify the path to the HTML file
HTML_FILE_PATH = "/var/www/html/iot/iot-control-2/index.html"

class GetStateHandler(RequestHandler):
    """Handler for returning the current state of switches."""
    def get(self):
        response = {
            "switch_1": switch_state["switch_1"],
            "switch_2": switch_state["switch_2"],
            "switch_3": switch_state["switch_3"]
        }
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(response))

class HTMLHandler(RequestHandler):
    """Handler for serving the HTML file."""
    async def get(self):
        try:
            print(f"Trying to serve HTML from: {HTML_FILE_PATH}")
            with open(HTML_FILE_PATH, 'r', encoding='utf-8') as file:
                html_content = file.read()
                self.set_header("Content-Type", "text/html; charset=UTF-8")
                self.write(html_content)
        except FileNotFoundError:
            self.set_status(404)
            self.write({"error": "HTML file not found"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

class ToggleHandler(RequestHandler):
    """Handler for toggling the switch state."""
    async def post(self):
        try:
            # Parse the request body
            data = json.loads(self.request.body)
            switch_id = data.get("switch_id")
            new_state = data.get("state")

            if switch_id and new_state in ["on", "off"]:
                # Update the state of the switch
                switch_state[switch_id] = new_state
                payload = {
                    "switch_id": switch_id,
                    "switch_state": new_state
                }

                # Simulate sending data to an external server
                try:
                    response = requests.post(POST_URL, json=payload)
                    server_response = response.text
                    self.set_header("Content-Type", "application/json")
                    self.write(json.dumps({
                        "status": "success",
                        "response": server_response,
                        "switch_state": switch_state[switch_id]
                    }))
                except requests.exceptions.RequestException as e:
                    self.set_status(500)
                    self.write({"status": "error", "message": str(e)})
            else:
                raise ValueError("Invalid payload")
        except (json.JSONDecodeError, ValueError):
            self.set_status(400)
            self.write({"status": "error", "message": "Invalid payload"})

class NotFoundHandler(RequestHandler):
    """Handler for undefined routes."""
    def prepare(self):
        self.set_status(404)
        self.write({"error": "Route not found"})

def make_app():
    """Create the Tornado application."""
    return Application([
        (r"/get_state", GetStateHandler),
        (r"/", HTMLHandler),
        (r"/toggle", ToggleHandler),
        (r".*", NotFoundHandler)  # Catch-all for undefined routes
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)  # Run on port 9000
    print("Tornado server running on port 9000...")
    IOLoop.current().start()
