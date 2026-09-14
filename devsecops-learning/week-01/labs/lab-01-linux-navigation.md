# Lab 01 — Linux Navigation and Files

**Time:** 45–60 minutes

**Goal:** Become comfortable moving around Linux and manipulating files without a GUI.

## Setup

Use a Linux machine, WSL, a disposable Linux VM, or another Linux environment you are authorized to use.

## Challenge A — Build the workspace

Starting from your home directory, create this structure using terminal commands only:

```text
devsecops-labs/
└── week01/
    ├── logs/
    ├── scripts/
    └── evidence/
```

Do not copy commands from an answer. Work out which commands you need.

## Challenge B — Create data

Inside `logs`, create `app.log` containing these lines:

```text
INFO application started
INFO database connected
WARN memory usage high
ERROR database timeout
INFO retry started
ERROR retry failed
```

Then use commands to:

1. print the entire file
2. display only lines containing `ERROR`
3. count the number of lines
4. copy the log into `evidence`
5. rename the copied file to `app-backup.log`

## Challenge C — Find it

Return to `devsecops-labs` and find every file ending in `.log` recursively.

## Evidence

Save the commands you used in:

```text
week01/evidence/lab01.txt
```

Also answer:

- What is your working directory?
- What does `..` mean?
- What is the difference between `cp` and `mv`?
- What does `grep` do?

## Pass condition

You pass only if you can delete the entire lab directory, recreate it, and repeat the core exercise without reading step-by-step commands.
