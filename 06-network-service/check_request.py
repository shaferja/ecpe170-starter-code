"""Activity 20: frame one request line and run it through decode_request_line."""

import sys
from protocol import ProtocolError, decode_request_line

line = sys.argv[1].encode("utf-8") + b"\n"       # frame it: add the newline
try:
    print("accepted:", decode_request_line(line))
except ProtocolError as err:
    print("rejected:", err.response())
