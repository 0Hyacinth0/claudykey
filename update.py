"""
ClaudyKey Updater
=================
Downloads the latest code from GitHub and updates local files.
Preserves: env/, config/, assets/templates/ (user data)
"""
import os
import sys
import io
import zipfile
import shutil
import urllib.request

REPO_URL = "https://github.com/0Hyacinth0/claudykey"
ZIP_URL = REPO_URL + "/archive/refs/heads/main.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# These folders/files will NOT be overwritten
PRESERVE = {
    "env",
    "config",
    os.path.join("assets", "templates"),
    ".git",
}


def should_skip(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    for p in PRESERVE:
        p_parts = p.replace("\\", "/").split("/")
        if parts[:len(p_parts)] == p_parts:
            return True
    return False


def main():
    print()
    print("=" * 50)
    print("  ClaudyKey Updater")
    print("=" * 50)
    print()
    print(f"  Repo: {REPO_URL}")
    print(f"  Local: {SCRIPT_DIR}")
    print()
    print("  This will update code files from GitHub.")
    print("  Your env/, config/, and templates are SAFE.")
    print()
    input("  Press Enter to start...")

    # Download ZIP
    print()
    print("[1/3] Downloading latest code from GitHub...")
    try:
        resp = urllib.request.urlopen(ZIP_URL)
        data = resp.read()
        print(f"       Downloaded {len(data) // 1024} KB")
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Extract
    print("[2/3] Extracting and updating files...")
    updated = 0
    skipped = 0

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        # Find the root folder name inside the zip (e.g. "claudykey-main/")
        names = zf.namelist()
        root_prefix = names[0] if names[0].endswith("/") else names[0].split("/")[0] + "/"

        for info in zf.infolist():
            if info.is_dir():
                continue

            # Strip the root folder prefix
            rel = info.filename[len(root_prefix):]
            if not rel:
                continue

            if should_skip(rel):
                skipped += 1
                continue

            dest = os.path.join(SCRIPT_DIR, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            with zf.open(info) as src, open(dest, "wb") as dst:
                dst.write(src.read())
            updated += 1
            print(f"    + {rel}")

    print()
    print(f"[3/3] Done!  Updated: {updated} files  Skipped: {skipped} (preserved)")
    print()
    print("=" * 50)
    print("  Update complete! Launch ClaudyKey.bat to run.")
    print("=" * 50)
    print()
    input("  Press Enter to exit...")


if __name__ == "__main__":
    main()
