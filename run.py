import subprocess

if __name__ == '__main__':
    subprocess.run('start "AutoBroker database control" python mysql_insert.py & start "YoBit AutoBroker" python main.py', shell=True)