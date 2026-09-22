# OpenPort implementation review

CAN/J2534: approve registry-first discovery and adapter isolation. Reject hard-coded Tactrix DLL paths.
Windows/platform: require x86/x64 architecture gate; use a bridge process when bitness differs.
Diagnostics: bitrate remains UNKNOWN until documented/measured; do not guess it for J11.
Safety/reliability: first hardware milestone is read-only capture and loss accounting.
UI: Adapter card must show Driver found / Device available / Architecture / Capture state separately.
QA: hardware-independent tests run in CI; OpenPort tests are a separately documented bench test.

Next increment: PE architecture inspection, J2534 DLL loader, PassThru symbol validation, Tactrix presence test, then x86 bridge if the installed driver requires it.
