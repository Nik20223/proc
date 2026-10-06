"""Парсер системных процессов `ps aux` (домашнее задание OTUS, тема Linux).

Скрипт собирает статистику по запущенным процессам, печатает отчёт в
стандартный поток вывода и сохраняет его в txt-файл с именем вида
`DD-MM-YYYY-HH:MM-scan.txt`.
"""

import subprocess
from datetime import datetime

PS_FIELDS = 11
NAME_MAX_LENGTH = 20


def get_processes():
    """Возвращает список процессов из вывода команды `ps aux`."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        check=True,
    )

    processes = []
    for line in result.stdout.splitlines()[1:]:
        if not line.strip():
            continue
        fields = line.split(maxsplit=PS_FIELDS - 1)
        if len(fields) != PS_FIELDS:
            continue
        processes.append(
            {
                "user": fields[0],
                "%cpu": float(fields[2]),
                "%mem": float(fields[3]),
                "command": fields[10],
            }
        )
    return processes


def build_report(processes):
    """Формирует текст отчёта по списку процессов."""
    users = []
    for process in processes:
        if process["user"] not in users:
            users.append(process["user"])

    processes_per_user = {}
    for process in processes:
        user = process["user"]
        processes_per_user[user] = processes_per_user.get(user, 0) + 1

    total_memory = sum(process["%mem"] for process in processes)
    total_cpu = sum(process["%cpu"] for process in processes)
    top_memory = max(processes, key=lambda process: process["%mem"])
    top_cpu = max(processes, key=lambda process: process["%cpu"])
    top_memory_name = top_memory["command"][:NAME_MAX_LENGTH]
    top_cpu_name = top_cpu["command"][:NAME_MAX_LENGTH]

    lines = [
        "Отчёт о состоянии системы:",
        "Пользователи системы: " + ", ".join(f"'{user}'" for user in users),
        f"Процессов запущено: {len(processes)}",
        "",
        "Пользовательских процессов:",
    ]
    lines += [f"{user}: {count}" for user, count in processes_per_user.items()]
    lines += [
        "",
        f"Всего памяти используется: {total_memory:.1f}%",
        f"Всего CPU используется: {total_cpu:.1f}%",
        f"Больше всего памяти использует: {top_memory_name}",
        f"Больше всего CPU использует: {top_cpu_name}",
    ]
    return "\n".join(lines)


def save_report(report):
    """Сохраняет отчёт в txt-файл и возвращает его имя."""
    filename = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
    with open(filename, "w", encoding="utf-8") as report_file:
        report_file.write(report + "\n")
    return filename


def main():
    processes = get_processes()
    report = build_report(processes)
    print(report)
    save_report(report)


if __name__ == "__main__":
    main()
