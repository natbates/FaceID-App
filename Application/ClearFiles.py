import os

def clear_directory(directory):
    """Clears all files and directories within the given directory."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            clear_directory(item_path)
            os.rmdir(item_path)

def refresh():
    """Clears images, profile images, and passwords directories."""
    directories = ["Passwords", "ProfileImages", "images"]
    dir = os.getcwd()
    for directory in directories:
        print(dir+"/"+directory+" Cleared")
        clear_directory(dir+"/"+directory)

    os.remove("trainer.yml")

refresh()