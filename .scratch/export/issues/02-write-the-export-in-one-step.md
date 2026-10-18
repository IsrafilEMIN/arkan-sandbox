# 02: Write the export in one step

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** `stock export` writes over today's CSV in place. Since tablet ticket 02, the accountant can download that file from the tablet. If she downloads it while an export runs, she can get an empty or half-written CSV. Write the new export to a temporary file the tablet does not list, then move it into place in one step.

**Touches:** the export module.

Found in the code review of tablet ticket 02. The in-place write is older than that ticket.
