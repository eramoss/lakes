import subprocess, psutil, time, csv, sys
import platform
from datetime import datetime

def get_page_faults_linux(pid):
    try:
        with open(f"/proc/{pid}/stat", "r") as f:
            data = f.read().split()
            minflt = int(data[9])
            majflt = int(data[11])
            return minflt, majflt
    except FileNotFoundError:
        return 0, 0

def get_page_faults_windows(p):
    try:
        mem_info = p.memory_info()
        if hasattr(mem_info, 'num_page_faults'):
            return mem_info.num_page_faults, 0
        else:
            return 0, 0
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0, 0

def monitor_process(command, interval=2, output_file="process_metrics.csv"):
    process = subprocess.Popen(command)
    pid = process.pid
    p = psutil.Process(pid)
    os_type = platform.system().lower()
    print(f"Started: {command} (PID: {pid}) on {os_type}")

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "pid",
            "rss_MB", "vms_MB",
            "minflt", "majflt"
        ])

        while True:
            if process.poll() is not None:
                break
            try:
                mem = p.memory_info()
                rss_mb = mem.rss / (1024 * 1024)
                vms_mb = mem.vms / (1024 * 1024)

                if os_type == "linux":
                    minflt, majflt = get_page_faults_linux(pid)
                else:
                    minflt, majflt = get_page_faults_windows(p)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([
                    timestamp, pid,
                    f"{rss_mb:.2f}", f"{vms_mb:.2f}",
                    minflt, majflt
                ])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

            time.sleep(interval)

    print(f"Process {pid} ended.")
    print(f"Metrics saved in {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monitor_process.py \"your command here\"")
        sys.exit(1)

    cmd = sys.argv[1:] 
    monitor_process(cmd, interval=2, output_file="process_metrics.csv")
