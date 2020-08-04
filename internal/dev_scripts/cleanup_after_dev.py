import fileinput
import os
import sys

build_clean = False
if len(sys.argv) > 1: 
    arg = sys.argv[1]
    if arg == 'build': 
        build_clean = True
        print('> Build cleanup')

print("*** CLEANUP starting ...")

#constants.py
f_constants_temp = open('.\\o8g\\Scripts\\constants.py.tmp', 'w')
f_constants = fileinput.input('.\\o8g\\Scripts\\constants.py')
after_imports = False
for line in f_constants:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_constants_temp.write(line)
f_constants_temp.close()
f_constants.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\constants.py')
    os.rename('.\\o8g\\Scripts\\constants.py.tmp', '.\\o8g\\Scripts\\constants.py')
print(">> constants.py cleaned")

#actions.py
f_actions_temp = open('.\\o8g\\Scripts\\actions.py.tmp', 'w')
f_actions = fileinput.input('.\\o8g\\Scripts\\actions.py')
after_imports = False
for line in f_actions:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_actions_temp.write(line)
f_actions_temp.close()
f_actions.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\actions.py')
    os.rename('.\\o8g\\Scripts\\actions.py.tmp', '.\\o8g\\Scripts\\actions.py')
print(">> actions.py cleaned")

#autoscripts.py
f_autoscripts_temp = open('.\\o8g\\Scripts\\autoscripts.py.tmp', 'w')
f_autoscripts = fileinput.input('.\\o8g\\Scripts\\autoscripts.py')
after_imports = False
for line in f_autoscripts:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_autoscripts_temp.write(line)
f_autoscripts_temp.close()
f_autoscripts.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\autoscripts.py')
    os.rename('.\\o8g\\Scripts\\autoscripts.py.tmp', '.\\o8g\\Scripts\\autoscripts.py')
print(">> autoscripts.py cleaned")

#customscripts.py
f_customscripts_temp = open('.\\o8g\\Scripts\\customscripts.py.tmp', 'w')
f_customscripts = fileinput.input('.\\o8g\\Scripts\\customscripts.py')
after_imports = False
for line in f_customscripts:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_customscripts_temp.write(line)
f_customscripts_temp.close()
f_customscripts.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\customscripts.py')
    os.rename('.\\o8g\\Scripts\\customscripts.py.tmp', '.\\o8g\\Scripts\\customscripts.py')
print(">> customscripts.py cleaned")

#events.py
f_events_temp = open('.\\o8g\\Scripts\\events.py.tmp', 'w')
f_events = fileinput.input('.\\o8g\\Scripts\\events.py')
after_imports = False
for line in f_events:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_events_temp.write(line)
f_events_temp.close()
f_events.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\events.py')
    os.rename('.\\o8g\\Scripts\\events.py.tmp', '.\\o8g\\Scripts\\events.py')
print(">> events.py cleaned")

#generic.py
f_generic_temp = open('.\\o8g\\Scripts\\generic.py.tmp', 'w')
f_generic = fileinput.input('.\\o8g\\Scripts\\generic.py')
after_imports = False
for line in f_generic:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_generic_temp.write(line)
f_generic_temp.close()
f_generic.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\generic.py')
    os.rename('.\\o8g\\Scripts\\generic.py.tmp', '.\\o8g\\Scripts\\generic.py')
print(">> generic.py cleaned")

#meta.py
f_meta_temp = open('.\\o8g\\Scripts\\meta.py.tmp', 'w')
f_meta = fileinput.input('.\\o8g\\Scripts\\meta.py')
after_imports = False
for line in f_meta:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    if line.startswith("debugVerbosity = ") and not build_clean: 
        f_meta_temp.write("debugVerbosity = -1 # At -1, means no debugging messages display\n")
    else: f_meta_temp.write(line)
f_meta_temp.close()
f_meta.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\meta.py')
    os.rename('.\\o8g\\Scripts\\meta.py.tmp', '.\\o8g\\Scripts\\meta.py')
print(">> meta.py cleaned")

#poker.py
f_poker_temp = open('.\\o8g\\Scripts\\poker.py.tmp', 'w')
f_poker = fileinput.input('.\\o8g\\Scripts\\poker.py')
after_imports = False
for line in f_poker:
    if (line.startswith("import") or line.startswith("from")) and not after_imports: continue
    after_imports = True
    f_poker_temp.write(line)
f_poker_temp.close()
f_poker.close()
if not build_clean:
    os.remove('.\\o8g\\Scripts\\poker.py')
    os.rename('.\\o8g\\Scripts\\poker.py.tmp', '.\\o8g\\Scripts\\poker.py')
print(">> poker.py cleaned")

#octgnAPI.py
if not build_clean:
    os.remove('.\\o8g\\Scripts\\octgnAPI.py')
    print(">> octgnAPI.py removed")

print("*** CLEANUP finished ...")
