# Nissan Qashqai J11 MR20DD — DTC P0603 / ECM power retention investigation

**Status:** investigation / unverified vehicle-specific pinout  
**Vehicle context:** Qashqai J11, 2014, MR20DD, 4WD, CVT, UK-built; factory navigation.  
**Project:** SherloCAN — evidence-first, read-only diagnostics.

> **Safety and evidence:** This dossier is a working investigation, not a verified Nissan wiring diagram. Confirm VIN-specific service documentation, IPDM part number, connector orientation and terminal numbering before probing. Do not bridge relay terminals, short power to control pins, or rely on AI-generated connector drawings.

## 1. Observed symptoms and history

- DTC **P0603** (ECM keep-alive/internal memory-related diagnostic), alongside reported **ECCS relay circuit** issues.
- Other observed messages: **chassis control system fault** and **engine signal unavailable**.
- Reported pattern: after DTC clearing, the fault does not recur until the ignition is switched OFF and then ON again.
- The **ignition shutdown / restart transition** is therefore the key capture window; this is a correlation, **not proof** of a failed IPDM or relay.
- No synchronized voltage/CAN/DTC capture or VIN-specific pinout confirmation is yet attached to this dossier.

## 2. Working system model (conceptual)

```text
Battery / charging / grounds
        |
        +--> IPDM E/R --> ECM power relay / ECCS-related power distribution --> ECM
        |        ^                                        |
        |        | ECM relay control / ignition-related signals
        |        +----------------------------------------+
        |
        +--> other vehicle loads

ECM <--> vehicle CAN <--> other controllers
```

**Important:** The diagram is functional only. It does not assert physical relay position, internal PCB architecture, connector shape, or precise feed topology.

## 3. Service-manual leads requiring VIN-specific confirmation

The earlier MR20DD service-manual review identified these **candidate** checks. Treat the numbers as **leads to verify against the correct wiring diagram and connector face view**, not as a validated pinout for this particular vehicle.

| Candidate element | Connector / terminal | Proposed check / evidence needed |
|---|---|---|
| IPDM fuse | No. 52, 15 A | Identify exact fuse in vehicle-specific layout; check both sides under appropriate conditions |
| IPDM fuse | No. 65, 5 A | Same; do not assume fuse purpose from the illustration |
| ECM relay-control circuit | ECM E57 / 121 | Confirm exact signal role and voltage-state specification |
| Corresponding IPDM circuit | IPDM F90 / 103 | Confirm continuity / harness route to ECM E57 / 121 |
| ECM ignition-related circuit | ECM E57 / 109 | Confirm expected OFF/ON voltages |
| Corresponding IPDM circuit | IPDM E38 / 19 | Confirm harness route to ECM E57 / 109 |
| ECM reference ground | ECM E57 / 128 | Confirm terminal assignment; measure voltage drop under load |

**Reported manual test-state lead (must be rechecked against the original page):**
- E57/121 relative to E57/128: approximately **0 V with ignition ON**, and approximately **battery voltage after ignition OFF plus ≥10 seconds**.
- E57/109 relative to E57/128: approximately **0 V ignition OFF**, and **battery voltage ignition ON**.

These counterintuitive control-signal values must **not** be generalized to a relay coil, IPDM output, or another variant. Confirm exact test conditions and whether connectors are connected before any measurement.

### Source leads

- MR20DD ECM power supply / ground diagnostic procedure (previously identified around ECM-145–147): https://sinref.ru/avtomobili/Nissan/004_10_00_Nissan_QASHQAI_J11_Manual_EN_4600_raznie_2_copi/292.htm
- MR20DD engine control wiring-diagram section: https://sinref.ru/avtomobili/Nissan/004_10_00_Nissan_QASHQAI_J11_Manual_EN_4600_raznie_2_copi/285.htm
- Additional Russian-language repair-manual PDF lead: https://krutilvertel.com/pdf/demo/mak/nissan-qashqai-2014.pdf

**Source quality caveat:** These are external copies / leads, not a newly authenticated VIN-specific Nissan document. The exact diagrams, edition, fuse roles and pin assignments still need manual verification.

## 4. Hypotheses (not confirmed diagnoses)

1. Intermittent ECM permanent supply or ground, especially during the power-down/keep-alive interval.
2. IPDM power relay/ECCS control path, contacts, internal driver, or feed intermittency.
3. Connector corrosion, terminal tension, harness damage, or vibration-related loss of contact.
4. Ignition-signal transition or abnormal shutdown timing.
5. ECM internal fault **only after** external supplies, grounds, control lines, and connector integrity have been validated.
6. CAN / chassis-control faults may be secondary effects of ECM reset or lost communication; capture timing before assigning causality.

## 5. Evidence-first diagnostic procedure

1. **Baseline:** record VIN, ECM and IPDM part numbers, software/calibration IDs, all DTCs and freeze-frame information. Save a timestamped report **before clearing**.
2. **Power and grounds:** test battery state, charging, main connections, engine/body grounds, ECM feed and ground voltage drop, using VIN-correct schematics and safe back-probing.
3. **Fuses:** confirm location and designation of candidate fuses 52/65, then check supply on both sides under the manual's specified conditions.
4. **Relay control:** after confirming terminal numbers and conditions, capture ECM command/relay-control signal and IPDM relay output **simultaneously**. A relay click alone is not proof of a good output.
5. **Critical sequence:** record at least several cycles: ignition ON → engine running (if safe) → OFF → wait ≥10 seconds → ON → DTC read. Preserve exact event timestamps.
6. **Correlate:** compare ECM supply voltage, relay command/output, CAN traffic disappearance/recovery, and DTC recurrence. Use oscilloscope or suitable high-rate logging for brief voltage events; a slow multimeter may miss transients.
7. **Connector/harness inspection:** check corrosion, moisture, loose contacts, wiring stress and terminal retention with power safely isolated as required.
8. **Decision:** distinguish observed failure from hypothesized root cause. Only consider ECM replacement or IPDM internal repair after manual-guided confirmation.

Do not inject power, jumper contacts, or probe unidentified terminals. Follow vehicle electrical safety precautions.

## 6. SherloCAN investigation workflow

**OBSERVE:** note ignition state, symptoms, DTCs, ECU communication state.  
**RECORD:** collect read-only CAN logs, scanner reports, and external oscilloscope / voltage traces with common time markers.  
**CORRELATE:** align ignition OFF/ON, relay-control changes, ECM power, CAN dropouts and P0603 reappearance.  
**TEST:** compare repeated cycles and known-good baseline where available; distinguish no-data from 0 V.  
**EXPLAIN:** generate an evidence-backed report listing observations, candidate causes, unresolved assumptions and next checks.

### Proposed event markers

`IGN_ON`, `ENGINE_START`, `ENGINE_STOP`, `IGN_OFF`, `ECM_POWER_DROP`, `RELAY_COMMAND_CHANGE`, `CAN_LOSS`, `CAN_RECOVERY`, `DTC_P0603_PRESENT`, `DTC_CLEAR`, `MEASUREMENT_UNAVAILABLE`.

### Proposed trace columns

`timestamp_monotonic`, `source`, `signal`, `value`, `unit`, `sample_rate`, `ignition_state`, `measurement_point`, `confidence`, `notes`.

**Data integrity:** keep raw captures immutable, store source/clock-offset metadata, mark manually inserted events, and never invent missing samples or inferred pin voltages.

## 7. Technical illustration / UI skill applications

Reference: https://github.com/jakubkrehel/skills/tree/main/skills

- **teardown:** conceptual exploded IPDM assembly and *verified* external connector views; mark any internal PCB/relay placement as illustrative.
- **state-machine:** diagnostic state viewer (OFF / ON / running / shutdown wait / restart / DTC read), with measured vs expected signals.
- **better-layout:** single synchronized view for wiring, voltage traces, CAN and DTC.
- **better-colors:** semantic colors for verified data, assumptions, warnings, supply/ground/control; do not encode meaning by color alone.
- **better-typography / better-writing:** legible connector IDs and unambiguous measurement instructions.
- **better-interface / better-ui / better-accessibility:** keyboard-operable investigation dashboard with clear unknown-data states.
- **break:** stress-test UI with absent CAN data, conflicting timestamps, missing voltage channels, partial logs and very large captures.
- **variant / interface-review:** compare designs and audit regressions.

These skills improve documentation, visualization and UI quality; they **do not validate** electrical facts.

## 8. Visual materials already discussed

Two conceptual IPDM exploded-view infographics and two P0603 diagnostic posters were generated in the chat. They are **not** authoritative wiring diagrams. In particular, illustrative E8–E10/E38/F90 connector pictures, relay locations, and relay IDs must not be treated as real physical pin maps. The poster's claim that a fixed percentage of cases are resolved by supply checks is **unsupported** and must not be repeated as fact. This repository document records their concepts, **not** the image binaries.

## 9. Next evidence to collect

- VIN-correct Nissan ECM/IPDM diagrams and connector-face drawings, with edition/page numbers.
- Photo of actual IPDM label and its installed connectors; ECM label and terminal orientation.
- Exact scan report: DTC status, subcodes, freeze-frame, related ECM/IPDM/CAN faults.
- Synchronized oscilloscope: battery/ECM supply, relay control/output and relevant CAN signals across OFF → wait → ON.
- Test results and repeatability across multiple ignition cycles.

**Current conclusion:** the shutdown/restart dependency makes the ECM power-retention and relay-control sequence a high-value test target, **not** a confirmed failed relay, IPDM or ECM.
