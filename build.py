import sys
import os.path
import shutil

try:
    sys.argv.append('build')
    import freeze
except:
    print('\n\nError generating executable\n\n')

CONFIG_FILE = os.path.abspath('default.conf')
DATA_DIR = os.path.abspath('data')
DIST_DIR = os.path.abspath('dist')
MAC_DIR = os.path.join(DIST_DIR, 'mac')
WINDOWS_DIR = os.path.join(DIST_DIR, 'window')
BUILD_DIR = os.path.abspath('build')
EXEC_DIR = os.path.abspath('executable')
EXEC_DATA_DIR = os.path.join(EXEC_DIR, 'data')
EXEC_DIST_DIR = os.path.join(EXEC_DIR, 'dist')

if __name__ == '__main__':
    print('Building executable\n\n')

    platform_path = MAC_DIR
    if sys.platform.startswith('win32'):
        platform_path = WINDOWS_DIR
    elif sys.platform.startswith('darwin'):
        platform_path = MAC_DIR

    print('Platform path:', platform_path)

    shutil.copytree(platform_path, EXEC_DIR)
    os.mkdir(EXEC_DATA_DIR)
    for directory in ['models', 'objects', 'observations', 'plots']:
        os.mkdir(os.path.join(EXEC_DATA_DIR, directory))
    shutil.copy(CONFIG_FILE, EXEC_DIR)

    build_output = os.path.abspath(
        os.path.join(BUILD_DIR, os.listdir(BUILD_DIR)[0]))
    shutil.copytree(build_output, EXEC_DIST_DIR)
    shutil.copy(CONFIG_FILE, EXEC_DIST_DIR)

    print('\n\n!! Done building executable !!')
