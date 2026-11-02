# Design review: Right Headphone & Microphone Daughter Board

Datasheet-level review of the schematic and layout by CopperPilot's independent review agent (`validate`). Severity: **P0** must be fixed before fabrication, **P1** should be fixed, **P2** worth a look.

Result: **0 P0**, **1 P1**, **2 P2**.

## P1

### P1.1 Hysteresis networks R23-R28 heavily load high-impedance nodes /V_REF_HI and /DET_IN, shifting thresholds by 503 mV and leaving only 38.2 mV unplug release margin

**Parts:** U1, U2, U3, R12, R13, R14, R16, R23, R24, R25, R26, R27, R28 · **Nets:** /V_REF_HI, /V_REF_LO, /DET_IN, /U1_INP, /U2_INP, /U3_INP, /MIC_SEL, /HP_DET_N

The window-comparator reference divider R13 (22k) + R14 (100k) + R16 (22k) has an unbuffered Thevenin source impedance of R13 || (R14 + R16) = 18.64 kOhm at /V_REF_HI, while the filtered sensing node /DET_IN has an unplugged source impedance of R11 (470R) + R1 (2.2k) + R12 (10k) = 12.67 kOhm. Because the positive-feedback hysteresis networks for U1 (R23=2.2k, R24=100k to /HP_DET_N), U2 (R25=2.2k, R26=100k to /MIC_SEL), and U3 (R27=2.2k, R28=100k to /MIC_SEL) use 100 kOhm feedback resistors that are only 5.5x to 8x larger than these source impedances, the hysteresis currents load /V_REF_HI and /DET_IN directly instead of dropping primarily across R23/R25/R27 (2.2k). Consequently, /V_REF_HI shifts by 503 mV between /MIC_SEL=LOW (2.365 V) and /MIC_SEL=HIGH (2.868 V), and when unplugging a CTIA headset (starting from U1 OUT=0 V, /MIC_SEL=HIGH), R23+R24 (102.2 kOhm to GND) pulls /DET_IN down to 2.966 V and /U1_INP to 2.902 V against /V_REF_HI = 2.864 V, leaving only 38.2 mV of release margin on U1 and 94.0 mV on U2 (any parallel leakage <= 68 kOhm on /HS_MIC_DET latches the circuit permanently in the plugged-in state).

**Evidence:** thin-laptop-cm5-audio_right.kicad_sch lines 3038-3502, 7458-8005, 8756-9421; KCL nodal analysis at VCC=3.3 V with U1_OUT=0 V and U2/U3_OUT=Hi-Z (R17=10k): V(/V_REF_HI)=2.8639 V, V(/DET_IN)=2.9659 V, V(/U1_INP)=2.9021 V (margin = 2.9021 - 2.8639 = +38.2 mV), V(/U2_INP)=2.8719 V (margin = 2.9659 - 2.8719 = +94.0 mV); TI TLV7041 datasheet (SLVSE13) input bias current I_B = 2 pA typ allows 10x higher hysteresis impedance

**Suggested fix:** Increase hysteresis resistor pairs by 10x (R24, R26, R28 = 1 MOhm and R23, R25, R27 = 22 kOhm) and/or reduce reference divider impedance (R13 = 2.2 kOhm, R14 = 10 kOhm, R16 = 2.2 kOhm) so /V_REF_HI and /DET_IN remain stiff across comparator output states.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

## P2

### P2.1 Non-switched TRRS jack J1 (PJ-320D) derives plug detection (/HP_DET) solely from CTIA Sleeve bias, causing false unplug events when a headset hardware mic-mute switch opens

**Parts:** J1, U1, R12, R4 · **Nets:** /HS_MIC_DET, /DET_IN, /HP_DET_N, /HP_DET

J1 (PJ-320D) is a 4-terminal TRRS receptacle without an isolated mechanical tip-detect switch, and comparator U1 derives /HP_DET (J2.7 to CM5 GPIO24) exclusively from /DET_IN on the CTIA Sleeve terminal (J1.1 /HS_MIC_DET). If a user connects a 4-pole CTIA headset equipped with an inline mechanical mic-mute switch and engages mute (opening the microphone circuit on J1.1), or connects a 4-pole audio line input with high DC impedance (>15 kOhm) on Sleeve, /HS_MIC_DET rises to +3.3 V (/DET_IN = 2.966 V > /V_REF_HI), causing U1 to release /HP_DET HIGH and signaling a false headphone unplug to the host while the headphones remain inserted.

**Evidence:** thin-laptop-cm5-audio_right.kicad_sch lines 2554-2635 (J1 PJ-320D 4-pin symbol), lines 3038-3122 (U1 TLV7041DBVR); lcsc.pretty/AUDIO-SMD_PJ-320D-1.kicad_mod lines 206-237 (only 4 signal pads: 1=Sleeve, 2=Ring2, 3=Ring1, 4=Tip); for R_sleeve > 15 kOhm, V(/U1_INP) > V(/V_REF_HI) = 2.864 V -> /HP_DET goes HIGH

**Suggested fix:** Use a 5-pin or 6-pin 3.5mm TRRS receptacle with an isolated normally-closed or normally-open mechanical tip switch for /HP_DET (U1), reserving Sleeve impedance sensing (U2/U3) strictly for /MIC_SEL multiplexer control.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P2.2 Unbalanced AC source impedance (2.2 kOhm vs 100 Ohm) and double mic-bias loading on pseudo-differential headset mic path degrade FFC CMRR to 6.8 dB

**Parts:** U4, R21, R22, C20, R8, R9, J2 · **Nets:** /HS_MIC_MUX, /HS_REF_MUX, /MIC_P, /MIC_N

When U4 (TS5A23159DGSR) selects the external CTIA headset microphone (/MIC_SEL=HIGH, NO1->COM1 and NO2->COM2), the positive leg (/MIC_P on J2.5) is driven through R1 (2.2k) || R_mic (~2.2k) = 1.1 kOhm in series with transient-protection resistor R21 (1 kOhm), C10 (2.2 uF), C13 (2.2 uF), and R8 (100R), presenting an AC source impedance of ~2.2 kOhm. In contrast, the pseudo-differential negative reference leg (/MIC_N on J2.6) connects U4.4 (NO2, /HS_REF_MUX) directly to AC ground via C20 (2.2 uF) with no series resistor matching R21 + (R1 || R_mic), presenting only R9 = 100 Ohm AC source impedance. When terminated into the main-board ES8388 differential bias resistors R51=2.2 kOhm and R52=2.2 kOhm (spec.yaml line 552), this 2.2 kOhm vs 100 Ohm mismatch converts 45.7% of any common-mode noise coupled along the 45 mm FFC cable (J2) or ground bounce between boards into a differential microphone signal (CMRR = 6.8 dB) and introduces an additional 6.6 dB signal attenuation across R21 and R51.

**Evidence:** thin-laptop-cm5-audio_right.kicad_sch lines 3608-3707, 6160-6235, 8520-8713; spec.yaml line 552 (main-board R51=2.2k/R52=2.2k bias network on /MIC_P and /MIC_N); AC divider at 1 kHz: V_P/V_cm = 2200/(2200+2200) = 0.500 vs V_N/V_cm = 100/(2200+100) = 0.0435, differential conversion = 0.4565 (-6.8 dB)

**Suggested fix:** Add a series impedance-matching resistor (~1.8 kOhm to 2.2 kOhm) between C20.1 and /HS_REF_MUX (U4.4) to balance R21 + (R1 || R_mic), and reduce R21 from 1 kOhm to 220 Ohm (which still limits peak C10 discharge current into D8 BAT54HT1G to 15 mA while reducing signal loss).

**Status:** open. Agree, disagree or have a better fix? Open an issue.
