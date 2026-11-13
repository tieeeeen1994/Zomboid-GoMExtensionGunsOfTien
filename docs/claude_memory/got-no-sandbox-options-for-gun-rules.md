---
name: got-no-sandbox-options-for-gun-rules
description: Guns of Tien gameplay rules decided by the gun (e.g. .22 subsonic racking) get no sandbox option
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8cd76b94-854b-482b-8478-5b292a15f86b
  modified: 2026-11-13T04:34:46.503Z
---

In Guns of Tien, a rule that follows from the gun itself (whether a round cycles it, racking) is just implemented,
with no sandbox option to turn it off. User, 2026-11-13: "why is there a sandbox option? NO OPTION. the gun decides
it." (the .22 LR Subsonic rack rule: self-loaders rack, revolvers / manual actions untouched).

**Why:** the behaviour is a fact of the gun, not a preference; an option adds clutter. ZomboidFixesB42's "every
feature has an option" convention does not carry over to GoT.
**How to apply:** for GoT ammo/gun behaviour, decide from the gun (shadow `base` item in the profile) and ship it
without an option; only add an option when the user asks. Related: [[follow-gom-patterns]].
