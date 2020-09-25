from subprocess import run
from sys import exit, argv
from shutil import copy, move
from os import path

overall_cp = 0

deploy_path = ""
if len(argv) > 1: 
    deploy_path = argv[1]

print("*** BUILD starting ...")
print("** pylint executions ...")

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\constants.py"])
if cp.returncode == 0: print("++ constants.py SUCCESS")
else: 
    overall_cp = cp
    print("!! constants.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\actions.py"])
if cp.returncode == 0: print("++ actions.py SUCCESS")
else: 
    overall_cp = cp
    print("!! actions.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\autoscripts.py"])
if cp.returncode == 0: print("++ autoscripts.py SUCCESS")
else: 
    overall_cp = cp
    print("!! autoscripts.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\customscripts.py"])
if cp.returncode == 0: print("++ customscripts.py SUCCESS")
else: 
    overall_cp = cp
    print("!! customscripts.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\events.py"])
if cp.returncode == 0: print("++ events.py SUCCESS")
else:
    overall_cp = cp    
    print("!! events.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\generic.py"])
if cp.returncode == 0: print("++ generic.py SUCCESS")
else:
    overall_cp = cp    
    print("!! generic.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\meta.py"])
if cp.returncode == 0: print("++ meta.py SUCCESS")
else:
    overall_cp = cp    
    print("!! meta.py FAILED rc={}".format(cp.returncode))

cp = run(["pylint3", "-E", ".\\o8g\\Scripts\\poker.py"])
if cp.returncode == 0: print("++ poker.py SUCCESS")
else:
    overall_cp = cp    
    print("!! poker.py FAILED rc={}".format(cp.returncode))

print("## pylint ended ...")

if overall_cp != 0: 
    print("!! ABORTING execution  ...")
    exit(-1)

print("## o8build starting ...")
cp = run([".\\internal\\o8build", "-d=./o8g"])
if cp.returncode == 0: print("++ o8build SUCCESS")
else: 
    print("!! o8build FAILED rc={}".format(cp.returncode))
    print("!! ABORTING execution  ...")
    exit(-1)

print("** Deploy files to " + deploy_path + "\\Data\\GameDatabase\\b440d120-025a-4fbe-9f8d-3873acacb37b\\Scripts\\")

cp = run(["python", ".\\internal\\dev_scripts\\cleanup_after_dev.py", "build"])

files = ['actions.py', 'autoscripts.py', 'CardScripts.py', 'constants.py', 'customscripts.py', 'events.py', 'generic.py', 'meta.py', 'poker.py', 'winForms.py']
for f in files:
    file_to_copy = '.\\o8g\\Scripts\\' + f
    if path.isfile(file_to_copy + '.tmp'): 
        file_to_copy += '.tmp'
        move(file_to_copy, deploy_path + '\\Data\\GameDatabase\\b440d120-025a-4fbe-9f8d-3873acacb37b\\Scripts\\' + f)
    else: copy(file_to_copy, deploy_path + '\\Data\\GameDatabase\\b440d120-025a-4fbe-9f8d-3873acacb37b\\Scripts')
copy('.\\o8g\\definition.xml', deploy_path + '\\Data\\GameDatabase\\b440d120-025a-4fbe-9f8d-3873acacb37b')

print("** Deploy DONE")