#!/bin/bash
U4_GIT_TOOL_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"

[[ -d "$U4_GIT_TOOL_DIR" ]] && PATH="$U4_GIT_TOOL_DIR:$PATH"

uniq_path(){
    python - "$PATH" <<'PYTHONEOF'
import sys

paths=sys.argv[1].split(':')
ret=[]
[ret.append(i) for i in paths if i not in ret ]
sys.stdout.write(':'.join(ret))

PYTHONEOF
}

PATH="$(uniq_path)"
export PATH

unset uniq_path
echo "PATH=$PATH"
