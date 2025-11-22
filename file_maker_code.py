import os

def show_directory(path, level=0):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return

    for item in items:
        item_path = os.path.join(path, item)
        indent = "    " * level
        if os.path.isdir(item_path):
            print(f"{indent}📁 {item}/")
            show_directory(item_path, level + 1)
        else:
            print(f"{indent}📄 {item}")

print("📂 Project Folder Structure Viewer")
base = os.getcwd()
print(f"Root: {base}\n")
show_directory(base)
