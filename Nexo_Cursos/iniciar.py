"""Instalação local, primeiro administrador e servidor no próprio computador."""
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

def run(*args):
    subprocess.run([str(PYTHON), *args], check=True, cwd=ROOT)

if __name__ == '__main__':
    try:
        if sys.version_info < (3, 10):
            raise RuntimeError('Instala Python 3.10 ou mais recente para continuar.')
        PYTHON = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if not PYTHON.exists():
            print('A preparar o ambiente do projeto...')
            venv.create(ROOT / '.venv', with_pip=True)
        installed = subprocess.run([str(PYTHON), '-c', 'import django; assert django.get_version() == "5.2.18"'], capture_output=True)
        if installed.returncode:
            print('A instalar as dependências. É necessária internet nesta primeira vez.')
            run('-m', 'pip', 'install', '-r', 'requirements.txt')
        run('manage.py', 'migrate', '--noinput')
        run('manage.py', 'seed_demo')
        check = subprocess.run([str(PYTHON), 'manage.py', 'shell', '-c', 'from academy.models import User; import sys; sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 3)'], capture_output=True)
        if check.returncode == 3:
            print('\nCria agora a tua conta de administrador. Ao escrever a senha, ela não aparece no ecrã.\n')
            run('manage.py', 'createsuperuser')
        elif check.returncode:
            raise RuntimeError(check.stderr.decode(errors='replace'))
        print('\nNexo Cursos: http://127.0.0.1:8000\nMantém esta janela aberta. Para parar, pressiona Ctrl+C.\n')
        def open_when_ready():
            import urllib.request
            for _ in range(30):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8000/', timeout=1) as response:
                        if response.status == 200:
                            webbrowser.open('http://127.0.0.1:8000/')
                            return
                except OSError:
                    time.sleep(1)
        threading.Thread(target=open_when_ready, daemon=True).start()
        run('manage.py', 'runserver', '127.0.0.1:8000', '--noreload')
    except KeyboardInterrupt:
        print('\nServidor encerrado.')
    except Exception as exc:
        print(f'\nNão foi possível iniciar: {exc}\nConfere o LEIA-ME.md. A mensagem acima ajuda a identificar o problema.')
        input('Pressiona Enter para fechar...')
