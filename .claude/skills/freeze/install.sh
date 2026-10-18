#!/usr/bin/env bash
# usage: install.sh [--dry-run] [--uninstall]
set -eu

dry=0
uninstall=0
for arg in "$@"; do
	case "$arg" in
		--dry-run) dry=1 ;;
		--uninstall) uninstall=1 ;;
		-h | --help)
			printf 'usage: install.sh [--dry-run] [--uninstall]\n'
			exit 0
			;;
		*)
			printf 'install.sh: unknown argument: %s\n' "$arg" >&2
			exit 64
			;;
	esac
done

say() { printf '%s\n' "$*"; }

act() {
	label="$1"
	shift
	if [ "$dry" = 1 ]; then
		say "would $label"
	else
		"$@"
		say "$label"
	fi
}

skill_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
home="${HOME:?HOME is not set}"

claude_root="$home/.claude"
claude_link="$claude_root/skills/freeze"
omp_root="$home/.omp/agent"
omp_link="$omp_root/hooks/pre/freeze.ts"
pi_root="$home/.pi/agent"
pi_link="$pi_root/extensions/freeze.ts"
codex_root="$home/.codex"
codex_hooks="$codex_root/hooks.json"
codex_bak="$codex_root/hooks.json.bak-freeze"
grok_root="$home/.grok"
grok_link="$grok_root/hooks/freeze.json"
hermes_root="$home/.hermes"
hermes_link="$hermes_root/skills/freeze"
adapter_ts="$skill_dir/adapters/freeze.ts"
adapter_grok="$skill_dir/adapters/grok-hooks.json"
hermes_snippet="$skill_dir/adapters/hermes-config.yaml"

ensure_dir() {
	if [ -d "$1" ]; then
		say "skip $1 (exists)"
	else
		act "mkdir $1" mkdir -p "$1"
	fi
}

link_path() {
	target="$1"
	link="$2"
	if [ -L "$link" ]; then
		if [ "$(readlink "$link")" = "$target" ]; then
			say "skip $link (already links to $target)"
		else
			act "relink $link -> $target" ln -sfn "$target" "$link"
		fi
	elif [ -e "$link" ]; then
		say "skip $link (exists and is not a symlink)"
	else
		act "link $link -> $target" ln -s "$target" "$link"
	fi
}

unlink_ours() {
	target="$1"
	link="$2"
	if [ ! -L "$link" ]; then
		say "skip $link (not a symlink)"
	elif [ "$(readlink "$link")" != "$target" ]; then
		say "skip $link (points elsewhere)"
	else
		act "remove $link" rm -f "$link"
	fi
}

if [ "$uninstall" = 1 ]; then
	[ -d "$claude_root" ] && unlink_ours "$skill_dir" "$claude_link" || say "skip $claude_link (no $claude_root)"
	[ -d "$omp_root" ] && unlink_ours "$adapter_ts" "$omp_link" || say "skip $omp_link (no $omp_root)"
	[ -d "$pi_root" ] && unlink_ours "$adapter_ts" "$pi_link" || say "skip $pi_link (no $pi_root)"
	[ -d "$grok_root" ] && unlink_ours "$adapter_grok" "$grok_link" || say "skip $grok_link (no $grok_root)"
	[ -d "$hermes_root" ] && unlink_ours "$skill_dir" "$hermes_link" || say "skip $hermes_link (no $hermes_root)"

	if [ -d "$codex_root" ]; then
		if [ ! -f "$codex_hooks" ]; then
			say "skip $codex_hooks (missing)"
		elif ! command -v jq >/dev/null 2>&1; then
			say "skip $codex_hooks (jq not found)"
		else
			act "remove freeze entry from $codex_hooks" sh -c '
				jq '"'"'
					.hooks = (.hooks // {})
					| .hooks.PreToolUse = (
						((.hooks.PreToolUse // [])
							| map(.hooks = ((.hooks // []) | map(select((.command // "") | test("freeze-guard\\.sh") | not))))
							| map(select((.hooks | length) > 0)))
					)
					| (if ((.hooks.PreToolUse // []) | length) == 0 then del(.hooks.PreToolUse) else . end)
					| (if (.hooks | length) == 0 then del(.hooks) else . end)
				'"'"' "$1" > "$1.tmp-freeze" && mv "$1.tmp-freeze" "$1"
			' sh "$codex_hooks"
		fi
	else
		say "skip $codex_hooks (no $codex_root)"
	fi

	say "hermes: the skill link is removed; $hermes_snippet was never applied by this script"
	exit 0
fi

if [ -d "$claude_root" ]; then
	ensure_dir "$claude_root/skills"
	link_path "$skill_dir" "$claude_link"
else
	say "skip $claude_link (no $claude_root)"
fi

if [ -d "$omp_root" ]; then
	ensure_dir "$omp_root/hooks/pre"
	link_path "$adapter_ts" "$omp_link"
else
	say "skip $omp_link (no $omp_root)"
fi

if [ -d "$pi_root" ]; then
	ensure_dir "$pi_root/extensions"
	link_path "$adapter_ts" "$pi_link"
else
	say "skip $pi_link (no $pi_root)"
fi

if [ -d "$grok_root" ]; then
	ensure_dir "$grok_root/hooks"
	link_path "$adapter_grok" "$grok_link"
else
	say "skip $grok_link (no $grok_root)"
fi

if [ -d "$codex_root" ]; then
	if ! command -v jq >/dev/null 2>&1; then
		say "skip $codex_hooks (jq not found)"
	else
		if [ -f "$codex_hooks" ] && [ ! -e "$codex_bak" ]; then
			act "backup $codex_hooks -> $codex_bak" cp "$codex_hooks" "$codex_bak"
		elif [ -e "$codex_bak" ]; then
			say "skip $codex_bak (exists)"
		fi
		act "merge freeze entry into $codex_hooks" sh -c '
			entry=$(jq -n --arg cmd "$2" '"'"'{matcher: "Bash|Write|Edit|MultiEdit|NotebookEdit|apply_patch", hooks: [{type: "command", command: $cmd, timeout: 10, statusMessage: "freeze guard"}]}'"'"')
			src=$1
			[ -f "$src" ] || printf "{}\n" > "$src"
			jq --argjson entry "$entry" '"'"'
				.hooks = (.hooks // {})
				| .hooks.PreToolUse = (
					((.hooks.PreToolUse // [])
						| map(.hooks = ((.hooks // []) | map(select((.command // "") | test("freeze-guard\\.sh") | not))))
						| map(select((.hooks | length) > 0)))
					+ [$entry]
				)
			'"'"' "$src" > "$src.tmp-freeze" && mv "$src.tmp-freeze" "$src"
		' sh "$codex_hooks" "\"$skill_dir/scripts/freeze-guard.sh\" hook"
	fi
else
	say "skip $codex_hooks (no $codex_root)"
fi

if [ -d "$hermes_root" ]; then
	ensure_dir "$hermes_root/skills"
	link_path "$skill_dir" "$hermes_link"
else
	say "skip $hermes_link (no $hermes_root)"
fi

say "hermes: the skill is now linked, the hook is not applied. add $hermes_snippet to your hermes config and approve the hook on first use"
