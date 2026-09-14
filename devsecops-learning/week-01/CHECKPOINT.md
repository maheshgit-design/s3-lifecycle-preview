# Week 1 Checkpoint

Do not use Google, ChatGPT or the notes for the first attempt.

## Explain

1. What is Linux?
2. What is a process?
3. What is a PID?
4. What do read/write/execute permissions mean?
5. What does `chmod` change?
6. What does a pipe do?
7. What is an IP address?
8. What is a port?
9. What problem does DNS solve?
10. What is the difference between TCP and UDP?
11. What is HTTPS protecting that plain HTTP does not?
12. What does `curl` help you troubleshoot?

## Troubleshooting scenarios

### Scenario 1

Your application is supposed to listen on port 8080, but `curl http://localhost:8080` fails.

Write the first three things you would investigate.

### Scenario 2

`example.com` fails by hostname, but a known IP endpoint is reachable.

Which layer would you investigate first and why?

### Scenario 3

A script exists but `./script.sh` returns a permission error.

What would you inspect before changing anything?

## Practical test

Without notes:

1. create a directory
2. create a text file
3. add several lines to it
4. search the file for a word
5. copy the file
6. find the copy recursively
7. inspect its permissions
8. start a harmless process
9. locate its PID
10. terminate only that process
11. start a local HTTP server on port 8080
12. request it with `curl`
13. prove something is listening on the expected port
14. stop the server

## Score

- 12–14 practical tasks without help: PASS
- 9–11: repeat weak areas
- 0–8: repeat Week 1

The objective is not speed. The objective is being able to reason about what the computer is doing.
