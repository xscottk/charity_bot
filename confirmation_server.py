import urllib
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import *
from sql_tables import *
from utils import *

engine = create_engine(SQLALCHEMY_ADDRESS)
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine

session = DBSession()

class SimpleHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    print("GET Received")
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    self.wfile.write(bytes('Thank you for your donation. You may close this window.', 'UTF-8'))

    try:
      query_string = urllib.parse.parse_qs(self.path[2:]) # The [2:] is needed to clip off '/?' from the self.path string
      donation_id  = query_string.get('donation_id')
      donation_id  = int(donation_id[0])

      if not (0 < donation_id < (2**31)):
        donation_id = None

      user_id      = query_string.get('user_id')
      user_id      = str(user_id[0])

      if len(user_id) > 50:
        user_id = None

      # print(donation_id,"/",user_id)

    except (TypeError, ValueError, OverflowError):  
      donation_id = None
      user_id     = None

    save_donation_id(donation_id, user_id)
    return

def start_server():
  try:
    server = HTTPServer((SERVER_IP, HTTP_PORT), SimpleHandler)
    print('Started http server')
    server.serve_forever()
  except KeyboardInterrupt:
    print('Shutting down http server')
    server.socket.close()

def save_donation_id(donation_id, user_id):
  print(donation_id,"/",user_id)

  if donation_id and user_id:
    sql_user = session.query(Donation).filter(Donation.user_id == user_id).one()
    # sql_user_id_exists = session.query(exists().where(Donation.user_id == user_id)).scalar()

    if sql_user:
      sql_user.donation_id = donation_id
      session.commit()

start_server()