#!/usr/bin/env python3
"""Парсинг процессов Linux (`ps aux`) и запись отчёта в файл."""
import subprocess
from datetime import datetime

NAME_LIMIT = 20

ps_output = subprocess.run(
    ["ps", "aux"], capture_output=True, text=True
).stdout

processes = []
for line in ps_output.splitlines()[1:]:
    user, _pid, cpu, mem, *_rest, command = line.split(maxsplit=10)
    processes.append(
        {
            "user": user,
            "cpu": float(cpu),
            "mem": float(mem),
            "command": command,
        }
    )

users = []
processes_per_user = {}
for process in processes:
    user = process["user"]
    if user not in users:
        users.append(user)
    processes_per_user[user] = processes_per_user.get(user, 0) + 1

total_mem = sum(process["mem"] for process in processes)
total_cpu = sum(process["cpu"] for process in processes)
top_mem = max(processes, key=lambda process: process["mem"])
top_cpu = max(processes, key=lambda process: process["cpu"])

report = "\n".join(
    [
        "Отчёт о состоянии системы:",
        "Пользователи системы: " + ", ".join(f"'{user}'" for user in users),
        f"Процессов запущено: {len(processes)}",
        "",
        "Пользовательских процессов:",
        *[f"{user}: {count}" for user, count in processes_per_user.items()],
        "",
        f"Всего памяти используется: {total_mem:.1f}%",
        f"Всего CPU используется: {total_cpu:.1f}%",
        f"Больше всего памяти использует: {top_mem['command'][:NAME_LIMIT]}",
        f"Больше всего CPU использует: {top_cpu['command'][:NAME_LIMIT]}",
    ]
)

print(report)

filename = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
with open(filename, "w", encoding="utf-8") as report_file:
    report_file.write(report + "\n")
