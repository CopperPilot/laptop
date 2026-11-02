# Left Dual USB-C PD & Data Daughter Board (`usb_left`)

## 1. Architecture & Block Summary (`usb_left_subboard`)

All components on `usb_left` are assembled on the top side (`F.Cu` only, `0` bottom-side components) so the CNC aluminum `bottom_shell` underneath `usb_left` is a continuous unperforated pan with no through-cutouts.

### 1.1 Front-Left 45–65 W (20 V) USB-C PD 3.0 Charging & Host Data Port (`J2`, `TYPE-C-31-M-12`, LCSC `C165948`)
- **Autonomous Hardware USB-PD 3.0 Sink Controller (`U1`, `CH224A`, LCSC `C42459160`):**
  - `U1` (`CH224A` in ESSOP-10, 4 V–30 V operating range) negotiates **20 V @ 2.25 A–3.25 A (45 W–65 W)** USB-PD 3.0 contracts autonomously in hardware with no processor or I2C controller required, feeding the main-board `BQ25798RQMR` 5 A 2S buck-boost NVDC battery charger (`3.6 V–24 V` operating input, `26 V` `VBUS_OVP`) over the 1.0 mm 5 A-rated harness `J5`.
  - Configured for **20 V PD request** using single-resistor `CFG1` strapping per WCH `CH224` Datasheet Section 5.2.1:
    - Pin 9 (`CFG1`, net `/PD_CFG1`) is strapped to `GND` via `R11 = 120 kOhm` 1% 0402 (`0402WGF1203TCE`, LCSC `C25750`) to request `20 V`.
    - Pins 2 (`CFG2_SCL`) and 3 (`CFG3_SDA`) are left open (`NC`, biased solely by `U1`'s internal pull-ups to its own internal `VDD33` rail), completely eliminating any external rail connection to `CFG2` and preventing CMOS back-powering when `U1.1` (`VHV`) is at `0 V`.
  - Pin 1 (`VHV`) is powered from unswitched receptacle rail `/J2_VBUS` through current-limiting resistor `R3 = 1 kOhm` (`0603WAF1001T5E`, LCSC `C21190`, `100 mW`, `75 V`) and decoupled to `GND` by `C5 = 1 uF` 50 V X5R 0603 (`CL10A105KB8NNNC`, LCSC `C15849`) on `/PD_VHV`.
  - Pin 8 (`VBUS`) senses `/J2_VBUS` through series resistor `R4 = 1 kOhm` (`0603WAF1001T5E`, LCSC `C21190`, `100 mW`, `75 V`) per `CH224` Datasheet Section 4.3.
  - Pins 4 and 5 (`DP`, `DM`) are left unconnected (`NC`) per `CH224` Datasheet Section 5.5 (`Use PD protocol only`) so `J2` USB 2.0 host data lines (`USB3-0-D_P/N`) pass undisturbed to the CM5 RP1 controller.
  - Pin 10 (`PG`, open-drain active-low Power Good indicator on `/PD_PG_N`) is pulled up to `/PD_VDD_3V3` via `R5 = 10 kOhm` (`0402WGF1002TCE`, LCSC `C25744`), drives the `/J2_VBUS -> /VBUS_PD` isolation load switch (`Q1`, `Q2`, `Q3`, `Q4`), and is routed via `R16 = 10 kOhm` to `J3` pin 1.
- **Cold-Socket `cSnkPwr` Compliance (`<= 4.7 uF`) & Adjacent Back-to-Back PFET Isolation Load Switch (`Q1`, `Q2` `AO4407A` + `Q3`, `Q4` `2N7002`):**
  - Unswitched capacitance on `/J2_VBUS` (`J2.A4B9`, `J2.B4A9`) is strictly limited to `C12 = 1 uF` 50 V 0603 (`C15849`) + `C13 = 100 nF` 50 V 0402 (`C307331`) = **`1.1 uF` (`<= 4.7 uF` and `<= 10 uF` USB Type-C `cSnkPwr` max)**, with `D6` (`SMF24A` TVS) and bleed resistor `R2 = 10 kOhm` 0603 (`C25804`).
  - Downstream bulk capacitance on `/VBUS_PD` (`C15 = 10 uF` 50 V 0805 `C440198` + `C16 = 100 nF` 50 V 0402 `C307331` + `D7 = SMF24A` at `J5`, plus main-board charger input capacitors) is isolated behind adjacent back-to-back common-source P-MOSFETs `Q1` (`(4.85, 35.30, rot=90)`) and `Q2` (`(12.80, 35.30, rot=-90)`) (`2x AO4407A`, LCSC `C2841482`, `-30 V`, `-12 A`, `13 mOhm` SOP-8):
    - `Q1` Drain (pins 5..8) connects to the `/J2_VBUS` `F.Cu` polygon pour, `Q1`/`Q2` common Source (pins 1..3) face each other directly across a continuous `F.Cu` polygon pour and dual `1.50 mm` copper bars on `/PD_SW_MID`, and `Q2` Drain (pins 5..8) connects to the `/VBUS_PD` `F.Cu` polygon pour feeding `J5`.
    - When `U1.10` (`PG`) is High-Z prior to PD contract completion, `Q3` (`2N7002`, LCSC `C8545`) is ON, holding `/PD_EN` at `0 V` and keeping 60 V N-MOSFET `Q4` (`2N7002`) OFF so `R13 = 10 kOhm` 0603 (`C25804`) holds `V_GS(Q1, Q2) = 0 V`.
    - When `U1.10` (`PG`) pulls LOW after 20 V PD negotiation, `Q3` turns OFF, `R15 = 10 kOhm` pulls `/PD_EN` to `3.3 V`, and `Q4` turns ON, pulling down `R14 = 10 kOhm` 0603 (`C25804`) to bias `V_GS(Q1, Q2) = -10.0 V` at 20 V (soft-started by `C17 = 100 nF` 50 V `C307331` with `tau = 0.5 ms` and hard-clamped to `|V_GS| <= 12.6 V` by 12 V 500 mW Zener diode `D9` `BZT52C12`, LCSC `C173429`).
- **24 V-Tolerant VBUS-to-CC/SBU Short Overvoltage & IEC 61000-4-2 ESD Port Protector (`U3`, `TPD6S300RUKR`, LCSC `C2649810`):**
  - Inserted between `J2` and `U1` (`CH224A`).
  - Connector-side pins `C_CC1` (pin 4) and `C_CC2` (pin 5) connect to `J2_CC1` (`J2.A5`) and `J2_CC2` (`J2.B5`), with dead-battery 5.1 kOhm `Rd` pins `RPD_G1` (pin 7) and `RPD_G2` (pin 6) tied to `J2_CC1` and `J2_CC2`.
  - Because `U3.10` (`VPWR`) is powered strictly from J2-derived `/PD_VDD_3V3` (with `D2` from `/+5V_USBC` removed), `U3.10` (`VPWR`) remains at `0 V` (`< 2.7 V` UVLO) whenever `J2` is unattached, ensuring `U3` always presents passive 5.1 kOhm `Rd` terminations to cold-socket USB-C PD chargers until `/J2_VBUS` rises.
  - `VPWR` (pin 10) is decoupled by `C9 = 100 nF` 50 V (`C307331`), `VBIAS` (pin 3) by `C8 = 100 nF` 50 V (`C307331`), and open-drain `~{FLT}` (pin 9, net `/U3_FLT_N`) is pulled up to `/PD_VDD_3V3` via `R6 = 10 kOhm` (`C25744`) and routed via `R17 = 10 kOhm` to `J3` pin 2.
- **Transient-Protected J2-Dedicated 3.3 V LDO (`U4`, `XC6216B332MR-G`, LCSC `C2891269`) with `R12 = 1 kOhm` + `D8` (`BZT52C16`, LCSC `C173426`) Pre-Clamp:**
  - Powered exclusively from `/J2_VBUS` via blocking diode `D3` (`1N4148WS`, LCSC `C2128`, net `/LDO_D3_K`) and series current-limiting resistor `R12 = 1 kOhm` 0603 (`0603WAF1001T5E`, LCSC `C21190`, `100 mW`, `75 V`) into `/LDO_VIN` (`U4.1 VIN` and `U4.4 CE`), which is clamped by 16 V 500 mW Zener diode `D8` (`BZT52C16`, LCSC `C173426`, `15.2 V–16.8 V`) and decoupled by `C6 = 1 uF` 50 V 0603 (`C15849`).

### 1.2 Rear-Left USB-C 5 V Cold-Socket DFP Accessory & Host Data Port (`J1`, `TYPE-C-31-M-12`, LCSC `C165948`)
- **Dedicated USB Type-C Cold-Socket DFP Controller & Power Switch (`U2`, `TPS25810RVCR`, LCSC `C473913`):**
  - `U2.IN1` (pins 2, 3), `U2.IN2` (pin 4), and `U2.AUX` (pin 5) are powered from `/+5V_USBC` via a continuous `F.Cu` polygon pour (`outlines=1`), while `U2.CHG` (pin 7) and `U2.CHG_HI` (pin 8) are both tied to `GND`, advertising **Default USB 500 mA Type-C DFP current** (`80 uA Rp` on `CC1`/`CC2`, with `1.7 A` typ / `1.85 A` max internal switch current limit coordinated below the upstream main-board `SY6280AAC` switch configured with `R31 = 3.3 kOhm` for `2.06 A` typ limit) per TI `TPS25810` Datasheet Table 1.
  - `U2.EN` (pin 6, net `/J1_EN`) is pulled up to `/+5V_USBC` via `R8 = 100 kOhm` (`0402WGF1003TCE`, LCSC `C25741`) and routed via `R21 = 10 kOhm` (`0402WGF1002TCE`, LCSC `C25744`) to `J3` pin 8 for host sleep/fault control (`V_EN = 0.46 V < 0.55 V V_IL` when `J3.8` is pulled low).
  - **USB Type-C `cSrcPwr` Bulk Input Capacitance (`>= 120 uF` Effective at 5 V Bias):** `/+5V_USBC` is decoupled by **2x `150 uF` 10 V 55 mOhm Polymer Tantalum capacitors (`C1`, `C18`, `T520C157M010ATE055`, LCSC `C600588`, zero DC-bias derating = `300 uF` effective)** + `C19 = 10 uF` 50 V X5R 0805 (`CL21A106KAYNNNE`, LCSC `C440198`, `~8.5 uF` effective at 5 V) + `C2 = 100 nF` 50 V X7R 0402 (`C307331`) = **`310.1 uF` nominal / `308.6 uF` effective at 5 V DC bias** (`>= 120 uF` `cSrcPwr`), while `/J1_VBUS` (`U2.OUT` pins 14, 15) connects to `J1` VBUS (`A4B9`, `B4A9`) via a continuous wide `F.Cu` polygon pour (`outlines=1`) and `1.20 mm` copper spine with `C3 = 10 uF` 50 V 0805 (`C440198`) + `C4 = 100 nF` 50 V 0402 (`C307331`) + `D4 = SMF6.0A` (`C178260`).
  - Open-drain status outputs `~{FAULT}` (pin 1, net `/J1_FAULT_N`) and `~{UFP}` (pin 19, net `/J1_UFP_N`) are pulled up to `/J1_VDD_3V3` (`3.3 V`) via `R9 = 10 kOhm` and `R10 = 10 kOhm` (`C25744`) and routed via `R19 = 10 kOhm` and `R20 = 10 kOhm` to `J3` pins 4 and 7.
- **Dedicated J1 3.3 V LDO (`U6`, `XC6206P332MR-G`, LCSC `C5446`) & CC/Data Port Protector (`U5`, `TPD6S300RUKR`, LCSC `C2649810`):**
  - `U6` (`XC6206P332MR-G`, SOT-23-3, `1.8 V–6.0 V` input, `3.3 V / 200 mA` output) regulates `/+5V_USBC` to `/J1_VDD_3V3` (`3.3 V`, decoupled by `C14 = 1 uF` 50 V 0603 `C15849` and `C11 = 100 nF` 50 V 0402 `C307331`), powering `U5.10` (`VPWR`) and `R7`/`R9`/`R10` independently of `J2`.
  - `U5.9` (`~{FLT}`, net `/U5_FLT_N`) is pulled up to `/J1_VDD_3V3` via `R7 = 10 kOhm` (`C25744`) and routed via `R18 = 10 kOhm` to `J3` pin 3.

---

## 2. Inter-Board Connector Pinouts & Segregated Power/Signal Routing

- **High-Current Power Harnesses (`J5` & `J4` Exclusively):**
  - **`J5` (`SM10B-SRSS-TB(LF)(SN)`, LCSC `C160409`, 10-pin 1.0 mm pitch, 1.0 A/pin, 50 V):** `Pins 1..5 = /VBUS_PD` (**5.0 A continuous rating** `> 3.25 A` max 20 V PD current), `Pins 6..10 = GND` (`5.0 A` return, plus grounded shell tabs `11..12`).
  - **`J4` (`SM06B-SRSS-TB(LF)(SN)`, LCSC `C160405`, 6-pin 1.0 mm pitch, 1.0 A/pin, 50 V):** `Pins 1..3 = /+5V_USBC` (**3.0 A continuous rating** `> 1.7 A` `U2` `I_OS` limit), `Pins 4..6 = GND` (`3.0 A` return, plus grounded shell tabs `7..8`).
- **Low-Current Signal & High-Speed Data FFC (`J3`, `FPC-05F-16PH20`, LCSC `C2856801`, 16-pin 0.5 mm Bottom-Contact FFC):**
  - `J3` (`FPC-05F-16PH20`, bottom-contact, `Pad 1` at North `y = 13.75 mm`, `Pad 16` at South `y = 21.25 mm`) mates 1-to-1 across straight FFC `c_usb_left` with main-board top-contact `J_USBL` (`05B20U16P`, `C18164516`, `Pad 1` at North `y = 18.25 mm`, `Pad 16` at South `y = 25.75 mm`):
  - `Pin 1`: `/PD_PG_N` (via `R16 = 10 kOhm` isolation resistor)
  - `Pin 2`: `/U3_FLT_N` (via `R17 = 10 kOhm` isolation resistor)
  - `Pin 3`: `/U5_FLT_N` (via `R18 = 10 kOhm` isolation resistor)
  - `Pin 4`: `/J1_FAULT_N` (via `R19 = 10 kOhm` isolation resistor)
  - `Pins 5, 6`: `GND` (Guard ground shield)
  - `Pin 7`: `/J1_UFP_N` (via `R20 = 10 kOhm` isolation resistor)
  - `Pin 8`: `/J1_EN` (via `R21 = 10 kOhm` isolation resistor)
  - `Pin 9`: `GND` (High-speed reference ground)
  - `Pins 10 / 11`: `USB3-0-D_P` / `USB3-0-D_N` (90-ohm differential pair to `J2`)
  - `Pin 12`: `GND` (High-speed reference ground)
  - `Pins 13 / 14`: `USB3-1-D_P` / `USB3-1-D_N` (90-ohm differential pair to `J1`)
  - `Pins 15, 16, 17, 18`: `GND` (High-speed reference ground and grounded mechanical shell tabs)
