import { spawnSync } from "node:child_process";

const GUARD = (process.env.HOME || "") + "/.agents/skills/freeze/scripts/freeze-guard.sh";

function toAbsolute(p, cwd) {
	if (typeof p !== "string" || p.length === 0) return "";
	if (p.charAt(0) === "/") return p;
	const base = typeof cwd === "string" && cwd.length > 0 ? cwd : "/";
	return base.replace(/\/+$/, "") + "/" + p;
}

function collectPathTargets(input) {
	const out = [];
	const single = ["file_path", "path", "file"];
	for (let i = 0; i < single.length; i++) {
		const v = input[single[i]];
		if (typeof v === "string" && v.length > 0) out.push(v);
	}
	if (Array.isArray(input.paths)) {
		for (let i = 0; i < input.paths.length; i++) {
			const v = input.paths[i];
			if (typeof v === "string" && v.length > 0) out.push(v);
		}
	}
	return out;
}

function runGuard(args, input, cwd) {
	try {
		const options = { input: typeof input === "string" ? input : "", encoding: "utf8" };
		if (typeof cwd === "string" && cwd.length > 0) options.cwd = cwd;
		const res = spawnSync(GUARD, args, options);
		if (!res || res.error || typeof res.status !== "number") return { status: 0, stdout: "", stderr: "" };
		return { status: res.status, stdout: res.stdout || "", stderr: res.stderr || "" };
	} catch {
		return { status: 0, stdout: "", stderr: "" };
	}
}

function report(pi, ctx, message) {
	try {
		if (ctx && ctx.ui && typeof ctx.ui.notify === "function") {
			ctx.ui.notify(message, "info");
			return;
		}
	} catch {}
	try {
		if (pi && typeof pi.sendMessage === "function") {
			pi.sendMessage({ customType: "freeze", content: message, display: true });
			return;
		}
	} catch {}
	try {
		if (typeof console !== "undefined" && console.log) console.log(message);
	} catch {}
}

function registerFreezeCommand(pi) {
	if (!pi || typeof pi.registerCommand !== "function") return;
	try {
		pi.registerCommand("freeze", {
			description: "freeze writes to a directory: /freeze arm <dir>, /freeze disarm, /freeze status",
			handler: async function (args, ctx) {
				try {
					const cwd = ctx && typeof ctx.cwd === "string" && ctx.cwd.length > 0 ? ctx.cwd : process.cwd();
					const raw = args == null ? "" : String(args);
					const parts = raw.trim().split(/\s+/).filter(function (p) { return p.length > 0; });
					const action = parts.length > 0 ? parts[0] : "status";

					if (action === "arm") {
						if (!parts[1]) {
							report(pi, ctx, "usage: /freeze arm <dir>");
							return;
						}
						const res = runGuard(["arm", toAbsolute(parts[1], cwd)], "", cwd);
						if (res.status === 0) report(pi, ctx, "freeze: armed on " + toAbsolute(parts[1], cwd));
						else report(pi, ctx, "freeze: arm failed: " + ((res.stderr || "").trim() || ("exit " + res.status)));
						return;
					}

					if (action === "disarm") {
						const res = runGuard(["disarm"], "", cwd);
						if (res.status === 0) report(pi, ctx, "freeze: disarmed");
						else report(pi, ctx, "freeze: disarm failed: " + ((res.stderr || "").trim() || ("exit " + res.status)));
						return;
					}

					if (action === "status") {
						const res = runGuard(["status"], "", cwd);
						const line = (res.stdout || "").trim();
						report(pi, ctx, line.length > 0 ? "freeze: " + line : "freeze: none");
						return;
					}

					report(pi, ctx, "usage: /freeze arm <dir> | /freeze disarm | /freeze status");
				} catch {
					report(pi, ctx, "freeze: command failed");
				}
			},
		});
	} catch {}
}

export default function (pi) {
	if (!pi || typeof pi.on !== "function") return;

	pi.on("tool_call", function (event, ctx) {
		try {
			const input = event && event.input && typeof event.input === "object" ? event.input : {};
			const cwd = ctx && typeof ctx.cwd === "string" && ctx.cwd.length > 0 ? ctx.cwd : process.cwd();
			const targets = [];
			const raw = collectPathTargets(input);
			for (let i = 0; i < raw.length; i++) {
				const abs = toAbsolute(raw[i], cwd);
				if (abs.length > 0) targets.push(abs);
			}

			let res;
			if (targets.length > 0) {
				res = runGuard(["write"].concat(targets), "", cwd);
			} else if (typeof input.command === "string" && input.command.length > 0) {
				res = runGuard(
					["hook"],
					JSON.stringify({ tool_name: event && event.toolName, tool_input: input }),
					cwd,
				);
			} else {
				return undefined;
			}

			if (res.status === 2) {
				const reason = (res.stderr || "").trim();
				return { block: true, reason: reason.length > 0 ? reason : "blocked: target is outside the frozen directory" };
			}
			return undefined;
		} catch {
			return undefined;
		}
	});

	registerFreezeCommand(pi);
}
