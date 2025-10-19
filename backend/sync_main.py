import shutil

source = r"c:\Users\v-nikolozij\Desktop\Hackaton\backend\app\main.py"
dest = r"c:\Users\v-nikolozij\Desktop\Hackaton\backend\wsl_main_temp.py"

shutil.copy(source, dest)
print("✅ MAIN.PY PREPARED FOR WSL SYNC!")
