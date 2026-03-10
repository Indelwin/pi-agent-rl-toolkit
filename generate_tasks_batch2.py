#!/usr/bin/env python3
"""Generate batch 2 of synthetic eval tasks — targeting 750+ more to reach 1000 total."""
import json
import os
import random

random.seed(99)
tasks = []
tid = 264  # continue from batch 1

def T(category, name, prompt, requires_tool, max_tool_calls, verify, expected_tool=None):
    global tid
    tid += 1
    t = {
        "id": f"syn_{tid:04d}",
        "category": category,
        "name": name,
        "prompt": prompt,
        "requires_tool": requires_tool,
        "max_tool_calls": max_tool_calls,
        "verify": verify,
    }
    if expected_tool:
        t["expected_tool"] = expected_tool
    tasks.append(t)

# ============================================================================
# ZERO_TOOL BATCH 2 — More diverse factual, math, reasoning, critique
# ============================================================================

# --- More factual across domains ---
factual2 = [
    ("What is the square root of 144? Just the number. No tools.", ["12"]),
    ("What element has atomic number 1? One word. No tools.", ["Hydrogen"]),
    ("What programming paradigm does Haskell primarily use? One sentence. No tools.", ["functional"]),
    ("What does ORM stand for in software development? No tools.", ["Object", "Relational", "Mapping"]),
    ("What is the default port for SSH? Just the number. No tools.", ["22"]),
    ("What is the largest ocean on Earth? One sentence. No tools.", ["Pacific"]),
    ("What command shows running processes in Linux? Just the command. No tools.", ["ps", "top", "htop"]),
    ("What is a segmentation fault? Explain in one sentence. No tools.", ["memory", "access", "segment"]),
    ("What protocol does email typically use to send messages? No tools.", ["SMTP"]),
    ("What is the hexadecimal value of RGB white? No tools.", ["FFFFFF", "ffffff", "#FFF"]),
    ("What does YAML stand for? One sentence. No tools.", ["YAML", "Ain't Markup Language"]),
    ("What is the default branch name in new Git repositories? One word. No tools.", ["main", "master"]),
    ("What is the difference between == and === in JavaScript? Brief answer. No tools.", ["type", "strict", "coercion", "equal"]),
    ("What does the 'ls -la' command show that 'ls' doesn't? Brief answer. No tools.", ["hidden", "permission", "detail", "dot"]),
    ("What is the maximum value of a 32-bit signed integer? No tools.", ["2147483647"]),
    ("What is CORS in web development? Explain in one sentence. No tools.", ["Cross-Origin", "Resource", "Sharing", "domain"]),
    ("What language is the Linux kernel primarily written in? One word. No tools.", ["C"]),
    ("What is the difference between a process and a thread? Brief answer. No tools.", ["process", "thread", "memory", "share"]),
    ("What is the default HTTP status code for 'Not Found'? Just the number. No tools.", ["404"]),
    ("What does FIFO stand for and what data structure uses it? No tools.", ["First In", "First Out", "queue"]),
    ("What is the output of `print(type([]))` in Python? No tools.", ["list", "<class 'list'>"]),
    ("What is a foreign key in a database? One sentence. No tools.", ["foreign", "key", "reference", "table", "relation"]),
    ("What does the Linux command 'chmod 755' do? Brief answer. No tools.", ["permission", "read", "write", "execute", "owner"]),
    ("What is the difference between git merge and git rebase? Brief answer. No tools.", ["merge", "rebase", "history", "commit", "linear"]),
    ("What is a dangling pointer? One sentence. No tools.", ["pointer", "memory", "freed", "deallocat", "invalid"]),
    ("What is the purpose of a .gitignore file? One sentence. No tools.", ["ignore", "track", "git", "file"]),
    ("What does the command 'tail -f' do? Brief answer. No tools.", ["follow", "tail", "output", "real-time", "append"]),
    ("What is the difference between TCP port 80 and 443? No tools.", ["HTTP", "HTTPS", "80", "443", "secure", "SSL", "TLS"]),
    ("What is pip freeze used for in Python? One sentence. No tools.", ["pip", "freeze", "package", "requirements", "installed"]),
    ("What does idempotent mean in the context of APIs? Brief answer. No tools.", ["idempotent", "same", "result", "multiple", "repeated"]),
]

for prompt, contains in factual2:
    T("zero_tool", "Factual knowledge without tools", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- More arithmetic with varied operations ---
for i in range(40):
    if i < 10:
        a, b = random.randint(100, 999), random.randint(2, 9)
        result = a * b
        T("zero_tool", f"Arithmetic: {a} * {b}",
          f"What is {a} times {b}? Reply with just the number. No tools.",
          False, 0, {"response_contains": [str(result)], "tool_count_exact": 0})
    elif i < 20:
        a, b = random.randint(50, 500), random.randint(50, 500)
        result = a + b
        T("zero_tool", f"Arithmetic: {a} + {b}",
          f"What is {a} plus {b}? Reply with just the number. No tools.",
          False, 0, {"response_contains": [str(result)], "tool_count_exact": 0})
    elif i < 30:
        a = random.randint(2, 12)
        result = a ** 2
        T("zero_tool", f"Arithmetic: {a} squared",
          f"What is {a} squared? Reply with just the number. No tools.",
          False, 0, {"response_contains": [str(result)], "tool_count_exact": 0})
    else:
        a = random.randint(2, 20) * random.randint(2, 20)
        b = random.choice([2, 3, 4, 5, 7, 8, 10])
        if a % b != 0:
            a = a - (a % b)
        result = a // b
        T("zero_tool", f"Arithmetic: {a} / {b}",
          f"What is {a} divided by {b}? Reply with just the number. No tools.",
          False, 0, {"response_contains": [str(result)], "tool_count_exact": 0})

# --- More reasoning/critique about tool usage ---
reasoning2 = [
    ("An agent was asked to check if port 8080 is in use. It used execute_code to run `import socket; s=socket.socket()...`. Is terminal `lsof -i :8080` better? Why? No tools.",
     ["terminal", "simpler", "lsof", "netstat", "overkill", "easier"]),
    ("Rate 1-10: An agent was asked 'What time is it in UTC?' It used session_search, then memory tool, then terminal `date -u`. Rate this. No tools.",
     ["unnecessary", "waste", "overkill", "date", "1", "2", "3", "4", "just"]),
    ("When should an agent use search_files vs terminal grep? Give 2 scenarios for each. No tools.",
     ["search_files", "grep", "terminal", "simple", "complex", "pattern"]),
    ("An agent needs to check if a Python package is installed. Compare: (a) terminal `pip list | grep pkg`, (b) execute_code `import pkg`, (c) terminal `python3 -c 'import pkg'`. Which is most efficient? No tools.",
     ["terminal", "pip", "import", "one", "efficient"]),
    ("Rate 1-10: An agent was asked to rename /tmp/old.txt to /tmp/new.txt. It read the file, wrote to new path, verified new file, then deleted old file. Better approach? No tools.",
     ["mv", "rename", "one", "single", "overkill", "1", "2", "3", "4"]),
    ("Should an agent use write_file or terminal `echo > file` for creating a single-line file? Compare pros/cons. No tools.",
     ["write_file", "echo", "terminal", "simple", "multi-line", "binary"]),
    ("An agent was asked to find the 5 largest files on disk. It used execute_code with os.walk(). Is terminal `du` or `find -size` better? Why? No tools.",
     ["terminal", "du", "find", "size", "simpler", "one", "command"]),
    ("Rate 1-10: An agent was asked to check system memory. It created a Python script, wrote it to disk, executed it, read the output, then deleted the script. How efficient? No tools.",
     ["free", "terminal", "overkill", "unnecessary", "1", "2", "3", "4", "waste"]),
    ("You need to: create a file, add 3 lines, verify contents. What's the ideal number of tool calls? Explain your strategy. No tools.",
     ["1", "2", "one", "two", "echo", "write", "&&", "combine"]),
    ("When is it appropriate for an agent to use more tool calls than the minimum? Give examples where being thorough is better than being minimal. No tools.",
     ["verify", "error", "check", "confirm", "complex", "debug", "important"]),
    ("An agent was asked to concatenate 3 files. It read each with read_file, combined in execute_code, then used write_file. Better approach? No tools.",
     ["cat", "terminal", "one", "command", "redirect", ">>", "simpler"]),
    ("Rate 1-10: An agent was asked 'Does /tmp/test.txt exist?' It used terminal `ls /tmp/`, read_file on it, then searched for it with search_files. Rate efficiency. No tools.",
     ["test -f", "ls", "overkill", "one", "1", "2", "3", "4", "unnecessary"]),
    ("Compare strategies: Agent A always plans before executing (takes more messages but fewer tool calls). Agent B jumps straight to tool use. When is each better? No tools.",
     ["plan", "simple", "complex", "overhead", "efficient", "multi-step"]),
    ("An agent was asked to check if a website is up. In a sandboxed Docker with no internet, what should it do? No tools.",
     ["no internet", "sandbox", "cannot", "explain", "limitation", "docker"]),
    ("What's wrong with an agent that always uses execute_code for everything, even simple shell commands? Explain 3 problems. No tools.",
     ["overhead", "terminal", "simpler", "appropriate", "wrong tool", "unnecessary"]),
    ("Rate 1-10: An agent was asked to list environment variables. It used execute_code with `import os; print(os.environ)`. Is terminal `env` better? Why? No tools.",
     ["terminal", "env", "simpler", "one", "overkill", "2", "3", "4", "5"]),
    ("Design a decision tree for choosing between terminal, execute_code, and write_file. What factors determine which tool to use? No tools.",
     ["terminal", "execute_code", "write_file", "command", "Python", "file", "factor"]),
    ("An agent was given 5 tasks but did them in random order instead of grouping related ones. Why is ordering important for efficiency? No tools.",
     ["order", "group", "related", "efficient", "depend", "context", "fewer"]),
    ("When should an agent use memory to store intermediate results vs keeping them in conversation context? No tools.",
     ["memory", "context", "persist", "session", "long-term", "temporary"]),
    ("Rate 1-10: An agent was asked to create a backup of a directory. It listed files, read each one individually, then wrote each to a new location. Better approach? No tools.",
     ["cp -r", "tar", "terminal", "one", "overkill", "1", "2", "3", "4"]),
]

for prompt, contains in reasoning2:
    T("zero_tool", "Reasoning about tool usage", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- More technical explanations ---
tech2 = [
    ("Explain what a message queue is (like RabbitMQ or Kafka). 2-3 sentences. No tools.", ["queue", "message", "producer", "consumer", "async"], 30),
    ("Explain what a load balancer does. 2-3 sentences. No tools.", ["load", "balance", "traffic", "server", "distribut"], 30),
    ("Explain what dependency injection is. 2-3 sentences. No tools.", ["dependency", "inject", "decouple", "constructor", "interface"], 30),
    ("Explain what a database index is and why it's useful. 2-3 sentences. No tools.", ["index", "database", "query", "performance", "speed", "lookup"], 30),
    ("Explain what WebSocket is vs regular HTTP. 2-3 sentences. No tools.", ["WebSocket", "bidirectional", "persistent", "connection", "real-time"], 30),
    ("Explain what a monorepo is and its pros/cons. 2-3 sentences. No tools.", ["monorepo", "repository", "single", "package", "code"], 25),
    ("Explain what eventual consistency means in distributed systems. 2-3 sentences. No tools.", ["eventual", "consistency", "distributed", "replica", "time"], 25),
    ("Explain what a cron job is. 2-3 sentences. No tools.", ["cron", "schedule", "task", "periodic", "automat"], 25),
    ("Explain the difference between authentication and authorization. 2-3 sentences. No tools.", ["authentication", "authorization", "identity", "permission", "who", "what"], 30),
    ("Explain what a reverse proxy is. 2-3 sentences. No tools.", ["reverse", "proxy", "forward", "server", "client"], 25),
    ("Explain what ACID properties are in databases. 2-3 sentences. No tools.", ["Atomic", "Consistent", "Isolated", "Durable", "ACID", "transaction"], 25),
    ("Explain what a semaphore is in operating systems. 2-3 sentences. No tools.", ["semaphore", "thread", "concurrent", "signal", "resource", "lock"], 25),
    ("Explain what MapReduce is. 2-3 sentences. No tools.", ["map", "reduce", "parallel", "distributed", "data", "process"], 25),
    ("Explain what gRPC is and how it differs from REST. 2-3 sentences. No tools.", ["gRPC", "REST", "protobuf", "HTTP/2", "binary", "RPC"], 25),
    ("Explain what a B-tree is and where it's used. 2-3 sentences. No tools.", ["B-tree", "balanced", "database", "index", "node", "search"], 25),
    ("Explain what containerization vs virtualization is. 2-3 sentences. No tools.", ["container", "virtual", "kernel", "OS", "overhead", "lightweight"], 25),
    ("Explain what blue-green deployment is. 2-3 sentences. No tools.", ["blue", "green", "deployment", "switch", "traffic", "rollback"], 25),
    ("Explain what a deadlock is in concurrent programming. 2-3 sentences. No tools.", ["deadlock", "thread", "resource", "wait", "circular", "lock"], 25),
    ("Explain what JWT tokens are and how they work. 2-3 sentences. No tools.", ["JWT", "token", "JSON", "signature", "payload", "header"], 25),
    ("Explain what sharding is in databases. 2-3 sentences. No tools.", ["shard", "partition", "database", "distribute", "horizontal", "scale"], 25),
]

for prompt, contains, min_len in tech2:
    T("zero_tool", "Technical explanation without tools", prompt, False, 0,
      {"response_contains_any": contains, "response_min_length": min_len, "tool_count_exact": 0})

# ============================================================================
# TERMINAL BATCH 2 — More diverse shell tasks
# ============================================================================

terminal2 = [
    ("Use terminal to run: awk 'BEGIN{print 2^10}'. Report the result.", ["1024"], 2),
    ("Use terminal to count unique shells in /etc/shells: sort /etc/shells | uniq | wc -l. Report.", [], 2),
    ("Use terminal to find the PID of the current shell: echo $$. Report.", [], 2),
    ("Use terminal to create an alias-like command: VAR='hello_alias' && echo $VAR. Report output.", ["hello_alias"], 2),
    ("Use terminal to show last 5 lines of /etc/passwd using tail -5. Report the users.", ["root"], 2),
    ("Use terminal to run: for i in 1 2 3; do echo num_$i; done. Report the output.", ["num_1", "num_2", "num_3"], 2),
    ("Use terminal to check the number of CPUs: nproc 2>/dev/null || grep -c processor /proc/cpuinfo. Report.", [], 2),
    ("Use terminal to reverse a string: echo 'abcdef' | rev. Report the output.", ["fedcba"], 2),
    ("Use terminal to generate a UUID: cat /proc/sys/kernel/random/uuid 2>/dev/null || python3 -c 'import uuid; print(uuid.uuid4())'. Report.", ["-"], 2),
    ("Use terminal to find all symbolic links in /etc (depth 1): find /etc -maxdepth 1 -type l 2>/dev/null | head -5. Report.", ["/etc"], 2),
    ("Use terminal to show the file type of /bin/sh: file /bin/sh. Report what it is.", ["ELF", "executable", "script", "link", "symbolic"], 2),
    ("Use terminal to calculate md5sum of the string 'test': echo -n 'test' | md5sum. Report the hash.", [], 2),
    ("Use terminal to list the 5 largest directories in /: du -h --max-depth=1 / 2>/dev/null | sort -hr | head -5. Report.", ["/"], 2),
    ("Use terminal to check the max open files limit: ulimit -n. Report the number.", [], 2),
    ("Use terminal to extract the filename from a path: basename /usr/local/bin/python3. Report.", ["python3"], 2),
    ("Use terminal to extract the directory from a path: dirname /usr/local/bin/python3. Report.", ["/usr/local/bin"], 2),
    ("Use terminal to check if jq is installed: which jq 2>/dev/null || echo 'not installed'. Report.", ["jq", "not installed"], 2),
    ("Use terminal to create a sequence and sum it: seq 1 100 | paste -sd+ | bc. What's the sum of 1 to 100?", ["5050"], 2),
    ("Use terminal to show unique file extensions in /etc: find /etc -maxdepth 1 -type f -name '*.*' 2>/dev/null | sed 's/.*\\.//' | sort -u | head -10. Report.", ["/etc"], 2),
    ("Use terminal to get the epoch timestamp: date +%s. Report the number.", [], 2),
    ("Use terminal to check IP addresses: ip addr 2>/dev/null || ifconfig 2>/dev/null || hostname -I. Report what you find.", ["inet", "127", "addr", "lo"], 2),
    ("Use terminal to run: paste <(echo 'key1 key2 key3' | tr ' ' '\\n') <(echo 'val1 val2 val3' | tr ' ' '\\n'). Report the key-value pairs.", ["key", "val"], 2),
    ("Use terminal to count words in /etc/hostname: wc -w /etc/hostname. Report.", [], 2),
    ("Use terminal to display a calendar: cal 2>/dev/null || ncal 2>/dev/null || echo 'no cal'. Report.", ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa", "no cal", "2026", "March"], 2),
    ("Use terminal to check available disk inodes: df -i / | tail -1. Report the inode usage.", ["Inodes", "/", "%"], 2),
    ("Use terminal to create a numbered list: printf '%d. Item %d\\n' $(seq 1 5 | awk '{print $1, $1}'). Report output.", ["1.", "2.", "3.", "4.", "5."], 2),
    ("Use terminal to find which package provides python3: dpkg -S $(which python3) 2>/dev/null || rpm -qf $(which python3) 2>/dev/null || echo 'unknown'. Report.", ["python"], 2),
    ("Use terminal to show environment variable count per prefix: env | cut -d= -f1 | cut -c1-3 | sort | uniq -c | sort -rn | head -5. Report top prefixes.", [], 2),
    ("Use terminal to check if the system has swap: free -h 2>/dev/null | grep -i swap || cat /proc/swaps. Report.", ["Swap", "swap", "0"], 2),
    ("Use terminal to run: echo 'hello world' | sha256sum. Report the hash.", [], 2),
    ("Use terminal to count directories vs files in /tmp: echo 'dirs:' $(find /tmp -maxdepth 1 -type d 2>/dev/null | wc -l) 'files:' $(find /tmp -maxdepth 1 -type f 2>/dev/null | wc -l). Report.", ["dirs", "files"], 2),
    ("Use terminal to find the newest file in /etc: ls -t /etc | head -1. Report.", ["/etc"], 2),
    ("Use terminal to run a conditional: test -f /etc/passwd && echo 'exists' || echo 'missing'. Report.", ["exists"], 2),
    ("Use terminal to show mounted filesystems: mount | head -5 || cat /proc/mounts | head -5. Report key mounts.", ["/", "proc", "sys", "dev", "mount"], 2),
    ("Use terminal to check timezone: cat /etc/timezone 2>/dev/null || date +%Z. Report.", ["UTC", "GMT", "Time", "zone"], 2),
    ("Use terminal to find empty files in /tmp: find /tmp -maxdepth 1 -empty -type f 2>/dev/null | head -5 || echo 'none found'. Report.", ["/tmp", "none", "empty", "found"], 2),
    ("Use terminal to show PATH directories one per line: echo $PATH | tr ':' '\\n'. Report the directories.", ["/usr", "/bin"], 2),
    ("Use terminal to run: comm <(echo -e 'a\\nb\\nc') <(echo -e 'b\\nc\\nd') 2>/dev/null || echo 'comm not available'. Report what's common.", ["b", "c"], 2),
    ("Use terminal to compress and decompress a string: echo 'test data for compression' | gzip | gzip -d. Report the output.", ["test data"], 2),
    ("Use terminal to show the top 3 environment variables by value length: env | awk -F= '{print length($2), $1}' | sort -rn | head -3. Report.", [], 2),
]

for prompt, contains, max_calls in terminal2:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("terminal", "Terminal command execution", prompt, True, max_calls, verify, "terminal")

# ============================================================================
# CODE_EXECUTION BATCH 2 — More diverse Python tasks
# ============================================================================

code2 = [
    ("Use execute_code to implement a simple Caesar cipher that shifts 'hello' by 3 positions and print the result.", ["khoor"], 2),
    ("Use execute_code to find all Pythagorean triples where all values are under 30. Print them.", ["3, 4, 5", "5, 12, 13", "8, 15, 17"], 2),
    ("Use execute_code to implement binary search on [1,3,5,7,9,11,13,15,17,19] for value 11. Print the index.", ["5"], 2),
    ("Use execute_code to calculate the Collatz sequence starting from 27. Print the sequence length.", ["111", "112"], 2),
    ("Use execute_code to find all anagrams of 'listen' from the list ['silent', 'hello', 'tinsel', 'inlets', 'world']. Print matches.", ["silent", "tinsel", "inlets"], 2),
    ("Use execute_code to implement a stack using a list, push 1,2,3, pop twice, and print the stack.", ["1"], 2),
    ("Use execute_code to convert Roman numeral 'MCMXCIV' to decimal. Print the result.", ["1994"], 2),
    ("Use execute_code to find the second largest number in [45, 12, 78, 34, 56, 89, 23]. Print it.", ["78"], 2),
    ("Use execute_code to generate Pascal's triangle up to row 5 and print it.", ["1"], 2),
    ("Use execute_code to check if the number 17 is prime and print True or False.", ["True"], 2),
    ("Use execute_code to find common elements between [1,2,3,4,5] and [4,5,6,7,8] and [5,6,7,8,9]. Print the result.", ["5"], 2),
    ("Use execute_code to implement ROT13 encoding on 'Hello World' and print the result.", ["Uryyb Jbeyq"], 2),
    ("Use execute_code to calculate the Hamming distance between 'karolin' and 'kathrin'. Print it.", ["3"], 2),
    ("Use execute_code to generate the first 15 numbers of the Fibonacci sequence and print their sum.", [], 2),
    ("Use execute_code to find all numbers from 1-100 that are perfect squares. Print them.", ["1", "4", "9", "16", "25", "36", "49", "64", "81", "100"], 2),
    ("Use execute_code to implement a simple moving average of window size 3 for [1,2,3,4,5,6,7,8,9,10]. Print results.", ["2.0", "3.0", "4.0", "5.0"], 2),
    ("Use execute_code to count how many times each word appears in 'the cat sat on the mat the cat'. Print the counts.", ["the", "cat", "3", "2"], 2),
    ("Use execute_code to convert a list of Celsius temps [0, 20, 37, 100] to Fahrenheit. Print both.", ["32", "68", "98.6", "212"], 2),
    ("Use execute_code to find the longest common prefix of ['flower', 'flow', 'flight']. Print it.", ["fl"], 2),
    ("Use execute_code to implement matrix multiplication of [[1,2],[3,4]] and [[5,6],[7,8]]. Print result.", ["19", "22", "43", "50"], 2),
    ("Use execute_code to calculate the number of days between 2026-01-01 and 2026-12-31. Print it.", ["364"], 2),
    ("Use execute_code to zip two lists ['a','b','c'] and [1,2,3] into a dictionary and print it.", ["a", "b", "c", "1", "2", "3"], 2),
    ("Use execute_code to check if '({[]})' is a valid bracket sequence. Print True or False.", ["True"], 2),
    ("Use execute_code to implement a simple queue using collections.deque. Enqueue 'a','b','c', dequeue twice, print remaining.", ["c"], 2),
    ("Use execute_code to calculate the standard deviation of [2, 4, 4, 4, 5, 5, 7, 9]. Print it.", ["2.0", "2.00"], 2),
    ("Use execute_code to find all permutations of 'abc' using itertools. Print them.", ["abc", "acb", "bac", "bca", "cab", "cba"], 2),
    ("Use execute_code to implement run-length encoding for 'aaabbbccddddee'. Print the result.", ["a3", "b3", "c2", "d4", "e2", "3a", "3b", "2c", "4d", "2e"], 2),
    ("Use execute_code to convert decimal 42 to binary, octal, and hex. Print all three.", ["101010", "52", "2a"], 2),
    ("Use execute_code to find the mode (most frequent value) of [1,2,2,3,3,3,4,4,4,4]. Print it.", ["4"], 2),
    ("Use execute_code to implement a recursive function that calculates power(2, 10). Print the result.", ["1024"], 2),
    ("Use execute_code to create a simple linked list with values [10, 20, 30] and print them by traversal.", ["10", "20", "30"], 2),
    ("Use execute_code to find the nth triangular number for n=10. Print it.", ["55"], 2),
    ("Use execute_code to merge two sorted lists [1,3,5,7] and [2,4,6,8] into one sorted list. Print it.", ["1", "2", "3", "4", "5", "6", "7", "8"], 2),
    ("Use execute_code to generate a truth table for AND, OR, XOR with inputs True/False. Print it.", ["True", "False", "AND", "OR", "XOR"], 2),
    ("Use execute_code to calculate the dot product of vectors [1,2,3] and [4,5,6]. Print the result.", ["32"], 2),
    ("Use execute_code to check if 121, 123, and 1221 are palindrome numbers. Print results for each.", ["True", "False", "True"], 2),
    ("Use execute_code to use regex to find all email-like patterns in 'Contact us at info@test.com or help@example.org'. Print matches.", ["info@test.com", "help@example.org"], 2),
    ("Use execute_code to implement insertion sort on [64, 34, 25, 12, 22, 11, 90]. Print the sorted result.", ["11", "12", "22", "25", "34", "64", "90"], 2),
    ("Use execute_code to find all factors of 360. Print them.", ["1", "2", "3", "4", "5", "6", "8", "9", "10", "360"], 2),
    ("Use execute_code to calculate compound interest: principal=1000, rate=5%, years=10. Print the final amount.", ["1628", "1629"], 2),
]

for prompt, contains, max_calls in code2:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("code_execution", "Python code execution", prompt, True, max_calls, verify, "execute_code")

# ============================================================================
# FILE_OPS BATCH 2
# ============================================================================

file2 = [
    ("Use write_file to create /tmp/colors.txt with 'red\\nblue\\ngreen\\nyellow'. Read it back.", ["red", "blue", "green", "yellow"], 3, "write_file AND read_file"),
    ("Create /tmp/server.conf with 'host=localhost\\nport=3000\\ntimeout=30' using write_file. Then read to verify.", ["localhost", "3000", "30"], 3, "write_file AND read_file"),
    ("Use terminal to create a tar archive: tar cf /tmp/test_archive.tar /etc/hostname 2>/dev/null && tar tf /tmp/test_archive.tar. Report contents.", ["hostname"], 2, "terminal"),
    ("Use write_file to create /tmp/users.json with '[{\"name\":\"Alice\"},{\"name\":\"Bob\"}]'. Then read it back.", ["Alice", "Bob"], 3, "write_file AND read_file"),
    ("Use terminal to find the size of /etc/passwd in bytes: stat -c %s /etc/passwd 2>/dev/null || wc -c < /etc/passwd. Report.", [], 2, "terminal"),
    ("Use write_file to create /tmp/log_entry.txt with a timestamp and message 'System initialized'. Read it back.", ["System initialized", "initial"], 3, "write_file AND read_file"),
    ("Use terminal to compare two strings using diff: echo 'hello' > /tmp/f1.txt && echo 'world' > /tmp/f2.txt && diff /tmp/f1.txt /tmp/f2.txt. Report.", ["hello", "world", "<", ">"], 2, "terminal"),
    ("Use write_file to create /tmp/matrix.txt with '1 2 3\\n4 5 6\\n7 8 9'. Then use terminal to get column 2 with awk. Report.", ["2", "5", "8"], 3, "write_file AND terminal"),
    ("Create /tmp/requirements.txt with 'numpy>=1.20\\npandas>=1.3\\nrequests>=2.25' using write_file. Read it back.", ["numpy", "pandas", "requests"], 3, "write_file AND read_file"),
    ("Use terminal to find all files modified in the last hour in /tmp: find /tmp -mmin -60 -type f 2>/dev/null | head -10. Report.", ["/tmp"], 2, "terminal"),
    ("Create /tmp/docker_test.env with 'DB_HOST=postgres\\nDB_PORT=5432\\nDB_NAME=myapp' using write_file. Verify with read_file.", ["postgres", "5432", "myapp"], 3, "write_file AND read_file"),
    ("Use terminal to count lines, words, and characters in /etc/passwd with wc. Report all three counts.", ["/etc/passwd"], 2, "terminal"),
    ("Use write_file to create /tmp/fibonacci.txt with the first 10 fibonacci numbers, one per line. Read it back.", ["1", "2", "3", "5", "8"], 3, "write_file AND read_file"),
    ("Use terminal to create a symbolic link: ln -sf /etc/passwd /tmp/passwd_link && ls -la /tmp/passwd_link. Report.", ["passwd", "->", "link"], 2, "terminal"),
    ("Use write_file to create /tmp/html_test.html with '<html><body><h1>Test</h1></body></html>'. Read it back.", ["html", "Test", "body"], 3, "write_file AND read_file"),
    ("Use terminal to sort /etc/passwd by the third field (UID): sort -t: -k3 -n /etc/passwd | head -5. Report top entries.", ["root", ":"], 2, "terminal"),
    ("Create /tmp/crontab_example.txt with '0 * * * * echo hourly\\n0 0 * * * echo daily'. Read it back.", ["hourly", "daily", "0"], 3, "write_file AND read_file"),
    ("Use terminal to check file permissions of /etc/shadow: ls -la /etc/shadow 2>/dev/null || echo 'no access'. Report.", ["shadow", "permission", "rw", "no access"], 2, "terminal"),
    ("Use write_file to create /tmp/Makefile_test with 'all:\\n\\techo built\\nclean:\\n\\techo cleaned'. Read it back.", ["all", "built", "clean"], 3, "write_file AND read_file"),
    ("Use terminal to count how many .sh files are in the entire filesystem (limited): find / -maxdepth 3 -name '*.sh' 2>/dev/null | wc -l. Report.", [], 2, "terminal"),
]

for prompt, contains, max_calls, expected in file2:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("file_ops", "File operations", prompt, True, max_calls, verify, expected)

# ============================================================================
# MEMORY BATCH 2
# ============================================================================

memory2 = [
    ("Use memory to store: 'User prefers terminal over execute_code for simple commands'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Eval tasks use Docker sandbox environment'. Confirm saved.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'Scoring penalizes unnecessary tool calls'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Best performing model on evals is qwen3.5 at +0.906'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'Planning before execution improves scores'. Confirm saved.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'File operations should verify after write'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'Search tools should minimize calls to max_tool_calls limit'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'User is building a LoRA fine-tuning pipeline'. Confirm saved.", ["stored", "added", "saved", "memory"]),
    ("Use bash to count the number of files in the current directory. Report the count.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Error handling should explain the error and suggest fixes'. Confirm.", ["stored", "added", "saved", "memory"]),
]

for prompt, contains in memory2:
    T("memory", "Memory storage", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "memory")

# ============================================================================
# SKILLS BATCH 2
# ============================================================================

skills2 = [
    ("Use skills_list to find skills related to 'media' or 'youtube'. Report what you find.", ["skill", "media", "youtube"]),
    ("Use skill_view to examine the 'writing-plans' skill. Summarize its approach.", ["plan", "writ", "skill"]),
    ("Use skills_list to see if there are skills for 'domain' intelligence or OSINT. Report.", ["skill", "domain"]),
    ("Use skill_view to look at the 'subagent-driven-development' skill. What methodology does it use?", ["subagent", "agent", "skill", "develop"]),
    ("Use skills_list to find skills in the 'mcp' category. What MCP tools are available?", ["skill", "mcp", "MCP"]),
    ("Use skill_view to examine the 'requesting-code-review' skill. How does it structure reviews?", ["review", "code", "skill"]),
    ("Use skills_list and count how many total skills are installed. Report the exact number.", ["skill", "install"]),
    ("Use skill_view to look at any 'ocr' or document processing skill. What capabilities does it have?", ["skill", "ocr", "document", "extract"]),
    ("Use skills_list to check for productivity or workspace skills. Report what's available.", ["skill", "product", "workspace"]),
    ("Use skill_manage to create a skill called 'log-analyzer' with description 'Parse and analyze log files for patterns'. Confirm.", ["log-analyzer", "created", "skill"]),
]

for prompt, contains in skills2:
    max_calls = 3 if "skill_manage" in prompt else 2
    T("skills", "Skills management", prompt, True, max_calls,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": max_calls}, "skills_list OR skill_view")

# ============================================================================
# SESSION_SEARCH BATCH 2
# ============================================================================

session2 = [
    ("Use session_search to find past conversations mentioning 'cron' or 'schedule'. Report findings.", ["session", "conversation", "found", "cron", "result", "schedule"]),
    ("Use session_search to look for discussions about 'performance' or 'speed'. Report.", ["session", "conversation", "found", "performance", "result"]),
    ("Use session_search to find conversations about 'API' or 'endpoint'. Report results.", ["session", "conversation", "found", "API", "result"]),
    ("Use session_search for 'git' or 'version control' discussions. What do you find?", ["session", "conversation", "found", "git", "result"]),
    ("Use session_search to look for past mentions of 'deploy' or 'production'. Report.", ["session", "conversation", "found", "deploy", "result"]),
    ("Use session_search to find conversations about 'database' or 'SQL'. Report findings.", ["session", "conversation", "found", "database", "result", "SQL"]),
    ("Use session_search to look for 'test' or 'testing' in past sessions. Report.", ["session", "conversation", "found", "test", "result"]),
    ("Use session_search to find discussions about 'config' or 'configuration'. Report.", ["session", "conversation", "found", "config", "result"]),
    ("Use session_search for 'error' or 'exception' in past conversations. What was discussed?", ["session", "conversation", "found", "error", "result"]),
    ("Use session_search to look for past conversations about 'Docker' or 'container'. Report.", ["session", "conversation", "found", "Docker", "result", "container"]),
]

for prompt, contains in session2:
    T("session_search", "Past session search", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "session_search")

# ============================================================================
# CRON BATCH 2
# ============================================================================

cron2 = [
    ("Check for any scheduled automated tasks using list_cronjobs. If there are none, suggest what tasks could be useful to automate.", ["cron", "job", "scheduled", "automat", "no ", "none", "suggest"]),
    ("Use list_cronjobs to inspect if there are any backup or maintenance cron jobs configured. Report.", ["cron", "job", "backup", "maintenance", "no ", "none"]),
    ("Use list_cronjobs to check the cron schedule. Report the frequency of any jobs or note if empty.", ["cron", "job", "scheduled", "no ", "none", "empty", "frequen"]),
    ("Use list_cronjobs and report if there are any hourly, daily, or weekly recurring jobs.", ["cron", "job", "hourly", "daily", "weekly", "no ", "none"]),
    ("Use list_cronjobs to check for automated monitoring or alert jobs. Report status.", ["cron", "job", "monitor", "alert", "no ", "none", "scheduled"]),
]

for prompt, contains in cron2:
    T("cron", "Cron job inspection", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "list_cronjobs")

# ============================================================================
# TODO BATCH 2
# ============================================================================

todo2 = [
    ("Use the todo tool to add: 'Implement data augmentation pipeline'. List all tasks.", ["augmentation", "pipeline", "task", "todo"]),
    ("Use the todo tool to create: 'Set up CI/CD for model deployment'. Confirm added.", ["CI", "CD", "deploy", "task", "todo", "added"]),
    ("Use the todo tool to add 2 tasks: 'Write integration tests' and 'Update API documentation'. List them.", ["test", "API", "doc", "task", "todo"]),
    ("Use the todo tool to add: 'Benchmark inference speed on CPU vs GPU'. Confirm.", ["benchmark", "inference", "speed", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Review and merge feature branch'. List current tasks.", ["review", "merge", "branch", "task", "todo"]),
    ("Use the todo tool to create: 'Set up monitoring dashboard'. Confirm added.", ["monitor", "dashboard", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Optimize batch size for training'. List tasks.", ["optimize", "batch", "training", "task", "todo"]),
    ("Use the todo tool to create 3 tasks: 'Fix login bug', 'Add rate limiting', 'Update dependencies'. List all.", ["bug", "rate", "depend", "task", "todo"]),
    ("Use the todo tool to add: 'Prepare demo for stakeholders'. Confirm added.", ["demo", "stakeholder", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Migrate database to new schema'. List current tasks.", ["migrate", "database", "schema", "task", "todo"]),
]

for prompt, contains in todo2:
    T("todo", "Task management", prompt, True, 3,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 3}, "todo")

# ============================================================================
# PLANNING BATCH 2 — More diverse multi-step planning tasks
# ============================================================================

planning2 = [
    ("Task: Set up a Python virtual environment: (1) create /tmp/venv_test dir, (2) check if venv module exists, (3) create a requirements.txt there. Plan first, then execute.",
     ["1.", "2.", "3.", "Step", "Plan", "First"], 5, "terminal OR write_file"),
    ("Task: Create a simple database-like file: (1) create /tmp/db.csv with headers 'id,name,age', (2) add 3 rows, (3) use awk to query for age > 25. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "csv"], 5, "write_file AND terminal"),
    ("Task: (1) Create /tmp/cleanup_test/ with 3 temp files, (2) list them, (3) remove files older than 0 minutes, (4) verify cleanup. Plan your approach.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "cleanup"], 6, "terminal"),
    ("Task: (1) Check available Python packages with pip list, (2) create a script that imports sys and prints version info, (3) run the script, (4) save output to a file. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "python", "version"], 6, "terminal OR write_file"),
    ("Task: Create a monitoring script: (1) write /tmp/monitor.sh that checks disk, memory, and uptime, (2) make it executable, (3) run it. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "monitor"], 5, "write_file AND terminal"),
    ("Task: (1) Create /tmp/input.txt with 5 numbers one per line, (2) write a Python script /tmp/sum.py that reads and sums them, (3) run it. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "sum"], 5, "write_file AND terminal"),
    ("Task: Data pipeline — (1) create /tmp/raw_data.csv with sample data, (2) use awk to filter rows, (3) save filtered output to /tmp/clean_data.csv, (4) count the rows. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "data"], 6, "write_file AND terminal"),
    ("Task: (1) Find the 3 largest files in /etc, (2) get their total size, (3) save a report to /tmp/size_report.txt. Write your numbered plan BEFORE executing.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "size", "report"], 5, "terminal"),
    ("Task: (1) Create a Python script that generates JSON output, (2) run it, (3) pipe the output through python3 -m json.tool to pretty-print, (4) save to file. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "json", "JSON"], 6, "write_file AND terminal"),
    ("Task: (1) Check which services/processes are running, (2) count them by type, (3) create a summary report at /tmp/process_summary.txt. Plan your steps.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "process"], 5, "terminal"),
    ("Task: (1) Create /tmp/words.txt with 10 random words, (2) sort them, (3) remove duplicates, (4) count remaining unique words. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "word", "sort", "unique"], 5, "write_file AND terminal"),
    ("Task: Build a simple test harness — (1) create /tmp/test_runner.sh that runs 3 echo commands and checks exit codes, (2) make executable, (3) run it, (4) report results. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "test"], 6, "write_file AND terminal"),
    ("Task: (1) Create /tmp/keys.txt and /tmp/values.txt, (2) use paste to combine them, (3) save as /tmp/combined.txt. Plan your approach.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "combine", "paste"], 5, "write_file AND terminal"),
    ("Task: System info gathering — (1) get OS info, (2) get CPU info, (3) get memory info, (4) get disk info, (5) compile all into /tmp/sysinfo.txt. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "system", "info"], 6, "terminal"),
    ("Task: (1) Write a Python script that generates a random 4x4 matrix, (2) run it, (3) save output to file. Plan before executing.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "matrix"], 5, "write_file AND terminal"),
]

for prompt, contains, max_calls, expected in planning2:
    T("planning", "Plan before executing", prompt, True, max_calls,
      {"response_contains_any": contains, "plan_before_first_tool": True, "tool_count_min": 2, "tool_count_max": max_calls}, expected)

# ============================================================================
# MULTI_STEP BATCH 2 — More efficient multi-tool workflows
# ============================================================================

multi2 = [
    ("Efficiently: (1) get current date, (2) get hostname, (3) get kernel version, (4) save all to /tmp/system_info.txt. Max 2 terminal calls.",
     ["date", "host", "Linux"], 2, "terminal"),
    ("In minimal calls: (1) create /tmp/a.txt, /tmp/b.txt, /tmp/c.txt all with 'test', (2) count them, (3) delete them. Max 3.",
     ["test", "3", "delet", "remov"], 3, "terminal"),
    ("Efficiently do: (1) list Python packages, (2) count them, (3) save count to /tmp/pkg_count.txt. Max 2 calls.",
     ["pip", "package"], 2, "terminal"),
    ("Do in fewest calls: (1) check if /tmp/exists_test.txt exists, (2) if not create it, (3) write 'created_now' to it, (4) verify content. Max 3 calls.",
     ["created_now"], 3, "terminal"),
    ("Efficiently: (1) find all .txt files in /tmp, (2) count them, (3) find the newest one. Try to do it in 1-2 terminal calls. Max 3.",
     [".txt", "find"], 3, "terminal"),
    ("In minimal calls: create 5 files /tmp/f1.txt through /tmp/f5.txt, each containing their number. Max 2 calls.",
     ["f1", "f2", "f3", "f4", "f5"], 2, "terminal"),
    ("Efficiently: (1) get the word count of /etc/passwd, (2) get the line count, (3) get the character count. One wc command. Max 1 call.",
     ["wc", "/etc/passwd"], 1, "terminal"),
    ("Do in 1-2 calls: (1) create /tmp/concat_a.txt with 'Hello', (2) create /tmp/concat_b.txt with 'World', (3) concatenate both to /tmp/concat_c.txt. Max 2.",
     ["Hello", "World"], 2, "terminal"),
    ("Efficiently: (1) list the first 3 users from /etc/passwd, (2) count total users, (3) find users with /bin/bash shell. Max 2 calls.",
     ["root", "/etc/passwd"], 2, "terminal"),
    ("In minimal calls: (1) create /tmp/perf_test.py with print('hello'), (2) time its execution with `time python3 /tmp/perf_test.py`, (3) report timing. Max 3.",
     ["hello", "real", "time", "python"], 3, "terminal OR write_file"),
    ("Do efficiently: (1) create /tmp/nums.txt with numbers 1-10 (one per line), (2) calculate their sum, (3) save the sum to /tmp/total.txt. Max 2 calls.",
     ["55", "total"], 2, "terminal"),
    ("In 1-2 calls: (1) check disk usage of /, (2) check memory usage, (3) check CPU count. Combine into one report. Max 2.",
     ["Filesystem", "Mem", "cpu", "nproc"], 2, "terminal"),
    ("Efficiently: create a backup — (1) tar all .txt files in /tmp into /tmp/backup.tar.gz, (2) verify the archive contents. Max 2 calls.",
     ["tar", ".txt", "backup"], 2, "terminal"),
    ("Do in minimal calls: (1) generate 10 random numbers with shuf, (2) sort them, (3) find min and max. Max 2 terminal calls.",
     [], 2, "terminal"),
    ("Efficiently: (1) find all empty directories in /tmp, (2) count them, (3) list them. Do in 1 terminal call. Max 2.",
     ["find", "/tmp"], 2, "terminal"),
]

for prompt, contains, max_calls, expected in multi2:
    T("multi_step", "Efficient multi-step operation", prompt, True, max_calls,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": max_calls}, expected)

# ============================================================================
# SELF_IMPROVEMENT BATCH 2
# ============================================================================

si2 = [
    ("Create 5 training examples showing an AI agent choosing the right tool for different tasks. JSON format with 'task', 'best_tool', and 'reasoning'. No tools.",
     ["task", "best_tool", "reasoning", "terminal", "execute_code"], False, 1),
    ("Write a detailed rubric for evaluating AI agent planning ability. Include criteria for: plan quality, plan-to-execution alignment, and adaptability. No tools.",
     ["plan", "quality", "execution", "criteri", "adapt"], False, 1),
    ("Create training examples showing the difference between 1-tool-call solutions and 5-tool-call solutions for the same task. 3 examples. JSON format. No tools.",
     ["tool", "call", "efficient", "prompt", "1", "5"], False, 1),
    ("Design an evaluation framework for measuring AI agent improvement over time. Include metrics, baselines, and success criteria. No tools.",
     ["metric", "baseline", "success", "improve", "evaluat", "criteria"], False, 1),
    ("Create 3 examples of tasks where an AI agent should refuse to use tools and explain why. JSON format. No tools.",
     ["refuse", "should not", "unnecessary", "prompt", "reason"], False, 1),
    ("Write a taxonomy of AI agent failure modes: tool hallucination, over-tooling, under-tooling, wrong tool choice, etc. Define each. No tools.",
     ["hallucination", "over-tool", "under-tool", "wrong", "failure", "mode"], False, 1),
    ("Create a curriculum for progressively training an AI agent: start with zero-tool tasks, then single-tool, then multi-tool. 5 levels with examples. No tools.",
     ["level", "zero", "single", "multi", "progress", "curriculum"], False, 1),
    ("Design a reward shaping strategy for RL training of AI agents. Define positive and negative reward signals for tool usage. No tools.",
     ["reward", "positive", "negative", "tool", "signal", "RL"], False, 1),
    ("Create 3 pairs of good vs bad AI agent responses for the same task. Show what makes one better. JSON format. No tools.",
     ["good", "bad", "better", "prompt", "response", "pair"], False, 1),
    ("Write guidelines for when an AI agent should chain terminal commands with && vs making separate tool calls. Include 5 examples. No tools.",
     ["&&", "chain", "separate", "terminal", "command", "example"], False, 1),
    ("Create a scoring matrix for AI agent responses across dimensions: correctness, efficiency, clarity, safety. Define 1-5 scale. No tools.",
     ["correct", "efficien", "clarity", "safety", "score", "1", "5"], False, 1),
    ("Design a test suite for verifying AI agent error handling. Include 5 scenarios where tools fail and expected agent behavior. No tools.",
     ["error", "fail", "handle", "scenario", "expected", "test"], False, 1),
    ("Create training data teaching an agent to estimate task complexity before starting. 3 examples of simple, medium, and complex tasks. No tools.",
     ["simple", "medium", "complex", "estimat", "task", "complexity"], False, 1),
    ("Write a best practices guide for AI agent memory usage: what to store, what not to store, when to update. No tools.",
     ["memory", "store", "update", "best practice", "should", "not"], False, 1),
    ("Create 3 examples of multi-step tasks where planning reduces total tool calls by 50%+. Show the planned vs unplanned approach. No tools.",
     ["plan", "tool", "call", "reduce", "fewer", "efficient"], False, 1),
]

for prompt, contains, requires, max_calls in si2:
    T("self_improvement", "Meta-reasoning and self-improvement", prompt, requires, max_calls,
      {"response_contains_any": contains, "tool_count_max": max_calls})

# ============================================================================
# Write output and merge with batch 1
# ============================================================================
from collections import Counter

print(f"Batch 2 tasks: {len(tasks)}")
cats = Counter(t["category"] for t in tasks)
print(f"\nBy category:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Load batch 1
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_tasks.json")) as f:
    batch1 = json.load(f)

all_tasks = batch1["tasks"] + tasks
print(f"\nBatch 1: {len(batch1['tasks'])}")
print(f"Batch 2: {len(tasks)}")
print(f"TOTAL: {len(all_tasks)}")

# Verify unique IDs
ids = [t["id"] for t in all_tasks]
assert len(ids) == len(set(ids)), f"Duplicate IDs found!"
print(f"All {len(all_tasks)} IDs unique ✓")

# Category totals
all_cats = Counter(t["category"] for t in all_tasks)
print(f"\nFinal category breakdown:")
for cat, count in sorted(all_cats.items()):
    print(f"  {cat}: {count}")

# Save merged file
output = {
    "meta": {
        "version": "2.1.0-synthetic",
        "description": "Synthetically generated eval tasks for Pi Agent training data collection",
        "base_version": "2.0.0",
        "generated_by": "claude-opus-4.6",
        "total_tasks": len(all_tasks),
    },
    "tasks": all_tasks,
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_tasks.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nWritten merged file to: {out_path}")
