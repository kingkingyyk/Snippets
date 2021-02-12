import os, sys, subprocess
from subprocess import PIPE
from paramiko.client import SSHClient, AutoAddPolicy

LOCAL_PATH = os.environ['LOCAL_PATH']
REMOTE_PATH = os.environ['REMOTE_PATH']
REMOTE_HOST = os.environ['REMOTE_HOST']
REMOTE_USER = os.environ['REMOTE_USER']
REMOTE_PASSWORD = os.environ['REMOTE_PASSWORD']
REMOTE_PATH_IDENTIFIER = REMOTE_PATH + '.ext'

def check_remote_path(client):
    global REMOTE_PATH_IDENTIFIER
    stdin, stdout, stderr = client.exec_command('test -f "{}"'.format(REMOTE_PATH_IDENTIFIER))
    return stdout.channel.recv_exit_status() == 0

def mount_remote_path(client):
    stdin, stdout, stderr = client.exec_command('sudo mount -a')
    stdin.flush()

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD)
if not check_remote_path(client):
    print('Remote path error, try to remount.')
    mount_remote_path(client)
if not check_remote_path:
    print('Remote path remount failure.')
    sys.exit(1)
client.close()

command = ['sudo', 'rsync', '-azvhe', 'ssh', '--rsync-path="sudo -A rsync"', '--progress', '--delete', LOCAL_PATH, REMOTE_USER+'@'+REMOTE_HOST+':'+REMOTE_PATH]
print(' '.join(command))
proc = subprocess.Popen(' '.join(command), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
stdout, stderr = proc.communicate()
ret_code = proc.wait()
print(stdout.decode(sys.getdefaultencoding()))
print(stderr.decode(sys.getdefaultencoding()))
if ret_code == 0:
    print('Done!')
else:
    print('Failed!')
    sys.exit(ret_code)
