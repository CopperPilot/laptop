# 13-inch Thin Aluminum CM5 Laptop — Hardware Design & Verification (`hardware/README.md`)

Generated from `rea/spec.yaml` and completed for the main carrier PCB (`hardware/thin-laptop-cm5`) and inter-board interfaces (`c_usb_left` and `c_audio_right`). Every placed BOM symbol carries a verified in-stock `LCSC` part number.

---

## 1. Inter-Board Cable Pinouts (`board.cable_pinout` 1:1 Straight Convention)

Both board-to-board FFC cables (`c_usb_left` and `c_audio_right`) and high-current wire-to-board harnesses (`J4`, `J5`) use a **1:1 straight pin-number mapping** (`Pin k` on `main` connects to `Pin k` on the sub-board with identical net semantics).

### 1.1 `c_usb_left`: Main Board `J_USBL` (`05B20U16P`, `C18164516`) <-> Left USB-C Board `J3` (`FPC-05F-16PH20`, `C2856801`) + High-Current Harnesses `J4` & `J5`

- **16-pin 0.5mm Type-B (Opposite-Side / Reversed-Contact) FFC (`c_usb_left`, `J_USBL` top-contact `05B20U16P` `C18164516` <-> `J3` bottom-contact `FPC-05F-16PH20` `C2856801`):**
  - Pins 1..4, 7..8 are protected on `main` by two 5-channel 3.3V ESD TVS arrays `D29` and `D30` (`2x PESD3V3L5UY`, `C2831531`, SOT-363):
    - Pin 1 `/USBL_PD_PG_N` (`U1.10 PG` via non-inverting 2-stage `2N7002` open-drain buffer `Q3` + `Q6` with `R5 = 10k`, `R24 = 100k` to `/PD_VDD_3V3`, and `R25` removed on `usb_left`) -> CM5 `GPIO9` (`U1` pin 40, pulled up exclusively via `R75 = 10k` to `/+3V3`)
    - Pin 2 `/USBL_U3_FLT_N` (`U3.9 ~FLT` via non-inverting 2-stage `2N7002` open-drain buffer `Q5` + `Q7` with `R6 = 10k`, `R23 = 100k` to `/PD_VDD_3V3`, and `R26` removed on `usb_left`) -> CM5 `GPIO10` (`U1` pin 44, pulled up exclusively via `R76 = 10k` to `/+3V3`)
    - Pin 3 `/USBL_U5_FLT_N` (`U5.9 ~FLT`, with `R7` removed on `usb_left`) -> CM5 `GPIO26` (`U1` pin 24, pulled up exclusively via `R77 = 10k` to `/+3V3`)
    - Pin 4 `/USBL_J1_FAULT_N` (`U2.1 ~FAULT`, with `R9` removed on `usb_left`) -> CM5 `GPIO6` (`U1` pin 30, pulled up exclusively via `R78 = 10k` to `/+3V3`)
  - Pins 5, 6: `GND` (Ground return)
  - Pins 7, 8:
    - Pin 7 `/USBL_J1_UFP_N` (`U2.19 ~UFP`, with `R10` removed on `usb_left`) -> CM5 `GPIO25` (`U1` pin 41, pulled up exclusively via `R79 = 10k` to `/+3V3`)
    - Pin 8 `/USBL_J1_EN` (`U2.6 EN` on `usb_left` `TPS25810RVCR` with local `R8 = 100 kOhm` pull-down to `/GND` + main-board `U_VBUS.4 EN` with `R8 = 100 kOhm` `C25741` pull-down to `/GND`) <- CM5 `VBUS_EN` (`U1` pin 111, `/CM5_VBUS_EN`) via `R91 = 10 kOhm` (`C25744`) series resistor, gated low below `V_THROT_FALL = 7.160V typ / 7.060V min` `/VSYS` (`V_THROT_RISE = 7.582V typ / 7.487V min`, `422mV` hysteresis via co-located `R88 = 80.6k` `0402WGF8062TCE` `C25798` / `R89 = 4.7k` `0402WGF4701TCE` `C25900` + `R97 = 100k` `C25741` / `Q6` `BSS138` `C52895` on `U_UVLO.4` `INB-` `/VSYS_THROT`) by low-battery load-shedding N-MOSFET `Q5` (`BSS138` `C52895`) driven by `U_UVLO` `OUTB` (`/VBUS_ISET_HI`, pulled up to `/+3V3` via `R90 = 47 kOhm` `0402WGF4702TCE` `C25792`)
  - Pin 9: `GND` (High-speed reference ground flanking `USB3-0` pair)
  - Pins 10 / 11: `USB3-0-D_P` (U1 pin 134) / `USB3-0-D_N` (U1 pin 136) <-> Front-left USB-C `J2` D+/D- (protected on `main` by `U_ESD1` `USBLC6-2SC6` with Pin 5 `VBUS` isolated onto dedicated local `100nF` capacitor `C90` `C307331` `/ESD1_VBUS` to `/GND` per ST `USBLC6-2SC6` Figure 4 so only the internal central Zener rail clamp is used without back-powering `/+5V_PER`)
  - Pin 12: `GND` (High-speed isolation ground between `USB3-0` and `USB3-1` differential pairs)
  - Pins 13 / 14: `USB3-1-D_P` (U1 pin 163) / `USB3-1-D_N` (U1 pin 165) <-> Rear-left USB-C `J1` D+/D- (protected on `main` by `U_ESD2` `USBLC6-2SC6` with Pin 5 `VBUS` isolated onto dedicated local `100nF` capacitor `C91` `C307331` `/ESD2_VBUS` to `/GND` per ST `USBLC6-2SC6` Figure 4 so only the internal central Zener rail clamp is used without back-powering `/+5V_PER`)
  - Pins 15, 16, 17, 18: `GND` (Return and grounded mechanical shell tabs)
- **10-pin 1.0mm Wire-to-Board Charging Harness (`J5` `SM10B-SRSS-TB(LF)(SN)`, `C160409`):**
  - Pins 1..5: `VBUS_PD` (5 x 1.0A = 5.0A rating > 2.25A hardware-capped 20V PD current [45W], clamped at `J5` by low-clamping 22V-standoff / 27.7V-clamping surge TVS `D7` `TVS2200DRVR` `C2875234` and switched into `U_CHG` `/CHG_VBUS` via back-to-back 40V N-MOSFETs `Q3`/`Q4` `2x SQ2318AES-T1_BE3` `C2847989` driven by `U_CHG` `ACDRV1`)
  - Pins 6..10, 11, 12: `GND` (5.0A continuous return + grounded shell tabs)
- **6-pin 1.0mm Wire-to-Board Accessory VBUS Harness (`J4` `SM06B-SRSS-TB(LF)(SN)`, `C160405`):**
  - Pins 1..3: `+5V_USBC` (3 x 1.0A = 3.0A continuous rating, switched from the 6A `/+5V_PER` synchronous buck rail `U_BUCK2` `TPS56628DDAR` by `U_VBUS` `SY6280AAC` `C55136` with fixed `R31 = 3.6 kOhm` 1% `C25891` on `/USB_ISET` setting `I_LIM = 1.89 A typ <= 2.0 A` continuous rating [matching `usb_left`'s `1.5 A` `TPS25810RVCR` Type-C Rp contract with zero current-limit mismatch] and `EN` synchronized with `usb_left` `TPS25810RVCR` `EN` on `/USBL_J1_EN` so both `U_VBUS` and the `1.5 A` Type-C Rp advertisement cleanly shed below `V_THROT_FALL = 7.160 V typ / 7.060 V min` `/VSYS` [`V_THROT_RISE = 7.582 V typ / 7.487 V min`, `422 mV` hysteresis via co-located `R88 = 80.6k` `0402WGF8062TCE` `C25798` / `R89 = 4.7k` `0402WGF4701TCE` `C25900` + `R97 = 100k` `C25741` / `Q6` `BSS138` `C52895` on `U_UVLO.4` `INB-`], keeping worst-case 2S battery discharge current `<= 5.35 A <= 6.0 A` continuous `BQ25798RQMR` internal BATFET rating down to `V_UVLO_FALL = 6.610 V`, decoupled by `C19 = 10uF` and clamped by unidirectional 5.0V low-clamping TVS `D2` `PSD05-LF-T7` `C139296`)
  - Pins 4..6, 7, 8: `GND` (3.0A continuous return + grounded shell tabs)

### 1.2 `c_audio_right`: Main Board `J_AUDR` (`FPC-05F-8PH20`, `C2856797`) <-> Right Audio Board `J2` (`FPC-05FB-8PH20`, `C2856828`)

- Pin 1: `GND` (Analog/headphone ground return)
- Pin 2: `HP_L` (`main -> audio_right`, AC-coupled Left headphone output via `C29 + C52 = 200uF` and `R61 = 10R` with `D10` `PESD5V0S1BA` ESD clamp)
- Pin 3: `HP_R` (`main -> audio_right`, AC-coupled Right headphone output via `C30 + C53 = 200uF` and `R62 = 10R` with `D11` `PESD5V0S1BA` ESD clamp)
- Pin 4: `GND` (Guard ground isolating headphone outputs from differential microphone inputs)
- Pin 5: `MIC_P` (`audio_right -> main`, differential microphone positive to `ES8388` `LIN1` via `C33 = 2.2uF` with symmetrical DC charge bleeder `R51 = 47k` `C25792` to `/GND` and `D12` `PESD5V0S1BA` ESD clamp)
- Pin 6: `MIC_N` (`audio_right -> main`, differential microphone negative to `ES8388` `RIN1` via `C34 = 2.2uF` with symmetrical DC charge bleeder `R52 = 47k` `C25792` to `/GND` and `D13` `PESD5V0S1BA` ESD clamp)
- Pin 7: `HP_DET` (`audio_right -> main`, active-low headphone plug detect from `TLV7041DBVR` on `audio_right`, routed to CM5 `GPIO24` `U1` pin 45 with `R37 = 10k` pull-up to `+3V3` and unidirectional 3.3V ESD diode `D14` `PESD3V3U1UA,115` `C403915`, isolated from main-board `/LID_SNS` on `GPIO13` `U1` pin 28)
- Pin 8: `+3V3_PER` (`main -> audio_right`, switched and current-limited +3.3V peripheral rail fed directly from `U_3V3` `TLV62569DBVR` `/+3V3_PER` with `F5` removed, locally decoupled by `C38 = 100nF` and clamped by 3.3V ESD TVS diode `D32` `PESD3V3U1UA,115` `C403915`)
- Pins 9, 10: `GND` (Mechanical shell tabs grounded)

---

## 2. Peripheral Connector Pinouts on Main Board

### 2.1 `J_DSI` (MIPI DSI1 22-pin 0.5mm FFC `FH12-22S-0.5SH(55)`, `C597981`) — Raspberry Pi 22-Way Standard
- Pins 1, 4, 7, 10, 13, 16, 19, 23, 24: `GND`
- Pins 2 / 3: `MIPI1_D0_N` (U1 pin 175) / `MIPI1_D0_P` (U1 pin 177)
- Pins 5 / 6: `MIPI1_D1_N` (U1 pin 181) / `MIPI1_D1_P` (U1 pin 183)
- Pins 8 / 9: `MIPI1_C_N` (U1 pin 187) / `MIPI1_C_P` (U1 pin 189)
- Pins 11 / 12: `MIPI1_D2_N` (U1 pin 193) / `MIPI1_D2_P` (U1 pin 195)
- Pins 14 / 15: `MIPI1_D3_N` (U1 pin 194) / `MIPI1_D3_P` (U1 pin 196)
- Pins 17 / 18: `DSI_RST_N` (U1 `GPIO7` pin 37 + `R55 = 10k` pull-down) / `DSI_EN` (U1 `GPIO8` pin 39 + `R56 = 10k` pull-down)
- Pins 20 / 21: `SCL0_PER` / `SDA0_PER` (isolated via `Q_I2C1`/`Q_I2C2` `BSS138` from U1 pins 80/82, pulled up via `R9 = 2.2k` `C25879` / `R10 = 2.2k` `C25879` to switched `+3V3_PER`)
- Pin 22: `+3V3_PER` (fed directly from low-impedance switched/current-limited `/+3V3_PER` buck rail `U_3V3` `TLV62569DBVR` with `F2` removed to eliminate PTC IR drop, locally decoupled by `C45 = 10uF` and `C46 = 100nF`; pins 17, 18, 20, 21, 22 are ESD-protected at `J_DSI` by 5-channel 3.3V SOT-363 TVS array `D33` `PESD3V3L5UY` `C2831531`)

### 2.2 `J_CSI` (MIPI CSI0 22-pin 0.5mm FFC `FH12-22S-0.5SH(55)`, `C597981`) — Raspberry Pi 22-Way Standard
- Pins 1, 4, 7, 10, 13, 16, 19, 23, 24: `GND`
- Pins 2 / 3: `MIPI0_D0_N` (U1 pin 115) / `MIPI0_D0_P` (U1 pin 117)
- Pins 5 / 6: `MIPI0_D1_N` (U1 pin 121) / `MIPI0_D1_P` (U1 pin 123)
- Pins 8 / 9: `MIPI0_C_N` (U1 pin 127) / `MIPI0_C_P` (U1 pin 129)
- Pins 11..15: Unconnected (`no_connect`, 2-lane CSI0 camera interface)
- Pins 17 / 18: `CAM_GPIO1` (`J_CSI` pin 17 camera shutdown/reset from `U1` pin 100 `/CAM_GPIO1_CM5` via `Q_CAM` `BSS138` `C52895` pass switch gated by `/+3V3_PER` with `R95 = 10k` pull-up to `/+3V3_PER` and `R96 = 100k` pull-down to `/GND` for 0.0 uA off-state back-drive) / `CAM_GPIO0` (`J_CSI` pin 18 24 MHz camera GPCLK clock from `U1` pin 97 `/CAM_GPIO0_SRC` via `R53 = 22R` series source damping resistor + `R54 = 10k` pull-down to `/GND`, protected at `J_CSI` by dedicated ultra-low-capacitance `0.65 pF` unidirectional 3.3V ESD diode `D40` `PESD3V3U1UA,115` `C403915` with `D34` pin 3 tied to `/GND`)
- Pins 20 / 21: `SCL0_PER` / `SDA0_PER`
- Pin 22: `+3V3_PER` (fed directly from `/+3V3_PER` with `F3` removed so local camera bulk/bypass capacitors `C47 = 10uF` and `C48 = 100nF` at `(125.8, 5.2..7.0) mm` directly decouple `J_CSI.22`; pins 17, 20, 21, 22 are ESD-protected at `J_CSI` by 5-channel 3.3V SOT-363 TVS array `D34` `PESD3V3L5UY` `C2831531` with unused pin 3 grounded, while pin 18 `/CAM_GPIO0` is protected by `0.65 pF` `D40` `PESD3V3U1UA,115` `C403915`)

### 2.3 `J_BL` (2-pin 2.0mm JST-PH Display Backlight Connector `S2B-PH-SM4-TB(LF)(SN)`, `C295747`)
- Pin 1: `LED_ANODE` (~24V 8S WLED boost output from `U_BL` `TPS61165DBVR` with `L3 = 10uH`, `D1 = B16WS`, and `C22 = 1uF` 50V, fed from `/VSYS` via `1A` `32V` fast-acting 0603 fuse `F6` `CFS06V3T1R0` `C163118` -> `/VSYS_BL_SW` and high-side P-MOSFET switch `Q_BL` `AO3401A` with `R35 = 100k` across Gate `/BL_SW_G` and Source `/VSYS_BL_SW` and `C92 = 10nF` Miller soft-start, and clamped below `U_BL.3` `SW` `40V` absolute maximum by unidirectional 33V flat-clamping TVS `D35` `ESTVS3300DRVR` `C42400190` [`V_BR = 34.5-37.8V`, `V_CL = 38.0V typ / 39.8V max < 40V`])
- Pin 2: `LED_CATHODE` (`200 mV` current-sense return across `R32 = 1.5R` 1% `C22769`, routed to `U_BL.6` `FB` `/BL_FB` through `R93 = 10 kOhm` `C25744` series overvoltage current-limiting resistor with local 5.1V Zener clamp `D38` `BZT52C5V1S` `C173436` on `/BL_FB` to `/GND`, and ESD-protected at `J_BL.2` by 36V unidirectional ESD diode `D36` `PESD36VS1UJX` `C5205187` rated to survive anode-to-cathode fault transients)

### 2.4 `J_BAT` (Single 9-pin 2.0mm JST-PH 2S2P Battery Pack Connector `S9B-PH-SM4-TB(LF)(SN)`, `C495694`)
- Pins 1, 2, 3, 4: `VBAT_PACK` (4 x 2.0A = 8.0A continuous contact rating, routed through 8A 32V 1206 SMD fuse `F1` `JFC1206-1800FS` `C136353` to `/VBAT` `U_CHG` pins 22/23, protected on `/VBAT` by unidirectional 12V 200W reverse-polarity crowbar / surge TVS diode `D24` `SMF12A` `C123800` to `/GND`, with low-leakage silicon switching diode `D37` `1N4148WS` `C2128` [`I_R <= 25 nA`] blocking reverse battery polarity ahead of `U_RTC.3` `VIN` `/RTC_VIN` [locally decoupled directly at `U_RTC` pin 3 `VIN` by `C57 = 1uF` 50V 0603 `CL10A105KB8NNNC` `C15849`], and `R50 = 100R` 1% `C25076` Kelvin battery positive voltage sense connected from fused `/VBAT` into `U_CHG` pin 18 `BATP`)
- Pin 5: `BAT_TS` (Pack 10k NTC thermistor sense routed through `R87 = 100R` 1% `C25076` adjacent-pin fault current-limiting resistor to `/CHG_TS` `U_CHG` pin 16 `TS`, biased from `REGN` via `R23 = 5.23k` 1% `C11631` / `R42 = 30.1k` 1% `C29402` JEITA divider and clamped by unidirectional 5.0V ESD diode `D19` `PESD5V0S1UA,115` `C179414`)
- Pins 6, 7, 8, 9, 10, 11: `GND` (4 x 2.0A = 8.0A continuous return + grounded mechanical mounting tabs 10 and 11)

### 2.5 `J_KB` (24-pin 0.5mm Keyboard FPC `05A20L24P`, `C5362158`) & `J_TP` (8-pin 0.5mm Trackpad FPC `FPC-05F-8PH20`, `C2856797`)
- `J_KB` Pins 1..8: `KB_ROW0..7` -> `U_KB` (`TCA8418RTWR`) pins 8..1; Pins 9..18: `KB_COL0..9` -> `U_KB` pins 9..18 (all 18 matrix lines protected by four 5-channel 3.3V ESD TVS arrays `D25..D28` `4x PESD3V3L5UY` `C2831531`); Pin 19: `PWR_BUT` (protected by unidirectional 5.0V ESD diode `D9` `PESD5V0S1UA,115` `C179414` and driving CM5 `/CM5_PWR_BUT` `U1.92` via ultra-low-leakage switching diode `D16` `1N4148WS` `C2128`, with `U_CHG.12` `~QON` left unconnected so long `>=10s` power-button presses never trigger unintended BQ25798 HIZ system reset); Pin 20..26: `GND`.
- `J_TP` Pin 1: `GND`; Pin 2: `+3V3_PER` (fed directly from `/+3V3_PER` with `F4` removed, decoupled by `C97 = 100nF` and clamped by `D31` `PESD3V3U1UA,115` `C403915`); Pin 3: `TP_SDA` (isolated from `/I2C_SDA` by N-MOSFET pass switch `Q_TP2` `BSS138` `C52895` gated by `/+3V3_PER`, pulled up to `/+3V3_PER` via `R83 = 2.2k` `C25879`, clamped by `D22` `PESD3V3U1UA,115`); Pin 4: `TP_SCL` (isolated from `/I2C_SCL` by N-MOSFET pass switch `Q_TP1` `BSS138` `C52895` gated by `/+3V3_PER`, pulled up to `/+3V3_PER` via `R82 = 2.2k` `C25879`, clamped by `D23` `PESD3V3U1UA,115`); Pin 5: `TP_INT_N` (`GPIO17` pin 50, pulled up to `/+3V3_PER` via `R18 = 10k`, clamped by unidirectional 3.3V ESD diode `D20` `PESD3V3U1UA,115` `C403915`); Pin 6: `TP_RST_N` (`GPIO27` pin 48, pulled up to `/+3V3_PER` via `R19 = 10k`, clamped by unidirectional 3.3V ESD diode `D21` `PESD3V3U1UA,115` `C403915`); Pins 7..10: `GND`.

---

## 3. Datasheet Rating & 2S 45–65W Power Architecture Verification Checklist

1. **Capacitor & TVS Voltage Ratings (>= 1.5x Max Rail Voltage Across All Rails):**
   - `VBUS_PD` / `CHG_VBUS` / `CHG_PMID` (20.0V USB-C PD operating): Decoupled by 50V-rated `10uF` 0805 (`GRM21BR61H106KE43L`, `C440198`) and `100nF` 50V 0402 (`CL05B104KB54PNC`, `C307331`) capacitors and protected by low-clamping 22V-standoff / 27.7V-clamping surge TVS `D7` (`TVS2200DRVR`, `C2875234`) plus external back-to-back 40V N-MOSFETs `Q3`/`Q4` (`2x SQ2318AES-T1_BE3`, `C2847989`) driven by `U_CHG` `ACDRV1`.
   - `VSYS` / `VBAT` (2S Li-Po 6.0V–8.4V, 8.6V max NVDC): Protected on `/VBAT` after 8A fuse `F1` by unidirectional 12V TVS / reverse-polarity crowbar `D24` (`SMF12A`, `C123800`) with series reverse-blocking low-leakage silicon switching diode `D37` (`1N4148WS`, `C2128`, `I_R <= 25 nA`) feeding `/RTC_VIN` (locally decoupled at `U_RTC` pin 3 `VIN` by `C57 = 1uF` 50V 0603 `C15849`) to protect `U_RTC` (`HT7530S`), and decoupled by 50V-rated `10uF` 0805 (`C440198`) and 25V-rated `22uF` 0805 (`CL21A226MAQNNNE`, `C45783`) capacitors.
   - `LED_ANODE` (~24V backlight boost output): Protected by `1A` `32V` input fuse `F6` (`CFS06V3T1R0`, `C163118`), decoupled by 50V-rated `1uF` 0603 (`CL10A105KB8NNNC`, `C15849`) with 60V Schottky diode `D1` (`B16WS`, `C364278`), and clamped below `40V` by unidirectional 33V flat-clamping TVS `D35` (`ESTVS3300DRVR`, `C42400190`).
   - `+5V`, `+5V_PER`, `+5V_USBC`: Clamped by 5.5V TVS `D3` (`TSD05CDYFR`, `C20611048`) on `/+5V` and unidirectional 5.0V low-clamping TVS diodes `D18` and `D2` (`2x PSD05-LF-T7`, `C139296`) on `/+5V_PER` and `/+5V_USBC`, and decoupled by 25V–50V X5R/X7R MLCCs.
   - `CODEC_AVDD` & `CODEC_HPVDD`: `U_CODEC` (`ES8388`) analog supply `AVDD` (Pin 17) is isolated by dedicated RC filter `R49 = 4.7R` + `C49 = 10uF` + `C50 = 100nF`, while Class-AB headphone driver supply `HPVDD` (Pin 16) is isolated on its own dedicated ferrite-filtered rail `/CODEC_HPVDD` via `FB5` (`BLM18PG121SN1D`, `C14709`) and `C99 = 10uF` (`C440198`).
2. **2S 45–65W Buck-Boost Charger & NVDC Power Path (`U_CHG` `BQ25798RQMR`, `C2876593`):**
   - Takes 5V–20V USB-C PD (`3.6V–24V` operating input, `26V` internal OVP) via `Q3`/`Q4` and charges the 2S2P 7.4V 9,000mAh (`66.6Wh`) pack at `VREG = 8.40V` (`R22 = 8.2k` 1% `C25981` on `PROG` pin 20 selecting 2S default and `750 kHz` switching with `L1 = 2.2 uH` 10A inductor `FXL0630-2R2-M` `C167218`), with hardware `ILIM_HIZ = 2.25A` (`R29 = 78.7k` `C2998104` / `R30 = 100k` `C25741`) for safe 45W startup and `~QON` (`U_CHG.12`) left unconnected (held high by internal `~200k` pull-up to `V_PULL` with `SFET_PRESENT = 0` so long power-button holds on `/PWR_BUT` never trigger unintended BQ25798 10s HIZ reset).
3. **Dual 5V / 6A Synchronous Buck Converters (`U_BUCK` & `U_BUCK2`, `2x TPS56628DDAR`, `C485522`) & `U_UVLO` (`TPS3700DDCR`, `C33002`):**
   - `U_BUCK` (`L2 = 2.2 uH` `FXL0630-2R2-M` `C167218`, `R27 = 137k` `C32298` / `R28 = 24k` `C25769` setting `5.13V`, `EN` pin 1 on `/BUCK_EN` driven by `U_UVLO` `OUTA` with `R33 = 82k` `C4142` / `R34 = 5.1k` `C25905` + `R81 = 1M` setting `V_UVLO_RISE = 6.960V`, `V_UVLO_FALL = 6.535V`) supplies CM5 `/+5V_CM5` via common-source blocking `AO4407A` P-MOSFETs `Q1`/`Q2` (`R84 = 1k` `C11702`, `R59 = 10k` `C25744`, and diode-isolated Miller soft-start network `C98 = 10nF` `C15195` + `D39 = 1N4148WS` `C2128` + `R94 = 22k` `C25768` on `/DBG_MILLER`) in parallel with `U_DBG` (`TPS2117DRLR` `C22399676`, with `C100 = 220nF` `C16772` RC delay filter on `PR1` `/DBG_PR1` [`tau = 2.64 ms >= 1 ms`, delaying `U_DBG` turn-off by `1.07 ms` across the `0.3-0.5 ms` `Q1`/`Q2` soft-start ramp] and co-located pogo-pin test pad cluster `TP1..TP6` at `X = 109.2..115.8 mm, Y = 31.0..37.0 mm`).
   - `U_BUCK2` (`L5 = 2.2 uH` `FXL0630-2R2-M` `C167218`, `R64 = 133k` `C25753` / `R65 = 24k` `C25769` setting `5.00V`, `EN` pin 1 gated by CM5 switched `/+3V3`) supplies `/+5V_PER` for `U_AMP` (`PAM8406DR`), `U_3V3` (`TLV62569DBVR` supplying `/+3V3_PER` directly to `J_DSI.22`, `J_CSI.22`, `J_TP.2`, and `J_AUDR.8` with `F2..F5` removed), and `U_VBUS` (`SY6280AAC` with fixed `R31 = 3.6k` `0402WGF3601TCE` `C25891` setting `1.89A typ` and `EN` synchronized with `usb_left` `TPS25810RVCR` `EN` via `Q5` `BSS138` controlled by `U_UVLO` `OUTB` on `/VBUS_ISET_HI` with `R90 = 47k` `0402WGF4702TCE` `C25792` pull-up to `/+3V3` and co-located `R88 = 80.6k` `0402WGF8062TCE` `C25798` / `R89 = 4.7k` `0402WGF4701TCE` `C25900` + `R97 = 100k` `C25741` / `Q6` `BSS138` `C52895` on `INB-` `/VSYS_THROT`, setting `V_THROT_FALL = 7.160V typ / 7.060V min` and `V_THROT_RISE = 7.582V typ / 7.487V min` (`422mV` hysteresis) to shed `/+5V_USBC` cleanly without relaxation oscillation or UVLO overlap).
