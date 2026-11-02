# Design review: Main board

Datasheet-level review of the schematic and layout by CopperPilot's independent review agent (`validate`). Severity: **P0** must be fixed before fabrication, **P1** should be fixed, **P2** worth a look.

Result: **0 P0**, **5 P1**, **4 P2**.

## P1

### P1.1 Backlight high-side load switch Q_BL/Q_BL_EN is hard-wired ON to /+3V3, leaving /LED_ANODE continuously energized

**Parts:** Q_BL, Q_BL_EN, R63, R35, U_BL, J_BL · **Nets:** /VSYS, /VSYS_BL, /BL_SW_G, /+3V3, /LED_ANODE, /BL_PWM

Non-synchronous boost LED driver U_BL (TPS61165DBVR) has a direct DC conduction path from /VSYS_BL through inductor L3 and Schottky catch diode D1 (B16WS) to /LED_ANODE (J_BL pin 1) that remains at V(VSYS) - V_F(D1) = 5.7V to 8.3V even when CTRL (/BL_PWM) is driven low. Although P-MOSFET Q_BL (AO3401A) and N-MOSFET pre-driver Q_BL_EN (2N7002) were added to disconnect /VSYS_BL when the display is off, Q_BL_EN pin 1 (gate) is tied directly to the always-on CM5 /+3V3 rail instead of a display/backlight enable signal, and its intended gate pull-down resistor R63 (100k) is wired directly across /+3V3 to /GND. Whenever CM5 is running (/+3V3 = 3.3V), Q_BL is permanently enabled, keeping the J_BL hinge harness energized during lid closure (/LID_SNS low) and display sleep (/3V3_PER_EN low).

**Evidence:** thin-laptop-cm5.kicad_sch netlist: Q_BL_EN.1(G) = /+3V3, Q_BL_EN.2(S) = /GND, Q_BL_EN.3(D) = /BL_SW_G; R63.1 = /+3V3, R63.2 = /GND; Q_BL.2(S) = /VSYS, Q_BL.3(D) = /VSYS_BL -> L3.2 -> L3.1(/BL_SW) -> D1.2 -> D1.1(/LED_ANODE) -> J_BL.1. TI TPS61165 datasheet (SLVS790E, Section 7.3): boost topology provides no true input-to-output disconnect when CTRL is low.

**Suggested fix:** Disconnect Q_BL_EN pin 1 (gate) and R63 pin 1 from /+3V3 and connect both to /DSI_EN (U1 pin 39, GPIO8) or /3V3_PER_EN (U1 pin 38, GPIO11) so Q_BL disconnects /VSYS_BL whenever the display is disabled.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.2 Battery connector J_BAT (/VBAT_PACK and /VBAT) lacks reverse-polarity protection, TVS clamping, and hot-plug RC damping

**Parts:** J_BAT, F1, U_CHG, U_RTC, C3, C69 · **Nets:** /VBAT_PACK, /VBAT

J_BAT (S8B-PH-SM4-TB(LF)(SN), pins 1-4 /VBAT_PACK) connects the 2S2P 7.4V (8.4V max) Li-Po battery pack through fuse F1 directly to /VBAT (U_CHG BQ25798RQMR BAT pins 22-23 and U_RTC HT7530S VIN pin 3), decoupled solely by low-ESR ceramic capacitors C3 (10uF), C69 (10uF), and C57 (1uF). Unlike /VBUS_PD—which has TVS D7 (ESTVS2200DRVR) and hot-plug snubber R60 (2.2R) + C58 (1uF)—neither /VBAT_PACK nor /VBAT has a TVS clamp or RC damping network. Hot-plugging a charged 8.4V low-impedance Li-Po pack across harness inductance into low-ESR MLCCs can produce LC voltage ringing approaching or exceeding BQ25798RQMR's 20V absolute maximum rating on BAT (pins 22-23) and BATP (pin 18). Furthermore, there is no reverse-polarity protection on J_BAT; a mis-wired battery harness (-8.4V) forward-biases the substrate diodes of U_CHG (BAT abs max -0.3V) and U_RTC (VIN abs max -0.3V), destroying both ICs before F1 opens.

**Evidence:** TI BQ25798 datasheet (SLUSDV2C, Section 6.1 Absolute Maximum Ratings, p. 11 & Figure 8-1 Note 2, p. 130): BAT and BATP absolute maximum rating is -0.3V to 20V, and TI notes that hot-plugging into low-ESR ceramic capacitors requires a damping RC snubber or TVS to prevent inductive overshoot above 20V.

**Suggested fix:** Add a 12V-15V unidirectional TVS diode (clamping <19V) and a 2.2R + 2.2uF RC damping network on /VBAT, and consider an ideal-diode/reverse-blocking P-MOSFET on /VBAT_PACK.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.3 Battery fuse F1 (5A JFC1206-1500FS) is undersized for the 2S battery discharge and 5A fast-charge current budget

**Parts:** F1, J_BAT, U_CHG · **Nets:** /VBAT_PACK, /VBAT, /VSYS

F1 (JFC1206-1500FS, LCSC C136351) is a 5.0A fast-acting 1206 SMD fuse carrying all 2S battery charge and discharge current between /VBAT_PACK (J_BAT pins 1-4) and /VBAT (U_CHG BAT pins 22-23). Standard SMD chip fuses require a 0.75x continuous current derating at 25C and ~0.85x thermal derating at 60C internal enclosure ambient, limiting continuous current to 3.19A (3.75A at 25C). On battery-only discharge near low battery (6.6V, 90% buck efficiency), concurrent operation of CM5 (15W), USB-C 5V accessory port via U_VBUS (7.5W-10.3W), stereo speakers via U_AMP (4.5W), display/camera via U_3V3 (1.5W), and backlight via U_BL (3.5W) totals 32W-35W, drawing 5.39A-5.89A from the battery, while spec.yaml also specifies up to 5.0A charge current from U_CHG (100% of F1 nominal rating with zero derating margin; spec.yaml line 329 calls for a 10A fuse). Additionally, J_BAT (S8B-PH-SM4-TB, 2.0A/pin JST-PH) allocates 4 pins (8.0A) to /VBAT_PACK but only 3 pins (6.0A) to /GND.

**Evidence:** thin-laptop-cm5.kicad_sch: F1 value = 5A, LCSC = C136351 (JDTfuse JFC1206-1500FS, 5.0A 32V 1206 fast-acting fuse). Calculation: I_cont(max) = 5.0A * 0.75 * 0.85 = 3.19A vs. I_BAT(35W @ 6.6V, 90% eff) = 35W / (0.90 * 6.6V) = 5.89A and I_CHG(max) = 5.0A.

**Suggested fix:** Replace F1 with a 10A slow-blow/time-lag or high-I2t SMD fuse (such as 1206/2410 10A rated for >=6.4A derated continuous current) and cap software fast-charge current in U_CHG (REG0x03 ICHG) to <=3.6A (0.4C) to coordinate with J_BAT's 3-pin (6.0A) GND return.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.4 CM5 internal +3.3v_(Output) PMIC rail (/+3V3) is routed directly off-board to three FFC/FPC connectors without overcurrent protection

**Parts:** U1, J_AUDR, J_KB, J_TP · **Nets:** /+3V3, /GND

The system /+3V3 rail is supplied directly by the CM5 module's internal PMIC output pins U1.84 and U1.86 (+3.3v_(Output), 600mA max) and also biases U1.78 (GPIO_VREF), U_CODEC (ES8388), U_KB (TCA8418RTWR), and U_HALL (DRV5032FADBZR). Unlike the display and camera connectors (J_DSI, J_CSI), which are isolated via switched buck regulator U_3V3 (/+3V3_PER), /+3V3 is routed directly off-board onto three 0.5mm pitch flex connectors—J_AUDR pin 8 (adjacent to GND pins 9/10), J_KB pin 20 (adjacent to GND pins 21-26), and J_TP pin 2 (adjacent to GND pin 1)—without any current-limiting switch, polyfuse, or series isolation. Any FFC misalignment, cable pinch against the aluminum enclosure, or daughterboard fault shorts the CM5 onboard PMIC +3.3V output directly to GND.

**Evidence:** thin-laptop-cm5.kicad_sch net /+3V3: connects U1.84, U1.86, and U1.78 directly to off-board connectors J_AUDR.8, J_KB.20, and J_TP.2 with no current-limiting or isolating element. Raspberry Pi Compute Module 5 datasheet (RP-008180-DS, Section 2.1): +3.3V output is generated by the onboard PMIC (600mA max total).

**Suggested fix:** Power off-board flex peripherals (J_AUDR.8, J_KB.20, J_TP.2) through a current-limited load switch or power them from the dedicated 2A buck rail /+3V3_PER (or a dedicated current-limited 3.3V switch) rather than directly from CM5 U1.84/86.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P1.5 Dual +5V buck converters U_BUCK and U_BUCK2 (TPS56628DDAR) EN UVLO dividers cut off the 2S battery prematurely at 6.53V-7.10V

**Parts:** U_BUCK, U_BUCK2, R33, R34, R67, R68 · **Nets:** /VSYS, /BUCK_EN, /BUCK2_EN

U_BUCK and U_BUCK2 (TPS56628DDAR) set their EN pin UVLO thresholds (/BUCK_EN and /BUCK2_EN) from /VSYS using R33 = R67 = 100k upper resistors and R34 = R68 = 22.1k lower resistors. Per the TI TPS56628 datasheet, the EN pin has V_EN(rising) = 1.23V typ (1.28V max), V_EN(falling) = 1.13V typ (1.18V max), and an internal pull-down resistor of 400k typ (200k min) to GND. In parallel with 22.1k, the internal pull-down lowers the effective bottom resistance to 20.94k typ (19.90k min), raising the divider ratio to 5.775 typ (6.025 max). This sets the /VSYS rising turn-on threshold to 7.10V typ (7.71V worst-case max; 6.80V even ignoring the internal pull-down) and falling shut-off threshold to 6.53V typ (6.89V worst-case). Because BQ25798RQMR regulates VSYSMIN = 7.0V only when external USB-C power is present and passes /VBAT directly through its internal BATFET on battery-only operation (6.0V-8.4V), the laptop cannot cold-boot on battery below 7.10V (3.55V/cell) and shuts off abruptly at 6.53V under load, stranding 20%-35% of usable 2S Li-Po capacity.

**Evidence:** TI TPS56628 datasheet (SLVSC63A, Section 6.5, p. 5): V_EN(rising) = 1.23V typ (1.28V max), V_EN(falling) = 1.13V typ (1.18V max), R_EN_PD = 400k typ (200k min). Calculation: R_bot,eff = 22.1k || 400k = 20.94k; V_SYS(rise,typ) = 1.23V * (1 + 100k / 20.94k) = 7.10V; V_SYS(rise,max) = 1.28V * (1 + 100k / 19.90k) = 7.71V; V_SYS(fall,typ) = 1.13V * 5.775 = 6.53V.

**Suggested fix:** Increase R34 and R68 from 22.1k to 28.7k or 30.1k (with R33 = R67 = 100k) so V_SYS(fall) is ~5.65V-5.85V and V_SYS(rise) is ~6.15V-6.35V across the 6.0V-8.4V 2S battery range.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

## P2

### P2.1 Display (J_DSI) and camera (J_CSI) share a single CM5 I2C bus (/SCL0, /SDA0) while CM5 ID_SC/ID_SD and CSI0 lanes 2-3 are left unconnected

**Parts:** J_DSI, J_CSI, U1, R9, R10 · **Nets:** /SCL0, /SDA0, /+3V3_PER

Both the 22-pin MIPI DSI1 display connector (J_DSI pins 20-21) and the 22-pin MIPI CSI0 camera connector (J_CSI pins 20-21) are wired in parallel to the same CM5 I2C bus (/SCL0 on U1.80 and /SDA0 on U1.82, pulled up via R9 = 2.2k and R10 = 2.2k to /+3V3_PER), whereas CM5's second camera/display I2C bus (U1.35 ID_SC and U1.36 ID_SD) is left unconnected. Standard Raspberry Pi CM5 device-tree overlays expect separate I2C buses for the two MIPI ports; sharing one bus requires custom device-tree bindings, prevents independent bus recovery if either flex peripheral hangs SDA0/SCL0, and risks I2C address collisions. Additionally, J_CSI leaves 4-lane CSI0 pins 11, 12, 14, and 15 (U1 pins 133, 135, 139, 141 MIPI0_D2_N/P and MIPI0_D3_N/P) unconnected, limiting J_CSI to 2-lane camera modules.

**Evidence:** thin-laptop-cm5.kicad_sch: J_DSI.20 and J_CSI.20 connect to /SCL0 (U1.80); J_DSI.21 and J_CSI.21 connect to /SDA0 (U1.82); U1.35 (ID_SC), U1.36 (ID_SD), J_CSI.11-12, J_CSI.14-15, and U1.133/135/139/141 are unconnected. Raspberry Pi CM5 IO Board datasheet (RP-008182-DS): routes ID_SD/ID_SC (GPIO0/1) and SDA0/SCL0 (GPIO38/39) to separate MIPI connectors.

**Suggested fix:** Route U1.35 (ID_SC) and U1.36 (ID_SD) with 2.2k pull-ups to /+3V3_PER to one of the two MIPI connectors (J_DSI or J_CSI) so DSI1 and CSI0 operate on independent I2C buses, and route MIPI0_D2_N/P and MIPI0_D3_N/P to J_CSI pins 11-12 and 14-15 if 4-lane CSI0 support is desired.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P2.2 Input OVP/reverse-blocking FETs Q3 and Q4 (SQ2318AES-T1_BE3) lack ACDRV1 slew-rate control passives and dissipate ~1.16W at 3.25A

**Parts:** Q3, Q4, U_CHG · **Nets:** /CHG_ACDRV1, /CHG_AC_SRC, /VBUS_PD, /CHG_VBUS

U_CHG (BQ25798RQMR) pin 11 (ACDRV1, net /CHG_ACDRV1) is wired directly to the gates of Q3 and Q4 (SQ2318AES-T1_BE3, LCSC C3280170, SOT-23-3) with no series gate resistor and no gate-to-source slew-rate capacitor on /CHG_AC_SRC (contrary to spec.yaml, which describes R69 = 10R on /CHG_ACDRV1 and R60 = 100R + C82 = 10nF on /CHG_AC_SRC). Without an ACDRV1 series resistor and gate-source capacitor, Q3/Q4 (Q_g ~ 6nC) switch on rapidly into 50.2uF of nominal capacitance on /CHG_VBUS (C1, C65, C77) and /CHG_PMID (C9, C66, C67, C68) at 20V, producing large hot-plug inrush current spikes through J5 and Q3/Q4. In addition, SQ2318AES-T1_BE3 has R_DS(on) = 38mOhm max at V_GS = 4.5V, 25C (~55mOhm hot at V_ACDRV1 = 5.0V), dissipating ~0.58W per SOT-23 package (~1.16W total) at 3.25A (65W) PD input.

**Evidence:** TI BQ25798 datasheet (SLUSDV2C, Section 8.2, Figures 8-1 to 8-3, pp. 130-132): specifies a series gate resistor on ACDRV1 and gate-to-source capacitor across ACFET1/RBFET1 to limit turn-on dV/dt and inrush current. Vishay SQ2318AES datasheet: R_DS(on) = 38mOhm max at V_GS = 4.5V (25C); P_D = 3.25A^2 * 0.055Ohm = 0.58W per SOT-23.

**Suggested fix:** Add a series gate resistor (47R-100R) between U_CHG.11 (ACDRV1) and Q3.1/Q4.1 plus a 10nF-47nF capacitor + 100k resistor between the gates and common source /CHG_AC_SRC, and consider lower-R_DS(on) PowerPAK/DFN N-MOSFETs (<15mOhm at 4.5V) for Q3/Q4.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P2.3 Parallel bypass MOSFETs Q1/Q2 (AO4407A) driven by U_DBG (TPS2117DRLR) ST pin bypass overcurrent limiting and turn ON during thermal shutdown

**Parts:** U_DBG, Q1, Q2, R59, Q_DBG · **Nets:** /+5V, /+5V_CM5, /DBG_GATE, /DBG_Q_SRC, /DBG_PWR, /DBG_PR1

U_DBG (TPS2117DRLR, 4A power mux) selects between VIN1 (/DBG_PWR on TP1) and VIN2 (/+5V from U_BUCK) to power VOUT (/+5V_CM5). Because CM5 can draw >4A peak, back-to-back common-source P-MOSFETs Q1 and Q2 (AO4407A, ~22mOhm combined R_DS(on)) are placed directly in parallel with U_DBG's VIN2-to-VOUT path (~40mOhm), with their gates (/DBG_GATE) driven directly by U_DBG pin 8 (ST). Per the TI TPS2117 datasheet (Table 8-1), open-drain output ST pulls LOW not only when VIN2 is active, but also when both channels are disabled or when U_DBG enters thermal shutdown. Because Q1 and Q2 bypass U_DBG's internal current-sense element and turn ON whenever ST is LOW while /+5V is present (Q1's drain-to-source body diode charges /DBG_Q_SRC to ~4.4V, developing V_GS = -4.4V), U_DBG cannot current-limit /+5V_CM5 faults or isolate /+5V during thermal shutdown.

**Evidence:** TI TPS2117 datasheet (SLVSEW1A, Section 8.3.1 & Table 8-1): ST pin is pulled low when VIN2 supplies VOUT, when both channels are disabled, or when thermal shutdown is active. thin-laptop-cm5.kicad_sch: Q1.5-8 = /+5V, Q2.5-8 = /+5V_CM5, Q1.1-3 & Q2.1-3 = /DBG_Q_SRC, Q1.4 & Q2.4 = /DBG_GATE (U_DBG.8 ST).

**Suggested fix:** Disconnect U_DBG pin 6 (VIN2) from the high-current /+5V path (using U_DBG solely as the 500mA TP1 /DBG_PWR switch on VIN1 when /+5V is absent) and drive Q1/Q2 gates from an active-low enable derived from /+5V presence and /DBG_PWR absence, or use a single >=6A ideal-diode power mux controller.

**Status:** open. Agree, disagree or have a better fix? Open an issue.

### P2.4 USB-C PD subsystem provides no contract-current telemetry to CM5, preventing safe 45W-vs-65W software override of U_CHG ILIM_HIZ

**Parts:** U_CHG, R29, R30, J_USBL · **Nets:** /CHG_ILIM, /CHG_REGN, /CHG_DPDM

spec.yaml states that U_CHG (BQ25798RQMR) ILIM_HIZ (pin 17, /CHG_ILIM) is set by R29 = 78.7k and R30 = 100k from /CHG_REGN (5.0V) to V_ILIM_HIZ = 2.80V (I_INDPM = 2.25A, or 45W at 20V) so 45W PD adapters are not overloaded at plug-in, while CM5 software can disable EN_EXTILIM over I2C to draw 3.25A (65W) when a 65W PD adapter is connected. However, the architecture provides zero hardware telemetry for CM5 to determine the negotiated PD current capability: (1) the usb_left PD sink (CH224A) is a fixed resistor-strapped controller with no I2C interface or CC current-capability output; (2) J_USBL pins 1-4 and 7-8 are unconnected on the main board (unconnected-(J_USBL-Pad1..4,7..8)), leaving all usb_left status/fault/enable lines unrouted; (3) U1 (CM5) CC1/CC2 pins 94/96 are unconnected; and (4) U_CHG D+ (pin 6) and D- (pin 7) are shorted together on floating net /CHG_DPDM, causing BC1.2 detection to always report a fixed USB DCP (3.25A register default, clamped to 2.25A by ILIM_HIZ). Consequently, CM5 software cannot safely know when it is permissible to disable EN_EXTILIM without overloading a 45W (20V @ 2.25A) adapter.

**Evidence:** TI BQ25798 datasheet (SLUSDV2C, Section 7.3.4.3 Eq. 1 & Table 7-4, pp. 27-28): I_LIM = (V_ILIM_HIZ - 1.0V) / 0.8 = (2.798V - 1.0V) / 0.8 = 2.25A; D+ shorted to D- detects as USB DCP (IINDPM = 3.25A). thin-laptop-cm5.kicad_sch: J_USBL pins 1, 2, 3, 4, 7, 8 are unconnected.

**Suggested fix:** Route the usb_left status/fault/enable signals on J_USBL pins 1-4 and 7-8 to available CM5 GPIOs (such as GPIO9, GPIO10, GPIO14, GPIO15, GPIO25, GPIO26) with pull-ups, and use an I2C-capable PD sink controller (or CC comparator sense) if software is expected to distinguish 2.25A (45W) from 3.25A (65W) PD contracts.

**Status:** open. Agree, disagree or have a better fix? Open an issue.
