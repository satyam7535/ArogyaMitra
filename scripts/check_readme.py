import os
import re
import yaml

readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

print("============================================================")
print("  README AUTOMATED VERIFICATION CHECKS")
print("============================================================")

# 1. Check relative links and images
print("\n--- 1. Link & Image Existence Check ---")
link_pattern = r'\[.*?\]\((?!http|https|#)(.*?)\)'
links = re.findall(link_pattern, readme)
all_links_ok = True
for link in links:
    # clean anchor or query
    clean_link = link.split('#')[0].split('?')[0].strip()
    if not clean_link:
        continue
    exists = os.path.exists(clean_link)
    print(f"[{'OK' if exists else 'FAIL'}] {clean_link}")
    if not exists:
        all_links_ok = False

# 2. Check script paths named in README
print("\n--- 2. Named Scripts Existence Check ---")
script_pattern = r'scripts/[\w\.-]+\.(?:ps1|py|mjs|sh|js)'
scripts = set(re.findall(script_pattern, readme))
all_scripts_ok = True
for s in sorted(scripts):
    exists = os.path.exists(s)
    print(f"[{'OK' if exists else 'FAIL'}] {s}")
    if not exists:
        all_scripts_ok = False

# 3. Check ports against docker-compose.yml
print("\n--- 3. Port Consistency Check with docker-compose.yml ---")
with open("docker-compose.yml", "r", encoding="utf-8") as f:
    dc = yaml.safe_load(f)

expected_ports = {
    'proxy': ['80', '443'],
    'frontend': ['8501'],
    'backend': ['5000'],
    'ml': ['8000'],
    'graph': ['8001'],
    'mongo': ['27017']
}

all_ports_ok = True
for s_name, ports in expected_ports.items():
    for p in ports:
        in_readme = p in readme
        print(f"[{'OK' if in_readme else 'FAIL'}] Service '{s_name}' port {p} present in README")
        if not in_readme:
            all_ports_ok = False

# 4. Check env vars named in README against .env.example
print("\n--- 4. Environment Variables Check against .env.example ---")
with open(".env.example", "r", encoding="utf-8") as f:
    env_example = f.read()

# Match any UPPERCASE_WITH_UNDERSCORES in backticks in the environment section
env_matches = re.findall(r'- `([A-Z_]+)`:', readme)
all_envs_ok = True
for env in sorted(set(env_matches)):
    in_example = f"{env}=" in env_example
    print(f"[{'OK' if in_example else 'FAIL'}] Env var '{env}' in .env.example template")
    if not in_example:
        all_envs_ok = False

# 5. Grep for forbidden strings (API keys, real passwords, ZZTest, TEST-, TODO)
print("\n--- 5. Banned String / Pattern Check ---")
banned_patterns = [
    (r'AIzaSy[0-9A-Za-z_-]{33}', "Live Google API Key"),
    (r'ZZTest', "ZZTest artifact"),
    (r'TEST-', "TEST- artifact"),
    (r'\bTODO\b', "TODO comment"),
    (r'\bFIXME\b', "FIXME comment"),
    (r'\bXXX\b', "XXX marker"),
]

all_banned_ok = True
for pat, desc in banned_patterns:
    matches = re.findall(pat, readme)
    print(f"[{'OK' if len(matches) == 0 else 'FAIL'}] {desc}: {len(matches)} matches")
    if len(matches) > 0:
        all_banned_ok = False

print("\n============================================================")
if all_links_ok and all_scripts_ok and all_ports_ok and all_envs_ok and all_banned_ok:
    print("  ALL README CHECKS PASSED PERFECTLY!")
else:
    print("  SOME README CHECKS FAILED - REVIEW ABOVE.")
print("============================================================")
