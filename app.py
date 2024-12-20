import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado import escape
import json

# IP address of the ESP32 server
SERVER_IP = "http://167.71.237.12:9000"  # Ensure that this is the correct address of the ESP32

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Render the main HTML page
        self.render("index.html")

class ToggleHandler(tornado.web.RequestHandler):
    # Fetch the current status of switches from the ESP32 server (GET request)
    async def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        try:
            # Send GET request to fetch switch status from ESP32
            response = await client.fetch(f"{SERVER_IP}/status")
            data = escape.json_decode(response.body)
            
            # Send back the status of all switches
            self.write({
                "switch1": data.get('switch1', "unknown"),
                "switch2": data.get('switch2', "unknown"),
                "switch3": data.get('switch3', "unknown")
            })
        except tornado.httpclient.HTTPError as e:
            print(f"HTTPError: {e}")
            self.write({"status": "error", "message": str(e)})
        except Exception as e:
            print(f"Error: {e}")
            self.write({"status": "error", "message": str(e)})

    # Toggle switch state (POST request)
    async def post(self):
        try:
            # Parse the JSON body data
            data = json.loads(self.request.body.decode('utf-8'))
            switch_id = data.get("switch_id")
            state = data.get("state")

            # Validate switch_id
            if switch_id not in ["switch_1", "switch_2", "switch_3"]:
                self.write({"status": "error", "message": "Invalid switch_id"})
                return
            
            # Map switch_id to its toggle URL for ESP32
            toggle_url = f"{SERVER_IP}/set-status"

            # Send POST request to ESP32 to toggle the switch
            client = tornado.httpclient.AsyncHTTPClient()
            payload = {
                "switch_id": switch_id,
                "state": state
            }
            try:
                response = await client.fetch(toggle_url, method="POST", body=json.dumps(payload), headers={'Content-Type': 'application/json'})
                response_data = escape.json_decode(response.body)
                self.write({"status": response_data.get('status', 'success')})
            except tornado.httpclient.HTTPError as e:
                print(f"HTTPError: {e}")
                self.write({"status": "error", "message": str(e)})
            except Exception as e:
                print(f"Error: {e}")
                self.write({"status": "error", "message": str(e)})

        except json.JSONDecodeError:
            self.write({"status": "error", "message": "Invalid JSON format"})
        except Exception as e:
            print(f"Error parsing request body: {e}")
            self.write({"status": "error", "message": "An error occurred"})

def make_app():
    # Define the routes for the application
    return tornado.web.Application([
        (r"/", MainHandler),  # Route for rendering the HTML page
        (r"/toggle", ToggleHandler),  # Route for handling switch toggles (both GET and POST)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)  # Run the Tornado server on port 9000
    print("Server is running on http://167.71.237.12:9000")
    tornado.ioloop.IOLoop.current().start()
