# ADR: Windows 8.1 x64 build 9600 target

Status: ACCEPTED FOR DEVELOPMENT; HARDWARE ACCEPTANCE PENDING

Target machine:
- Windows 8.1 x64
- NT version 6.3
- build 9600

Runtime policy:
- Maintain a dedicated Win8.1 release lane.
- Use a pinned CPython line that officially supports Windows 8.1; Python 3.12 is the last Python family whose current documentation explicitly directs Windows 8.1 users to it.
- Do not use Node.js on the target laptop; ship prebuilt frontend assets.
- Build an offline wheelhouse matching Windows x64 and the selected CPython ABI.
- J2534/OpenPort DLL architecture must match the Python process.
- Do not label the lane VERIFIED until it boots and passes acceptance on the physical build-9600 laptop.

Acceptance:
1. offline setup succeeds;
2. app starts and /health passes;
3. OpenPort provider/DLL discovery works;
4. SD wizard works end-to-end without destructive formatting API;
5. imported log Evidence/SHA-256 path works;
6. controlled J2534 device/channel/capture test passes on vehicle.
