# 02: Download exports from the tablet

**Role:** ready-for-agent
**Closed:** no
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** the accountant comes in on Fridays and wants the CSV exports on her laptop. Right now I copy them onto a USB stick. Let the tablet page do it instead, so she can get them from anything on the shop wifi: a link on the home page to `/exports`, a page there that lists every file in the exports folder (newest first), and a link for each file that downloads it from `/exports/<file name>`.

**Touches:** the web module.

- [ ] the home page links to `/exports`
- [ ] `/exports` lists the files in the exports folder, newest first, each one a link
- [ ] `/exports/<file name>` downloads that file as CSV, saved under its own name
