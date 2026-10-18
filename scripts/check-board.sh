#!/usr/bin/env bash
# usage: check-board.sh [repo-root]
# Checks that TODO.md (the board) and the tickets under .scratch/ agree.
# Rules: the ## Board section of docs/agents/issue-tracker.md. Exits 1 on any problem.
set -eu

root="${1:-$(git -C "$(dirname "$0")" rev-parse --show-toplevel)}"
board="$root/TODO.md"
[ -f "$board" ] || { printf 'check-board: no TODO.md in %s\n' "$root" >&2; exit 2; }

roles=" needs-triage needs-info ready-for-agent ready-for-human wontfix "
types=" research prototype grilling task "
problems=0
fail() { printf 'TODO.md:%s: %s\n' "$1" "$2"; problems=$((problems + 1)); }

# card fields, by card index
c_line=() c_name=() c_lane=() c_tick=() c_nn=() c_feat=() c_tags=() c_path=() c_refs=()
declare -A by_path=() by_ref=()

trim() { local s="$1"; s="${s#"${s%%[![:space:]]*}"}"; printf '%s' "${s%"${s##*[![:space:]]}"}"; }

# "05" or "arkan-flow 05" -> "arkan-flow 05"; prints nothing if malformed
qualify() {
	local ref="$1" home="$2"
	if [[ $ref =~ ^[0-9]{2}$ ]]; then printf '%s %s' "$home" "$ref"
	elif [[ $ref =~ ^[a-z0-9-]+\ [0-9]{2}$ ]]; then printf '%s' "$ref"
	fi
}

# comma list of refs -> sorted qualified list, or "none"; returns 1 if a ref is malformed
canon_refs() {
	local list="$1" home="$2" out=() r q
	[ "$list" = none ] && { printf none; return 0; }
	IFS=, read -ra parts <<<"$list"
	for r in "${parts[@]}"; do
		q="$(qualify "$(trim "$r")" "$home")"
		[ -n "$q" ] || return 1
		out+=("$q")
	done
	printf '%s\n' "${out[@]}" | sort -u | paste -sd, - | sed 's/,/, /g'
}

# the ticket's **Blocked by:** line before its first ## heading, as a ref list
ticket_refs() {
	local file="$1" line text
	while IFS= read -r line; do
		[[ $line == '## '* ]] && break
		if [[ $line == '**Blocked by:**'* ]]; then
			text="${line#'**Blocked by:**'}"
			text="${text//\`/}"
			text="$(trim "${text,,}")"
			[[ $text == none* ]] && { printf none; return 0; }
			# refs end at a note: "(...)", " — ...", or ". ..."
			text="${text%%(*}"; text="${text%% —*}"; text="${text%%. *}"; text="${text%.}"
			trim "$text"
			return 0
		fi
	done <"$file"
	printf missing
}

# pass 1: read lanes and cards
mapfile -t lines <"$board"
lanes=() lane="" n=${#lines[@]} i=0
while [ $i -lt $n ]; do
	line="${lines[$i]}" ln=$((i + 1))
	i=$((i + 1))
	case "$line" in
		'## '*) lane="${line#'## '}"; lanes+=("$lane"); continue ;;
		'# '* | '') continue ;;
	esac
	[ -n "$lane" ] || { fail $ln "text above the first lane: $line"; continue; }
	if [[ ! $line =~ ^-\ \[([ x])\]\ (.+)$ ]]; then
		fail $ln "not a card (cards are '- [ ] ...' with one indented note line): $line"
		continue
	fi
	tick="${BASH_REMATCH[1]}" body="${BASH_REMATCH[2]}"
	# peel trailing #tags and the due date off the title
	tags=() title="$body"
	while :; do
		last="${title##* }"
		if [[ $last == '#'* ]]; then tags=("${last#'#'}" "${tags[@]}")
		elif [[ $last =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ && ${title% *} == *' 📅' ]]; then title="${title% *}"
		else break
		fi
		title="${title% *}"
	done
	name="$body"
	nn="" feat="${tags[0]:-}"
	if [[ $title =~ ^([0-9]{2}):\ (.+)$ ]]; then nn="${BASH_REMATCH[1]}"; fi
	[ -n "$nn" ] && name="$feat $nn: ${BASH_REMATCH[2]}" || name="$feat: $title"
	name="card \"$name\""
	k=${#c_line[@]}
	c_line+=("$ln") c_name+=("$name") c_lane+=("$lane") c_tick+=("$tick") c_nn+=("$nn")
	c_feat+=("$feat") c_tags+=(" ${tags[*]:1} ") c_path+=("") c_refs+=("")

	# the note line
	path=""
	note="${lines[$i]:-}" shape="'\`<path>\` · blocked by: <refs, or none>'"
	if [[ ! $note =~ ^[[:space:]]+[^[:space:]] ]]; then
		fail $ln "$name: no note line $shape under it"
	else
		i=$((i + 1))
		if [[ $note =~ ^[[:space:]]+\`([^\`]+)\`\ ·\ blocked\ by:\ (.+)$ ]] &&
			c_refs[$k]="$(canon_refs "${BASH_REMATCH[2]}" "$feat")"; then
			path="${BASH_REMATCH[1]}" c_path[$k]="$path"
		else
			fail $ln "$name: note line must be $shape, got: $(trim "$note")"
			c_refs[$k]=""
		fi
	fi
	if [[ ${lines[$i]:-} =~ ^[[:space:]]+[^[:space:]] ]]; then
		fail $ln "$name: more than one note line"
		while [[ ${lines[$i]:-} =~ ^[[:space:]]+[^[:space:]] ]]; do i=$((i + 1)); done
	fi

	# title, tags, path shape
	is_spec=0
	[[ ${c_tags[$k]} == *' spec '* ]] && is_spec=1
	if [ $is_spec = 1 ]; then
		[ -z "$nn" ] || fail $ln "$name: a #spec card has no number"
		[ -z "$path" ] || [ "$path" = ".scratch/$feat/spec.md" ] || fail $ln "$name: a #spec card points at .scratch/$feat/spec.md"
	elif [ -z "$nn" ]; then
		fail $ln "$name: title must start with '<NN>: '"
	else
		[ -z "$path" ] || [[ $path == ".scratch/$feat/issues/$nn-"*.md ]] || fail $ln "$name: path must be .scratch/$feat/issues/$nn-<slug>.md, got $path"
	fi
	[[ $feat =~ ^[a-z0-9-]+$ && -d "$root/.scratch/$feat" ]] || fail $ln "$name: first tag must be #<feature-slug>, a .scratch/ directory"
	nrole=0 ntype=0
	for t in ${c_tags[$k]}; do
		if [[ $roles == *" $t "* ]]; then nrole=$((nrole + 1))
		elif [[ $types == *" $t "* ]]; then ntype=$((ntype + 1))
		elif [ "$t" != spec ]; then fail $ln "$name: unknown tag #$t"
		fi
	done
	[ $nrole -le 1 ] || fail $ln "$name: more than one #<role> tag"
	[ $nrole = 1 ] || [ $ntype = 1 ] || [ $is_spec = 1 ] || fail $ln "$name: no #<role> tag"

	# the file
	if [ -n "$path" ]; then
		if [ ! -f "$root/$path" ]; then fail $ln "$name: has no ticket ($path is not a file)"
		elif [ -n "${by_path[$path]:-}" ]; then fail $ln "$name: second card for $path"
		else by_path[$path]=$k
		fi
	fi
	[ -n "$nn" ] && by_ref["$feat $nn"]=$k
done

[ "${lanes[*]:-}" = "Backlog Todo Done" ] || fail 1 "lanes must be '## Backlog', '## Todo', '## Done' in that order, got: ${lanes[*]:-none}"

# every ticket and spec has a card
while IFS= read -r f; do
	rel="${f#"$root"/}"
	[ -n "${by_path[$rel]:-}" ] || { printf '%s: ticket has no card on the board\n' "$rel"; problems=$((problems + 1)); }
done < <(find "$root/.scratch" -path '*/issues/*.md' -o -name spec.md 2>/dev/null | sort)

# pass 2: blocked by and the lane rule
for k in "${!c_line[@]}"; do
	ln="${c_line[$k]}" name="${c_name[$k]}" path="${c_path[$k]}" refs="${c_refs[$k]}"
	[ -n "$path" ] && [ -f "$root/$path" ] && [ -n "$refs" ] || continue
	raw="$(ticket_refs "$root/$path")"
	if [ "$raw" = missing ]; then
		[[ ${c_tags[$k]} == *' spec '* ]] && want=none || { fail $ln "$name: $path has no **Blocked by:** line"; continue; }
	elif ! want="$(canon_refs "$raw" "${c_feat[$k]}")"; then
		fail $ln "$name: cannot read the **Blocked by:** line in $path ('$raw')"; continue
	fi
	# the note lists only the open blockers: drop those whose card is in Done
	if [ "$want" != none ]; then
		IFS=, read -ra wl <<<"$want"
		open=()
		for b in "${wl[@]}"; do
			b="$(trim "$b")" bk="${by_ref[$b]:-}"
			[ -n "$bk" ] && [ "${c_lane[$bk]}" = Done ] || open+=("$b")
		done
		want=none
		[ ${#open[@]} = 0 ] || want="$(printf '%s\n' "${open[@]}" | paste -sd, - | sed 's/,/, /g')"
	fi
	[ "$refs" = "$want" ] || fail $ln "$name: blocked by '$refs' but $path says '$want' (its open blockers)"

	# lane rule: Done if closed; else Todo if ready; else Backlog
	if [ "${c_tick[$k]}" = x ]; then expect=Done
	else
		ready=1 why=""
		[[ ${c_tags[$k]} == *' spec '* ]] && { ready=0; why="a #spec card is never ready"; }
		if [ $ready = 1 ] && [ "$refs" != none ]; then
			IFS=, read -ra bl <<<"$refs"
			for b in "${bl[@]}"; do
				b="$(trim "$b")" bk="${by_ref[$(trim "$b")]:-}"
				if [ -z "$bk" ]; then fail $ln "$name: blocker '$b' has no card"; ready=0; why="blocker $b has no card"
				elif [ "${c_lane[$bk]}" != Done ]; then ready=0; why="blocker $b is open"
				fi
			done
		fi
		if [ $ready = 1 ] && [[ ${c_tags[$k]} != *' ready-for-agent '* && ${c_tags[$k]} != *' ready-for-human '* ]]; then
			# wayfinder tickets carry a type, not a role
			wf=0
			for t in $types; do [[ ${c_tags[$k]} == *" $t "* ]] && wf=1; done
			[ $wf = 1 ] || { ready=0; why="role is not ready-for-agent or ready-for-human"; }
		fi
		[ $ready = 1 ] && expect=Todo why="ready" || expect=Backlog
	fi
	if [ "${c_lane[$k]}" != "$expect" ]; then
		if [ "$expect" = Done ]; then fail $ln "$name: ticked, so it belongs in Done, not ${c_lane[$k]}"
		elif [ "${c_lane[$k]}" = Done ]; then fail $ln "$name: in Done but not ticked"
		else fail $ln "$name: belongs in $expect ($why), not ${c_lane[$k]}"
		fi
	fi
done

if [ $problems -gt 0 ]; then printf 'check-board: %s problem(s)\n' "$problems"; exit 1; fi
printf 'check-board: ok (%s cards)\n' "${#c_line[@]}"
