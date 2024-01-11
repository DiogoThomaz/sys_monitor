import os
import platform
import time
import psutil
from multiprocessing import Process, Queue




class Banner:
    @staticmethod
    def load_banner_text() -> str:
        banner = None
        with open('banner.txt', 'r') as f:
            banner = f.read()
            # remove linhas em branco
            banner = '\n'.join([linha for linha in banner.splitlines() if linha.strip() != ''])
        return banner


class TerminalStyle:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    RESET = '\033[0m'
    BREAK_LINE = '\n'
    DOUBLE_BREAK_LINE = '\n\n'
    DIVISION_LINE = '-'*80
    SETA_DIREITA = '➔'
    BANNER_LOGO = Banner.load_banner_text()
    BANNER = f"{BANNER_LOGO}{BREAK_LINE}{DIVISION_LINE}{BREAK_LINE}"
    NOME_PROGRAMA = "AméricaMonitor"
    LIMPAR_CONSOLE = 'cls' if platform.system() == 'Windows' else 'clear'


class DadosTerminalFactory:
    @staticmethod
    def obter_dados():
        try:
            
            cpu_percent = psutil.cpu_percent()
            cpu_cores = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq().current

            ram_gb = psutil.virtual_memory().used / (1024 ** 3)
            max_ram_gb = psutil.virtual_memory().total / (1024 ** 3)

            disk_name = psutil.disk_usage('/')
            disk_usage = disk_name.percent
            disk_name = disk_name.free / (1024 ** 3)

            internet_send = psutil.net_io_counters().bytes_sent / (1024 ** 2)
            internet_receive = psutil.net_io_counters().bytes_recv / (1024 ** 2)

            return {
                'cpu_percent': cpu_percent,
                'cpu_freq': cpu_freq,
                'cpu_cores': cpu_cores,
                'ram_gb': ram_gb,
                'max_ram_gb': max_ram_gb,
                'internet_send': internet_send,
                'internet_receive': internet_receive,
                'disk_name': disk_name,
                'disk_usage': disk_usage,
            }
        except Exception as e:
            print(f"Erro ao obter dados do sistema: {e}")
            return None


def monitorar_sistema(queue):
    while True:
        dados = DadosTerminalFactory.obter_dados()
        if dados:
            queue.put(dados)
        time.sleep(2)  


def exibir_logs(queue):
    while True:
        dados = queue.get()
        if dados:
            # Limpar o console
            os.system(TerminalStyle.LIMPAR_CONSOLE)

            # Exibir banner e nome do programa
            print(f"{TerminalStyle.VERDE}{TerminalStyle.BANNER}{TerminalStyle.RESET}")

            print(f"{TerminalStyle.VERMELHO}CPU Estatísticas{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Número de núcleos: {dados['cpu_cores']}{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Frequência do cpu: {dados['cpu_freq']:.2f} MHz{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Uso do CPU: {dados['cpu_percent']}%{TerminalStyle.RESET}")

            print(f"{TerminalStyle.BREAK_LINE}")
            print(f"{TerminalStyle.VERMELHO}RAM Estatísticas{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Uso de RAM: {dados['ram_gb']:.2f}/{dados['max_ram_gb']:.2f} GB{TerminalStyle.RESET}")
            
            print(f"{TerminalStyle.BREAK_LINE}")
            print(f"{TerminalStyle.VERMELHO}Discos Estatísticas{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Uso do Disco: {dados['disk_usage']}%{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Espaço livre: {dados['disk_name']:.2f} GB{TerminalStyle.RESET}")
  
            print(f"{TerminalStyle.BREAK_LINE}")
            print(f"{TerminalStyle.VERMELHO}Internet Estatísticas{TerminalStyle.RESET}")
            print(f"{TerminalStyle.VERDE}{TerminalStyle.SETA_DIREITA}Uso da Internet: {dados['internet_send']:.2f} MB/s (envio) | {dados['internet_receive']:.2f} MB/s (recebimento){TerminalStyle.RESET}")




if __name__ == "__main__":
    # Criar a fila
    fila = Queue()

    # Criar os processos
    processo_monitorar = Process(target=monitorar_sistema, args=(fila,), daemon=True)
    processo_exibir_logs = Process(target=exibir_logs, args=(fila,), daemon=True)

    # Iniciar os processos
    processo_monitorar.start()
    processo_exibir_logs.start()

    # Aguardar interrupção do programa (pode ser feito com um sinal, como Ctrl+C)
    try:
        processo_monitorar.join()
        processo_exibir_logs.join()
    except KeyboardInterrupt:
        processo_monitorar.terminate()
        processo_exibir_logs.terminate()
        processo_monitorar.join()
        processo_exibir_logs.join()
        print("Programa interrompido.")
