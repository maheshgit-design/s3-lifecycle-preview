# Linux Basics — Beginner Notes

## 1. What is Linux?

Linux is an operating-system family widely used on servers, cloud machines, containers and engineering infrastructure. In DevSecOps, you need to be comfortable operating from a terminal.

Think of the shell as a text interface for telling the operating system what to do.

## 2. Your location in the filesystem

```bash
pwd
```

`pwd` prints your current working directory.

```bash
ls
ls -la
```

`ls` lists files. `-l` gives details and `-a` includes hidden files.

```bash
cd /tmp
cd ~
cd ..
```

`cd` changes directory. `~` means your home directory and `..` means the parent directory.

## 3. Create, copy, move and delete

```bash
mkdir devsecops-lab
cd devsecops-lab
touch hello.txt
cp hello.txt hello-copy.txt
mv hello-copy.txt renamed.txt
rm renamed.txt
```

Be careful with `rm`: deleting from the command line can be destructive.

## 4. Read files

```bash
cat hello.txt
less hello.txt
head hello.txt
tail hello.txt
```

For logs, a common command is:

```bash
tail -f application.log
```

It follows new lines as they are written.

## 5. Permissions

Run:

```bash
ls -l
```

You may see something like:

```text
-rw-r--r--
```

The permission groups are:

```text
owner | group | others
```

And the permission letters are:

- `r` = read
- `w` = write
- `x` = execute

Example:

```bash
chmod u+x script.sh
```

This gives the owner execute permission.

## 6. Processes

A process is a running program.

```bash
ps
ps aux
```

Search for a process:

```bash
ps aux | grep python
```

`|` is a pipe. It sends the output of one command into another command.

## 7. Find things

```bash
find . -name "*.txt"
grep "ERROR" application.log
```

`find` searches filesystem objects. `grep` searches text.

## 8. Environment variables

```bash
export APP_ENV=development
echo "$APP_ENV"
```

Applications commonly use environment variables for configuration. Never treat environment variables as automatically safe for secrets; their security depends on how the system manages and exposes them.

## 9. Why Linux matters for DevSecOps

When production breaks, you may need to answer:

- Is the process running?
- Is the port listening?
- Is disk space exhausted?
- Are permissions wrong?
- What do the logs say?
- Can the machine reach another service?

Those questions require Linux and networking knowledge, not merely security tools.

## Memory check

Without looking above, explain `pwd`, `ls -la`, `cd`, `grep`, `chmod`, `ps`, `|`, and an environment variable.
