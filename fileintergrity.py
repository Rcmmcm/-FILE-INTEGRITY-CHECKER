import os
import hashlib
import json


HASH_FILE = 'hashes.json'
WATCH_DIRS = 'D:\\DOWNLOADS'

EXCLUDE_DIRS = [
    'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\ProgramData', 'C:\\$Recycle.Bin',
    '/proc', '/sys', '/dev', '/run', '/tmp', '/var/lib', '/var/run'
    ]



def calculate_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def scan_directory(directory):
    hash_dict = {}
    for root, _, files in os.walk(directory, topdown=True):
        if any(root.startswith(ex) for ex in EXCLUDE_DIRS):
            continue
        for name in files:
            filepath = os.path.join(root, name)
            try:
                if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
                    hash_dict[filepath] = calculate_hash(filepath)
            except Exception:
                continue
    return hash_dict


def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=4)


def compare_hashes(old, new):
    added = [f for f in new if f not in old]
    deleted = [f for f in old if f not in new]
    modified = [f for f in new if f in old and new[f] != old[f]]
    return added, deleted, modified


def main():
    print("[*] Scanning for file changes...")
    old_hashes = load_hashes()
    new_hashes = scan_directory(WATCH_DIRS)
    added, deleted, modified = compare_hashes(old_hashes, new_hashes)

    if not (added or deleted or modified):
        print("[+] No changes detected.")
    else:
        if added:
            print("[+] Added files:")
            for f in added:
                print(f"  + {f}")
        if deleted:
            print("[-] Deleted files:")
            for f in deleted:
                print(f"  - {f}")
        if modified:
            print("[!] Modified files:")
            for f in modified:
                print(f"  * {f}")

    save_hashes(new_hashes)


if __name__ == "__main__":
    main()
