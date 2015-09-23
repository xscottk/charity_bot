import urllib

from http.server import BaseHTTPRequestHandler, HTTPServer
from uuid import UUID

from settings import *
from utils import *

class SimpleHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    print("GET Received")
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write(bytes('Thank you for your donation', 'UTF-8'))

    try:
      query_string = urllib.parse.parse_qs(self.path[2:]) # The [2:] clips off '/?' from the self.path string
      donation_id  = query_string.get('donation_id')
      donation_id  = int(donation_id[0])
      user_id      = query_string.get('user_id')
      user_id      = UUID(user_id[0])
      # print(donation_id,"/",user_id)

    except TypeError:  
      donation_id = None
      user_id     = None

    save_donation_id(donation_id, user_id)
    return

def start_server():
  try:
    server = HTTPServer((HTTP_HOSTNAME, HTTP_PORT), SimpleHandler)
    print('Started http server')
    server.serve_forever()
  except KeyboardInterrupt:
    print('Shutting down http server')
    server.socket.close()

def save_donation_id(donation_id, user_id):
  print(donation_id,"/",user_id)

  if donation_id and user_id:
    pass


start_server()