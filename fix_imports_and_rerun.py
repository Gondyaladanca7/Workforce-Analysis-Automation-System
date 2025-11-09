import os

# Base path (current project directory)
base_path = os.getcwd()

# Track what changes are made
fix_count = 0

# Loop through all .py files in the project
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            # Fix deprecated Streamlit rerun
            content = content.replace("st.rerun()", "st.rerun()")

            # Fix incorrect auth import
            content = content.replace("from utils.auth import", "from utils.auth import")

            # If file was changed, overwrite it
            if content != original:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path}")
                fix_count += 1

print(f"\n🎯 Auto-fix complete. {fix_count} files updated successfully.")
