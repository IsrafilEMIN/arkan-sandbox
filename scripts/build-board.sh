#!/usr/bin/env bash
# usage: build-board.sh [repo-root]
# Writes TODO.md (the board) from the tickets under .scratch/.
# Rules: the ## Board section of docs/agents/issue-tracker.md. Exits 1 on a bad ticket.
set -eu

root="${1:-$(git -C "$(dirname "$0")" rev-parse --show-toplevel)}"
board="$root/TODO.md"
[ -d "$root/.scratch" ] || { printf 'build-board: no .scratch/ in %s\n' "$root" >&2; exit 2; }

roles=" needs-triage needs-info ready-for-agent ready-for-human wontfix "
types=" research prototype grilling task "
problems=0
fail() { printf '%s: %s\n' "$1" "$2" >&2; problems=$((problems + 1)); }

trim() { local s="$1"; s="${s#"${s%%[![:space:]]*}"}"; printf '%s' "${s%"${s##*[![:space:]]}"}"; }

# ticket fields, by ticket index
t_path=() t_feat=() t_nn=() t_title=() t_role=() t_type=() t_due=() t_closed=() t_prio=() t_refs=() t_spec=()
declare -A by_ref=()

# pass 1: read each ticket's heading and the fields above its first ## heading
while IFS= read -r f; do
	rel="${f#"$root"/}" feat="${rel#.scratch/}" feat="${feat%%/*}"
	spec=0 nn=""
	if [[ $rel == */spec.md ]]; then spec=1
	else nn="${rel##*/}" nn="${nn%%-*}"
	fi
	title="" role="" type="" due="" closed="" prio="" refs=""
	while IFS= read -r line; do
		case "$line" in
			'## '*) break ;;
			'# '*) [ -n "$title" ] || title="${line#'# '}" ;;
			'**Role:**'*) role="$(trim "${line#'**Role:**'}")" ;;
			'**Type:**'*) type="$(trim "${line#'**Type:**'}")" ;;
			'**Due:**'*) due="$(trim "${line#'**Due:**'}")" ;;
			'**Closed:**'*) closed="$(trim "${line#'**Closed:**'}")" ;;
			'**Priority:**'*) prio="$(trim "${line#'**Priority:**'}")" ;;
			'**Blocked by:**'*)
				text="${line#'**Blocked by:**'}"
				text="${text//\`/}"
				text="$(trim "${text,,}")"
				# refs end at a note: "(...)", " — ...", or ". ..."
				text="${text%%(*}"; text="${text%% —*}"; text="${text%%. *}"; text="${text%.}"
				refs="$(trim "$text")"
				[[ $refs == none* ]] && refs=none
				;;
		esac
	done <"$f"

	# a ticket's heading is "# <NN>: <title>"; the card title starts with a capital
	if [ $spec = 0 ]; then
		[[ $title == "$nn: "* ]] || fail "$rel" "heading must be '# $nn: <title>'"
		title="${title#"$nn: "}"
	fi
	[ -n "$title" ] || fail "$rel" "no '# ' heading"
	title="${title^}"
	[ $spec = 1 ] || [[ $roles == *" $role "* ]] || [[ $types == *" $type "* ]] ||
		fail "$rel" "needs a **Role:** line (one of:${roles% }) or a **Type:** line (one of:${types% })"
	[ -z "$role" ] || [[ $roles == *" $role "* ]] || fail "$rel" "unknown role '$role'"
	[ -z "$type" ] || [[ $types == *" $type "* ]] || fail "$rel" "unknown type '$type'"
	[ -z "$due" ] || [[ $due =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || fail "$rel" "**Due:** must be YYYY-MM-DD, got '$due'"
	[[ $closed == yes || $closed == no ]] || fail "$rel" "needs a **Closed:** line, yes or no"
	[[ $prio =~ ^[0-9]+$ ]] || fail "$rel" "needs a **Priority:** line, a number"
	[ -n "$refs" ] || { [ $spec = 1 ] && refs=none; } || fail "$rel" "needs a **Blocked by:** line"

	k=${#t_path[@]}
	t_path+=("$rel") t_feat+=("$feat") t_nn+=("$nn") t_title+=("$title") t_role+=("$role") t_type+=("$type")
	t_due+=("$due") t_closed+=("$closed") t_prio+=("${prio:-0}") t_refs+=("$refs") t_spec+=("$spec")
	[ -n "$nn" ] && by_ref["$feat $nn"]=$k
done < <(find "$root/.scratch" -path '*/issues/*.md' -o -name spec.md 2>/dev/null | sort)

# "05" or "arkan-flow 05" -> ticket index; prints nothing if unknown
lookup() {
	local ref="$1" home="$2"
	[[ $ref =~ ^[0-9]{2}$ ]] && ref="$home $ref"
	printf '%s' "${by_ref[$ref]:-}"
}

# pass 2: the lane rule, and each ticket's blockers as ticket indexes;
# the card note keeps only the open blockers (the ticket's line is history)
t_lane=() t_block=()
for k in "${!t_path[@]}"; do
	refs="${t_refs[$k]}" ready=1 block=""
	if [ "$refs" != none ]; then
		IFS=, read -ra parts <<<"$refs"
		open=()
		for r in "${parts[@]}"; do
			r="$(trim "$r")" b="$(lookup "$r" "${t_feat[$k]}")"
			if [ -z "$b" ]; then fail "${t_path[$k]}" "blocker '$r' is not a ticket"; continue; fi
			block+=" $b"
			[ "${t_closed[$b]}" = yes ] && continue
			ready=0 open+=("$r")
		done
		t_refs[$k]=none
		[ ${#open[@]} = 0 ] || t_refs[$k]="$(printf '%s\n' "${open[@]}" | paste -sd, - | sed 's/,/, /g')"
	fi
	t_block+=("$block ")
	# lane rule: Done if closed; else Todo if ready; else Backlog
	[ "${t_spec[$k]}" = 1 ] && ready=0
	[[ ${t_role[$k]} == ready-for-agent || ${t_role[$k]} == ready-for-human || -n ${t_type[$k]} ]] || ready=0
	if [ "${t_closed[$k]}" = yes ]; then t_lane+=(Done)
	elif [ $ready = 1 ]; then t_lane+=(Todo)
	else t_lane+=(Backlog)
	fi
done

if [ $problems -gt 0 ]; then printf 'build-board: %s problem(s), TODO.md not written\n' "$problems" >&2; exit 1; fi

card() {
	local k="$1" tick=" " head="" tags
	[ "${t_lane[$k]}" = Done ] && tick=x
	[ -n "${t_nn[$k]}" ] && head="${t_nn[$k]}: "
	tags="#${t_feat[$k]}"
	[ -z "${t_role[$k]}" ] || tags+=" #${t_role[$k]}"
	[ -z "${t_type[$k]}" ] || tags+=" #${t_type[$k]}"
	[ "${t_spec[$k]}" = 0 ] || tags+=" #spec"
	[ -z "${t_due[$k]}" ] || tags+=" 📅 ${t_due[$k]}"
	printf -- '- [%s] %s%s %s\n  `%s` · blocked by: %s\n' "$tick" "$head" "${t_title[$k]}" "$tags" "${t_path[$k]}" "${t_refs[$k]}"
}

# pass 3: each lane in order of priority (lower first), then feature and number;
# then a card waits until its blockers in the same lane are above it
out="$(mktemp)"
trap 'rm -f "$out"' EXIT
{
	printf '# TODO\n'
	for lane in Backlog Todo Done; do
		printf '\n## %s\n' "$lane"
		order=()
		while IFS=$'\t' read -r _ _ _ k; do order+=("$k"); done < <(
			for k in "${!t_path[@]}"; do
				[ "${t_lane[$k]}" = "$lane" ] && printf '%s\t%s\t%s\t%s\n' "${t_prio[$k]}" "${t_feat[$k]}" "${t_nn[$k]:-00}" "$k"
			done | sort -t$'\t' -k1,1n -k2,2 -k3,3 -k4,4n
		)
		declare -A placed=()
		left=${#order[@]}
		while [ $left -gt 0 ]; do
			for k in "${order[@]}"; do
				[ -z "${placed[$k]:-}" ] || continue
				wait=0
				for b in ${t_block[$k]}; do
					[ "${t_lane[$b]}" = "$lane" ] && [ -z "${placed[$b]:-}" ] && wait=1
				done
				[ $wait = 0 ] || continue
				printf '\n'; card "$k"
				placed[$k]=1 left=$((left - 1))
				continue 2
			done
			printf 'build-board: blockers in a loop in lane %s\n' "$lane" >&2; exit 1
		done
		unset placed
	done
} >"$out"
cat "$out" >"$board"
printf 'build-board: wrote TODO.md (%s cards)\n' "$(grep -c '^- \[' "$board")"
