import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

class PageFaultAnalyzer:
    def __init__(self, output_dir="graficos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_csv(self, filepath):
        """Carrega um CSV de métricas"""
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Calcula tempo relativo em segundos
        df['time_s'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
        return df
    
    def plot_memory_evolution(self, csv_file, title, output_name):
        """Gráfico de evolução de memória (RSS e VMS)"""
        df = self.load_csv(csv_file)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # RSS
        ax1.plot(df['time_s'], df['rss_MB'], 'b-', linewidth=2, label='RSS')
        ax1.fill_between(df['time_s'], df['rss_MB'], alpha=0.3)
        ax1.set_ylabel('RSS (MB)', fontsize=12, fontweight='bold')
        ax1.set_title(f'{title} - Evolução de Memória', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # VMS
        ax2.plot(df['time_s'], df['vms_MB'], 'g-', linewidth=2, label='VMS')
        ax2.fill_between(df['time_s'], df['vms_MB'], alpha=0.3, color='green')
        ax2.set_xlabel('Tempo (segundos)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('VMS (MB)', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_memoria.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def plot_page_faults_evolution(self, csv_file, title, output_name):
        """Gráfico de evolução de page faults"""
        df = self.load_csv(csv_file)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(df['time_s'], df['minflt'], 'b-', linewidth=2, label='Minor Faults', marker='o', markersize=4)
        ax.plot(df['time_s'], df['majflt'], 'r-', linewidth=2, label='Major Faults', marker='s', markersize=4)
        
        ax.set_xlabel('Tempo (segundos)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Page Faults', fontsize=12, fontweight='bold')
        ax.set_title(f'{title} - Evolução de Page Faults', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_pagefaults.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def plot_comparison_bar(self, csv_files, labels, title, output_name, metric='minflt'):
        """Gráfico de barras comparativo"""
        data = []
        for csv_file in csv_files:
            df = self.load_csv(csv_file)
            if metric == 'minflt':
                data.append(df['minflt'].iloc[-1])
            elif metric == 'majflt':
                data.append(df['majflt'].iloc[-1])
            elif metric == 'rss_MB':
                data.append(df['rss_MB'].mean())
            elif metric == 'vms_MB':
                data.append(df['vms_MB'].mean())
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = sns.color_palette("husl", len(labels))
        bars = ax.bar(labels, data, color=colors, edgecolor='black', linewidth=1.5)
        
        # Adiciona valores no topo das barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        metric_names = {
            'minflt': 'Minor Page Faults',
            'majflt': 'Major Page Faults',
            'rss_MB': 'RSS Médio (MB)',
            'vms_MB': 'VMS Médio (MB)'
        }
        
        ax.set_ylabel(metric_names[metric], fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_{metric}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def plot_threads_impact(self, csv_files, thread_counts, title, output_name):
        """Gráfico de impacto de threads"""
        minor_faults = []
        major_faults = []
        avg_rss = []
        
        for csv_file in csv_files:
            df = self.load_csv(csv_file)
            minor_faults.append(df['minflt'].iloc[-1])
            major_faults.append(df['majflt'].iloc[-1])
            avg_rss.append(df['rss_MB'].mean())
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Page Faults vs Threads
        ax1.plot(thread_counts, minor_faults, 'bo-', linewidth=2, markersize=8, label='Minor Faults')
        ax1.plot(thread_counts, major_faults, 'rs-', linewidth=2, markersize=8, label='Major Faults')
        ax1.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Page Faults', fontsize=12, fontweight='bold')
        ax1.set_title('Page Faults vs Threads', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(thread_counts)
        
        # RSS vs Threads
        ax2.plot(thread_counts, avg_rss, 'go-', linewidth=2, markersize=8)
        ax2.fill_between(thread_counts, avg_rss, alpha=0.3, color='green')
        ax2.set_xlabel('Número de Threads', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSS Médio (MB)', fontsize=12, fontweight='bold')
        ax2.set_title('Consumo de Memória vs Threads', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(thread_counts)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_threads.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def plot_os_comparison(self, csv_windows, csv_linux, title, output_name):
        """Comparação entre Windows e Linux"""
        df_win = self.load_csv(csv_windows)
        df_linux = self.load_csv(csv_linux)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Minor Faults
        ax1.plot(df_win['time_s'], df_win['minflt'], 'b-', linewidth=2, label='Windows')
        ax1.plot(df_linux['time_s'], df_linux['minflt'], 'r-', linewidth=2, label='Linux')
        ax1.set_ylabel('Minor Faults', fontsize=11, fontweight='bold')
        ax1.set_title('Minor Page Faults', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Major Faults
        ax2.plot(df_win['time_s'], df_win['majflt'], 'b-', linewidth=2, label='Windows')
        ax2.plot(df_linux['time_s'], df_linux['majflt'], 'r-', linewidth=2, label='Linux')
        ax2.set_ylabel('Major Faults', fontsize=11, fontweight='bold')
        ax2.set_title('Major Page Faults', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # RSS
        ax3.plot(df_win['time_s'], df_win['rss_MB'], 'b-', linewidth=2, label='Windows')
        ax3.plot(df_linux['time_s'], df_linux['rss_MB'], 'r-', linewidth=2, label='Linux')
        ax3.set_xlabel('Tempo (s)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('RSS (MB)', fontsize=11, fontweight='bold')
        ax3.set_title('Memória Residente (RSS)', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # VMS
        ax4.plot(df_win['time_s'], df_win['vms_MB'], 'b-', linewidth=2, label='Windows')
        ax4.plot(df_linux['time_s'], df_linux['vms_MB'], 'r-', linewidth=2, label='Linux')
        ax4.set_xlabel('Tempo (s)', fontsize=11, fontweight='bold')
        ax4.set_ylabel('VMS (MB)', fontsize=11, fontweight='bold')
        ax4.set_title('Memória Virtual (VMS)', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{title} - Comparação Windows vs Linux', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_comparacao_os.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def plot_memory_contention(self, csv_low, csv_high, title, output_name):
        """Comparação baixa vs alta contenção"""
        df_low = self.load_csv(csv_low)
        df_high = self.load_csv(csv_high)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Minor Faults
        ax1.plot(df_low['time_s'], df_low['minflt'], 'g-', linewidth=2, label='Baixa Contenção')
        ax1.plot(df_high['time_s'], df_high['minflt'], 'r-', linewidth=2, label='Alta Contenção')
        ax1.set_ylabel('Minor Faults', fontsize=11, fontweight='bold')
        ax1.set_title('Minor Page Faults', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Major Faults
        ax2.plot(df_low['time_s'], df_low['majflt'], 'g-', linewidth=2, label='Baixa Contenção')
        ax2.plot(df_high['time_s'], df_high['majflt'], 'r-', linewidth=2, label='Alta Contenção')
        ax2.set_ylabel('Major Faults', fontsize=11, fontweight='bold')
        ax2.set_title('Major Page Faults', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # RSS
        ax3.plot(df_low['time_s'], df_low['rss_MB'], 'g-', linewidth=2, label='Baixa Contenção')
        ax3.plot(df_high['time_s'], df_high['rss_MB'], 'r-', linewidth=2, label='Alta Contenção')
        ax3.set_xlabel('Tempo (s)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('RSS (MB)', fontsize=11, fontweight='bold')
        ax3.set_title('Memória Residente (RSS)', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Barras comparativas finais
        categories = ['Minor Faults', 'Major Faults']
        low_vals = [df_low['minflt'].iloc[-1], df_low['majflt'].iloc[-1]]
        high_vals = [df_high['minflt'].iloc[-1], df_high['majflt'].iloc[-1]]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, low_vals, width, label='Baixa Contenção', color='green', alpha=0.7)
        bars2 = ax4.bar(x + width/2, high_vals, width, label='Alta Contenção', color='red', alpha=0.7)
        
        ax4.set_ylabel('Quantidade', fontsize=11, fontweight='bold')
        ax4.set_title('Comparação Total de Page Faults', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(categories)
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle(f'{title} - Impacto de Contenção de Memória', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}_contencao.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Salvo: {output_path}")
        
    def generate_summary_table(self, csv_files, labels, output_name):
        """Gera tabela resumo em CSV"""
        summary_data = []
        
        for csv_file, label in zip(csv_files, labels):
            df = self.load_csv(csv_file)
            summary_data.append({
                'Configuração': label,
                'RSS Médio (MB)': f"{df['rss_MB'].mean():.2f}",
                'RSS Máximo (MB)': f"{df['rss_MB'].max():.2f}",
                'VMS Médio (MB)': f"{df['vms_MB'].mean():.2f}",
                'Minor Faults': int(df['minflt'].iloc[-1]),
                'Major Faults': int(df['majflt'].iloc[-1]),
                'Tempo Total (s)': f"{df['time_s'].iloc[-1]:.1f}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        output_path = self.output_dir / f"{output_name}_resumo.csv"
        summary_df.to_csv(output_path, index=False)
        print(f"✓ Tabela resumo salva: {output_path}")
        return summary_df





if __name__ == "__main__":
    analyzer = PageFaultAnalyzer(output_dir="graficos")

   # analyzer.plot_memory_evolution('dados/memorycost_100mb_windows.csv',
    #                               'memory cost 100mb - windows',
     #                              'memorycost_100mb_win')

    csv_files = ['process_metrics_rustlefeed_linux_rust.csv', 
                 'process_metrics_rustlefeed_linux_node.csv']
    labels = ['linux rust', 'linux node']#, 'windows rust', 'windows node']
    analyzer.plot_comparison_bar(csv_files, labels, 
                                 'rustlefeed - comparação de linguagem e sistema',
                                 'rustlefeed', 
                                 metric='rss_MB')

