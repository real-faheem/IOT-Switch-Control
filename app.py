import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import requests

# Server Configuration
SERVER_IP = "http://167.71.237.12"
SERVER_PORT = "9000"
POST_URL = f"{SERVER_IP}:{SERVER_PORT}/api/receive"

# Store switch state globally for simplicity (you may want a database in a real-world scenario)
switch_state = {
    "switch_1": "off",
    "switch_2": "off",
    "switch_3": "off"
}

# Specify the path to the HTML file
HTML_FILE_PATH = os.path.join(os.path.dirname(__file__), 'IOTSWITCH-MAIN', 'new.html')


class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        """Set common headers."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/get_state":
            # Return the current state of the switches
            response = {
                "switch_1": switch_state["switch_1"],
                "switch_2": switch_state["switch_2"],
                "switch_3": switch_state["switch_3"]
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            # Serve the HTML page (your separate HTML file)
            try:
                # Open the HTML file and send it as a response
                with open(HTML_FILE_PATH, 'r') as file:
                    html_content = file.read()
                    self._set_headers(200)
                    self.wfile.write(html_content.encode())
            except FileNotFoundError:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "HTML file not found"}).encode())
        else:
            # Handle unknown routes
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Route not found"}).encode())

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/toggle":
            # Parse the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Update switch state based on the request payload
                data = json.loads(post_data)
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
                        self._set_headers()
                        self.wfile.write(json.dumps({
                            "status": "success",
                            "response": server_response,
                            "switch_state": switch_state[switch_id]
                        }).encode())
                    except requests.exceptions.RequestException as e:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
                else:
                    raise ValueError("Invalid payload")
            except (json.JSONDecodeError, ValueError) as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid payload"}).encode())
        else:
            # Handle unknown routes
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Route not found"}).encode())

# Run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=9000):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
