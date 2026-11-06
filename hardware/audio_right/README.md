# Right Audio & Microphone Sub-Board (`audio_right`)

## Overview
- **Project**: `hardware/audio_right/thin-laptop-cm5-audio_right.kicad_pro`
- **Dimensions**: `36.0 mm x 38.0 mm`, 2-layer FR-4 PCB (`1.6 mm` thickness, `2.0 mm` corner radius)
- **World Placement**: `[190.5, -4.0, 0.0] mm` inside the 13-inch thin aluminum laptop lower deck
- **Mating Cable (`c_audio_right`)**: 8-pin `0.5 mm` pitch **Type-B (opposite-side / reversed-contact)** FFC ribbon (`45.0 mm` length) connecting main-board bottom-contact `J_AUDR` (`FPC-05F-8PH20`, LCSC `C2856797`, contacts `-Z`, Pad 1 at South `y=23.75 mm`, Pad 8 at North `y=20.25 mm`) 1-to-1 to `audio_right` top-contact `J2` (`FPC-05FB-8PH20`, LCSC `C2856828`, contacts `+Z`, Pad 1 at South `y=19.75 mm`, Pad 8 at North `y=16.25 mm`)

---

## Sub-Board Architecture & Design Review Verification

1. **CTIA / AHJ 3.5 mm 6-Pin Switched TRRS Jack Mapping (`J1`, XKB Connection `PJ-3701-SMT`, LCSC `C2684645`, `[P1]` Resolved)**:
   - Replaced unswitched 4-pin `PJ-320D` with 6-pin `XKB Connection PJ-3701-SMT` (LCSC `C2684645`, `lcsc:AUDIO-SMD_PJ-3701-SMT`) placed at `(28.50, 19.00) mm`, `rot = 180.0 deg` on `F.Cu` (`mouth` facing `+X` `[1, 0, 0]` into right-edge case cutout `F_AUDIO`).
   - Verified pin-to-contact mapping against the `PJ-3701-SMT` mechanical drawing and schematic (`SCHEMATIC(PLUG OUT)`):
     - **Pin 4 (Tip, `12.21 mm` deepest contact at pad `(24.02, 22.85) mm`)**: `/HP_L_JACK` (Left headphone audio).
     - **Pin 3 (Ring 1, `4.79 mm` middle contact at pad `(30.02, 22.85) mm`)**: `/HP_R_JACK` (Right headphone audio).
     - **Pin 2 (Ring 2, `7.84 mm` common return contact at pad `(32.98, 15.15) mm`)**: `/GND` (CTIA common ground return, Kelvin-sensed via `C20 = 2.2 uF` placed at `(32.30, 12.50) mm` with dedicated `F.Cu` Kelvin trace directly to `J1.2` and `R29 = 1.3 kOhm` into `/HS_REF_MUX`).
     - **Pin 1 (Sleeve, `1.81 mm` entrance contact at pad `(31.92, 22.85) mm`)**: `/HS_MIC_DET` (CTIA headset microphone & bias/sense, clamped by unidirectional 3.3 V ESD diode `D3` `PESD3V3U1UA,115`, LCSC `C403915`).
     - **Pin 5 (`/TIP_SW` at pad `(24.02, 15.15) mm`) & Pin 6 (`/GND` at pad `(26.02, 15.15) mm`)**: Isolated Normally-Closed (NC) Mechanical Tip Plug-Detect Switch (`5 VDC`, `0.5 A`, `<= 70 mOhm` closed resistance). When unplugged (`PLUG OUT`), Pin 5 is shorted to Pin 6 (`/GND`), holding `/TIP_SW = 0.000 V`. When any 3.5 mm plug is fully seated, Tip lifts insulator block `#9` to open Pin 5 from Pin 6, allowing `/TIP_SW` to charge via `R30 = 22 kOhm` (`C25768`) toward `/+2V8_ANA` (`2.80 V`) across `C23 = 2.2 uF` (`C159814`, `tau = 48.4 ms`, crossing `U1` rising threshold `V_TH+ = 2.365 V` at `t_qual = 90.1 ms` after contact bounce and Sleeve insertion wiping have completed), protected by ESD diode `D10` (`PESD3V3U1UA,115`, LCSC `C403915`).

2. **Decoupled Mechanical Headphone Plug Detection (`U1`) & Deterministic Monostable Microphone Source Selection (`U2, U3`, `3x TI TLV7041DBVR`, LCSC `C702122`, `[P1]` & `[P2]` Resolved)**:
   - **Headphone Plug Detection (`U1` driving `/HP_DET_N -> R4 = 1 kOhm -> /HP_DET` on `J2.7`)**:
     - `U1.4` (`IN-`) senses `/TIP_SW`; `U1.3` (`IN+`) senses `/U1_INP` (`V_REF_HI = 2.344 V` via `R23 = 22 kOhm` with `R31 = 1 MOhm` positive feedback to `/HP_DET_N`, giving `V_TH+ = 2.365 V` rising at `t = 90.1 ms` and `V_TH- = 2.293 V` falling, `72 mV` hysteresis).
     - `/HP_DET` is **100% independent of Sleeve microphone impedance**: inline hardware mic-mute switches (`R_sleeve = inf`), detached boom mics, or open-mic Y-splitters never cause false unplug events on `/HP_DET`.
   - **Synchronous Debounced Plug-Presence Gate (`U2`) & Deterministic 3-Pole TRS vs 4-Pole CTIA Classifier (`U3`) on `/MIC_SEL` (`R17 = 2.2 kOhm` pull-up to `/+3V3`)**:
     - Reference divider on `/+2V8_ANA` (`2.80 V`): `R13 = 2.2 kOhm`, `R14 = 10 kOhm`, `R16 = 1.3 kOhm` (`C25866`) -> `V_REF_HI = 2.344 V` (`C17 = 100 nF`), `V_REF_LO = 0.270 V` (`C18 = 100 nF`).
     - **Synchronous Plug-Presence Gate (`U2`)**: `U2.3` (`IN+`) = `/V_REF_HI` (`2.344 V`), `U2.4` (`IN-`) = `/HP_DET_N` (driven directly by `U1.1`'s debounced output with `72 mV` hysteresis). Whenever unplugged (`V_TIP_SW < 2.365 V`) or during the first `90.1 ms` of plug insertion (`/HP_DET_N = 3.30 V`), `U2.1` holds `/MIC_SEL` LOW (`0.00 V`, selecting internal MEMS mic `MK1`). Once `U1` qualifies the seated plug at `t = 90.1 ms` (`/HP_DET_N = 0.00 V`), `U2.1` releases `/MIC_SEL` synchronously with `/HP_DET_N`.
     - **Non-Loading Sleeve Sense Tap & Rail-to-Rail Clamp (`R12, C12, D11`)**:
       - Sleeve `/HS_MIC_DET` is sensed through high-impedance `R12 = 47 kOhm` (`C25792`) and `C12 = 4.7 nF` (`C1538`, `tau = 221 us << 90.1 ms`), loading the positive mic leg by `< 0.2 dB` across `20 Hz .. 20 kHz` so `/HS_MIC_MUX` (`1.29 kOhm .. 1.32 kOhm`) stays balanced within `1.5%` of `/HS_REF_MUX` (`R29 = 1.30 kOhm`).
       - `D11` (`BAV99,215`, LCSC `C2500`, `I_R < 1 nA` typ) clamps `/DET_IN` between `/GND` (Pin 1) and `/+2V8_ANA` (Pin 2) behind `R12 = 47 kOhm`, ensuring `/DET_IN` never exceeds `-0.3 V` or `+2V8_ANA + 0.3 V`.
     - **Deterministic 3-Pole TRS vs 4-Pole CTIA Selection (`U3`)**:
       - `U3.4` (`IN-`) = `/V_REF_LO` (`0.270 V`); `U3.3` (`IN+` = `/U3_INP`) is connected via `R27 = 2.2 kOhm` (`C25879`) to `/DET_IN` with `R28 = 1 MOhm` (`C26083`) hysteresis to `/MIC_SEL`.
       - **3-Pole TRS Headphones (`R_sleeve < 100 Ohm`, e.g. `0 Ohm` grounded Sleeve)**: `V_HS_MIC_DET < 0.100 V` settles on `/DET_IN` in `< 1.1 ms << 90.1 ms`. Even if `/MIC_SEL` were transiently `3.30 V`, `V_U3P(R_sleeve = 0 Ohm, MIC_SEL = 3.30 V) = 3.30 V * (47k + 2.2k) / (47k + 2.2k + 1000k) = 0.155 V < V_REF_LO (0.270 V)` (`V_TH- = 0.121 V` [`120 Ohm`], `V_TH+ = 0.283 V` [`300 Ohm`]). Thus `U3.1` deterministically holds or resets `/MIC_SEL = 0.00 V` (internal mic `MK1`) with **zero bistable lockup** on TRS contact bounce.
       - **4-Pole CTIA Headset (`680 Ohm <= R_sleeve <= 10 kOhm`, or `R_sleeve = inf` when inline hardware mute switch is open at boot, plug-in, or during capture)**: `0.568 V <= V_HS_MIC_DET <= 2.800 V -> 0.541 V <= V_U3P <= 2.823 V > V_REF_LO (0.270 V)`. Both `U2.1` and `U3.1` release `/MIC_SEL` to `3.30 V`, switching `U4` (`TS5A23159DGSR`) to the external headset microphone (`NO1/NO2`) so a muted CTIA headset never silently falls back to internal mic `MK1`.

3. **Ultra-Low-Noise 2.8 V Analog LDO & Back-Drive Protection (`U5`, TI `LP5907MFX-2.8/NOPB`, LCSC `C186700`, `R24`, `D12`, `[P1]` Resolved)**:
   - Powered from `/+3V3` with local `1 uF` input cap `C22` (`C52923`) within `1.5 mm` of `U5.1`/`U5.2` and local `1 uF` output cap `C21` (`C52923`) on `/+2V8_ANA`.
   - `R24 = 1.3 kOhm` (`C25866`) minimum preload bleeder from `/+2V8_ANA` to `/GND` (`2.154 mA`) combines with the reference dividers (`0.237 mA`) and `MK1` (`0.185 mA` min) to guarantee `>= 2.575 mA` continuous sink load on `/+2V8_ANA`, exceeding the maximum back-drive current (`(6.0 V - 2.8 V) / (2.67k || 47k) = 1.27 mA`) under external `3 V .. 6 V` faults on `J1.1` before `D3` (`PESD3V3U1UA,115`) and `D12` (`PESD3V3U1UA,115` on `/+2V8_ANA`) clamp to `/GND`.

4. **Dual SPDT Differential Microphone Multiplexer (`U4`, TI `TS5A23159DGSR`, LCSC `C42751`) & Matched Low-Leakage Silicon Clamps (`D8, D9`, `BAV99,215`, LCSC `C2500`)**:
   - Biased at `/MUX_BIAS_FILT = 0.795 V` via `R18 = 68 kOhm` (`C36871`) and `R19 = 27 kOhm` (`C25771`) from `/+2V8_ANA`, matching `MK1` (`ICS-40720`) `0.80 V` DC common-mode output within `5 mV` for clickless switching.
   - Clamped by matched ultra-low-leakage dual-series silicon diodes `D8` (on `/HS_MIC_MUX`) and `D9` (on `/HS_REF_MUX`) between `/GND` and `/+3V3`.
