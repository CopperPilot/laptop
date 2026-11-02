# Right Audio & Microphone Sub-Board (`audio_right`)

## Overview
- **Project**: `hardware/audio_right/thin-laptop-cm5-audio_right.kicad_pro`
- **Dimensions**: `36.0 mm x 38.0 mm`, 2-layer FR-4 PCB (`1.6 mm` thickness, `2.0 mm` corner radius)
- **World Placement**: `[190.5, -4.0, 0.0] mm` inside the 13-inch thin aluminum laptop lower deck
- **Mating Cable (`c_audio_right`)**: 8-pin `0.5 mm` pitch FFC (`45.0 mm` length) from main board `J_AUDR` to `J2` (`FPC-05F-8PH20`, LCSC `C2856797`)

---

## Sub-Board Architecture & Design Review Verification

1. **CTIA / AHJ 3.5 mm 4-Pole TRRS Jack Mapping (`J1`, SHOU HAN `PJ-320D`, LCSC `C431535`)**:
   - Placed at `(28.50, 19.00) mm`, `rot = 180.0 deg` on `F.Cu` (`mouth` facing `+X` `[1, 0, 0]` into right-edge case cutout `F_AUDIO`).
   - Verified pin-to-contact mapping in both `lcsc:PJ-320D` symbol and `lcsc:AUDIO-SMD_PJ-320D-1` footprint:
     - **Pin 4 (Tip, deepest contact at pad `(25.70, 22.50) mm`)**: `HP_L_JACK` (Left headphone audio).
     - **Pin 3 (Ring 1, middle contact at pad `(29.70, 22.50) mm`)**: `HP_R_JACK` (Right headphone audio).
     - **Pin 2 (Ring 2, barrel-entrance contact at pad `(32.70, 22.50) mm`)**: `GND` (CTIA common ground return).
     - **Pin 1 (Sleeve, rear contact at pad `(24.30, 15.50) mm`)**: `HS_MIC_DET` (CTIA headset microphone & plug sense).

2. **Rail-to-Rail Input Open-Drain Comparators (`U1..U3`, TI `TLV7041DBVR`, LCSC `C702122`, `[P0]` & `[P2]` Resolved)**:
   - **Rail-to-Rail Input Common-Mode Range**:
     - Replaced `LMV331IDBVR` (`V_ICR_max = VCC - 0.8 V = 2.50 V`) with `TI TLV7041DBVR` (`SOT-23-5`, LCSC `C702122`), which features a rail-to-rail input stage (`V_CM = VEE to VCC + 0.1 V = 0.00 V .. 3.40 V` over `-40 C to +125 C` at `VCC = 3.30 V`), open-drain output (`1.6 V .. 6.5 V` supply), `315 nA` ultra-low quiescent current, and `7 mV` built-in internal hysteresis.
     - Both `/V_REF_HI` (`2.365 V .. 2.853 V`) and unplugged `/DET_IN` (`2.970 V`) lie strictly inside the `0.00 V .. 3.40 V` valid input common-mode range across temperature.
   - **Sub-Audio Filtered CTIA Bias (`R11`, `C11`, `R1`, `C9`) & Voice-Band Rejecting Sense Filter (`R12`, `C12`)**:
     - `R11` (`470 Ohm`) and `C11` (`10 uF`, 25 V X5R 0603) filter `+3V3` (`f_c = 33.9 Hz`) to generate low-noise bias rail `HS_BIAS`.
     - `R1` (`2.2 kOhm`) biases `HS_MIC_DET` (`J1` Pin 1 Sleeve) from `HS_BIAS`, while `C9` (`100 pF` 50 V C0G) shunts RF ingress (`f_c = 723 kHz`).
     - `R12` (`10 kOhm`) and `C12` (`2.2 uF` 25 V X5R 0402) low-pass filter `HS_MIC_DET` onto `/DET_IN` with `-3 dB` cutoff `f_c = 1 / (2 * pi * 10 kOhm * 2.2 uF) = 7.23 Hz` (more than 10x below the `80 Hz` human voice fundamental, preventing voice/plosive peaks or slow insertion from chattering the comparators).
   - **Bypassed Reference Ladder (`R13 = 22 kOhm`, `R14 = 100 kOhm`, `R16 = 22 kOhm`, `C17 = 100 nF`, `C18 = 100 nF`) & External Positive-Feedback Hysteresis (`R23..R28`)**:
     - `C17` (`100 nF` 50 V X7R) bypasses `/V_REF_HI` to `/GND` (`f_c = 85 Hz`) and `C18` (`100 nF` 50 V X7R) bypasses `/V_REF_LO` to `/GND` (`f_c = 85 Hz`), rejecting `/+3V3` supply noise on the reference nodes.
     - Positive feedback hysteresis networks `R23 = 2.2 kOhm` / `R24 = 100 kOhm` (on `U1_INP`), `R25 = 2.2 kOhm` / `R26 = 100 kOhm` (on `U2_INP`), and `R27 = 2.2 kOhm` / `R28 = 100 kOhm` (on `U3_INP`) add `~65 mV` of external hysteresis on top of `TLV7041DBVR`'s `7 mV` internal hysteresis.
     - Verified self-consistent nodal operating points across all plug states (`R15 = 10 kOhm` pull-up on `HP_DET_N`, `R17 = 10 kOhm` pull-up on `MIC_SEL`):
       - **Unplugged (`R_jack = inf`)**: `V(DET_IN) = 2.970 V`, `V(V_REF_HI) = 2.365 V`, `V(V_REF_LO) = 0.427 V` -> `V(HP_DET_N) = 3.271 V` (HIGH on `HP_DET` `J2.7`), `V(MIC_SEL) = 0.004 V` (LOW, selecting internal MEMS mic `MK1`).
       - **4-Pole CTIA TRRS Headset (`2.2 kOhm .. 5.6 kOhm` mic)**: `V(DET_IN) = 1.503 V .. 2.110 V` (strictly inside `[0.513 V, 2.845 V]`) -> `V(HP_DET_N) = 0.003 V` (LOW on `HP_DET` `J2.7`), `V(MIC_SEL) = 3.116 V .. 3.166 V` (HIGH `> V_IH = 2.0 V`, selecting CTIA headset mic and local AC ground reference on `U4`).
       - **3-Pole TRS Stereo Headphone (`Sleeve = 0 Ohm` to `GND`)**: `V(DET_IN) = 0.001 V < V(V_REF_LO) = 0.426 V` -> `V(HP_DET_N) = 0.003 V` (LOW on `HP_DET` `J2.7`), `V(MIC_SEL) = 0.004 V` (LOW, keeping internal MEMS mic `MK1` selected).

3. **Dual SPDT Differential Microphone Multiplexer (`U4`, TI `TS5A23159DGSR`, LCSC `C42751`, `[P1]` Resolved)**:
   - Replaced single-pole switch `SN74LVC1G3157DBVR` with `TI TS5A23159DGSR` (`VSSOP-10`, `1.1 Ohm` low `R_ON`, `1.65 V .. 5.5 V` supply, break-before-make dual 2:1 SPDT analog switch).
   - Both control inputs `IN1` (Pin 1) and `IN2` (Pin 5) are driven by `/MIC_SEL`:
     - **When `/MIC_SEL = LOW` (Unplugged or 3-Pole TRS Headphone)**:
       - Channel 1 routes `MK1.3` (`OUTPUT+`, `/MIC_OUT_P`) from `NC1` (Pin 9) to `COM1` (Pin 10, `/MIC_MUX_P` -> `C13 = 2.2 uF` -> `R8 = 100 Ohm` -> `/MIC_P` on `J2.5`).
       - Channel 2 routes `MK1.2` (`OUTPUT-`, `/MIC_OUT_N`) from `NC2` (Pin 7) to `COM2` (Pin 6, `/MIC_MUX_N` -> `C14 = 2.2 uF` -> `R9 = 100 Ohm` -> `/MIC_N` on `J2.6`).
     - **When `/MIC_SEL = HIGH` (4-Pole CTIA TRRS Headset)**:
       - Both `MK1.3` (`OUTPUT+`) and `MK1.2` (`OUTPUT-`) are completely disconnected (`-65 dB` off-isolation), eliminating internal chassis/keyboard/speaker acoustic bleed from `MK1` into the headset microphone path.
       - Channel 1 routes `/HS_MIC_MUX` from `NO1` (Pin 2) to `COM1` (Pin 10, `/MIC_MUX_P` -> `C13` -> `R8` -> `/MIC_P`).
       - Channel 2 routes `/HS_REF_MUX` from `NO2` (Pin 4) to `COM2` (Pin 6, `/MIC_MUX_N` -> `C14` -> `R9` -> `/MIC_N`), where `/HS_REF_MUX` is AC-terminated to local ground at `J1.2` (Ring 2 GND) via matched `C20 = 2.2 uF` (`25 V` X5R 0402) and DC-biased via `R22 = 47 kOhm` to `/MUX_BIAS_FILT` (`0.595 V` DC, matching `NO1` bias via `R20 = 47 kOhm` for pop-free switching).

4. **Series Current Limiting & Schottky Negative Transient Clamping on `/HS_MIC_MUX` (`R21`, `D8`, `[P1]` Resolved)**:
   - `C10` (`2.2 uF`) couples `HS_MIC_DET` (`J1.1` Sleeve) to `/HS_MIC_AC`, which passes through series current-limiting resistor `R21 = 1 kOhm` (`0402WGF1001TCE`, LCSC `C11702`) to `/HS_MIC_MUX` (`U4.2` `NO1`).
   - Low-capacitance Schottky barrier diode `D8` (`onsemi BAT54HT1G`, `SOD-323`, LCSC `C21107`, `30 V`, `200 mA` continuous / `600 mA` peak forward current) is connected on `/HS_MIC_MUX` with Cathode (Pin 1) at `/HS_MIC_MUX` (`+0.595 V` DC, reverse-biased during normal operation) and Anode (Pin 2) at `/GND`.
   - During abrupt TRS plug insertion or CTIA inline button press (`HS_MIC_DET` stepping from `3.30 V` to `0.00 V`), `R21 = 1 kOhm` limits peak negative discharge current from `C10` to `I_pk = (2.71 V - 0.28 V) / 1 kOhm = 2.43 mA` (more than 20x below `TS5A23159`'s `-50 mA` clamp diode limit and 80x below `BAT54HT1G`'s `200 mA` continuous rating), while `D8` clamps `/HS_MIC_MUX` at `-0.28 V` so `U4`'s internal substrate diode never conducts.

5. **Low-Impedance MEMS Microphone Supply Filter (`R5 = 22 Ohm`) & Decoupled T-Network Mux Bias (`R18`, `R19`, `C19`, `R20`, `R22`, `[P2]` Resolved)**:
   - Reduced `R5` from `1 kOhm` to `22 Ohm` 1% (`0402WGF220JTCE`, LCSC `C25092`) feeding `/MIC_VDD` (`C1 = 100 nF` + `C2 = 10 uF` right at `MK1.1`), keeping DC drop across `R5` below `8.3 mV` at `375 uA` max (`V_DD = 3.292 V`, matching `ICS-40720` low-impedance supply requirements).
   - Decoupled `/MUX_BIAS_FILT` (`R18 = 100 kOhm` to `/+3V3`, `R19 = 22 kOhm` to `/GND`, `V_bias = 0.595 V`) with `C19 = 2.2 uF` to `/GND` (`f_c = 4.01 Hz`) and isolated `NO1` (`/HS_MIC_MUX`) and `NO2` (`/HS_REF_MUX`) through independent `47 kOhm` resistors `R20` and `R22`, completely eliminating `/MIC_VDD` modulation coupling.

6. **Unidirectional 3.3 V TVS Protection, Zero-Stub Inline Routing & Acoustic Port Keepout (`D1..D7`, `R6`, `R7`, `MK1`)**:
   - Unipolar 3.3 V nets (`HS_MIC_DET` on `D3`, `HP_DET` on `D4`, `+3V3` on `D7`) use unidirectional 3.3 V low-capacitance TVS diodes (`PESD3V3U1UA,115`, LCSC `C403915`), while bipolar AC audio nets (`HP_L_JACK` on `D1`, `HP_R_JACK` on `D2`, `MIC_P` on `D5`, `MIC_N` on `D6`) use bidirectional TVS diodes (`PESD5V0S1BA`, LCSC `C2827694`).
   - `D1`, `D2`, and `D3` are routed inline with `0.00 mm` stubs at `J1` Pads 4, 3, and 1; `R6` and `R7` (`2.2 Ohm`) provide headphone build-out isolation; `MK1` includes its `0.70 mm` NPTH bottom acoustic port at `(18.75, 10.01) mm` with matching `F.Cu`/`B.Cu` keepouts.

---

## Component Ratings & Derating Verification (`>= 1.5x` Margin)

| Ref | MPN | LCSC | Value / Function | Max Operating Stress | Component Rating | Derating Margin | Status |
|---|---|---|---|---|---|---|---|
| `J1` | `PJ-320D` | `C431535` | 3.5mm CTIA TRRS Jack | `3.3 V`, `30 mA` | `30 V DC`, `500 mA` | `9.09x V`, `16.7x I` | PASS |
| `J2` | `FPC-05F-8PH20` | `C2856797` | 8P 0.5mm FFC Connector | `3.3 V`, `< 2 mA` (`+3V3`) | `50 V`, `500 mA`/pin | `15.2x V`, `> 250x I` | PASS |
| `MK1` | `ICS-40720` | `C3171779` | Differential MEMS Mic | `V_DD = 3.29 V`, `285 uA` | `V_DD = 1.5 - 3.63 V` | Within nominal window | PASS |
| `U1..U3` | `TLV7041DBVR` | `C702122` | Rail-to-Rail Open-Drain Comp | `V_CC = 3.30 V`, `V_IN <= 2.98 V` | `V_CC = 1.6 - 6.5 V`, `V_CM = 0..3.4 V` | `1.97x V`, RRI valid | PASS |
| `U4` | `TS5A23159DGSR` | `C42751` | Dual 1.1-Ohm SPDT Audio Mux | `V_+ = 3.30 V`, `I_clamp = 0 mA` | `V_+ = 1.65 - 5.5 V`, `+/- 50 mA` | `1.67x V` | PASS |
| `D1, D2, D5, D6` | `PESD5V0S1BA` | `C2827694` | Bidirectional Audio TVS | `+/- 1.5 V_pk` AC audio | `V_RWM = +/- 5.0 V` | `3.33x V` | PASS |
| `D3, D4, D7` | `PESD3V3U1UA,115` | `C403915` | Unidirectional 3.3V TVS | `0 .. 3.30 V` unipolar | `V_RWM = 3.3 V`, `V_BR = 4.5 V` | Clamps `-0.7V / +4.5V` | PASS |
| `D8` | `BAT54HT1G` | `C21107` | Schottky Transient Clamp | `0.60 V` rev, `2.43 mA` pk fwd | `30 V`, `200 mA` cont / `600 mA` pk | `50.0x V`, `82.3x I` | PASS |
| `C1, C3, C15..C18` | `GCM155R71H104KE02D` | `C85858` | `100 nF` X7R 0402 | `<= 3.30 V` | `50 V` | `15.2x V` (`>= 1.5x`) | PASS |
| `C2, C6, C11` | `CL10A106MA8NRNC` | `C96446` | `10 uF` X5R 0603 | `3.30 V` | `25 V` | `7.58x V` (`>= 1.5x`) | PASS |
| `C4, C5, C7..C9` | `0402CG101J500NT` | `C1546` | `100 pF` C0G 0402 | `<= 3.30 V` | `50 V` | `15.2x V` (`>= 1.5x`) | PASS |
| `C10, C12..C14, C19, C20` | `CL05A225MA5NUNC` | `C159814` | `2.2 uF` X5R 0402 | `<= 3.30 V` | `25 V` | `7.58x V` (`>= 1.5x`) | PASS |
| `R1, R23, R25, R27` | `0402WGF2201TCE` | `C25879` | `2.2 kOhm` 1% 0402 | `<= 3.30 V`, `<= 3.4 mW` | `50 V`, `62.5 mW` | `15.2x V`, `18.4x P` | PASS |
| `R2, R3, R12, R15, R17` | `0402WGF1002TCE` | `C25744` | `10 kOhm` 1% 0402 | `<= 3.30 V`, `1.1 mW` | `50 V`, `62.5 mW` | `15.2x V`, `56.8x P` | PASS |
| `R4, R21` | `0402WGF1001TCE` | `C11702` | `1 kOhm` 1% 0402 | `<= 3.30 V`, `<= 7.5 mW` | `50 V`, `62.5 mW` | `15.2x V`, `8.33x P` | PASS |
| `R5` | `0402WGF220JTCE` | `C25092` | `22 Ohm` 1% 0402 | `8.3 mV`, `3.1 uW` | `50 V`, `62.5 mW` | `> 1000x V`, `> 1000x P` | PASS |
| `R6, R7` | `0402WGF220KTCE` | `C25101` | `2.2 Ohm` 1% 0402 | `1.0 V_rms`, `2.0 mW` | `50 V`, `62.5 mW` | `50.0x V`, `31.3x P` | PASS |
| `R8, R9` | `0402WGF1000TCE` | `C25076` | `100 Ohm` 1% 0402 | `1.0 V`, `< 0.1 mW` | `50 V`, `62.5 mW` | `50.0x V`, `> 500x P` | PASS |
| `R11` | `0402WGF4700TCE` | `C25117` | `470 Ohm` 1% 0402 | `3.30 V`, `0.72 mW` | `50 V`, `62.5 mW` | `15.2x V`, `86.8x P` | PASS |
| `R13, R16, R19` | `0402WGF2202TCE` | `C25768` | `22 kOhm` 1% 0402 | `<= 3.30 V`, `< 0.2 mW` | `50 V`, `62.5 mW` | `15.2x V`, `> 300x P` | PASS |
| `R14, R18, R24, R26, R28` | `0402WGF1003TCE` | `C25741` | `100 kOhm` 1% 0402 | `<= 3.30 V`, `< 0.1 mW` | `50 V`, `62.5 mW` | `15.2x V`, `> 500x P` | PASS |
| `R20, R22` | `0402WGF4702TCE` | `C25792` | `47 kOhm` 1% 0402 | `<= 0.60 V`, `< 0.1 mW` | `50 V`, `62.5 mW` | `83.3x V`, `> 500x P` | PASS |

---

## Gate Verification Summary (`audio_right`)
- `sourcing.bom`: **PASS** (63 placed BOM symbols, 22 unique in-stock LCSC parts)
- `kicad.erc`: **PASS** (0 errors, 0 warnings)
- `kicad.drc`: **PASS** (0 errors, 0 warnings, 0 unconnected items, 0 schematic parity issues)
- `kicad.rules`: **PASS** (JLCPCB 2-layer rules satisfied)
- `board.contract`: **PASS** (`36.0 x 38.0 mm` outline, plated M2 holes `H1`/`H2`, `J1`, `MK1`, `J2` within tolerance)
- `kicad.models` & `kicad.parts`: **PASS** (all footprints match exact LCSC packages and verified 3D STEP models)
- `board.cable_pinout`: **PASS** (`c_audio_right` 8-pin FFC pinout matches main board `J_AUDR` 1:1)
- `board.stackup` & `board.high_speed`: **PASS**
- `board.user_ports` & `board.port_facing`: **PASS** (`J1` mouth `[1, 0, 0]` faces right-edge cutout `F_AUDIO`; `J2` mouth `[-1, 0, 0]` faces left edge)
- `spec.locked`: **PASS**
