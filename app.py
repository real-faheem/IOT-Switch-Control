import tornado.ioloop
import tornado.web
import tornado.httpclient
from tornado import escape

# IP address of the ESP32 server
SERVER_IP = "http://167.71.237.12:9000"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Render the main HTML page
        self.render("index.html")

class ToggleHandler(tornado.web.RequestHandler):
    async def get(self):
        # Fetch the current status of switches from the ESP32 server
        client = tornado.httpclient.AsyncHTTPClient()
        try:
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

    async def post(self):
        # Toggle a specific switch based on the input argument
        switch = self.get_argument("switch", None)
        if switch not in ["switch1", "switch2", "switch3"]:
            self.write({"status": "error", "message": "Invalid switch name"})
            return

        # Map switch to its toggle URL
        toggle_url = f"{SERVER_IP}/{switch}"

        client = tornado.httpclient.AsyncHTTPClient()
        try:
            # Send POST request to ESP32 to toggle the switch
            response = await client.fetch(toggle_url, method="POST")
            data = escape.json_decode(response.body)
            self.write({"status": data.get('status', 'success')})
        except tornado.httpclient.HTTPError as e:
            print(f"HTTPError: {e}")
            self.write({"status": "error", "message": str(e)})
        except Exception as e:
            print(f"Error: {e}")
            self.write({"status": "error", "message": str(e)})

def make_app():
    # Define the routes
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/toggle", ToggleHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)  # Run the server on port 9000
    print("Server is running on port 9000")
    tornado.ioloop.IOLoop.current().start()
