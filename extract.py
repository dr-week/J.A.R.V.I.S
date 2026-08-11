import re

with open('scripts/devloop.py', 'r', encoding='utf-8') as f:
    content = f.read()

imports = '''
from core.board_io import (
    parse_frontmatter, dump_frontmatter, issue_path, load_issue, save_issue,
    list_issues, sort_key, sort_pair, is_unblocked, open_issues, owner_norm,
    append_note, unchecked_task_lines, utc_now
)
from core.feedback_log import (
    load_feedback, post_feedback, feedback_for_owner, render_feedback_md
)
from core.board_snapshot import (
    pick_for_owner, rebuild_board, make_snapshot, write_live_plan_file, refresh_code_map
)
'''

# 1. Add imports after `from helpers.issue_lane_verify import verify_issue`
content = content.replace(
    "from helpers.issue_lane_verify import verify_issue",
    "from helpers.issue_lane_verify import verify_issue\n" + imports
)

# 2. Block 1: `def utc_now` down to `def cmd_who` (excluding cmd_who)
s1 = content.find("def utc_now() -> str:")
e1 = content.find("def cmd_who(_: argparse.Namespace) -> None:")
if s1 != -1 and e1 != -1:
    content = content[:s1] + content[e1:]

# 3. Block 2: `def make_snapshot` down to `def cmd_refresh` (excluding cmd_refresh)
s2 = content.find("def make_snapshot() -> dict[str, Any]:")
e2 = content.find("def cmd_refresh(_: argparse.Namespace) -> None:")
if s2 != -1 and e2 != -1:
    content = content[:s2] + content[e2:]

with open('scripts/devloop.py', 'w', encoding='utf-8') as f:
    f.write(content)
