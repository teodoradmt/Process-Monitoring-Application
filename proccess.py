import psutil
import time
from prettytable import PrettyTable

def monitor_processes(x=5):
    while True:

        print("\033[H\033[J", end="")

        print("======= Process Monitoring =======")
        print(f"Interval: {x} seconds")

        table = PrettyTable(['PID', 'Process Name', 'CPU %', 'MEM %'])

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                table.add_row([
                    info['pid'],
                    info['name'][:20], 
                    f"{info['cpu_percent']:.1f}",
                    f"{info['memory_percent']:.1f}"
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print(table)

        time.sleep(x)

if __name__ == "__main__":
    try:
        x = int(input("Enter monitoring interval (in seconds): "))
    except ValueError:
        x = 5

    monitor_processes(x)
