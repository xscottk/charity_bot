import praw
import requests
import time

from requests.auth import HTTPBasicAuth

from settings import *

def justgiving_request_wrapper(resource, method, additional_headers=None, **kwargs):
  # Return either the requested resource (in JSON), POST confirmation, or None if something failed
  # QUESTION: Should I do subclassing instead here? Or overriding or something?
  # TODO: Figure out how to merge default headers and optional additional headers passed to justgiving_request_wrapper

  default_headers = {'accept':'application/json'}

  if additional_headers == None:
    all_headers = default_headers
  else:
    all_headers = default_headers.copy()
    all_headers.update(additional_headers)

# TODO: I don't like this, but I don't know how else to do it...
  if method == 'GET':
    jg_request = requests.get(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  elif method == 'POST':
    jg_request = requests.post(JUSTGIVING_API_URL + resource, auth=HTTPBasicAuth(JUSTGIVING_USER, JUSTGIVING_PASS), headers=all_headers, **kwargs)

  else:
    return None

  return jg_request

def handle_ratelimit(func, *args, **kwargs):
  while True:
    try:
      return func(*args, **kwargs)
      break
    except praw.errors.RateLimitExceeded as error:
      sleep_time = error.sleep_time + 70 # Extra safety buffer
      print('Rate limit exceeded, sleeping for', sleep_time, 'seconds')
      time.sleep(sleep_time)