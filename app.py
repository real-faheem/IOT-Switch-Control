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

# Specify the path to the HTML file located in "d:/newproject"
HTML_FILE_PATH = "/var/www/html/iot/iot-control-2/index.html"  # Adjust the path to match your actual location   

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status_code=200):
        """Set common headers."""
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
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
            self._set_headers("application/json")
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            # Serve the HTML page (your separate HTML file)
            try:
                print(f"Trying to serve HTML from: {HTML_FILE_PATH}")
                with open(HTML_FILE_PATH, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                    self._set_headers("text/html; charset=UTF-8", 200)  # Set the correct content type for HTML
                    self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                self._set_headers("application/json", 404)
                self.wfile.write(json.dumps({"error": "HTML file not found"}).encode())
            except Exception as e:
                self._set_headers("application/json", 500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            # Handle unknown routes
            self._set_headers("application/json", 404)
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
                        self._set_headers("application/json")
                        self.wfile.write(json.dumps({
                            "status": "success",
                            "response": server_response,
                            "switch_state": switch_state[switch_id]
                        }).encode())
                    except requests.exceptions.RequestException as e:
                        self._set_headers("application/json", 500)
                        self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
                else:
                    raise ValueError("Invalid payload")
            except (json.JSONDecodeError, ValueError) as e:
                self._set_headers("application/json", 400)
                self.wfile.write(json.dumps({"status": "error", "message": "Invalid payload"}).encode())
        else:
            # Handle unknown routes
            self._set_headers("application/json", 404)
            self.wfile.write(json.dumps({"error": "Route not found"}).encode())

# Run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=9000):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
