#!/usr/bin/env python3
"""Generate batch 3 — final push to 1000+ total tasks."""
import json
import os
import random

random.seed(777)
tasks = []
tid = 564  # continue from batch 2

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
# ZERO_TOOL BATCH 3 — More diverse knowledge & reasoning
# ============================================================================

# --- Science, history, geography ---
factual3 = [
    ("What is Avogadro's number approximately? No tools.", ["6.022", "6.02", "10^23"]),
    ("What is the chemical formula for water? One word answer. No tools.", ["H2O"]),
    ("What year did World War II end? Just the year. No tools.", ["1945"]),
    ("What is the official language of Brazil? One word. No tools.", ["Portuguese"]),
    ("How many bits are in a byte? Just the number. No tools.", ["8"]),
    ("What does API stand for? One sentence. No tools.", ["Application Programming Interface"]),
    ("What is the Pythagorean theorem formula? No tools.", ["a^2", "a²", "c^2", "c²", "hypotenuse"]),
    ("What is the main gas that plants absorb from the atmosphere? No tools.", ["carbon dioxide", "CO2"]),
    ("What protocol is used for secure web browsing? No tools.", ["HTTPS", "TLS", "SSL"]),
    ("What is the command to change file permissions in Linux? No tools.", ["chmod"]),
    ("What is the difference between stack and heap memory? Brief answer. No tools.", ["stack", "heap", "local", "dynamic", "allocat"]),
    ("What is a mutex? One sentence. No tools.", ["mutex", "mutual exclusion", "lock", "thread", "synchron"]),
    ("What does the 'grep' command name stand for? No tools.", ["Global", "Regular Expression", "Print"]),
    ("What is the output of bool('') in Python? No tools.", ["False"]),
    ("What is the difference between a compiler and an interpreter? Brief. No tools.", ["compiler", "interpreter", "machine", "runtime", "translate"]),
    ("What does LIDAR stand for? No tools.", ["Light", "Detection", "Ranging"]),
    ("What is the standard indentation in Python? No tools.", ["4 spaces", "4", "four", "spaces"]),
    ("What is a singleton pattern? One sentence. No tools.", ["singleton", "one", "instance", "single", "class"]),
    ("What does the 'cd' command do in a terminal? No tools.", ["change", "directory"]),
    ("What is the IPv4 loopback address? No tools.", ["127.0.0.1"]),
]

for prompt, contains in factual3:
    T("zero_tool", "Factual knowledge without tools", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- More arithmetic with word problems ---
word_math = [
    ("A store has 24 apples and sells 7. How many remain? Just the number. No tools.", ["17"]),
    ("If a train travels at 60 mph for 2.5 hours, how far does it go? Just the number in miles. No tools.", ["150"]),
    ("What is 15% of 200? Just the number. No tools.", ["30"]),
    ("A rectangle is 8m by 5m. What is its area? Just the number with unit. No tools.", ["40"]),
    ("If you buy 3 items at $12.50 each, what's the total? No tools.", ["37.50", "37.5"]),
    ("What is the average of 10, 20, 30, 40, and 50? Just the number. No tools.", ["30"]),
    ("A circle has radius 5. What is its circumference? Round to 1 decimal. No tools.", ["31.4"]),
    ("Convert 72 Fahrenheit to Celsius. Round to nearest integer. No tools.", ["22"]),
    ("How many seconds in 3 hours? Just the number. No tools.", ["10800"]),
    ("What is 2^16? Just the number. No tools.", ["65536"]),
    ("If a pizza is cut into 8 slices and you eat 3, what fraction remains? No tools.", ["5/8", "five eighths"]),
    ("What is the perimeter of an equilateral triangle with side length 9? No tools.", ["27"]),
    ("A car uses 8 liters per 100km. How many liters for 350km? No tools.", ["28"]),
    ("What is 1000 in binary? No tools.", ["1111101000"]),
    ("How many permutations of 4 items? (4!) No tools.", ["24"]),
    ("What is the sum of integers from 1 to 20? No tools.", ["210"]),
    ("If a cube has side length 3, what is its volume? No tools.", ["27"]),
    ("What is 0.125 as a fraction? No tools.", ["1/8"]),
    ("A bag has 5 red and 3 blue marbles. What's the probability of picking red? No tools.", ["5/8", "0.625", "62.5"]),
    ("What is the LCM of 12 and 18? No tools.", ["36"]),
]

for prompt, contains in word_math:
    T("zero_tool", "Word problem without tools", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- More diverse reasoning ---
reasoning3 = [
    ("An agent was asked to find which process uses port 3000. It read /etc/services, searched memory, then ran netstat. What's the ideal approach? No tools.",
     ["lsof", "netstat", "ss", "one", "command", "overkill"]),
    ("Compare: Using execute_code to parse JSON vs using terminal with jq. When is each better? No tools.",
     ["jq", "execute_code", "simple", "complex", "terminal"]),
    ("An agent was asked to check if a directory is empty. It listed files, counted them, and checked if count is 0. Better approach? No tools.",
     ["test", "find", "ls", "one", "single", "empty", "rmdir"]),
    ("When should an agent save a skill vs just doing the task? Give criteria. No tools.",
     ["repeated", "reuse", "complex", "skill", "save", "future"]),
    ("Rate 1-10: An agent needs to append a line to a file. It reads the entire file, adds the line in memory, writes the whole file back. Better way? No tools.",
     [">>", "echo", "append", "overkill", "2", "3", "4"]),
    ("An agent needs to validate a JSON file. Compare: (a) read_file + execute_code, (b) terminal `python3 -m json.tool < file`, (c) terminal `jq . file`. Which is best? No tools.",
     ["json.tool", "jq", "terminal", "one", "command", "simplest"]),
    ("When should an agent use parallel tool calls vs sequential? Give examples. No tools.",
     ["parallel", "sequential", "independent", "depend", "order", "faster"]),
    ("An agent was asked to monitor a log file for errors. It used read_file every 5 seconds in a loop of execute_code calls. Better approach? No tools.",
     ["tail -f", "grep", "terminal", "watch", "one", "overkill"]),
    ("Design a mental checklist: Before making ANY tool call, what 3 questions should an agent ask itself? No tools.",
     ["necessary", "need", "tool", "simpler", "right", "minimal", "question"]),
    ("Rate 1-10: An agent was asked to set an environment variable. It created a Python script that uses os.environ, ran it, then verified with another Python script. Better approach? No tools.",
     ["export", "terminal", "one", "overkill", "1", "2", "3", "4"]),
]

for prompt, contains in reasoning3:
    T("zero_tool", "Reasoning about tool usage", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- Programming concept explanations ---
concepts = [
    ("Explain what a closure is in programming. 2-3 sentences. No tools.", ["closure", "function", "variable", "scope", "enclos"], 25),
    ("Explain the Observer pattern. 2-3 sentences. No tools.", ["observer", "pattern", "event", "notify", "subscribe", "listen"], 25),
    ("Explain what memoization is. 2-3 sentences. No tools.", ["memoization", "cache", "result", "computed", "store", "previous"], 25),
    ("Explain what a microservice architecture is. 2-3 sentences. No tools.", ["microservice", "service", "independent", "API", "deploy", "small"], 25),
    ("Explain what a garbage collector does. 2-3 sentences. No tools.", ["garbage", "collect", "memory", "free", "allocat", "automat"], 25),
    ("Explain what event-driven programming is. 2-3 sentences. No tools.", ["event", "driven", "callback", "handler", "trigger", "asynchron"], 25),
    ("Explain what polymorphism is in OOP. 2-3 sentences. No tools.", ["polymorphism", "interface", "method", "override", "form", "inherit"], 25),
    ("Explain what a graph database is (like Neo4j). 2-3 sentences. No tools.", ["graph", "node", "edge", "relationship", "Neo4j", "query"], 25),
    ("Explain what continuous integration (CI) is. 2-3 sentences. No tools.", ["continuous", "integration", "build", "test", "automat", "merge"], 25),
    ("Explain what a bloom filter is. 2-3 sentences. No tools.", ["bloom", "filter", "probabilistic", "false positive", "member", "set"], 25),
]

for prompt, contains, min_len in concepts:
    T("zero_tool", "Technical explanation without tools", prompt, False, 0,
      {"response_contains_any": contains, "response_min_length": min_len, "tool_count_exact": 0})

# ============================================================================
# TERMINAL BATCH 3
# ============================================================================

terminal3 = [
    ("Use terminal to run: printf 'Hello\\tWorld\\n' | expand. Report the output.", ["Hello", "World"], 2),
    ("Use terminal to generate numbers 1-20 and filter for those divisible by 3: seq 1 20 | awk '$1%3==0'. Report.", ["3", "6", "9", "12", "15", "18"], 2),
    ("Use terminal to find how many groups exist: cat /etc/group | wc -l. Report the count.", [], 2),
    ("Use terminal to check what version of bash is running: bash --version | head -1. Report.", ["bash", "version", "GNU"], 2),
    ("Use terminal to replace spaces with underscores in a string: echo 'hello world test' | tr ' ' '_'. Report.", ["hello_world_test"], 2),
    ("Use terminal to show only unique lines from: printf 'apple\\nbanana\\napple\\ncherry\\nbanana\\n' | sort -u. Report.", ["apple", "banana", "cherry"], 2),
    ("Use terminal to run: echo '3.14 * 2' | bc -l. Report the result.", ["6.28"], 2),
    ("Use terminal to list all running processes with their PIDs: ps -eo pid,comm | head -10. Report.", ["PID", "COMMAND"], 2),
    ("Use terminal to extract just the usernames from /etc/passwd: cut -d: -f1 /etc/passwd | head -5. Report.", ["root"], 2),
    ("Use terminal to check how long the system has been up: cat /proc/uptime | awk '{print $1}'. Report in seconds.", [], 2),
    ("Use terminal to generate a random number between 1 and 100: echo $((RANDOM % 100 + 1)). Report.", [], 2),
    ("Use terminal to show the inode number of /etc/passwd: ls -i /etc/passwd. Report.", [], 2),
    ("Use terminal to test if /tmp is writable: test -w /tmp && echo 'writable' || echo 'not writable'. Report.", ["writable"], 2),
    ("Use terminal to count running processes by name: ps aux | awk '{print $11}' | sort | uniq -c | sort -rn | head -5. Report top 5.", [], 2),
    ("Use terminal to show disk usage in percentage: df / | tail -1 | awk '{print $5}'. Report.", ["%"], 2),
    ("Use terminal to double each line: echo -e 'a\\nb\\nc' | sed 'p'. Report the output.", ["a", "b", "c"], 2),
    ("Use terminal to calculate: echo '2^32' | bc. Report the result.", ["4294967296"], 2),
    ("Use terminal to find which shell /etc/passwd uses most: cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn | head -3. Report.", ["/bin", "sh", "bash", "nologin"], 2),
    ("Use terminal to check total number of files in /etc: find /etc -maxdepth 1 -type f 2>/dev/null | wc -l. Report.", [], 2),
    ("Use terminal to show the size of /etc/ directory: du -sh /etc 2>/dev/null. Report.", ["/etc"], 2),
    ("Use terminal to run: yes 'test' | head -3. Report the output.", ["test"], 2),
    ("Use terminal to get the parent directory of /usr/local/bin: dirname /usr/local/bin. Report.", ["/usr/local"], 2),
    ("Use terminal to check if Python has ssl module: python3 -c 'import ssl; print(ssl.OPENSSL_VERSION)'. Report.", ["OpenSSL", "SSL"], 2),
    ("Use terminal to show line numbers for /etc/hostname: nl /etc/hostname || cat -n /etc/hostname. Report.", ["1"], 2),
    ("Use terminal to run: echo 'Hello World' | fold -w 5. Report the output.", ["Hello", "World"], 2),
]

for prompt, contains, max_calls in terminal3:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("terminal", "Terminal command execution", prompt, True, max_calls, verify, "terminal")

# ============================================================================
# CODE_EXECUTION BATCH 3
# ============================================================================

code3 = [
    ("Use execute_code to implement a function that checks if a string is a valid IPv4 address. Test with '192.168.1.1' and '999.1.1.1'. Print results.", ["True", "False", "valid", "invalid"], 2),
    ("Use execute_code to find the longest increasing subsequence in [10, 22, 9, 33, 21, 50, 41, 60]. Print it.", ["10", "22", "33", "50", "60"], 2),
    ("Use execute_code to implement a simple LRU cache with max size 3. Insert keys a,b,c,d and show eviction. Print state.", ["evict", "a", "d"], 2),
    ("Use execute_code to generate all subsets of {1, 2, 3}. Print them.", ["[]", "[1]", "[2]", "[3]", "[1, 2]", "[1, 3]", "[2, 3]", "[1, 2, 3]"], 2),
    ("Use execute_code to implement Tower of Hanoi for 3 disks. Print each move.", ["Move", "disk", "1", "2", "3"], 2),
    ("Use execute_code to find the kth smallest element (k=3) in [7, 10, 4, 3, 20, 15]. Print it.", ["7"], 2),
    ("Use execute_code to implement a simple trie insert and search for words 'apple', 'app', 'apt'. Print search results.", ["True", "False", "apple", "app"], 2),
    ("Use execute_code to calculate the edit distance (Levenshtein) between 'kitten' and 'sitting'. Print it.", ["3"], 2),
    ("Use execute_code to implement depth-first search on a graph {A:[B,C], B:[D], C:[D,E], D:[], E:[]}. Print traversal order.", ["A", "B", "C", "D", "E"], 2),
    ("Use execute_code to find all pairs in [1,5,7,3,4,2] that sum to 7. Print the pairs.", ["5, 2", "3, 4", "7, 0", "(5", "(3"], 2),
    ("Use execute_code to implement a basic calculator that evaluates '3 + 4 * 2 - 1'. Print result (respecting operator precedence).", ["10"], 2),
    ("Use execute_code to convert a Roman numeral function: test with 'XIV', 'XLII', 'MMXXVI'. Print decimal values.", ["14", "42", "2026"], 2),
    ("Use execute_code to implement breadth-first search on a graph {1:[2,3], 2:[4], 3:[4,5], 4:[], 5:[]}. Print traversal.", ["1", "2", "3", "4", "5"], 2),
    ("Use execute_code to find the median of [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]. Print it.", ["4"], 2),
    ("Use execute_code to implement a simple hash function for strings and test on 'hello', 'world', 'test'. Print the hashes.", ["hello", "world", "test"], 2),
    ("Use execute_code to check if a binary tree represented as [1,2,3,4,5,None,6] is balanced. Print True or False.", ["True", "False", "balanced"], 2),
    ("Use execute_code to implement merge sort on [38, 27, 43, 3, 9, 82, 10]. Print the sorted result.", ["3", "9", "10", "27", "38", "43", "82"], 2),
    ("Use execute_code to find the longest palindromic substring in 'babad'. Print it.", ["bab", "aba"], 2),
    ("Use execute_code to implement a simple state machine that processes 'aabbc' with states: start->a->b->c->end. Print transitions.", ["start", "a", "b", "c", "end"], 2),
    ("Use execute_code to calculate the determinant of matrix [[1,2],[3,4]]. Print the result.", ["-2"], 2),
    ("Use execute_code to find all prime factors of 84. Print them.", ["2", "3", "7"], 2),
    ("Use execute_code to implement a simple bloom filter with 3 hash functions. Insert 'cat','dog' and check 'cat','bird'. Print results.", ["cat", "dog", "True", "False"], 2),
    ("Use execute_code to rotate a list [1,2,3,4,5] by 2 positions to the right. Print the result.", ["4", "5", "1", "2", "3"], 2),
    ("Use execute_code to find the maximum subarray sum in [-2, 1, -3, 4, -1, 2, 1, -5, 4] using Kadane's algorithm. Print it.", ["6"], 2),
    ("Use execute_code to implement a simple JSON parser that extracts all keys from '{\"name\":\"Alice\",\"age\":30,\"city\":\"NYC\"}'. Print the keys.", ["name", "age", "city"], 2),
    ("Use execute_code to generate the first 10 happy numbers. Print them.", ["1", "7", "10", "13", "19", "23", "28", "31", "44", "49"], 2),
    ("Use execute_code to implement a function that groups anagrams from ['eat','tea','tan','ate','nat','bat']. Print the groups.", ["eat", "tea", "ate", "tan", "nat", "bat"], 2),
    ("Use execute_code to calculate the nth Catalan number for n=5. Print it.", ["42"], 2),
    ("Use execute_code to implement a simple regex matcher that checks if 'aab' matches pattern 'a*b'. Print True or False.", ["True"], 2),
    ("Use execute_code to find the number of islands in a grid [[1,1,0],[0,1,0],[0,0,1]]. Print the count.", ["2"], 2),
]

for prompt, contains, max_calls in code3:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("code_execution", "Python code execution", prompt, True, max_calls, verify, "execute_code")

# ============================================================================
# FILE_OPS BATCH 3
# ============================================================================

file3 = [
    ("Use write_file to create /tmp/changelog.md with '# Changelog\\n## v1.0\\n- Initial release\\n## v1.1\\n- Bug fixes'. Read it back.", ["Changelog", "v1.0", "v1.1"], 3, "write_file AND read_file"),
    ("Use terminal to find duplicate files by size in /tmp: find /tmp -maxdepth 1 -type f -printf '%s %p\\n' 2>/dev/null | sort -n | head -10. Report.", ["/tmp"], 2, "terminal"),
    ("Create /tmp/api_config.yaml with 'endpoint: /api/v1\\ntimeout: 30\\nretries: 3' using write_file. Verify with read_file.", ["endpoint", "timeout", "retries"], 3, "write_file AND read_file"),
    ("Use terminal to check file types in /etc: file /etc/passwd /etc/hostname /etc/group 2>/dev/null. Report.", ["ASCII", "text"], 2, "terminal"),
    ("Write /tmp/gitignore_sample with '*.pyc\\n__pycache__/\\n.env\\nnode_modules/' using write_file. Read back.", ["pyc", "pycache", "env", "node_modules"], 3, "write_file AND read_file"),
    ("Use terminal to find all files owned by root in /tmp: find /tmp -maxdepth 1 -user root 2>/dev/null | head -5. Report.", ["/tmp", "root"], 2, "terminal"),
    ("Create /tmp/haiku.txt with a haiku about coding (3 lines: 5-7-5 syllables). Read it back.", [], 3, "write_file AND read_file"),
    ("Use terminal to check the file system type: df -T / | tail -1. Report the filesystem type.", ["ext", "overlay", "xfs", "btrfs", "tmpfs"], 2, "terminal"),
    ("Write /tmp/nginx_snippet.conf with 'server {\\n  listen 80;\\n  server_name localhost;\\n}' using write_file. Read back.", ["server", "listen", "80", "localhost"], 3, "write_file AND read_file"),
    ("Use terminal to find all hard links to a file: find / -maxdepth 2 -samefile /etc/passwd 2>/dev/null || echo 'search done'. Report.", ["passwd", "done"], 2, "terminal"),
    ("Write /tmp/docker-compose.yml with 'version: \"3\"\\nservices:\\n  web:\\n    image: nginx' using write_file. Read back.", ["version", "services", "web", "nginx"], 3, "write_file AND read_file"),
    ("Use terminal to get file creation time: stat /etc/passwd 2>/dev/null | grep -i 'birth\\|change\\|modify'. Report.", ["Modify", "Change", "Birth", "Access"], 2, "terminal"),
    ("Write /tmp/sql_sample.sql with 'CREATE TABLE users (id INT, name TEXT);\\nINSERT INTO users VALUES (1, \"Alice\");'. Read back.", ["CREATE", "TABLE", "users", "Alice"], 3, "write_file AND read_file"),
    ("Use terminal to show the 5 oldest files in /etc: ls -ltr /etc | head -6. Report.", ["/etc"], 2, "terminal"),
    ("Create /tmp/test_data.xml with '<root><item id=\"1\">First</item><item id=\"2\">Second</item></root>' using write_file. Read back.", ["root", "item", "First", "Second"], 3, "write_file AND read_file"),
]

for prompt, contains, max_calls, expected in file3:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("file_ops", "File operations", prompt, True, max_calls, verify, expected)

# ============================================================================
# MORE PLANNING, MULTI_STEP, TOOL-SPECIFIC TASKS
# ============================================================================

# Planning batch 3
planning3 = [
    ("Task: Create a log rotation system — (1) create /tmp/app.log with 20 lines, (2) move it to /tmp/app.log.1, (3) create a new empty /tmp/app.log, (4) verify both exist. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "log"], 6, "terminal"),
    ("Task: (1) Write a bash script that generates system stats, (2) make it executable, (3) run it, (4) save output to a report. Plan your numbered steps first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "script"], 6, "write_file AND terminal"),
    ("Task: Create a simple build pipeline — (1) create src/main.py, (2) create tests/test_main.py, (3) run the test, (4) report results. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "test", "main"], 6, "write_file AND terminal"),
    ("Task: (1) Download environment info, (2) create a diagnostic report with CPU, memory, disk, (3) save to /tmp/diagnostic.txt, (4) verify completeness. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "diagnostic"], 5, "terminal"),
    ("Task: File deduplication — (1) create 5 files in /tmp/dedup/, some with identical content, (2) find duplicates by checksum, (3) report which are duplicates. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "duplicate", "checksum"], 6, "terminal"),
    ("Task: (1) Count all Python files in the system, (2) find the largest one, (3) count its lines, (4) create a summary report. Plan before executing.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "python", ".py"], 5, "terminal"),
    ("Task: (1) Create a simple key-value store as a bash script, (2) use it to set 3 keys, (3) retrieve and verify them. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "key", "value"], 6, "write_file AND terminal"),
    ("Task: (1) Write a Python script that reads /etc/passwd and prints user stats, (2) run it, (3) save output. Plan your approach.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "passwd", "user"], 5, "write_file AND terminal"),
]

for prompt, contains, max_calls, expected in planning3:
    T("planning", "Plan before executing", prompt, True, max_calls,
      {"response_contains_any": contains, "plan_before_first_tool": True, "tool_count_min": 2, "tool_count_max": max_calls}, expected)

# Multi-step batch 3
multi3 = [
    ("Efficiently: (1) create a temp dir, (2) populate it with 3 numbered files, (3) tar them all, (4) verify the archive. Max 3 calls.",
     ["tar", ".txt"], 3, "terminal"),
    ("In minimal calls: (1) get system load average, (2) get memory usage percent, (3) get disk usage percent. Combine all in 1 command. Max 1.",
     ["load", "Mem", "Use%"], 1, "terminal"),
    ("Efficiently: (1) create /tmp/before.txt listing /etc contents, (2) add a temp file to /etc, (3) create /tmp/after.txt, (4) diff them. Max 3 calls.",
     ["diff", "/etc"], 3, "terminal"),
    ("Do in 1-2 calls: Check Python version, pip version, and list the first 5 installed packages. Max 2.",
     ["Python", "pip", "3."], 2, "terminal"),
    ("Minimal calls: create /tmp/stats.txt containing date, uptime, and free memory — all in one terminal call. Max 1.",
     ["date", "uptime", "free", "Mem"], 1, "terminal"),
    ("Efficiently: (1) find all users with /bin/bash shell, (2) count them, (3) list their home dirs. Max 2 calls.",
     ["bash", "/home", "root"], 2, "terminal"),
    ("Do in fewest calls: create files /tmp/x1 through /tmp/x10, write sequence number in each, and count total lines across all. Max 2.",
     ["10"], 2, "terminal"),
    ("Efficiently: (1) compress a string with gzip, (2) show compressed size, (3) decompress and verify. Max 2 calls.",
     ["gzip", "byte"], 2, "terminal"),
]

for prompt, contains, max_calls, expected in multi3:
    T("multi_step", "Efficient multi-step operation", prompt, True, max_calls,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": max_calls}, expected)

# More memory tasks
memory3 = [
    ("Use memory to store: 'Agent should combine related terminal commands with &&'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Zero-tool tasks should never trigger tool calls'. Confirm saved.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'Planning before execution reduces total tool calls'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Code execution tasks prefer execute_code over terminal python3 -c'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'File verification after write is a best practice'. Confirm saved.", ["stored", "added", "saved", "memory"]),
]

for prompt, contains in memory3:
    T("memory", "Memory storage", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "memory")

# More session search
session3 = [
    ("Use session_search to find conversations about 'backup' or 'restore'. Report.", ["session", "conversation", "found", "result", "backup", "restore"]),
    ("Use session_search for past mentions of 'network' or 'connection'. Report.", ["session", "conversation", "found", "result", "network", "connection"]),
    ("Use session_search to find discussions about 'security' or 'permission'. Report.", ["session", "conversation", "found", "result", "security", "permission"]),
    ("Use session_search for 'optimize' or 'performance' in past sessions. Report.", ["session", "conversation", "found", "result", "optim", "perform"]),
    ("Use session_search to look for conversations about 'automation' or 'script'. Report.", ["session", "conversation", "found", "result", "automat", "script"]),
]

for prompt, contains in session3:
    T("session_search", "Past session search", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "session_search")

# More skills
skills3 = [
    ("Use skills_list to find skills related to 'arxiv' or 'research papers'. Report.", ["skill", "arxiv", "research", "paper"]),
    ("Use skill_view to examine the 'google-workspace' skill. What Google services does it support?", ["skill", "google", "workspace", "gmail", "docs", "drive"]),
    ("Use skills_list to count total skills and list the categories. Report all.", ["skill", "categor"]),
    ("Use skill_view to look at the 'youtube-content' skill. What can it do?", ["skill", "youtube", "video", "transcript"]),
    ("Use skills_list to check for any 'smart-home' or 'IoT' related skills. Report.", ["skill", "smart", "home", "openhue"]),
]

for prompt, contains in skills3:
    T("skills", "Skills management", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "skills_list OR skill_view")

# More cron
cron3 = [
    ("Use list_cronjobs to verify the cron system is working. Report the status and any configured jobs.", ["cron", "job", "status", "no ", "none", "scheduled", "working"]),
    ("Use list_cronjobs to check for any monitoring or health-check cron jobs. Report findings.", ["cron", "job", "monitor", "health", "no ", "none"]),
    ("Use list_cronjobs to review scheduled tasks. If none, suggest 3 useful cron jobs for a development environment.", ["cron", "job", "suggest", "no ", "none", "useful"]),
]

for prompt, contains in cron3:
    T("cron", "Cron job inspection", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "list_cronjobs")

# More todo
todo3 = [
    ("Use todo to add: 'Validate synthetic training data quality'. List tasks.", ["valid", "synthetic", "quality", "task", "todo"]),
    ("Use todo to add 3 items: 'Run A/B test', 'Analyze results', 'Write report'. List all.", ["A/B", "analyze", "report", "task", "todo"]),
    ("Use todo to create: 'Implement early stopping for training'. Confirm added.", ["early", "stopping", "training", "task", "todo", "added"]),
    ("Use todo to add: 'Profile GPU memory usage during inference'. List tasks.", ["GPU", "memory", "profile", "task", "todo"]),
    ("Use todo to create: 'Set up automated eval pipeline'. Confirm added.", ["automated", "eval", "pipeline", "task", "todo", "added"]),
]

for prompt, contains in todo3:
    T("todo", "Task management", prompt, True, 3,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 3}, "todo")

# More self-improvement
si3 = [
    ("Create a comprehensive evaluation rubric for measuring AI agent tool selection accuracy. Include 5 dimensions with examples. No tools.",
     ["tool", "selection", "accuracy", "dimension", "criteri", "example"], False, 1),
    ("Design a data augmentation strategy specifically for tool-use training data. How can you create more diverse examples from existing ones? No tools.",
     ["augment", "diverse", "tool", "training", "example", "data"], False, 1),
    ("Write a post-mortem analysis template for failed AI agent tasks. What should be captured and how? No tools.",
     ["post-mortem", "fail", "analysis", "root cause", "capture", "template"], False, 1),
    ("Create guidelines for when an AI agent should ask for clarification vs making assumptions. Include decision criteria. No tools.",
     ["clarif", "assum", "ask", "criteria", "decision", "ambiguous"], False, 1),
    ("Design a testing strategy for verifying that a fine-tuned model improves on specific weaknesses. Include pre/post metrics. No tools.",
     ["test", "fine-tun", "improve", "metric", "pre", "post", "weakness"], False, 1),
]

for prompt, contains, requires, max_calls in si3:
    T("self_improvement", "Meta-reasoning and self-improvement", prompt, requires, max_calls,
      {"response_contains_any": contains, "tool_count_max": max_calls})

# ============================================================================
# Merge with existing and write output
# ============================================================================
from collections import Counter

print(f"Batch 3 tasks: {len(tasks)}")
cats = Counter(t["category"] for t in tasks)
print(f"\nBy category:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Load existing merged file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_tasks.json")) as f:
    existing = json.load(f)

all_tasks = existing["tasks"] + tasks
print(f"\nExisting: {len(existing['tasks'])}")
print(f"Batch 3: {len(tasks)}")
print(f"TOTAL: {len(all_tasks)}")

# Verify unique IDs
ids = [t["id"] for t in all_tasks]
dupes = [x for x in ids if ids.count(x) > 1]
if dupes:
    print(f"WARNING: Duplicate IDs: {set(dupes)}")
else:
    print(f"All {len(all_tasks)} IDs unique ✓")

# Category totals
all_cats = Counter(t["category"] for t in all_tasks)
print(f"\nFinal category breakdown:")
for cat, count in sorted(all_cats.items()):
    print(f"  {cat}: {count}")

# Count tool vs no-tool
tool_tasks = sum(1 for t in all_tasks if t.get("requires_tool", False))
no_tool = len(all_tasks) - tool_tasks
print(f"\nRequires tool: {tool_tasks}")
print(f"No tool: {no_tool}")

# Save
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
print(f"\nWritten to: {out_path}")
