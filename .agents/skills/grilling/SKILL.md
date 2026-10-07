---
name: grilling
description: Stress-test a SherloCAN feature, platform decision, or architecture before implementation.
source: https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling
---

Interview the user until shared understanding is reached. Map decisions as a design tree.
Ask each currently unblocked decision frontier in one round, number the questions, and provide a recommended answer worded so "yes" accepts it.
Find technical facts from the repository, documentation, hardware specifications, or tools yourself; do not ask the user for facts that can be researched.
Do not implement the grilled feature until the user confirms shared understanding.

SherloCAN additions:
- For CAN/J2534/OpenPort changes, explicitly cover evidence integrity, active-vs-passive bus behavior, bitrate/protocol assumptions, failure handling, and hardware acceptance.
- For platform/release changes, cover exact OS/build/architecture, runtime versions, offline installation, driver architecture, rollback, and acceptance criteria.
- Record settled material decisions in docs/decisions before implementation.
