# Material client runtime result — PASS

2026-09-09, fresh stage `isolated-runtime/material-client-20260909-072449-528`. The full client compiled and resolved 109 dependencies; the native run passed **7,773 assertions**, exited 0 and completed Gradle in **1m51s**. The candidate has subsequently been installed through the separate scoped deployment; this file records test evidence, not a survival playthrough.

## Exact identities

- Candidate 0.5.0: `8DF80E5C7E4B447F651696A9383A1487B26F557A67D6263DEAFA3805BC675D91`.
- Catalog (299 recipes): `31F344D33295A70F4CC19C1F38B56C604DD13965C7E77E7EC701BC3EFAD4AD45`.
- Content: `2F56C071A584FAFAE4EE59F6ED8AE87CEAFBD851E0EE9F87F4E89D30942A693B`.
- `material-client-report.json`: `43A94194ED1A8DB58E8D142995BBC8FCE2E3A699571F8426659B58B8AE88D67B`.
- Log: `client-launch.log`; `MATERIAL_CLIENT_RENDER_PASS` at line 7437, successful build at line 7459.
- Physical mod JARs: **241**, including all six server-held originals. Loaded mod IDs: **338**; these are intentionally distinct counts.
- Renderer: NVIDIA GeForce RTX 4090, OpenGL 4.6.0 / NVIDIA 610.88, LWJGL 3.3.3+5.

## Native measured coverage

All 74 component item models were present, baked and used their configured stitched textures. All 25 fluid source/flow pairs were linked, bucketless and used the expected native fluid type/tint; 50 still/flow sprites were checked. All 41 geology/placer models retained 258 quads. The applied production Radiance redirect was found on the actual loaded Create class and its Refined Radiance branch returned false. No world or server connection was opened.

Four actual 1280×720 framebuffer captures, each after 120 frames (480 total), were visually inspected by the lead agent. They are native Minecraft renders, not AI-generated artwork or replacement images:

| File under `material-client-screenshots/` | SHA-256 |
| --- | --- |
| `01-geology-blocks.png` | `2BAEB3CDA1BBAC90B9D791CF5DEF7CA830260DA80878A3D87441362AAE713875` |
| `02-material-items-a.png` | `4014CA0CE174B976145344134DACD0A0FD36876E0A927CF6F5F64D2150FB5969` |
| `03-material-items-b.png` | `F28807814703AD4EB6CEAFD5B44C59DE49BED074D5B60DF801C4A4A78A8E4D45` |
| `04-tank-fluids.png` | `DEA7EE741A2DB2F996DE5B1B1C7573B52F3D9723692D8868AB02576B7725768A` |

Some component icons are intentionally functional gray placeholders using existing textures, not missing sprites or finished bespoke artwork. Separate source/package verification passed 563 asset byte comparisons (one existing Gradle-excluded research resource omitted deliberately) and preserved all 42 approved PNGs unchanged.

## First-launch setup and failed predecessor

The predecessor `material-client-20260909-070642-400` compiled but reached accessibility onboarding and produced unusable white captures. The parent observed its render thread in native GL drawing via Iris and stopped only the positively identified isolated client process. It ended after 7m20s without a render PASS. This does not prove the orientation screen was the only cause.

The successful **new** profile seeded exactly `onboardAccessibility:false` followed by LF; initial seed SHA-256 `FBEC202E13E01A12E7D56027F1245C9FC941CF176681640D56EBBB47CBA4963B`. The option was verified against native Minecraft and checked in the running client. All other settings retained native defaults. No live options/accounts, authentication/privacy changes, automatic screen dismissal or UI interception were used. The old profile and failed evidence were not overwritten.

## Limits

This proves scoped native item/fluid rendering and the merged Radiance branch, not physical tanks, a thrown-entity conversion, Shadow Steel behavior, powered factory operation, real-player manual burner/hammer use, survival balance or multiplayer. Material recipe-manager and Lithosphere A/B results are independently documented in `MATERIAL_PROCESSING_ACCEPTANCE.md`. Gold placer sediment selection remains an explicit TODO. Do not relaunch this completed evidence stage.
