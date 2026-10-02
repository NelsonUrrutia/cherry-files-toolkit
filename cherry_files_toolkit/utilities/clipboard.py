import shutil
import subprocess
import sys

def copy_with_system_clipboard(text: str) -> bool:
    "Copies text using the OS clipboard tool. Returns False if none is available"
    if sys.platform == "darwin":
        commands = [["pbcopy"]]
    elif sys.platform == "win32":
        commands = [["clip"]]
    else:
        commands = [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]

    for command in commands:
        if shutil.which(command[0]) is None:
            continue
        try:
            subprocess.run(command, input=text, text=True, check=True)
            return True
        except (OSError, subprocess.CalledProcessError):
            continue
    return False
