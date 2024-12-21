import tornado.ioloop
import tornado.web
import tornado.httpclient
import json

ESP32_IP = "http://167.71.237.12"  # Replace with your ESP32 IP address

class SwitchStatusHandler(tornado.web.RequestHandler):
    async def get(self):
        # Fetch the current switch status from the ESP32
        client = tornado.httpclient.HTTPClient()
        try:
            response = client.fetch(f"http://{ESP32_IP}:9000/get-status")
            data = json.loads(response.body)
            self.set_header("Access-Control-Allow-Origin", "*")  # Enable CORS
            self.write(data)
        except tornado.httpclient.HTTPError as e:
            self.set_status(e.code)
            self.write({"error": "Failed to fetch status from ESP32"})

    async def post(self):
        # Set the switch status on the ESP32
        switch_id = self.get_argument("switch_id", None)
        state = self.get_argument("state", None)

        if switch_id and state:
            client = tornado.httpclient.HTTPClient()
            try:
                response = client.fetch(
                    f"http://{ESP32_IP}:9000/set-status",
                    method="POST",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    body=f"switch_id={switch_id}&state={state}"
                )
                self.set_header("Access-Control-Allow-Origin", "*")  # Enable CORS
                result = json.loads(response.body)
                self.write(result)
            except tornado.httpclient.HTTPError as e:
                self.set_status(e.code)
                self.write({"error": "Failed to change status on ESP32"})
        else:
            self.set_status(400)
            self.write({"error": "Invalid parameters"})

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")  # Renders the frontend page

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/switch-status", SwitchStatusHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9000)  # Tornado server listens on port 8081
    print("Server started")
    tornado.ioloop.IOLoop.current().start()
