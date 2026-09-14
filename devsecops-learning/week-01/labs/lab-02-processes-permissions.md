# Lab 02 — Processes and Permissions

**Time:** 45–60 minutes

## Part 1 — Permissions

Create a file called `hello.sh` with:

```bash
#!/usr/bin/env bash
echo "DevSecOps lab running"
```

Try executing it directly:

```bash
./hello.sh
```

Observe what happens. Inspect its permissions with `ls -l`, add execute permission for the owner, then run it again.

Write down **why** the behavior changed.

## Part 2 — Processes

Start a harmless background process:

```bash
sleep 300 &
```

Now find it using process-inspection commands.

Record:

- PID
- command
- user running the process

Terminate only the `sleep` process you created.

Verify it is gone.

## Part 3 — Pipes

Use a pipe to filter the process list for a word of your choice.

Explain this structure:

```text
command A | command B
```

## Security connection

Answer in your own words:

1. Why are excessive file permissions dangerous?
2. Why should a service not run as root unless necessary?
3. If an unknown process appears on a production server, what information would you collect before terminating it?

## Evidence

Save your commands and answers to `week01/evidence/lab02.txt`.

## Pass condition

Explain `r`, `w`, `x`, PID, process and pipe without checking the notes.
