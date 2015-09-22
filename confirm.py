import json
import os
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from settings import *
from utils import *

class SimpleHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    print("GET Received")
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write('Thank you for your donation')

    try:
      query_string = urllib.parse.parse_qs(os.environ['QUERY_STRING'])
      donation_id  = query_string.get('donation_id')
      donation_id  = str(donation_id)
    except:  
      donation_id = None

    save_donation_id(donation_id)
    confirm_accepted_donation(donation_id)
    return

def start_server():
  try:
    server = HTTPServer((HTTP_HOSTNAME, HTTP_PORT), SimpleHandler)
    print('Started http server')
    server.serve_forever()
  except KeyboardInterrupt:
    print('Shutting down server')
    server.socket.close()

def save_donation_id(donation_id):
  if donation_id:
    pass


start_server()