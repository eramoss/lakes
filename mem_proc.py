import subprocess
import psutil
import time
import csv
import sys
from datetime import datetime

def monitor_process(command, interval=2, output_file="process_metrics.csv"):
    process = subprocess.Popen(command, shell=True)
    pid = process.pid
    p = psutil.Process(pid)
    print(f"Started: {command} (PID: {pid})")

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "pid", "cpu_percent", "rss_MB", "vms_MB"])

        while True:
            if process.poll() is not None:
                break

            try:
                with p.oneshot():
                    cpu = p.cpu_percent(interval=None)
                    mem_info = p.memory_info()
                    rss_mb = mem_info.rss / (1024 * 1024)
                    vms_mb = mem_info.vms / (1024 * 1024)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp, pid, cpu, f"{rss_mb:.2f}", f"{vms_mb:.2f}"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

            time.sleep(interval)

    print(f"Process {pid} ended.")
    print(f"Metrics saved in {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monitor_process.py \"your command here\"")
        sys.exit(1)

    cmd = sys.argv[1]
    monitor_process(cmd, interval=2, output_file="process_metrics.csv")
