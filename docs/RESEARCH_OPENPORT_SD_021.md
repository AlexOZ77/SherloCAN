# Research 021 — OpenPort SD auto-discovery and import

Date: 2026-09-22

## Sources reviewed before implementation

- Tactrix states that OpenPort 2.0 can continuously log from an ECU to its built-in microSD without a PC.
- OpenECU standalone logger beta documentation states that OP2 supports microSD/SDHC formatted FAT12/FAT16/FAT32 and exposes the inserted card as a drive when OP2 is attached by USB.
- Existing OpenPort examples use logcfg.txt in the SD root and produce parameter-oriented CSV logs. OBD examples use type=obd / ISO15765 and are active diagnostic logging, not passive RAW CAN.
- OPCONFIG already solves logcfg generation from PID CSV definitions. SherloCAN should not duplicate its general PID-configurator concept.
- python-can already supplies readers for established CAN log formats including ASC, BLF, its CSV, SQLite, can-utils LOG, MF4 and TRC. SherloCAN should reuse python-can for formats it actually recognizes instead of writing duplicate parsers.
- cantools already supports candump decoding and DBC-based CAN decoding; it remains the later decode layer, not evidence ingestion.

## Team review / decision

**CAN/data:** Never choose a parser by extension alone. Tactrix parameter CSV is not a raw CAN frame log merely because it is CSV.

**Evidence:** Preserve original bytes and SHA-256 before parsing. Detection result and parser provenance must be stored separately. Unknown stays UNKNOWN.

**Windows/platform:** Detect candidate removable drives automatically, but keep manual folder selection as fallback because OP2 may expose its SD through USB in ways Windows classifies differently.

**Diagnostics:** Parameter logs can be useful evidence, but they must not be fed into First Divergence CAN-ID analysis unless converted from a verified frame-level source.

**UX:** Show three distinct classes: RAW_CAN_SUPPORTED, PARAMETER_LOG, UNKNOWN. Only RAW_CAN_SUPPORTED gets a future “Convert to SherloCAN RAW” action.

## Optimal implementation

1. Windows drive discovery using Win32 GetLogicalDrives/GetDriveTypeW, no new dependency.
2. Candidate scoring: removable drive + logcfg.txt and/or likely log files. Never claim a drive is OpenPort solely from drive type.
3. Content sniffing before parsing.
4. Recognize only conservative signatures:
   - can-utils/candump line -> RAW_CAN_SUPPORTED, parser=python-can/canutils.
   - canonical SherloCAN CSV header -> RAW_CAN_SUPPORTED, parser=sherlocan-csv.
   - parameter-oriented CSV (sample time and named signals, no CAN ID/data columns) -> PARAMETER_LOG.
   - anything else -> UNKNOWN.
5. Import always preserves immutable original + SHA-256 + detection metadata.
6. Do not auto-convert Tactrix parameter CSV to CAN frames.
7. Later add python-can conversion adapters for each positively recognized frame-level format.

## Deferred until real samples are available

Exact Tactrix standalone output naming and all CSV dialects are not treated as universal. A real SD sample from the user's OpenPort will be used to add a fixture and a verified Tactrix parameter parser.
