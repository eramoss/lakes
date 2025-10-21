import pandas as pd
import matplotlib.pyplot as plt
import sys

def load_csv(filepath):
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['time_s'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
    return df

def plot_pagefaults_time(csv_file, title, output_file):
    df = load_csv(csv_file)
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['time_s'], df['minflt'], 'b-', linewidth=2, label='Minor Faults', marker='o')
    plt.plot(df['time_s'], df['majflt'], 'r-', linewidth=2, label='Major Faults', marker='s')
    
    plt.xlabel('Tempo (segundos)', fontsize=12)
    plt.ylabel('Page Faults', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Salvo: {output_file}")

def plot_rustlefeed_comparison(csv_windows, csv_linux, output_file):
    df_win = load_csv(csv_windows)
    df_linux = load_csv(csv_linux)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.plot(df_win['time_s'], df_win['minflt'], 'b-', linewidth=2, label='Windows')
    ax1.plot(df_linux['time_s'], df_linux['minflt'], 'r-', linewidth=2, label='Linux')
    ax1.set_xlabel('Tempo (segundos)', fontsize=12)
    ax1.set_ylabel('Minor Page Faults', fontsize=12)
    ax1.set_title('Minor Faults', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(df_win['time_s'], df_win['majflt'], 'b-', linewidth=2, label='Windows')
    ax2.plot(df_linux['time_s'], df_linux['majflt'], 'r-', linewidth=2, label='Linux')
    ax2.set_xlabel('Tempo (segundos)', fontsize=12)
    ax2.set_ylabel('Major Page Faults', fontsize=12)
    ax2.set_title('Major Faults', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('RustleFeed - Windows vs Linux', fontsize=15, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Salvo: {output_file}")

def plot_contention_4cases(csv_win_low, csv_win_high, csv_linux_low, csv_linux_high, output_file):
    """Comparação de Contenção: 4 casos (Baixa/Alta em Win/Linux)"""
    df_win_low = load_csv(csv_win_low)
    df_win_high = load_csv(csv_win_high)
    df_linux_low = load_csv(csv_linux_low)
    df_linux_high = load_csv(csv_linux_high)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    ax1.plot(df_win_low['time_s'], df_win_low['minflt'], 'g-', linewidth=2, label='Baixa Contenção')
    ax1.plot(df_win_high['time_s'], df_win_high['minflt'], 'r-', linewidth=2, label='Alta Contenção')
    ax1.set_xlabel('Tempo (s)', fontsize=11)
    ax1.set_ylabel('Minor Faults', fontsize=11)
    ax1.set_title('Windows - Minor Faults', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Linux - Minor Faults
    ax3.plot(df_linux_low['time_s'], df_linux_low['minflt'], 'g-', linewidth=2, label='Baixa Contenção')
    ax3.plot(df_linux_high['time_s'], df_linux_high['minflt'], 'r-', linewidth=2, label='Alta Contenção')
    ax3.set_xlabel('Tempo (s)', fontsize=11)
    ax3.set_ylabel('Minor Faults', fontsize=11)
    ax3.set_title('Linux - Minor Faults', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Linux - Major Faults
    ax4.plot(df_linux_low['time_s'], df_linux_low['majflt'], 'g-', linewidth=2, label='Baixa Contenção')
    ax4.plot(df_linux_high['time_s'], df_linux_high['majflt'], 'r-', linewidth=2, label='Alta Contenção')
    ax4.set_xlabel('Tempo (s)', fontsize=11)
    ax4.set_ylabel('Major Faults', fontsize=11)
    ax4.set_title('Linux - Major Faults', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Impacto de Contenção de Memória', fontsize=15, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Salvo: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "simple":
        if len(sys.argv) != 5:
            print("uso: python graph.py simple <csv> \"<título>\" <output.png>")
            sys.exit(1)
        csv_file = sys.argv[2]
        title = sys.argv[3]
        output = sys.argv[4]
        plot_pagefaults_time(csv_file, title, output)
        
    elif mode == "rustlefeed":
        if len(sys.argv) != 5:
            print("uso: python graph.py rustlefeed <csv_windows> <csv_linux> <output.png>")
            sys.exit(1)
        csv_win = sys.argv[2]
        csv_linux = sys.argv[3]
        output = sys.argv[4]
        plot_rustlefeed_comparison(csv_win, csv_linux, output)
        
    elif mode == "contention":
        if len(sys.argv) != 7:
            print("uso: python graph.py contention <win_low> <win_high> <linux_low> <linux_high> <output.png>")
            sys.exit(1)
        win_low = sys.argv[2]
        win_high = sys.argv[3]
        linux_low = sys.argv[4]
        linux_high = sys.argv[5]
        output = sys.argv[6]
        plot_contention_4cases(win_low, win_high, linux_low, linux_high, output)
