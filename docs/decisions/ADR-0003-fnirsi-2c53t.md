# ADR-0003: FNIRSI 2C53T integration boundary

Status: GRILL IN PROGRESS
Target: FNIRSI 2C53T only

## Established facts
- Dual-channel oscilloscope, 50 MHz analog bandwidth, 250 MS/s advertised sample rate, 1 Kpts record depth.
- Device supports saved waveform screenshots and export over Type-C.
- Available manual describes saved waveform artifacts as BMP images in device flash / pic folder.
- No numeric waveform/CSV/streaming-PC export is assumed until observed on the physical device.
- Firmware-update tooling is outside this integration and must not be used on the Windows 8.1 diagnostic laptop unless separately verified.

## Architecture boundary
Phase A (safe, implementable after Grill):
FNIRSI removable-storage source -> artifact inventory -> SHA-256 Evidence copy -> BMP metadata/parser -> capture record -> SherloCAN waveform evidence view.

Phase B (blocked on evidence):
If physical-device inventory reveals numeric waveform data or a documented/observed USB protocol:
numeric adapter -> canonical sampled trace -> time calibration -> CAN correlation.

## Truthfulness rules
- BMP pixels are rendered evidence, not raw ADC samples.
- Pixel-to-voltage/time reconstruction, if later offered, must be labelled DERIVED and retain calibration uncertainty.
- CAN-to-FNIRSI alignment is not VERIFIED from file timestamps alone.
- Never infer 250 MS/s effective sampling for a saved screenshot; it is an instrument capability, not proof of the saved artifact's sample grid.

## Acceptance
CI: fixture BMP import, malformed BMP rejection, SHA-256 preservation, no source mutation.
Win8.1: Type-C storage is readable and artifacts import offline.
Hardware: exact 2C53T artifact inventory captured; one known waveform saved/imported; displayed metadata compared to device screen.
