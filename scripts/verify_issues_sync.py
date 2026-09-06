"""
Script to audit bilateral synchronization and compute definitive issue counts.
"""
import re

def audit():
    with open('essays/existence/issues_log.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    master_active = set()
    master_resolved = set()
    master_depri = set()

    for l in lines[15:85]: # Master table
        if '| Active |' in l or '| **Active** |' in l:
            m = re.search(r'ISSUE-(\d+\.\d+\w*)', l)
            if m: master_active.add(m.group(1))
        elif '| Resolved |' in l or '| **Resolved** |' in l:
            m = re.search(r'ISSUE-(\d+\.\d+\w*)', l)
            if m: master_resolved.add(m.group(1))
        elif '| Deprioritized |' in l or '| **Deprioritized** |' in l:
            m = re.search(r'ISSUE-(\d+\.\d+\w*)', l)
            if m: master_depri.add(m.group(1))

    body_resolved = []
    body_open = []
    body_depri = []

    for l in lines[85:]: # Detailed body
        if re.match(r'^\s*-\s*\[[xX]\]', l):
            m = re.search(r'ISSUE-(\d+\.\d+\w*)', l)
            if m: body_resolved.append(m.group(1))
        elif re.match(r'^\s*-\s*\[\s*\]', l):
            m = re.search(r'ISSUE-(\d+\.\d+\w*)', l)
            if m:
                if 'DEPRIORITIZED' in l.upper():
                    body_depri.append(m.group(1))
                else:
                    body_open.append(m.group(1))

    body_open_set = set(body_open)

    print('=' * 75)
    print('FINAL ISSUES LOG AUDIT & COUNT RECONCILIATION')
    print('=' * 75)
    print(f'Master Table Active ({len(master_active)}): {sorted(master_active)}')
    print(f'Detailed Body Open  ({len(body_open_set)}): {sorted(body_open_set)}')
    print(f'Master Table Deprioritized ({len(master_depri)}): {sorted(master_depri)}')
    print(f'Detailed Body Deprioritized ({len(body_depri)}): {sorted(body_depri)}')
    print('-' * 75)
    sync_ok = (master_active == body_open_set)
    print(f'Bilateral Synchronization: {"PASS (EXACT MATCH)" if sync_ok else "FAIL"}')
    if not sync_ok:
        print(f'  Difference: {master_active ^ body_open_set}')

    total_resolved_body = len(body_resolved)
    total_active_body = len(body_open)
    total_depri_body = len(body_depri)
    total_body = total_resolved_body + total_active_body + total_depri_body
    pct = (total_resolved_body / total_body) * 100

    print(f'Resolved in Body:   {total_resolved_body}')
    print(f'Active in Body:     {total_active_body}')
    print(f'Deprioritized:      {total_depri_body}')
    print(f'Total Registered:   {total_body}')
    print(f'Resolution Rate:    {pct:.2f}%')
    print('=' * 75)
    
    assert sync_ok, f"Bilateral sync failed: {master_active ^ body_open_set}"
    assert len(master_active) == 15, f"Expected 15 active frontiers, got {len(master_active)}"
    print("ALL ASSERTIONS PASSED: 15 active frontiers, 100% bilateral synchronization.")

if __name__ == '__main__':
    audit()
