# Design review: Left Dual USB-C PD & Data Daughter Board

Datasheet-level review of the schematic and layout by CopperPilot's independent review agent (`validate`). Severity: **P0** must be fixed before fabrication, **P1** should be fixed, **P2** worth a look.

Result: **0 P0**, **3 P1**, **2 P2**.

## P1

### P1.1 20V PD rail TVS clamping voltage (D6/D7 SMF24A, 38.9V) exceeds Q1/Q2 AO4407A (-30V), U1 CH224A (32V), and C15 (25V) ratings

**Parts:** D6, D7, Q1, Q2, C15, U1 · **Nets:** /J2_VBUS, /VBUS_PD

The 20V USB-C PD input (/J2_VBUS) and switched output (/VBUS_PD) are protected by unidirectional avalanche TVS diodes D6 and D7 (SMF24A, LCSC C169430), whose breakdown voltage is 26.7V-29.5V and maximum clamping voltage is V_C = 38.9V at I_PP = 5.1A. However, the series load-switch P-MOSFETs Q1 and Q2 (AO4407A, LCSC C2841482) have an absolute maximum V_DSS of -30V, the PD sink controller U1 (CH224A) has a maximum VHV rating of 32V, and the output bulk capacitor C15 (CL21A106KAYNNNE, LCSC C440198) is a 25V-rated X5R 0805 MLCC (misidentified in spec.yaml as 50V). During cable hot-plug inductive ringing or surge events on J2, D6/D7 allow rail transients up to 38.9V, overstressing C15 (+13.9V above its 25V rating; already at 80% rating at nominal 20V DC), Q1/Q2 (+8.9V above 30V V_DSS), and U1 (+6.9V above 32V VHV).

**Evidence:** thin-laptop-cm5-usb_left.kicad_sch lines 10653, 10685 (Q1, Q2 AO4407A V_DSS = -30V), lines 10849, 10875 (D6, D7 SMF24A V_RWM = 24V, V_BR = 26.7-29.5V, V_C = 38.9V @ 5.1A), line 11317 (C15 CL21A106KAYNNNE = 10uF 25V X5R 0805, Samsung voltage code A = 25V); WCH CH224A datasheet VHV max = 32V.

**Suggested fix:** Replace C15 with a 50V-rated 10uF 0805 MLCC (or 35V/50V polymer/MLCC), and replace D6/D7 (SMF24A) with flat-clamping 22V surge TVS devices (such as TI TVS2200DRVR, V_C = 27.7V, already used on the main board) or upgrade Q1/Q2 to -40V P-MOSFETs.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.2 CH224A VHV/VBUS pins use CH224K 1k series resistors (R3, R4) and PG-gated 1:1 divider (R13/R14) blocks <20V charging and under-drives Q1/Q2 at low VBUS

**Parts:** U1, R3, R4, Q1, Q2, R13, R14, C17, D9 · **Nets:** /PD_VHV, /PD_VBUS_SNS, /PD_PG_N, /PD_SW_G, /PD_SW_MID

First, U1 (CH224A, LCSC C42459160) has Pin 1 (VHV) and Pin 8 (VBUS) connected to /J2_VBUS through 1k resistors R3 and R4. Unlike the older CH224K (which uses a 3.3V shunt regulator on Pin 1 VDD requiring a 1k dropping resistor), CH224A integrates a 32V LDO on Pin 1 (VHV) and its datasheet specifies connecting VHV directly to VBUS (with 1uF C5 to GND) and shorting VBUS (Pin 8) to VHV; R3=1k drops 1V-2V during 300kbps BMC transmission on CC1/CC2, reducing vSafe5V headroom. Second, Q1/Q2 (AO4407A) are gated by U1.10 (PG) via Q3/Q4 and a 1:1 divider R13=10k / R14=10k with C17=100nF connected Gate-to-Source (/PD_SW_G to /PD_SW_MID). Because U1 is strapped for 20V (R11=120k on CFG1), PG stays high-Z on 5V-only USB-C chargers, completely blocking 5V fallback charging into the main-board BQ25798RQMR (3.6V-24V buck-boost charger). Moreover, R13=10k / R14=10k divides V_SG to 0.5 * V_J2_VBUS (making D9 BZT52C12 redundant at 20V where V_SG = 10V, while producing only V_SG = 2.15V-2.5V during 5V transitions where AO4407A V_GS(th) is -1.7V to -2.5V), and placing C17=100nF Gate-to-Source instead of Gate-to-Drain (Miller feedback to /VBUS_PD) neither linearizes dV/dt on /VBUS_PD nor allows fast fault turn-off (tau_off = R13 * C17 = 1.0ms, t_off = 1.68ms).

**Evidence:** thin-laptop-cm5-usb_left.kicad_sch lines 10427 (U1 CH224A), 11499 (R3 1k), 11525 (R4 1k), 11759 (R13 10k), 11785 (R14 10k), 11369 (C17 100nF); WCH CH224A datasheet (C42459160) Pin Description (Pin 1 VHV 32V supply, Pin 8 VBUS shorted to VHV); AO4407A datasheet (V_GS(th) = -1.7V to -2.5V, R_DS(on) rated at V_GS = -4.5V and -10V).

**Suggested fix:** Connect U1.1 (VHV) and U1.8 (VBUS) per the CH224A datasheet (0R-10R in place of R3=1k), change the R13/R14 ratio (e.g., R13=47k, R14=10k) so D9 (BZT52C12) clamps V_SG at 12V for 20V while providing V_SG >= 4.1V at 5V, and move the slew-rate control capacitor from Gate-Source to Gate-Drain of Q2.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.3 U4 (XC6216B332MR-G) upstream dropper (D3 + R12=1k + D8=BZT52C16) risks /PD_VDD_3V3 brownout at minimum vSafe5V and overloads R12 during surges

**Parts:** U4, D3, R12, D8, U3 · **Nets:** /J2_VBUS, /LDO_D3_K, /LDO_VIN, /PD_VDD_3V3

Although U4 (XC6216B332MR-G, LCSC C2891269) is a 28V-rated LDO (operating input 2.0V-28.0V, abs max 30V), its input /LDO_VIN is fed from /J2_VBUS through silicon diode D3 (1N4148WS) and series resistor R12 (1k 0603, rated 0.1W) clamped by a 16V Zener D8 (BZT52C16). During 5V startup before 20V PD negotiation completes, U1.10 (PG) is high-impedance so R5 (10k) turns ON Q3, pulling /PD_EN low through R15 (10k) and drawing 0.33mA continuously from /PD_VDD_3V3 (rising to 0.69mA if U3 ~FLT asserts low through R6=10k). The resulting drop across D3 (0.62V) and R12 (0.36V-0.69V) is 0.98V-1.31V, causing /PD_VDD_3V3 (U3.10 VPWR) to drop below TPD6S300RUKR's 3.0V minimum operating voltage when vSafe5V at J2 is <=4.3V-4.6V (USB PD vSafe5V sink min is 4.0V). Conversely, at 20V-21V PD, D8 (V_Z,min = 15.3V) draws up to 5.05mA continuously through R12 (106mW wasted), and during a 38.9V transient at D6, R12 dissipates (38.9 - 0.7 - 16.0)^2 / 1k = 0.493W (4.9x its 0.1W 0603 rating).

**Evidence:** thin-laptop-cm5-usb_left.kicad_sch lines 10552 (U4 XC6216B332MR-G), 10771 (D3 1N4148WS), 10901 (D8 BZT52C16), 11733 (R12 1k 0603WAF1001T5E 0.1W); TI TPD6S300 datasheet Section 6.3 (VPWR recommended 3.0V to 3.6V); Torex XC6216 datasheet (V_IN = 2.0V to 28.0V).

**Suggested fix:** Replace D3 with a low-V_F Schottky diode, reduce R12 from 1k to 47R-100R (for RC surge filtering only), and replace D8 (16V BZT52C16) with a 24V-27V Zener above the 21V max PD operating rail so zero Zener current flows during normal 20V operation while keeping U4 VIN below 28V.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

## P2

### P2.1 Overcurrent limit overlap between main-board U_VBUS (SY6280AAC, 1.55A min) and usb_left U2 (TPS25810RVCR, 1.70A typ / 1.85A max) collapses /+5V_USBC and /J1_VDD_3V3

**Parts:** U2, U6, U5, J4 · **Nets:** /+5V_USBC, /J1_VBUS, /J1_VDD_3V3

The 5V accessory USB-C port J1 relies on cascading main-board switch U_VBUS (SY6280AAC with R31=3.3k setting I_LIM = 1.55A min / 2.06A typ / 2.58A max) into usb_left DFP controller U2 (TPS25810RVCR with CHG=GND, CHG_HI=GND setting I_OS = 1.55A min / 1.70A typ / 1.85A max). Because SY6280AAC's minimum current limit (1.55A) is below TPS25810RVCR's typical (1.70A) and maximum (1.85A) current limits, a J1 load fault between 1.55A and 1.85A can trip upstream U_VBUS first. When U_VBUS trips, /+5V_USBC collapses, cutting input power to U2 (IN1/IN2/AUX) and to 3.3V LDO U6 (XC6206P332MR-G) which supplies /J1_VDD_3V3 (U5 TPD6S300RUKR VPWR), causing the entire J1 port controller and CC protector to brown out and reset instead of cleanly regulating the overcurrent.

**Evidence:** thin-laptop-cm5-usb_left.kicad_sch lines 10462 (U2 TPS25810RVCR CHG=GND, CHG_HI=GND), 10626 (U6 XC6206P332MR-G on /+5V_USBC); spec.yaml lines 378, 521 (U_VBUS SY6280AAC R31=3.3k: 2.06A typ / 1.55A min); TI TPS25810 datasheet Section 6.5 (I_OS = 1.55A min, 1.70A typ, 1.85A max for CHG=Low, CHG_HI=Low).

**Suggested fix:** Feed /+5V_USBC directly from the 6A /+5V rail (since U2 TPS25810RVCR already provides a precision 1.55A-1.85A current-limited switch and EN control) or lower R31 on U_VBUS so its minimum current limit exceeds 1.85A.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P2.2 Six port telemetry/control signals (R16..R21 to J3 pins 1..4, 7..8) terminate at unconnected main-board pins, preventing 45W vs 65W PD current discrimination

**Parts:** J3, U1, R16, R17, R18, R19, R20, R21 · **Nets:** Net-(J3-Pad1), Net-(J3-Pad2), Net-(J3-Pad3), Net-(J3-Pad4), Net-(J3-Pad7), Net-(J3-Pad8), /PD_PG_N, /J1_EN

Resistors R16..R21 (6x 10k 0402) route /PD_PG_N (J3.1), /U3_FLT_N (J3.2), /U5_FLT_N (J3.3), /J1_FAULT_N (J3.4), /J1_UFP_N (J3.7), and /J1_EN (J3.8) to the 16-pin FFC connector J3, while U1 (CH224A) I2C/CFG pins CFG2_SCL (U1.2) and CFG3_SDA (U1.3) are left unconnected. Per spec.yaml, mating main-board connector J_USBL leaves pins 1..4 and 7..8 uncommitted (no_connect), yet spec.yaml also states that CM5 software can override BQ25798RQMR's hardware 2.25A (45W) ILIM_HIZ limit over I2C to draw 3.25A (65W) on 65W PD contracts. Because neither CC1/CC2 PD contract telemetry nor J3.1..4/7..8 is connected to the CM5, the system has no way to detect whether an attached 20V PD adapter is rated for 2.25A (45W) or 3.25A (65W), nor can it monitor J1/J2 OVP/OCP faults or control /J1_EN.

**Evidence:** thin-laptop-cm5-usb_left.kicad_sch lines 10317 (J3), 10427 (U1.2/U1.3 no_connect), 11837-11967 (R16..R21); spec.yaml lines 346, 415-419, 518-520 (J_USBL pins 1..4 and 7..8 uncommitted/no_connect on main board).

**Suggested fix:** Either connect the J3 status/control lines (and CH224Q/I2C or CC telemetry if dynamic 3.25A scaling is desired) on the main board, or restrict BQ25798RQMR I_INDPM to <=2.25A (45W) unless a 65W source is explicitly verified.

**Status:** open. Agree, disagree or have a better fix? Open an issue.
