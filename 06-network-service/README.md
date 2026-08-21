# Network Vector Search Service Starter Packet

This packet supplies a small localhost vector-search service for Activities 20-23.
It uses newline-delimited JSON (NDJSON): one UTF-8 JSON object followed by `\n` for
each request and response. TCP supplies a byte stream; the newline is the
application's framing rule.

The code uses only the Python standard library and runs natively on AMD64 or ARM64
Ubuntu. It is intentionally a local teaching service, not a cloud, deployment,
security, or production-reliability framework.

## Files

- `protocol.py`: framing, JSON parsing, and request validation.
- `vector_search.py`: deterministic three-dimensional exact-search dataset/kernel.
- `server.py`: serial or threaded localhost server with lightweight request logs.
- `client.py`: valid and raw-request client.
- `protocol_tests.py`: minimal protocol-conformance tests.
- `load_test.py`: concurrent end-to-end load generator with summary/CSV output.
- `debugging-receipt-template.md`: symptom-to-next-experiment investigation record.

## Protocol v1

A valid request has this shape:

```json
{"type":"query","request_id":"demo-1","query":[1.0,2.0,3.0],"k":1}
```

Every response contains `ok` and `request_id`. Successful responses also contain
`best_index` and squared `distance`. Error responses contain a stable `error` code
and readable `message`.

Run the conformance tests before starting the server:

```bash
python3 protocol_tests.py
```

The minimum conformance paths are a valid request, malformed JSON, dimension
mismatch, a missing field, and an unsupported request type. These cases separate
framing/parsing/validation failures from vector computation.

## One-client smoke test

Terminal 1:

```bash
python3 server.py --host 127.0.0.1 --port 17000 --mode serial --trace
```

Terminal 2:

```bash
python3 client.py --host 127.0.0.1 --port 17000 \
  --request-id valid-1 --query 1.0,2.0,3.0
python3 client.py --host 127.0.0.1 --port 17000 \
  --raw '{"type":"query","request_id":"malformed-1"'
python3 client.py --host 127.0.0.1 --port 17000 \
  --request-id dim-1 --query 1.0,2.0
```

The request trace is:

```text
client sends bytes -> server reads through newline -> parses JSON -> validates shape
-> computes exact search (valid path only) -> formats JSON -> sends through newline
```

With `--trace`, the server prints stage events. Every completed request also prints
one compact JSON log with request ID, byte counts, `parse_ms`, `compute_ms`,
end-to-end `response_ms`, status, and `error_path`. An error path should normally
have no vector-compute time.

## Multiple clients and load testing

Keep the server running and compare one versus four concurrent clients:

```bash
python3 load_test.py --clients 1 --requests 40 --host 127.0.0.1 --port 17000
python3 load_test.py --clients 4 --requests 40 --host 127.0.0.1 --port 17000
```

`--requests` is the total request count, while `--clients` is the maximum number of
requests in flight. The load test reports successful/error counts, elapsed time,
p50 and p95 end-to-end latency, and successful-request throughput. Percentiles use
linear interpolation over the sorted successful-request latencies. A response counts
as successful only when its request ID and known nearest-vector result are correct.

Start `server.py --mode threaded` and rerun the same commands to compare scheduling
policies. This starter does not implement service batching; Activity 22 asks you to
use its request evidence to propose where a batch queue and flush policy would fit.

To append a summary receipt for several runs:

```bash
mkdir -p results
python3 load_test.py --clients 4 --requests 100 \
  --host 127.0.0.1 --port 17000 --csv results/load-summary.csv
```

Name the timed scope when using these results: the load-test latency includes client
connect, request serialization/send, localhost TCP, server parse/validate/compute,
response serialization/send, and client response parsing. It excludes server
startup and load-test input generation.
