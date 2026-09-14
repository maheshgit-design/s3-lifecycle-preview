# Lab 03 — See Networking Happen

**Time:** 60–75 minutes

**Goal:** Connect IP addresses, DNS, ports and HTTP to things you can actually observe.

Only test public services intended for normal client access and systems you own or are authorized to test. This lab does not require port scanning.

## Part 1 — DNS

Resolve:

```text
example.com
```

Use `nslookup` or `dig`.

Record one returned address and explain what DNS did.

## Part 2 — HTTP

Run:

```bash
curl -I https://example.com
```

Identify:

- HTTP status code
- at least two response headers

Then run verbose curl against the same URL:

```bash
curl -v https://example.com
```

Observe the connection/TLS/HTTP information. Do not worry if you do not understand every line yet.

## Part 3 — Local web server

Create a directory with an `index.html` containing:

```html
<h1>My DevSecOps Lab</h1>
```

If Python 3 is installed, from that directory run:

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

In another terminal:

```bash
curl http://127.0.0.1:8080
```

Inspect listening TCP sockets using an available local tool such as:

```bash
ss -lnt
```

Stop the server when finished.

## Explain the experiment

Describe what each item means:

```text
127.0.0.1
8080
HTTP
curl
listening socket
```

Then explain what would happen conceptually if the application were moved from your laptop to an AWS EC2 instance.

## Evidence

Save command output and explanations to `week01/evidence/lab03.txt`.

## Pass condition

Draw this from memory and explain every arrow:

```text
Client -> DNS -> IP -> Server -> Port -> Application
```
