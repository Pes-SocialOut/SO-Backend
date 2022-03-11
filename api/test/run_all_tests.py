import os
import subprocess

def run_tests_in_dir(dir):
    for x in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, x)) and x.endswith('_test.py'):
            print('Test case:', x[:-3], '-----------------------------------------')
            subprocess.run(['python3', os.path.join(dir, x)])

def examine_dir(dir):
    for x in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, x)):
            if x.startswith('module_'):
                print()
                print('\t\t Running tests for test module:', x)
                run_tests_in_dir(os.path.join(dir, x))
            examine_dir(os.path.join(dir, x))

if __name__ == "__main__":
    examine_dir(os.path.abspath(__file__)[:-17])
