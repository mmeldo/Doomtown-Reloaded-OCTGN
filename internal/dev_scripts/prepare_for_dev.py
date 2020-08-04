import shutil
import os
import subprocess

print("*** PREP starting ...")

#constants.py
f_constants_temp = open('.\\o8g\\Scripts\\constants_temp.py', 'wb')
f_constants = open('.\\o8g\\Scripts\\constants.py', 'rb')
f_constants_import = open('.\\internal\\imports\\constants_import.py', 'rb')
shutil.copyfileobj(f_constants_import, f_constants_temp)
shutil.copyfileobj(f_constants, f_constants_temp)
f_constants_temp.close()
f_constants.close()
os.remove('.\\o8g\\Scripts\\constants.py')
os.rename('.\\o8g\\Scripts\\constants_temp.py', '.\\o8g\\Scripts\\constants.py')
print(">> constants.py prepared")

#poker.py
f_poker_temp = open('.\\o8g\\Scripts\\poker_temp.py', 'wb')
f_poker = open('.\\o8g\\Scripts\\poker.py', 'rb')
f_poker_import = open('.\\internal\\imports\\poker_import.py', 'rb')
shutil.copyfileobj(f_poker_import, f_poker_temp)
shutil.copyfileobj(f_poker, f_poker_temp)
f_poker_temp.close()
f_poker.close()
os.remove('.\\o8g\\Scripts\\poker.py')
os.rename('.\\o8g\\Scripts\\poker_temp.py', '.\\o8g\\Scripts\\poker.py')
print(">> poker.py prepared")

#actions.py
f_actions_temp = open('.\\o8g\\Scripts\\actions_temp.py', 'wb')
f_actions = open('.\\o8g\\Scripts\\actions.py', 'rb')
f_actions_import = open('.\\internal\\imports\\actions_import.py', 'rb')
shutil.copyfileobj(f_actions_import, f_actions_temp)
shutil.copyfileobj(f_actions, f_actions_temp)
f_actions_temp.close()
f_actions.close()
os.remove('.\\o8g\\Scripts\\actions.py')
os.rename('.\\o8g\\Scripts\\actions_temp.py', '.\\o8g\\Scripts\\actions.py')
print(">> actions.py prepared")

#autoscripts.py
f_autoscripts_temp = open('.\\o8g\\Scripts\\autoscripts_temp.py', 'wb')
f_autoscripts = open('.\\o8g\\Scripts\\autoscripts.py', 'rb')
f_autoscripts_import = open('.\\internal\\imports\\autoscripts_import.py', 'rb')
shutil.copyfileobj(f_autoscripts_import, f_autoscripts_temp)
shutil.copyfileobj(f_autoscripts, f_autoscripts_temp)
f_autoscripts_temp.close()
f_autoscripts.close()
os.remove('.\\o8g\\Scripts\\autoscripts.py')
os.rename('.\\o8g\\Scripts\\autoscripts_temp.py', '.\\o8g\\Scripts\\autoscripts.py')
print(">> autoscripts.py prepared")

#customscripts.py
f_customscripts_temp = open('.\\o8g\\Scripts\\customscripts_temp.py', 'wb')
f_customscripts = open('.\\o8g\\Scripts\\customscripts.py', 'rb')
f_customscripts_import = open('.\\internal\\imports\\customscripts_import.py', 'rb')
shutil.copyfileobj(f_customscripts_import, f_customscripts_temp)
shutil.copyfileobj(f_customscripts, f_customscripts_temp)
f_customscripts_temp.close()
f_customscripts.close()
os.remove('.\\o8g\\Scripts\\customscripts.py')
os.rename('.\\o8g\\Scripts\\customscripts_temp.py', '.\\o8g\\Scripts\\customscripts.py')
print(">> customscripts.py prepared")

#events.py
f_events_temp = open('.\\o8g\\Scripts\\events_temp.py', 'wb')
f_events = open('.\\o8g\\Scripts\\events.py', 'rb')
f_events_import = open('.\\internal\\imports\\events_import.py', 'rb')
shutil.copyfileobj(f_events_import, f_events_temp)
shutil.copyfileobj(f_events, f_events_temp)
f_events_temp.close()
f_events.close()
os.remove('.\\o8g\\Scripts\\events.py')
os.rename('.\\o8g\\Scripts\\events_temp.py', '.\\o8g\\Scripts\\events.py')
print(">> events.py prepared")

#generic.py
f_generic_temp = open('.\\o8g\\Scripts\\generic_temp.py', 'wb')
f_generic = open('.\\o8g\\Scripts\\generic.py', 'rb')
f_generic_import = open('.\\internal\\imports\\generic_import.py', 'rb')
shutil.copyfileobj(f_generic_import, f_generic_temp)
shutil.copyfileobj(f_generic, f_generic_temp)
f_generic_temp.close()
f_generic.close()
os.remove('.\\o8g\\Scripts\\generic.py')
os.rename('.\\o8g\\Scripts\\generic_temp.py', '.\\o8g\\Scripts\\generic.py')
print(">> generic.py prepared")

#meta.py
f_meta_temp = open('.\\o8g\\Scripts\\meta_temp.py', 'wb')
f_meta = open('.\\o8g\\Scripts\\meta.py', 'rb')
f_meta_import = open('.\\internal\\imports\\meta_import.py', 'rb')
shutil.copyfileobj(f_meta_import, f_meta_temp)
shutil.copyfileobj(f_meta, f_meta_temp)
f_meta_temp.close()
f_meta.close()
os.remove('.\\o8g\\Scripts\\meta.py')
os.rename('.\\o8g\\Scripts\\meta_temp.py', '.\\o8g\\Scripts\\meta.py')
print(">> meta.py prepared")

#octgnAPI.py
shutil.copyfile('.\\internal\\imports\\octgnAPI.py', '.\\o8g\\Scripts\\octgnAPI.py')
print(">> octgnAPI.py copied")

print("*** PREP finished ...")