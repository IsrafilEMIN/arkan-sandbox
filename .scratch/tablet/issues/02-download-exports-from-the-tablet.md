# 02: Download exports from the tablet

**Role:** ready-for-agent
**Closed:** yes
**Priority:** 2
**Blocked by:** None (can start immediately)

**What to build:** the accountant comes in on Fridays and wants the CSV exports on her laptop. Right now I copy them onto a USB stick. Let the tablet page do it instead, so she can get them from anything on the shop wifi: a link on the home page to `/exports`, a page there that lists every file in the exports folder (newest first), and a link for each file that downloads it from `/exports/<file name>`.

**Touches:** the web module.

- [x] the home page links to `/exports`
- [x] `/exports` lists the files in the exports folder, newest first, each one a link
- [x] `/exports/<file name>` downloads that file as CSV, saved under its own name

## Comments

Done on branch `tablet-02`. The page lists only regular files directly in the exports folder. It leaves out subfolders, links (a link could point anywhere on the computer) and names that are not valid text. A download is looked up by name in that list, so a request can reach no other file. Anything put in the exports folder can be downloaded by anyone on the shop wifi. The DNS rebinding risk from the security review is ticket 04.
