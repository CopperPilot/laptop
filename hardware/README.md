# 13-inch Thin Aluminum CM5 Laptop — Hardware Design & Verification (`hardware/README.md`)

Generated from `rea/spec.yaml` and completed for the main carrier PCB (`hardware/thin-laptop-cm5`) and inter-board interfaces (`c_usb_left` and `c_audio_right`). Every placed BOM symbol carries a verified in-stock `LCSC` part number.

---

## 1. Inter-Board Cable Pinouts (`board.cable_pinout` 1:1 Straight Convention)

Both board-to-board FFC cables (`c_usb_left` and `c_audio_right`) and high-current wire-to-board harnesses (`J4`, `J5`) use a **1:1 straight pin-number mapping** (`Pin k` on `main` connects to `Pin k` on the sub-board with identical net semantics).

### 1.1 `c_usb_left`: Main Board `J_USBL` (`05B20U16P`, `C18164516`) <-> Left USB-C Board `J3` (`FPC-05F-16PH20`, `C2856801`) + High-Current Harnesses `J4` & `J5`

- **16-pin 0.5mm FFC (`J_USBL` <-> `J3`):**
  - Pins 1..4: Uncommitted (`no_connect` on `main`; `/VBUS_PD` removed from the 0.5mm FFC so 100% of 20V PD current flows exclusively through the 5.0A-rated `J5` harness)
  - Pins 5, 6: `GND` (Ground return)
  - Pins 7, 8: Uncommitted (`no_connect` on `main`; `/+5V_USBC` removed from the 0.5mm FFC so 100% of 5V accessory current flows exclusively through the 3.0A-rated `J4` harness)
  - Pin 9: `GND` (High-speed reference ground flanking `USB3-0` pair)
  - Pins 10 / 11: `USB3-0-D_P` (U1 pin 134) / `USB3-0-D_N` (U1 pin 136) <-> Front-left USB-C `J2` D+/D- (`nets_must_connect`, protected on `main` by `U_ESD1` `USBLC6-2SC6`)
  - Pin 12: `GND` (High-speed isolation ground between `USB3-0` and `USB3-1` differential pairs)
  - Pins 13 / 14: `USB3-1-D_P` (U1 pin 163) / `USB3-1-D_N` (U1 pin 165) <-> Rear-left USB-C `J1` D+/D- (`nets_must_connect`, protected on `main` by `U_ESD2` `USBLC6-2SC6`)
  - Pins 15, 16, 17, 18: `GND` (Return and grounded mechanical shell tabs)
- **10-pin 1.0mm Wire-to-Board Charging Harness (`J5` `SM10B-SRSS-TB(LF)(SN)`, `C160409`):**
  - Pins 1..5: `VBUS_PD` (5 x 1.0A = 5.0A continuous rating > 3.25A max 20V PD current [65W], clamped at `J5` by low-clamping 22V-standoff / 27.7V-clamping surge TVS `D7` `TVS2200DRVR` `C2875234` and switched into `U_CHG` `/CHG_VBUS` via back-to-back 30V N-MOSFETs `Q3`/`Q4` `2x AO3400A` `C20917` driven by `U_CHG` `ACDRV1`)
  - Pins 6..10, 11, 12: `GND` (5.0A continuous return + grounded shell tabs)
- **6-pin 1.0mm Wire-to-Board Accessory VBUS Harness (`J4` `SM06B-SRSS-TB(LF)(SN)`, `C160405`):**
  - Pins 1..3: `+5V_USBC` (3 x 1.0A = 3.0A continuous rating, fed by `U_VBUS` `SY6280AAC` with `R31 = 3.3k` `C25890` setting `I_LIM = 6800 / 3300 = 2.06A` typ / `1.55A` min, clamped by 5.5V-standoff TVS `D2` `PESD5V0S1BL` `C1970515`)
  - Pins 4..6, 7, 8: `GND` (3.0A continuous return + grounded shell tabs)

### 1.2 `c_audio_right`: Main Board `J_AUDR` (`FPC-05F-8PH20`, `C2856797`) <-> Right Audio Board `J2` (`FPC-05F-8PH20`, `C2856797`)

- Pin 1: `GND` (Analog/headphone ground return)
- Pin 2: `HP_L` (`main -> audio_right`, AC-coupled Left headphone output via `C29 + C52 = 200uF` and `R61 = 10R` with `D10` `PESD5V0S1BA` ESD clamp)
- Pin 3: `HP_R` (`main -> audio_right`, AC-coupled Right headphone output via `C30 + C53 = 200uF` and `R62 = 10R` with `D11` `PESD5V0S1BA` ESD clamp)
- Pin 4: `GND` (Guard ground isolating headphone outputs from differential microphone inputs)
- Pin 5: `MIC_P` (`audio_right -> main`, differential microphone positive to `ES8388` `LIN1` via `C33 = 1uF` with `R51 = 2.2k` `C25879` to `MICBIAS` and `D12` `PESD5V0S1BA` ESD clamp)
- Pin 6: `MIC_N` (`audio_right -> main`, differential microphone negative to `ES8388` `RIN1` via `C34 = 1uF` with `R52 = 2.2k` `C25879` to `GND` and `D13` `PESD5V0S1BA` ESD clamp)
- Pin 7: `HP_DET` (`audio_right -> main`, active-low headphone plug detect from `TLV7041DBVR` on `audio_right`, routed to CM5 `GPIO24` `U1` pin 45 with `R37 = 10k` pull-up to `+3V3` and `D14` `PESD5V0S1BA` ESD clamp, isolated from main-board `/LID_SNS` on `GPIO13` `U1` pin 28)
- Pin 8: `+3V3` (`main -> audio_right`, +3.3V supply from CM5 `+3.3v_(Output)` pins 84, 86)
- Pins 9, 10: `GND` (Mechanical shell tabs grounded)

---

## 2. Peripheral Connector Pinouts on Main Board

### 2.1 `J_DSI` (MIPI DSI1 22-pin 0.5mm FFC `FH12-22S-0.5SH(55)`, `C597981`) — Raspberry Pi 22-Way Standard
Matches `hardware/pinout-cm5.md` Port 1 table:
- Pins 1, 4, 7, 10, 13, 16, 19, 23, 24: `GND`
- Pins 2 / 3: `MIPI1_D0_N` (U1 pin 175) / `MIPI1_D0_P` (U1 pin 177)
- Pins 5 / 6: `MIPI1_D1_N` (U1 pin 181) / `MIPI1_D1_P` (U1 pin 183)
- Pins 8 / 9: `MIPI1_C_N` (U1 pin 187) / `MIPI1_C_P` (U1 pin 189)
- Pins 11 / 12: `MIPI1_D2_N` (U1 pin 193) / `MIPI1_D2_P` (U1 pin 195)
- Pins 14 / 15: `MIPI1_D3_N` (U1 pin 194) / `MIPI1_D3_P` (U1 pin 196)
- Pins 17 / 18: `DSI_RST_N` (U1 `GPIO7` pin 37 + `R55 = 10k` pull-down) / `DSI_EN` (U1 `GPIO8` pin 39 + `R56 = 10k` pull-down)
- Pins 20 / 21: `SCL0` (U1 pin 80) / `SDA0` (U1 pin 82), pulled up via `R9 = 2.2k` (`C25879`) / `R10 = 2.2k` (`C25879`) to switched `+3V3_PER`
- Pin 22: `+3V3_PER` (soft-started 3.3V from `U_3V3` `TLV62569DBVR`, never 5V)

### 2.2 `J_CSI` (MIPI CSI0 22-pin 0.5mm FFC `FH12-22S-0.5SH(55)`, `C597981`) — Raspberry Pi 22-Way Standard
Matches `hardware/pinout-cm5.md` Port 0 table:
- Pins 1, 4, 7, 10, 13, 16, 19, 23, 24: `GND`
- Pins 2 / 3: `MIPI0_D0_N` (U1 pin 115) / `MIPI0_D0_P` (U1 pin 117)
- Pins 5 / 6: `MIPI0_D1_N` (U1 pin 121) / `MIPI0_D1_P` (U1 pin 123)
- Pins 8 / 9: `MIPI0_C_N` (U1 pin 127) / `MIPI0_C_P` (U1 pin 129)
- Pins 11..15: Unconnected (`no_connect`, 2-lane CSI0 camera interface)
- Pins 17 / 18: `CAM_GPIO0` (U1 pin 97 + `R54 = 10k` pull-down) / `CAM_GPIO1` (U1 pin 100 via `R53 = 22R` series source damping resistor)
- Pins 20 / 21: `SCL0` (U1 pin 80) / `SDA0` (U1 pin 82)
- Pin 22: `+3V3_PER` (never 5V)

### 2.3 `J_BAT` (Single 8-pin 2.0mm JST-PH 2S2P Battery Pack Connector `S8B-PH-SM4-TB(LF)(SN)`, `C265121`)
- Pins 1, 2, 3, 4: `VBAT_PACK` (4 x 2.0A = 8.0A continuous contact rating, routed through 5A 1206 SMD fuse `F1` `JFC1206-1500FS` `C136351` to `/VBAT` `U_CHG` pins 22/23, with `R50 = 100R` 1% `C25076` Kelvin battery positive voltage sense connected from the fused `/VBAT` side of `F1` into `U_CHG` pin 18 `BATP` so `R50` cannot be overloaded if `F1` opens)
- Pin 5: `CHG_TS` (Pack 10k NTC thermistor sense to `U_CHG` pin 16 `TS`, biased from `REGN` via `R23 = 5.23k` 1% `C11631` / `R42 = 30.1k` 1% `C29402` JEITA divider and clamped by 5.5V bidirectional TVS diode `D19` `TSD05CDYFR` `C20611048`)
- Pins 6, 7, 8, 9, 10: `GND` (3 x 2.0A = 6.0A continuous return + grounded mechanical mounting tabs)

### 2.4 `J_KB` (24-pin 0.5mm Keyboard FPC `05A20L24P`, `C5362158`) & `J_TP` (8-pin 0.5mm Trackpad FPC `FPC-05F-8PH20`, `C2856797`)
- `J_KB` Pins 1..8: `KB_ROW0..7` -> `U_KB` (`TCA8418RTWR`) pins 8..1; Pins 9..18: `KB_COL0..9` -> `U_KB` pins 9..18; Pin 19: `PWR_BUT` (protected by `D9` `PESD5V0S1BA` and isolated from `U_CHG` `/CHG_QON` and CM5 `/CM5_PWR_BUT` via dual-anode blocking Schottky diodes `D16`/`D17` `2x B16WS` `C364278`); Pin 20: `+3V3`; Pins 21..26: `GND`.
- `J_TP` Pin 1: `GND`; Pin 2: `+3V3`; Pin 3: `I2C_SDA` (`GPIO2` pin 58); Pin 4: `I2C_SCL` (`GPIO3` pin 56); Pin 5: `TP_INT_N` (`GPIO17` pin 50, `R18 = 10k` to `+3V3`); Pin 6: `TP_RST_N` (`GPIO27` pin 48, `R19 = 10k` to `+3V3`); Pins 7..10: `GND`.

---

## 3. Datasheet Rating & 2S 45–65W Power Architecture Verification Checklist

1. **Capacitor & TVS Voltage Ratings (>= 1.5x Max Rail Voltage Across All Rails):**
   - `VBUS_PD` / `CHG_VBUS` / `CHG_PMID` (20.0V USB-C PD operating): Decoupled by 50V-rated `10uF` 0805 (`GRM21BR61H106KE43L`, `C440198`) and `100nF` 50V 0402 (`CL05B104KB54PNC`, `C307331`) capacitors (`50V / 20V = 2.50x` margin) and protected by low-clamping 22V-standoff / 27.7V-clamping surge TVS `D7` (`TVS2200DRVR`, `C2875234`, `V_C = 27.7V < 30.0V` `U_CHG` abs max) plus external back-to-back 30V N-MOSFETs `Q3`/`Q4` (`2x AO3400A`, `C20917`) driven by `U_CHG` `ACDRV1`.
   - `VSYS` / `VBAT` (2S Li-Po 6.0V–8.4V, 8.6V max NVDC): Decoupled by 50V-rated `10uF` 0805 (`C440198`, `5.81x` margin) and 25V-rated `22uF` 0805 (`CL21A226MAQNNNE`, `C45783`, `25V / 8.6V = 2.91x` margin).
   - `LED_ANODE` (~24V backlight boost output): Decoupled by 50V-rated `1uF` 0603 (`CL10A105KB8NNNC`, `C15849`, `50V / 24V = 2.08x` margin) with 60V Schottky diode `D1` (`B16WS`, `C364278`).
   - `+5V`, `+5V_PER`, `+5V_USBC`: Clamped by 5.5V-standoff TVS diodes `D3`, `D18`, and `D2` (`3x PESD5V0S1BL`, `C1970515`, `V_RWM = 5.5V > 5.06V` regulated buck output) and decoupled by 25V–50V X5R/X7R MLCCs.
2. **2S 45–65W Buck-Boost Charger & NVDC Power Path (`U_CHG` `BQ25798RQMR`, `C2876593`):**
   - Takes 20V USB-C PD (`3.6V–24V` operating input, `26V` internal OVP) via `Q3`/`Q4` (`2x AO3400A`) and charges the 2S2P 7.4V 9,000mAh (`66.6Wh`) pack at `VREG = 8.40V` (`R28 = 8.2k` 1% `C25981` on `PROG` pin 20 selecting 2S default and `750 kHz` switching with `L1 = 2.2 uH` 10A inductor `FXL0630-2R2-M` `C167218` between `SW1` pin 28 and `SW2` pin 26).
   - `ILIM_HIZ` (pin 17, `/CHG_ILIM`) is biased from `REGN` (`4.7uF` 50V `C29823`) via `R29 = 78.7k` 1% (`C2998104`) / `R30 = 100k` 1% (`C25741`), setting `V(ILIM_HIZ) = 2.80V` -> `I_INDPM = 2.25A` (`45W` hardware input current limit at 20V so a 45W 20V@2.25A PD adapter is never overloaded prior to software override; CM5 software can disable `EN_ILIM_HIZ_PIN` over I2C to allow `3.25A` / `65W` on 65W contracts).
3. **Dual 5V / 6A Synchronous Buck Converters (`U_BUCK` & `U_BUCK2`, `2x TPS56628DDAR`, `C485522`) & `/VSYS_BL` Backlight Feed:**
   - `U_BUCK` (`L2 = 2.2 uH` `FXL0630-2R2-M` `C167218`, `R27 = 133k` `C25753` / `R28 = 24k` `C25769` setting `5.00V`, `R33 = 100k` / `R34 = 22.1k` `C163478` UVLO divider setting `>= 6.63V` battery cutoff for full dropout headroom) steps down 2S `/VSYS` to `/+5V` (`5.00V`, `6A` continuous) dedicated to CM5 `/+5V_CM5` (up to `5.0A`) and `U_VBUS` (`SY6280AAC`, `R31 = 3.3k` `C25890` setting `2.06A` typ / `1.55A` min limit on `/+5V_USBC`).
   - `U_BUCK2` (`L5 = 2.2 uH` `FXL0630-2R2-M` `C167218`, `R64 = 133k` `C25753` / `R65 = 24k` `C25769` setting `5.00V`, `R67 = 100k` / `R68 = 22.1k` `C163478` UVLO divider setting `>= 6.63V` cutoff) steps down 2S `/VSYS` to `/+5V_PER` (`5.00V`, `6A` continuous) powering `U_AMP` (`PAM8406DR`) and `U_3V3` (`TLV62569DBVR`).
   - `U_BL` (`TPS61165DBVR`) and `L3` (`22 uH`) are powered directly from 2S `/VSYS` (`6.0V–8.6V`) via high-side P-MOSFET switch `Q_BL` (`AO3401A` `C15127`, gated by `Q_BL_EN` `2N7002` `C8545` + `R72 = 100k` / `R73 = 10k` from `/+3V3`) on `/VSYS_BL`, reducing `U_BL` peak switch current to `~0.62A < 0.96A` min switch limit.
4. **30V-Input RTC LDO (`U_RTC` `HT7530S`, `C347214`) & CM5 USB OTG `rpiboot` Path (`SW1`, `TP1..TP5`):**
   - `U_RTC` (`HT7530S`, 30V max VIN, `2 uA` Iq) regulates always-on 2S `/VBAT` (`6.0V–8.4V`) to `3.0V` (`/RTC_3V0`) for CM5 `PMIC_BAT_V` (pin 76).
   - `U_DBG` (`TPS2117DRLR`, `C22399676`, with `MODE` pin 5 tied to `/DBG_PWR` and `PR1` pin 4 on `/DBG_PR1` biased by `R58 = 30k` `C25776` / `R7 = 10k` `C25744` and pulled low by `2N7002` N-MOSFET `Q_DBG` `C8545` gated by `/+5V` so internal 6A `/+5V` always takes priority over external 500mA `TP1` `/DBG_PWR` whenever `/+5V` is present) + common-source back-to-back `Q1`/`Q2` (`2x AO4407A`, `C2841482`, gated on `/DBG_GATE` by `U_DBG` `ST` pin 8 and `R59 = 10k` `C25744` tied to common source `/DBG_Q_SRC` so `V_GS = 0V` strictly when `ST` is Hi-Z) mux `/+5V` and top-side service pad `TP1` (`DBG_PWR`) to `/+5V_CM5`.
