#!/usr/bin/env python3
"""Generate synthetic eval tasks for Pi Agent training data collection."""
import json
import os
import random

tasks = []
tid = 0

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
# ZERO_TOOL — Factual, math, reasoning, critique (no tools needed)
# ============================================================================

# --- Factual questions ---
factual = [
    ("What is the largest planet in our solar system? Answer in one sentence. Do NOT use any tools.", ["Jupiter"]),
    ("What programming language was created by Guido van Rossum? Answer in one sentence. No tools.", ["Python"]),
    ("What is the chemical symbol for gold? Reply with just the symbol. No tools.", ["Au"]),
    ("What year did the Berlin Wall fall? Reply with just the year. No tools.", ["1989"]),
    ("What is the speed of light in meters per second, approximately? No tools needed.", ["300000000", "3e8", "299792458", "300,000,000"]),
    ("Name the four fundamental forces of nature. No tools needed.", ["gravity", "electromagnetic", "strong", "weak"]),
    ("What data structure uses LIFO (Last In, First Out)? Answer briefly. No tools.", ["stack"]),
    ("What does HTTP stand for? Answer in one sentence. No tools.", ["Hypertext Transfer Protocol", "HyperText"]),
    ("What is the smallest prime number? Reply with just the number. No tools.", ["2"]),
    ("What continent is Brazil in? Answer in one sentence. No tools.", ["South America"]),
    ("Who wrote the theory of general relativity? One sentence. No tools.", ["Einstein"]),
    ("What does CPU stand for? Answer briefly. No tools.", ["Central Processing Unit"]),
    ("What is the boiling point of water in Celsius? Just the number. No tools.", ["100"]),
    ("What sorting algorithm has average O(n log n) complexity and is commonly used in practice? No tools.", ["quicksort", "merge sort", "mergesort", "timsort"]),
    ("What is the binary representation of the decimal number 10? No tools.", ["1010"]),
    ("What is the standard port number for HTTPS? Just the number. No tools.", ["443"]),
    ("What Linux command lists files in a directory? Just name the command. No tools.", ["ls"]),
    ("What does JSON stand for? One sentence. No tools.", ["JavaScript Object Notation"]),
    ("What is the time complexity of binary search? Answer briefly. No tools.", ["O(log n)", "log n", "logarithmic"]),
    ("In networking, what does DNS stand for? One sentence. No tools.", ["Domain Name System", "Domain Name Service"]),
    ("What is the derivative of x squared? Answer briefly. No tools.", ["2x", "2*x"]),
    ("What is the most abundant gas in Earth's atmosphere? One word answer. No tools.", ["nitrogen"]),
    ("What command is used to install packages in Python? Just the command name. No tools.", ["pip"]),
    ("What does CRUD stand for in database operations? No tools.", ["Create", "Read", "Update", "Delete"]),
    ("What is 0 in binary? Just answer. No tools.", ["0"]),
]

for prompt, contains in factual:
    T("zero_tool", "Factual knowledge without tools", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# --- Arithmetic ---
import random
random.seed(42)
arith_ops = [
    (lambda a,b: a+b, "+", "sum"),
    (lambda a,b: a*b, "*", "product"),
    (lambda a,b: a-b, "-", "difference"),
]
for i in range(25):
    a = random.randint(3, 99)
    b = random.randint(3, 99)
    op_fn, op_sym, op_name = arith_ops[i % 3]
    result = op_fn(a, b)
    T("zero_tool", f"Arithmetic: {a} {op_sym} {b}",
      f"What is {a} {op_sym} {b}? Reply with just the number. No tools.",
      False, 0, {"response_contains": [str(result)], "tool_count_exact": 0})

# --- Technical explanations ---
tech_explanations = [
    ("Explain what a Python decorator is in 2-3 sentences. No tools.", ["decorator", "@", "function", "wrap"], 40),
    ("Explain what a REST API is in 2-3 sentences. No tools.", ["REST", "HTTP", "API", "endpoint", "resource"], 40),
    ("Explain what recursion is in programming in 2-3 sentences. No tools.", ["recursion", "recursive", "itself", "base case", "call"], 40),
    ("Explain what a Docker container is in 2-3 sentences. No tools.", ["container", "Docker", "image", "isolat", "virtuali"], 40),
    ("Explain the difference between a list and a tuple in Python. 2-3 sentences. No tools.", ["list", "tuple", "mutable", "immutable"], 30),
    ("Explain what Git branching is in 2-3 sentences. No tools.", ["branch", "git", "merge", "commit"], 30),
    ("Explain what a hash table is in 2-3 sentences. No tools.", ["hash", "key", "value", "O(1)", "collision"], 30),
    ("Explain what async/await does in Python in 2-3 sentences. No tools.", ["async", "await", "asynchronous", "coroutine", "concurrent"], 30),
    ("Explain what a virtual environment is in Python in 2-3 sentences. No tools.", ["virtual", "environment", "venv", "packages", "isolat"], 30),
    ("Explain what SQL injection is in 2-3 sentences. No tools.", ["SQL", "injection", "query", "input", "sanitiz"], 30),
    ("Explain what TCP and UDP are and their key difference. 2-3 sentences. No tools.", ["TCP", "UDP", "reliable", "connection", "packet"], 30),
    ("Explain what a linked list is and when you'd use one. 2-3 sentences. No tools.", ["linked", "list", "node", "pointer", "next"], 30),
    ("Explain what environment variables are in Linux. 2-3 sentences. No tools.", ["environment", "variable", "PATH", "export", "shell"], 30),
    ("Explain the CAP theorem in distributed systems. 2-3 sentences. No tools.", ["consistency", "availability", "partition", "CAP"], 30),
    ("Explain what a lambda function is in Python. 2-3 sentences. No tools.", ["lambda", "anonymous", "function", "inline"], 25),
    ("Explain what middleware is in web frameworks. 2-3 sentences. No tools.", ["middleware", "request", "response", "process"], 25),
    ("Explain what a race condition is. 2-3 sentences. No tools.", ["race", "condition", "thread", "concurrent", "simultaneous"], 25),
    ("Explain what containerization is and why it's useful. 2-3 sentences. No tools.", ["container", "deploy", "isolat", "environment", "consistent"], 30),
    ("Explain the difference between compiled and interpreted languages. 2-3 sentences. No tools.", ["compiled", "interpreted", "machine code", "runtime"], 30),
    ("Explain what a webhook is. 2-3 sentences. No tools.", ["webhook", "callback", "HTTP", "event", "URL"], 25),
]

for prompt, contains, min_len in tech_explanations:
    T("zero_tool", "Technical explanation without tools", prompt, False, 0,
      {"response_contains_any": contains, "response_min_length": min_len, "tool_count_exact": 0})

# --- Reasoning / Critique ---
reasoning = [
    ("Rate 1-10: An agent was asked to list files in /tmp. It used execute_code to run os.listdir('/tmp') instead of using the terminal tool. How efficient is this? Explain. No tools.",
     ["unnecessary", "terminal", "simpler", "overkill", "could have", "should have", "inefficient"]),
    ("Rate 1-10: An agent was asked 'What is the capital of Japan?' It searched 3 past sessions, ran a terminal command, then answered 'Tokyo'. Rate the tool usage. No tools.",
     ["waste", "unnecessary", "overkill", "didn't need", "no tools", "inefficient", "1", "2", "3"]),
    ("You have these tasks: (a) check disk space, (b) write a 3-line config file, (c) analyze a 50MB log file for anomalies. Which needs the most tool calls and why? No tools.",
     ["c", "log", "analyze", "complex", "large"]),
    ("An agent used 5 separate terminal calls to: mkdir /tmp/a, mkdir /tmp/a/b, mkdir /tmp/a/b/c, touch /tmp/a/b/c/file.txt, cat /tmp/a/b/c/file.txt. How could this be more efficient? No tools.",
     ["mkdir -p", "one", "single", "combine", "fewer", "&&"]),
    ("When should an AI agent use the memory tool vs just answering from context? Give 2 examples of each. No tools.",
     ["memory", "persist", "remember", "future", "session", "context"]),
    ("Rate 1-10: An agent was asked to calculate 15% tip on $45. It wrote a Python script, executed it, then read the output. How good is this approach? No tools.",
     ["overkill", "unnecessary", "simple", "mental", "head", "inefficient", "1", "2", "3", "4"]),
    ("What's the difference between using terminal to run 'python3 -c \"print(42)\"' vs using execute_code? When would you prefer each? No tools.",
     ["terminal", "execute_code", "simple", "complex", "output", "environment"]),
    ("You need to: rename a file, check its new contents, and verify permissions. What's the minimum number of terminal calls needed? Explain. No tools.",
     ["1", "2", "one", "two", "&&", "chain", "combine"]),
    ("An agent was asked to find all .py files larger than 1MB. It used search_files 10 times in different directories. What's a better approach? No tools.",
     ["find", "terminal", "one", "single", "command", "-size"]),
    ("When is it appropriate for an AI agent to use the clarify tool to ask the user a question instead of guessing? Give examples. No tools.",
     ["ambiguous", "unclear", "clarif", "multiple", "interpret", "ask"]),
    ("Rate 1-10: An agent was asked to sort a list of 5 names alphabetically. It wrote a Python script with a bubble sort implementation. How efficient is this? No tools.",
     ["overkill", "unnecessary", "sorted", "simple", "built-in", "1", "2", "3", "4", "inefficient"]),
    ("You need to check if a process is running, kill it if yes, and start a new one. How many terminal calls minimum? No tools.",
     ["1", "2", "one", "two", "&&", "chain", "pipe"]),
    ("Explain when an agent should use write_file vs terminal echo/cat for creating files. Give pros and cons. No tools.",
     ["write_file", "terminal", "echo", "binary", "simple", "complex"]),
    ("Rate 1-10: An agent was asked to count lines in a file. It read the entire file with read_file, then used execute_code to count newlines. Better approach? No tools.",
     ["wc", "terminal", "wc -l", "overkill", "unnecessary", "simpler", "one", "1", "2", "3"]),
    ("Should an agent store API keys in memory? Why or why not? No tools.",
     ["no", "security", "sensitive", "secret", "never", "risk", "dangerous"]),
]

for prompt, contains in reasoning:
    T("zero_tool", "Reasoning about tool usage", prompt, False, 0,
      {"response_contains_any": contains, "tool_count_exact": 0})

# ============================================================================
# TERMINAL — Shell command tasks
# ============================================================================

terminal_tasks = [
    ("Use terminal to run: whoami. Report the output.", ["root"], 2),
    ("Use terminal to run: pwd. Report the current directory.", ["/"], 2),
    ("Use terminal to run: date '+%Y'. Report just the year.", ["2026", "202"], 2),
    ("Use terminal to check how much disk space is available using df -h /. Report the result.", ["Filesystem", "/dev", "Use%", "Available", "Size", "G", "M"], 2),
    ("Use terminal to run: uname -s. What operating system is this?", ["Linux"], 2),
    ("Use terminal to check the Python version with: python3 --version. Report it.", ["Python", "3."], 2),
    ("Use terminal to count the number of environment variables: env | wc -l. Report the number.", [], 2),
    ("Use terminal to create a directory /tmp/eval_dir_test and verify it exists with ls -d /tmp/eval_dir_test. Do this efficiently.", ["/tmp/eval_dir_test"], 3),
    ("Use terminal to run: echo $HOME. What is the home directory?", ["/root", "/home"], 2),
    ("Use terminal to check how many processes are running: ps aux | wc -l. Report the count.", [], 2),
    ("Use terminal to run: cat /etc/hostname. Report the hostname.", [], 2),
    ("Use terminal to list all files in /tmp sorted by modification time: ls -lt /tmp. Report what you see.", ["/tmp"], 3),
    ("Use terminal to check available memory with: free -h. Report the total memory.", ["Mem", "total", "free", "available", "G", "M"], 2),
    ("Use terminal to run: echo 'test_123' | wc -c. Report the character count.", ["9", "10"], 2),
    ("Use terminal to find all directories in /etc with: find /etc -maxdepth 1 -type d 2>/dev/null | head -10. Report some.", ["/etc"], 2),
    ("Use terminal to check the current shell: echo $SHELL. Report it.", ["sh", "bash", "zsh", "/bin"], 2),
    ("Use terminal to run: seq 1 5 | paste -sd+ | bc. What is the sum of 1 through 5?", ["15"], 2),
    ("Use terminal to check if curl is installed: which curl. Report the path.", ["curl", "/usr"], 2),
    ("Use terminal to create a file with: echo 'eval_marker_42' > /tmp/marker.txt && cat /tmp/marker.txt. Report the content.", ["eval_marker_42"], 2),
    ("Use terminal to count .txt files in /tmp: find /tmp -name '*.txt' 2>/dev/null | wc -l. Report the count.", [], 2),
    ("Use terminal to show the first 3 lines of /etc/passwd. Use head -3 /etc/passwd.", ["root"], 2),
    ("Use terminal to calculate disk usage of /tmp: du -sh /tmp 2>/dev/null. Report the size.", ["/tmp"], 2),
    ("Use terminal to run: printf '%s\\n' banana apple cherry | sort. Report the sorted output.", ["apple", "banana", "cherry"], 2),
    ("Use terminal to check if git is installed: git --version 2>/dev/null || echo 'not installed'. Report the result.", ["git", "not installed"], 2),
    ("Use terminal to run: expr 17 + 28. Report the result.", ["45"], 2),
    ("Use terminal to create a 3-line file using: printf 'line1\\nline2\\nline3\\n' > /tmp/three_lines.txt && wc -l /tmp/three_lines.txt. Report the count.", ["3"], 2),
    ("Use terminal to list environment variables starting with P: env | grep ^P. Report what you find.", ["P", "PATH"], 3),
    ("Use terminal to check uptime: uptime or cat /proc/uptime. Report the result.", ["up", "load", "day", "min", "hour"], 2),
    ("Use terminal to run: tr '[:lower:]' '[:upper:]' <<< 'hello world'. Report the output.", ["HELLO WORLD", "HELLO"], 2),
    ("Use terminal to run: wc -w <<< 'the quick brown fox jumps'. How many words?", ["5"], 2),
    ("Use terminal to check CPU info: cat /proc/cpuinfo 2>/dev/null | head -5 || echo 'not available'. Report key details.", ["cpu", "model", "processor", "not available"], 2),
    ("Use terminal to find the largest file in /tmp: ls -lS /tmp 2>/dev/null | head -5. Report what you find.", ["/tmp"], 2),
    ("Use terminal to run: echo {1..5} | tr ' ' '\\n' | tac | tr '\\n' ' '. What's the output?", ["5", "4", "3", "2", "1"], 2),
    ("Use terminal to check if /tmp/nonexistent_file.txt exists using: test -f /tmp/nonexistent_file.txt && echo exists || echo 'does not exist'. Report the result.", ["not exist", "does not"], 2),
    ("Use terminal to run: date -u '+%H:%M'. Report the current UTC time.", [":"], 2),
]

for prompt, contains, max_calls in terminal_tasks:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("terminal", "Terminal command execution", prompt, True, max_calls, verify, "terminal")

# ============================================================================
# CODE_EXECUTION — Python tasks
# ============================================================================

code_tasks = [
    ("Use execute_code to calculate the factorial of 10 and print the result.", ["3628800"], 2),
    ("Use execute_code to generate and print a list of all prime numbers under 50.", ["2", "3", "5", "7", "11", "13", "47"], 2),
    ("Use execute_code to reverse the string 'Hello, World!' and print it.", ["!dlroW ,olleH"], 2),
    ("Use execute_code to calculate the sum of squares from 1 to 10 and print it.", ["385"], 2),
    ("Use execute_code to sort the list [64, 25, 12, 22, 11] and print the result.", ["11", "12", "22", "25", "64"], 2),
    ("Use execute_code to count vowels in 'The quick brown fox jumps over the lazy dog' and print the count.", ["11"], 2),
    ("Use execute_code to convert the decimal number 255 to hexadecimal and print it.", ["ff", "FF", "0xff", "0xFF"], 2),
    ("Use execute_code to find the GCD of 48 and 18 using math.gcd and print it.", ["6"], 2),
    ("Use execute_code to generate a list of the first 8 powers of 2 (2^0 through 2^7) and print it.", ["1", "2", "4", "8", "16", "32", "64", "128"], 2),
    ("Use execute_code to check if 'racecar' is a palindrome and print True or False.", ["True"], 2),
    ("Use execute_code to count the frequency of each character in 'mississippi' and print the result.", ["s", "i", "p", "m"], 2),
    ("Use execute_code to flatten the nested list [[1,2],[3,[4,5]],[6]] into a single list and print it.", ["1", "2", "3", "4", "5", "6"], 2),
    ("Use execute_code to calculate the mean of [10, 20, 30, 40, 50] and print it.", ["30"], 2),
    ("Use execute_code to find all even numbers from 1 to 20 using a list comprehension and print them.", ["2", "4", "6", "8", "10", "12", "14", "16", "18", "20"], 2),
    ("Use execute_code to generate a simple multiplication table for 7 (7x1 through 7x10) and print it.", ["7", "14", "21", "28", "35", "42", "49", "56", "63", "70"], 2),
    ("Use execute_code to find the length of the longest word in 'the quick brown fox jumps over the lazy dog' and print it.", ["5"], 2),
    ("Use execute_code to compute 2^100 and print the exact result.", ["1267650600228229401496703205376"], 2),
    ("Use execute_code to create a dictionary from two lists: keys=['a','b','c'] values=[1,2,3] and print it.", ["a", "b", "c", "1", "2", "3"], 2),
    ("Use execute_code to remove duplicates from [1,2,2,3,3,3,4,4,4,4] while preserving order and print the result.", ["1", "2", "3", "4"], 2),
    ("Use execute_code to print the current Python version using sys.version.", ["3.", "Python"], 2),
    ("Use execute_code to implement FizzBuzz for numbers 1-20 and print the output.", ["Fizz", "Buzz", "FizzBuzz"], 2),
    ("Use execute_code to find the intersection of sets {1,2,3,4,5} and {3,4,5,6,7} and print it.", ["3", "4", "5"], 2),
    ("Use execute_code to encode the string 'Hello World' to base64 and print both the encoded and decoded versions.", ["SGVsbG8gV29ybGQ", "Hello World"], 2),
    ("Use execute_code to calculate pi to 10 decimal places using the math module and print it.", ["3.14159265", "3.1415926535"], 2),
    ("Use execute_code to transpose a 3x3 matrix [[1,2,3],[4,5,6],[7,8,9]] and print the result.", ["1", "4", "7", "2", "5", "8", "3", "6", "9"], 2),
    ("Use execute_code to run: import this and report the first principle of the Zen of Python.", ["Beautiful", "better", "ugly"], 2),
    ("Use execute_code to find all two-digit numbers that are divisible by both 3 and 7. Print them.", ["21", "42", "63", "84"], 2),
    ("Use execute_code to convert the temperature 100 Fahrenheit to Celsius and print the result.", ["37.7", "37.8"], 2),
    ("Use execute_code to generate a random password of 12 characters using letters and digits. Print it.", [], 2),
    ("Use execute_code to calculate the area of a circle with radius 7 using math.pi. Print the result.", ["153.9", "153.93"], 2),
]

for prompt, contains, max_calls in code_tasks:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("code_execution", "Python code execution", prompt, True, max_calls, verify, "execute_code")

# ============================================================================
# FILE_OPS — File create/read/write/search/delete
# ============================================================================

file_tasks = [
    ("Use write_file to create /tmp/greeting.txt with content 'Hello from synthetic eval'. Then read_file to verify.", ["Hello from synthetic eval"], 3, "write_file AND read_file"),
    ("Use write_file to create /tmp/numbers.txt with the numbers 1 through 5, one per line. Then read_file to confirm.", ["1", "2", "3", "4", "5"], 3, "write_file AND read_file"),
    ("Use write_file to create /tmp/config_test.ini with '[settings]\\nmode=production\\nport=8080'. Then read it back.", ["settings", "production", "8080"], 3, "write_file AND read_file"),
    ("Create /tmp/poem.txt with any 4-line poem using write_file. Then read it back with read_file.", [], 3, "write_file AND read_file"),
    ("Use write_file to create /tmp/data.csv with 'name,age\\nAlice,30\\nBob,25'. Then read it and report the contents.", ["name", "age", "Alice", "Bob"], 3, "write_file AND read_file"),
    ("Use search_files or terminal grep to find files containing 'root' in /etc/. Report the first few matches.", ["root", "/etc"], 3, "search_files OR terminal"),
    ("Use search_files or terminal grep to find .py files in /usr/ containing 'import'. Report some matches.", ["import", ".py"], 3, "search_files OR terminal"),
    ("Use terminal to create /tmp/multi_test.txt with 'line one', verify it exists, then append 'line two'. Minimize tool calls.", ["line"], 3, "terminal"),
    ("Use write_file to create /tmp/json_test.json with valid JSON: {\"key\": \"value\", \"count\": 42}. Read it back.", ["key", "value", "42"], 3, "write_file AND read_file"),
    ("Create /tmp/script_test.sh with '#!/bin/bash\\necho test_output' using write_file. Then use terminal to run it with bash /tmp/script_test.sh.", ["test_output"], 3, "write_file AND terminal"),
    ("Use terminal to find all .json files in ~/.config/ (first level only): find ~/.config -maxdepth 1 -name '*.json'. Report what you find.", [".json"], 2, "terminal"),
    ("Use write_file to create /tmp/overwrite_test.txt with 'version 1'. Then overwrite it with 'version 2'. Read to confirm.", ["version 2"], 4, "write_file AND read_file"),
    ("Use terminal to create a directory /tmp/nested/dirs/here using mkdir -p, then create a file inside it. Verify with ls.", ["nested", "dirs", "here"], 3, "terminal"),
    ("Read the file /etc/os-release using read_file. Report the OS name and version.", ["NAME", "VERSION", "ID"], 2, "read_file"),
    ("Use write_file to create /tmp/todo_list.txt with 3 items: 'Buy milk\\nFix bug\\nDeploy app'. Read it back.", ["Buy milk", "Fix bug", "Deploy app"], 3, "write_file AND read_file"),
    ("Use terminal to count how many lines are in /etc/passwd: wc -l /etc/passwd. Report the count.", ["/etc/passwd"], 2, "terminal"),
    ("Use write_file to create /tmp/math_results.txt with '2+2=4\\n3*3=9\\n10/2=5'. Then use terminal to grep for '=' in that file.", ["=", "4", "9", "5"], 3, "write_file AND terminal"),
    ("Use terminal to find the 3 most recently modified files in /tmp/: ls -lt /tmp | head -5. Report them.", ["/tmp"], 2, "terminal"),
    ("Create /tmp/env_dump.txt with the output of the env command using terminal redirection: env > /tmp/env_dump.txt. Then read it.", ["PATH", "HOME"], 3, "terminal AND read_file"),
    ("Use write_file to create /tmp/alphabet.txt with all 26 lowercase letters, one per line. Then count lines with wc -l.", ["26"], 3, "write_file AND terminal"),
]

for prompt, contains, max_calls, expected in file_tasks:
    verify = {"tool_count_min": 1, "tool_count_max": max_calls}
    if contains:
        verify["response_contains_any"] = contains
    T("file_ops", "File operations", prompt, True, max_calls, verify, expected)

# ============================================================================
# MEMORY — Store/recall memories
# ============================================================================

memory_tasks = [
    ("Use the memory tool to add: 'User prefers Python over JavaScript'. Confirm it was stored.", ["stored", "added", "saved", "memory", "Python"]),
    ("Use the memory tool to add: 'Eval run completed on March 4 2026'. Confirm storage.", ["stored", "added", "saved", "memory", "eval"]),
    ("Use the memory tool to add: 'Default model is qwen3-8b for fine-tuning'. Confirm.", ["stored", "added", "saved", "memory", "qwen"]),
    ("Use the memory tool to store: 'Project uses Docker sandbox for tool execution'. Confirm it saved.", ["stored", "added", "saved", "memory", "Docker"]),
    ("Use the memory tool to add: 'Training data threshold is score >= 0.5'. Confirm storage.", ["stored", "added", "saved", "memory", "training"]),
    ("Use the memory tool to store a note about the current date and time. Confirm it was saved.", ["stored", "added", "saved", "memory", "date"]),
    ("Use the memory tool to add: 'LoRA config uses r=32, alpha=64'. Confirm.", ["stored", "added", "saved", "memory", "LoRA"]),
    ("Use bash to check available disk space with df -h. Report the results.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'OpenRouter API key is configured for qwen3-8b'. Confirm saved.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store a reminder: 'Re-run baselines after fine-tuning'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Fibonacci task timed out on qwen3-8b'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to store: 'Terminal tool uses emoji prefix for result lines'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'Max tool calls should be minimized for efficiency'. Confirm it was stored.", ["stored", "added", "saved", "memory"]),
    ("Use the memory tool to store: 'User's project directory is ~/self-improve/'. Confirm.", ["stored", "added", "saved", "memory"]),
    ("Use memory to add: 'SFT training requires score >= 0.5 for inclusion'. Confirm saved.", ["stored", "added", "saved", "memory"]),
]

for prompt, contains in memory_tasks:
    T("memory", "Memory storage", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "memory")

# ============================================================================
# SKILLS — List, view, search skills
# ============================================================================

skills_tasks = [
    ("Use skills_list to list all installed skills. How many categories do you see?", ["skill", "categor", "installed"]),
    ("Use skills_list to find skills related to 'code' or 'development'. What do you find?", ["skill", "code", "develop"]),
    ("Use skill_view to look at the 'git-assistant' skill. What does it do?", ["git", "skill"]),
    ("Use skill_view to examine any skill related to machine learning or AI. Summarize it.", ["skill", "ML", "AI", "model", "train", "learn"]),
    ("Use skills_list to check if there's a skill for 'note-taking' or 'obsidian'. Report.", ["skill", "note", "obsidian"]),
    ("Use skills_list to count how many skills are in the 'software-development' category.", ["skill", "software", "develop"]),
    ("Use skill_view to look at any skill that involves 'debugging'. Summarize in 2 sentences.", ["skill", "debug"]),
    ("Use skills_list and report the 3 most interesting skills you find. Briefly describe each.", ["skill"]),
    ("Use skill_view to examine the 'test-driven-development' skill. What methodology does it describe?", ["test", "TDD", "skill"]),
    ("Use skills_list to find any skills related to writing or documentation. Report what you find.", ["skill", "writ", "doc"]),
    ("Use skill_manage to create a skill called 'data-pipeline' with description 'ETL data processing helper'. Confirm creation.", ["data-pipeline", "created", "skill"]),
    ("Use skill_manage to create a skill called 'code-reviewer' with description 'Automated code review assistant'. Then verify with skills_list.", ["code-reviewer", "skill"]),
    ("Use skills_list to find skills in the 'research' category. What research tools are available?", ["skill", "research"]),
    ("Use skill_view to look at the 'systematic-debugging' skill. Summarize the debugging approach.", ["debug", "skill", "system"]),
    ("Use skills_list to check what productivity skills are available. List them.", ["skill", "productiv"]),
]

for prompt, contains in skills_tasks:
    max_calls = 3 if "skill_manage" in prompt else 2
    T("skills", "Skills management", prompt, True, max_calls,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": max_calls}, "skills_list OR skill_view")

# ============================================================================
# SESSION_SEARCH — Search past conversations
# ============================================================================

session_tasks = [
    ("Use session_search to find past conversations about 'Docker'. Report what you find.", ["session", "conversation", "found", "Docker", "result"]),
    ("Use session_search to find past conversations about 'memory' or 'remember'. Report results.", ["session", "conversation", "found", "memory", "result"]),
    ("Use session_search to look for past discussions about 'error' or 'bug'. What do you find?", ["session", "conversation", "found", "error", "result"]),
    ("Use session_search to find conversations about 'training' or 'model'. Report what's there.", ["session", "conversation", "found", "training", "result"]),
    ("Use session_search to find past conversations about 'file' operations. Report results.", ["session", "conversation", "found", "file", "result"]),
    ("Use session_search to search for 'python' in past conversations. What did you find?", ["session", "conversation", "found", "python", "result"]),
    ("Use session_search to look for 'eval' or 'evaluation' in past sessions. Report findings.", ["session", "conversation", "found", "eval", "result"]),
    ("Use session_search to find conversations about 'terminal' commands. Report what you find.", ["session", "conversation", "found", "terminal", "result"]),
    ("Use session_search to search for 'install' or 'setup' in past sessions. Report results.", ["session", "conversation", "found", "install", "result", "setup"]),
    ("Use session_search to look for any conversation mentioning 'skill' or 'tool'. Report.", ["session", "conversation", "found", "skill", "result", "tool"]),
]

for prompt, contains in session_tasks:
    T("session_search", "Past session search", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "session_search")

# ============================================================================
# CRON — Cron job listing
# ============================================================================

cron_tasks = [
    ("Use list_cronjobs to check what jobs are scheduled. Report any jobs or state that none exist.", ["cron", "job", "scheduled", "no ", "none", "empty", "0"]),
    ("Use list_cronjobs to see if any automated tasks are set up. Summarize what you find.", ["cron", "job", "scheduled", "task", "no ", "none"]),
    ("Check for scheduled cron jobs using list_cronjobs. Are there any recurring tasks? Report.", ["cron", "job", "scheduled", "recurring", "no ", "none"]),
    ("Use list_cronjobs to inspect the cron schedule. Report the status of scheduled jobs.", ["cron", "job", "scheduled", "status", "no ", "none"]),
    ("Use list_cronjobs to check if there are any daily or weekly automated tasks. Report.", ["cron", "job", "daily", "weekly", "no ", "none", "scheduled"]),
]

for prompt, contains in cron_tasks:
    T("cron", "Cron job inspection", prompt, True, 2,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 2}, "list_cronjobs")

# ============================================================================
# TODO — Task management
# ============================================================================

todo_tasks = [
    ("Use the todo tool to add: 'Review training data quality'. Then list all tasks.", ["review", "training", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Optimize model hyperparameters'. Confirm it was added.", ["optimize", "hyperparameter", "task", "todo", "added"]),
    ("Use the todo tool to create 2 tasks: 'Write unit tests' and 'Run benchmarks'. List all tasks.", ["test", "benchmark", "task", "todo"]),
    ("Use the todo tool to add: 'Deploy fine-tuned model to API'. Then list current tasks.", ["deploy", "model", "task", "todo"]),
    ("Use the todo tool to add: 'Clean up temporary eval files'. Confirm and list tasks.", ["clean", "eval", "task", "todo"]),
    ("Use the todo tool to add 3 tasks: 'Fix timeout bug', 'Add error handling', 'Update docs'. List them.", ["fix", "error", "docs", "task", "todo"]),
    ("Use the todo tool to add: 'Compare baseline vs fine-tuned scores'. Confirm added.", ["compare", "baseline", "score", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Generate DPO preference pairs'. List current tasks.", ["DPO", "preference", "task", "todo"]),
    ("Use the todo tool to add: 'Profile model inference latency'. Confirm.", ["profile", "latency", "task", "todo", "added"]),
    ("Use the todo tool to add: 'Archive old evaluation results'. List all tasks.", ["archive", "eval", "task", "todo"]),
]

for prompt, contains in todo_tasks:
    T("todo", "Task management", prompt, True, 3,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": 3}, "todo")

# ============================================================================
# PLANNING — Plan before executing multi-step tasks
# ============================================================================

planning_tasks = [
    ("Task: (1) Create /tmp/planning_a.txt with 'step 1 done', (2) read it back, (3) delete it. Write your plan BEFORE making tool calls. Then execute.",
     ["1.", "2.", "3.", "Step", "Plan", "First"], 5, "terminal OR write_file"),
    ("Task: (1) Check if Python3 is installed, (2) create a Python script at /tmp/test_plan.py that prints 'success', (3) run it. Plan first, then execute.",
     ["1.", "2.", "3.", "Step", "Plan", "First"], 5, "terminal OR write_file"),
    ("Task: (1) List files in /tmp, (2) create /tmp/plan_log.txt with the count, (3) verify the file. Plan your approach first.",
     ["1.", "2.", "3.", "Step", "Plan", "First"], 5, "terminal OR write_file"),
    ("Task: Set up a simple project structure: (1) create /tmp/myproject/ directory, (2) create /tmp/myproject/main.py with a hello world print, (3) create /tmp/myproject/README with 'My Project', (4) list the directory. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "myproject"], 6, "terminal OR write_file"),
    ("Task: (1) Check disk usage of /tmp, (2) create a 'report.txt' file summarizing the usage, (3) read it back. Write a numbered plan before executing.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "report"], 5, "terminal OR write_file"),
    ("Task: (1) Find all .txt files in /tmp, (2) count them, (3) save the count to /tmp/file_count.txt, (4) verify. Plan your approach first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "count"], 5, "terminal OR write_file"),
    ("Task: (1) Create /tmp/backup/ directory, (2) copy /etc/hostname into it, (3) verify the copy. Write your plan BEFORE any tool calls.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "backup"], 5, "terminal"),
    ("Task: (1) Write a Python script /tmp/calc.py that computes 2^20, (2) run it, (3) save the output to /tmp/result.txt. Plan first, then execute.",
     ["1.", "2.", "3.", "Step", "Plan", "First"], 5, "write_file AND terminal"),
    ("Task: (1) Check what shells are available in /etc/shells, (2) count them, (3) create a summary file. Plan your steps first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "shell"], 5, "terminal OR read_file"),
    ("Task: (1) Create /tmp/log_test.txt with timestamp using date, (2) append 'task started', (3) append 'task completed', (4) read the full log. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "log"], 6, "terminal"),
    ("Task: (1) List running processes, (2) count them, (3) create a report at /tmp/process_report.txt. Write your numbered plan BEFORE executing.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "process"], 5, "terminal"),
    ("Task: Debug workflow — (1) create /tmp/buggy.py with 'print(1/0)', (2) run it and capture the error, (3) fix the script to handle ZeroDivisionError, (4) run it again. Plan first.",
     ["1.", "2.", "3.", "Step", "Plan", "First", "Zero", "error"], 6, "write_file AND terminal"),
]

for prompt, contains, max_calls, expected in planning_tasks:
    T("planning", "Plan before executing", prompt, True, max_calls,
      {"response_contains_any": contains, "plan_before_first_tool": True, "tool_count_min": 2, "tool_count_max": max_calls}, expected)

# ============================================================================
# MULTI_STEP — Efficient multi-tool workflows
# ============================================================================

multi_tasks = [
    ("Do all of this efficiently: (1) create /tmp/eff_test.txt with 'efficiency', (2) count its characters, (3) delete it. Minimize tool calls. Max 4.",
     ["efficiency", "10", "delet"], 4, "terminal"),
    ("Efficiently: (1) check if /tmp/multi_a.txt exists, (2) create it with 'data_123', (3) read it, (4) delete it. Use as few tool calls as possible. Max 4.",
     ["data_123"], 4, "terminal"),
    ("In the fewest calls possible: (1) create /tmp/chain1.txt with 'hello', (2) copy it to /tmp/chain2.txt, (3) verify both exist. Max 3 calls.",
     ["hello", "chain"], 3, "terminal"),
    ("Efficiently do: (1) make directory /tmp/eff_dir, (2) create 3 files inside it (a.txt, b.txt, c.txt), (3) list the directory. Minimize calls. Max 4.",
     ["a.txt", "b.txt", "c.txt"], 4, "terminal"),
    ("Do this in minimal tool calls: (1) write 'START' to /tmp/log_eff.txt, (2) append 'MIDDLE', (3) append 'END', (4) read the full file. Max 3 calls.",
     ["START", "MIDDLE", "END"], 3, "terminal"),
    ("Efficiently: (1) check Python version, (2) check pip version, (3) list installed packages. Do it in 1-2 terminal calls. Max 3.",
     ["Python", "pip", "3."], 3, "terminal"),
    ("In minimal calls: (1) create /tmp/sorted_input.txt with 'cherry\\napple\\nbanana', (2) sort it, (3) save sorted output to /tmp/sorted_output.txt. Max 3.",
     ["apple", "banana", "cherry"], 3, "terminal"),
    ("Do efficiently: (1) find all .conf files in /etc (depth 1), (2) count them, (3) save the count to /tmp/conf_count.txt. Max 3 calls.",
     ["conf", "count"], 3, "terminal"),
    ("Minimal calls: (1) get current date, (2) get hostname, (3) get kernel version. Combine into one report. Max 2 terminal calls.",
     ["date", "host", "Linux"], 2, "terminal"),
    ("Efficiently: (1) create /tmp/upper.txt with 'hello world', (2) convert contents to uppercase, (3) save to /tmp/upper_result.txt, (4) verify. Max 3 calls.",
     ["HELLO", "WORLD"], 3, "terminal"),
    ("Do in fewest calls: write a Python one-liner that prints numbers 1-10 and their squares. Use terminal or execute_code. Max 2 calls.",
     ["1", "4", "9", "16", "25"], 2, "terminal OR execute_code"),
    ("Efficient workflow: (1) create /tmp/test_input.csv with 'a,1\\nb,2\\nc,3', (2) use awk to extract the second column, (3) report the numbers. Max 3 calls.",
     ["1", "2", "3"], 3, "terminal"),
]

for prompt, contains, max_calls, expected in multi_tasks:
    T("multi_step", "Efficient multi-step operation", prompt, True, max_calls,
      {"response_contains_any": contains, "tool_count_min": 1, "tool_count_max": max_calls}, expected)

# ============================================================================
# SELF_IMPROVEMENT — Meta-reasoning about AI capabilities
# ============================================================================

self_improvement_tasks = [
    ("Create 3 training examples in JSON format showing an AI agent efficiently using terminal commands. Each needs 'prompt' and 'ideal_response'. Output valid JSON array. No tools needed.",
     ["prompt", "ideal_response", "terminal"], False, 1),
    ("Create 3 training examples showing when an AI should NOT use tools. JSON array with 'prompt' and 'ideal_response'. No tools needed.",
     ["prompt", "ideal_response", "no tool", "without"], False, 1),
    ("Write a rubric for evaluating AI agent tool efficiency. Include 5 criteria, each scored 1-5. No tools needed.",
     ["efficiency", "criteri", "score", "1", "5", "tool"], False, 1),
    ("Design 3 test cases to evaluate if an AI agent handles errors gracefully when tools fail. JSON format with prompt and expected_behavior. No tools.",
     ["error", "fail", "graceful", "prompt", "expected"], False, 1),
    ("Create a scoring system for rating AI agent responses. Include categories: accuracy, tool efficiency, response clarity, error handling. Define 1-5 scale for each. No tools.",
     ["accuracy", "efficiency", "clarity", "error", "1", "5"], False, 1),
    ("Write 3 examples of BAD tool usage by an AI agent and explain why each is bad. JSON format. No tools.",
     ["bad", "wrong", "unnecessary", "inefficient", "waste", "prompt"], False, 1),
    ("Design a benchmark task that tests whether an AI agent can plan before executing. Describe the task, inputs, expected outputs, and scoring criteria. No tools.",
     ["plan", "benchmark", "task", "score", "criteria", "expected"], False, 1),
    ("Create 3 training examples teaching an AI to combine multiple shell commands with && instead of making separate tool calls. JSON format. No tools.",
     ["&&", "combine", "prompt", "ideal_response", "terminal"], False, 1),
    ("Write a comparison table of tool-use strategies: 'minimal tools', 'defensive tools', 'exploratory tools'. When is each appropriate? No tools.",
     ["minimal", "defensive", "exploratory", "appropriate", "when"], False, 1),
    ("Create 5 increasingly difficult tasks for testing AI agent file operations, from simple write to complex multi-file workflows. Describe each. No tools.",
     ["file", "write", "read", "complex", "task", "simple"], False, 1),
    ("Design a reward function for training AI agents on tool efficiency. Define positive and negative signals. Include formula or pseudocode. No tools.",
     ["reward", "positive", "negative", "efficient", "score", "penalty"], False, 1),
    ("Create 3 examples of tasks where using execute_code is better than terminal, and 3 where terminal is better. Explain the differences. No tools.",
     ["execute_code", "terminal", "better", "prefer", "when"], False, 1),
    ("Write a checklist an AI agent should follow before making a tool call. Include at least 5 items. No tools.",
     ["check", "before", "tool", "necessary", "need"], False, 1),
    ("Create training data showing how an AI should respond when it doesn't know something vs when it should use tools to find out. 3 examples each. No tools.",
     ["don't know", "uncertain", "tool", "look up", "search", "find"], False, 1),
    ("Design a progressive difficulty scale for AI agent evaluation. Level 1: simple queries, Level 5: complex multi-step workflows. Describe each level. No tools.",
     ["level", "1", "5", "simple", "complex", "difficult"], False, 1),
]

for prompt, contains, requires, max_calls in self_improvement_tasks:
    T("self_improvement", "Meta-reasoning and self-improvement", prompt, requires, max_calls,
      {"response_contains_any": contains, "tool_count_max": max_calls})

# ============================================================================
# Write output
# ============================================================================

output = {
    "meta": {
        "version": "2.1.0-synthetic",
        "description": "Synthetically generated eval tasks for Pi Agent training data collection",
        "base_version": "2.0.0",
        "generated_by": "claude-opus-4.6",
        "total_tasks": len(tasks),
    },
    "tasks": tasks,
}

# Count by category
from collections import Counter
cats = Counter(t["category"] for t in tasks)
print(f"Total tasks: {len(tasks)}")
print(f"\nBy category:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_tasks.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nWritten to: {out_path}")
