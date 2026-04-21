---
description: "Add a new PayloadSender implementation for PS MultiInjector. Use when scaffolding a new sender subclass in src/payload_sender.py that follows the existing abstract base class and send(ip, port, payload_path) contract."
name: "Add Payload Sender"
argument-hint: "<sender class name> <transport or tool>"
agent: "agent"
---
Add a new payload sender implementation to PS MultiInjector.

Project references:
- [Payload sender base classes](../../src/payload_sender.py)
- [GUI sender usage](../../src/main.py)
- [Agent instructions](../../AGENTS.md)

Requirements:
- Follow the existing `PayloadSender` ABC pattern in `src/payload_sender.py`.
- Add a concrete subclass with a `send(self, ip, port, payload_path)` method.
- Keep the implementation style consistent with `TCPSender` and `SocatSender`: simple, direct, and local to the sender.
- Reuse existing error-handling conventions. If the sender needs localized user-facing errors, use `LangManager` and the translation JSON files instead of hardcoding new GUI strings in random modules.
- Avoid refactoring unrelated sender code unless required for the new sender to fit cleanly.
- If the request includes UI wiring, make the minimal matching change in `src/main.py` to expose the new sender option.
- If the request does not mention UI wiring, scaffold only the sender class and any imports or helper code it actually needs.
- Keep platform-specific behavior explicit when necessary; this project supports Linux, Windows, macOS Intel, and macOS ARM.

Implementation checklist:
- Decide whether the sender uses sockets, a subprocess, or another transport.
- Add only the imports needed by the new sender.
- Keep file-path handling based on `payload_path`; the GUI already downloads or selects the file.
- Preserve the existing public interface so the GUI can instantiate and call the sender the same way.

Expected output:
- The new sender subclass in `src/payload_sender.py`.
- Optional minimal UI wiring in `src/main.py` if requested.
- A short note about any new translation keys, external tools, or platform assumptions.
