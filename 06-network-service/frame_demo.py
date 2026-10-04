"""Activity 20: decode received bytes whole, then split them at newlines first."""

from protocol import ProtocolError, decode_request_line, encode_message
from vector_search import find_nearest

with open("results/stream-bytes.bin", "rb") as f:
    data = f.read()

print("A) Decode everything recv() returned as one request:")
try:
    decode_request_line(data)
except ProtocolError as err:
    print("  ", err.response())

print("B) Split at each newline first:")
*frames, leftover = data.split(b"\n")
for frame in frames:
    line = frame + b"\n"                                   # framing: one complete line
    request = decode_request_line(line)                    # parsing and validation
    best_index, distance = find_nearest(request["query"])  # computation
    reply = encode_message({"ok": True, "request_id": request["request_id"],
                            "best_index": best_index, "distance": distance})
    print("   request:", request)
    print("   reply:  ", reply)                            # response
print("   leftover:", leftover)
