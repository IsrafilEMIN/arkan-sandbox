#!/usr/bin/env bash
# usage: link-agents.sh [--check]
# Links ~/.agents/AGENTS.md and ~/.agents/skills/* into every agent that cannot read ~/.agents itself.
# Creates missing links only. Reports copies, conflicts and dangling links; never deletes anything.
set -eu

check=0
case "${1:-}" in
	--check) check=1 ;;
	"") ;;
	*) printf 'usage: link-agents.sh [--check]\n' >&2; exit 64 ;;
esac

home="${HOME:?HOME is not set}"
canon="$home/.agents"
problems=0

# relative target when both paths are under $HOME (matches the existing ../../.agents/... links), else absolute
rel() {
	target="$1" link_dir="$2"
	case "$link_dir/" in
		"$home"/*)
			sub="${link_dir#"$home"}" up=""
			while [ -n "$sub" ]; do up="../$up"; sub="${sub%/*}"; done
			printf '%s%s\n' "$up" "${target#"$home"/}"
			;;
		*) printf '%s\n' "$target" ;;
	esac
}

link() {
	target="$1" path="$2"
	if [ -L "$path" ]; then
		if [ "$(realpath "$path" 2>/dev/null)" = "$(realpath "$target")" ]; then
			return
		fi
		printf 'CONFLICT %s -> %s (expected %s)\n' "$path" "$(readlink "$path")" "$target"
		problems=1
	elif [ -e "$path" ]; then
		if diff -rq "$path" "$target" >/dev/null 2>&1; then
			printf 'COPY %s (identical to %s, replace it with a link)\n' "$path" "$target"
		else
			printf 'COPY %s (differs from %s, merge it first)\n' "$path" "$target"
		fi
		problems=1
	elif [ "$check" = 1 ]; then
		printf 'MISSING %s\n' "$path"
		problems=1
	else
		ln -sn "$(rel "$target" "$(dirname "$path")")" "$path"
		printf 'linked %s\n' "$path"
	fi
}

# global instructions: one link per agent home that exists. an agent that is not installed gets nothing.
for agent_home in "$home/.claude:CLAUDE.md" "${CODEX_HOME:-$home/.codex}:AGENTS.md" \
	"$home/.pi/agent:AGENTS.md" "${DSH_HOME:-$home/.dsh}:AGENTS.md"; do
	dir="${agent_home%:*}"
	if [ -d "$dir" ]; then link "$canon/AGENTS.md" "$dir/${agent_home##*:}"; fi
done

# skills: claude code is the only agent that cannot read ~/.agents/skills.
# claude_builtin: skills claude code ships itself; ~/.agents holds them for the other agents only.
claude_builtin=" simplify "
mirror="$home/.claude/skills"
mkdir -p "$mirror"
for skill in "$canon"/skills/*/; do
	name="$(basename "$skill")"
	case "$claude_builtin" in *" $name "*) continue ;; esac
	link "$canon/skills/$name" "$mirror/$name"
done

# a skill removed from ~/.agents leaves a dangling link behind
for path in "$mirror"/*; do
	if [ -L "$path" ] && [ ! -e "$path" ] && case "$(readlink "$path")" in *.agents/*) true ;; *) false ;; esac; then
		printf 'DANGLING %s (its skill is gone from %s/skills)\n' "$path" "$canon"
		problems=1
	fi
done

for skill in "$canon"/skills/*/; do
	name="$(basename "$skill")"
	yaml="$skill/agents/openai.yaml"
	if [ ! -f "$yaml" ]; then
		printf 'NO-OPENAI-YAML %s/agents/openai.yaml\n' "$canon/skills/$name"
		problems=1
		continue
	fi
	manual=0 implicit_off=0
	grep -q '^disable-model-invocation:[[:space:]]*true' "$skill/SKILL.md" 2>/dev/null && manual=1
	grep -q '^[[:space:]]*allow_implicit_invocation:[[:space:]]*false' "$yaml" && implicit_off=1
	if [ "$manual" != "$implicit_off" ]; then
		printf 'POLICY-MISMATCH %s (disable-model-invocation and allow_implicit_invocation disagree)\n' "$yaml"
		problems=1
	fi
done

[ "$problems" = 0 ] && printf 'ok\n'
exit "$problems"
