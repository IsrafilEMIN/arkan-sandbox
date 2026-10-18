# 04: Refuse requests for other host names

**Role:** needs-triage
**Closed:** no
**Priority:** 3
**Blocked by:** None (can start immediately)

**What to build:** `stock serve` answers a request whatever its `Host` header says. So a web page that the tablet opens could use DNS rebinding to point its own domain at the shop computer, then read `/`, `/items.json` and the files under `/exports`. Decide if this matters for the shop. If it does, answer only requests whose host is this computer's address or name, and give any other request a 404 or a 421.

**Touches:** the web module.

Found in the security review of tablet ticket 02. The risk was already on `main` for `/` and `/items.json`; ticket 02 adds the exports to what is exposed.
