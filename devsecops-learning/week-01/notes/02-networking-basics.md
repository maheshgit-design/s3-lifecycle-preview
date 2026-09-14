# Networking Basics — Beginner Notes

## The mental model

Before cloud security, understand how two computers communicate.

```text
Your laptop
   |
   | request
   v
Network -> Router -> Internet -> Server
                              |
                              v
                           Service
```

## IP address

An IP address identifies a network interface so traffic can be routed to it.

Examples:

```text
192.168.1.20
10.0.1.15
```

Private IPv4 ranges commonly used inside networks include `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`.

## Port

An IP gets you to a machine/network interface. A port helps identify the application/service endpoint on that host.

Common examples:

```text
22   SSH
80   HTTP
443  HTTPS
```

## DNS

Humans prefer names such as:

```text
example.com
```

Networks ultimately need addresses. DNS resolves names to records that help clients locate services.

Try:

```bash
nslookup example.com
```

or, where installed:

```bash
dig example.com
```

## TCP vs UDP

TCP is connection-oriented and provides ordered, reliable byte delivery between endpoints.

UDP is connectionless and does not provide TCP's delivery/order guarantees. It has less protocol overhead and is useful where the application can tolerate loss or implement its own reliability behavior.

Do not memorize simply as "TCP slow, UDP fast." Understand the guarantees.

## HTTP and HTTPS

HTTP is an application protocol used by web clients and servers.

HTTPS is HTTP protected using TLS, providing encryption in transit and authentication of the server when certificate validation succeeds.

## Useful troubleshooting commands

```bash
ping 8.8.8.8
curl https://example.com
nslookup example.com
```

On Linux, inspect listening sockets with:

```bash
ss -lntup
```

`curl` is especially important because it lets you directly test HTTP endpoints.

## Cloud connection

AWS networking is easier once this model is clear:

```text
Internet
  |
Internet Gateway
  |
VPC
  |
Subnet
  |
Security Group
  |
EC2 / Load Balancer / Container
  |
Application Port
```

Later labs will build this architecture.

## Memory check

Explain in your own words:

1. IP address
2. port
3. DNS
4. TCP
5. UDP
6. HTTP vs HTTPS
7. what `curl` helps you test
