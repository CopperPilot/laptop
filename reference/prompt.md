Build a thin laptop like the one in these photos: aluminum chassis, clean keyboard, thin display, big
trackpad, similar dimensions. Use a Raspberry Pi Compute Module 5 as the brain; our main PCB is a small
carrier board that handles the module, keyboard, trackpad, USB-C charging and data, speakers, mic,
headphone jack, a lid sensor and a webcam above the display. Ports: 2 USB-C on the left, 1 headphone jack on
the right. Focus on battery life (standard LiPo packs fill the rest of the body). Daughter boards connect to
the main board with ribbon cables. Every part must be real and assemblable by JLCPCB.

It must open and close like a laptop: the lid carries the display and webcam on real torque hinges, and the
build video must show it opening and closing. Show every ribbon cable and how it connects: display to the main
board through the hinge, keyboard and trackpad to the main board, daughter boards to the main board, and the
battery. The USB-C ports and headphone jack must be visible on the edges.

Decisions already made:
- Keyboard: a bought laptop keyboard module (scissor switches, printed legends, FPC tail into the carrier
  board). Specify it in detail from a dimensioned drawing (outline, key layout, mounting tabs, tail position,
  pin count and pitch) so the assembly and collision checks are real. Every key's legend must be readable.
- Hinge: a pair of bought laptop torque hinges.
- Battery: standard LiPo packs with their wire lead into a board connector (no ribbon needed there).
- USB-C: the front-left port is the charging port (USB-C PD sink, about 45-65 W, using one integrated PD charger
  chip with its reference design) and also carries data; the second left port is data plus 5 V out for
  accessories. Both look identical on the edge.

Owner feedback on run i11:
- **Battery.** Fill the base with battery the way the reference's teardown does. Use several flat Li-Po cells in
  parallel around and under the trackpad; empty floor is wasted runtime.
- **CM5 flashing port.** Put it on test or pogo pads, or behind a service opening. Never a USB-C buried inside the
  case.
- **CM5 model.** Use the real module model from `rea-hw ref cm5`.
- **Cables.** The display and camera cables run inside the lid, behind the bezel, never along its outside edge.

Owner feedback on run i12:
- **Battery: 2S, not 1S.** Re-arrange the battery as 2S2P (7.4 V nominal, 6.0-8.4 V) so it still fills the base around
  and under the trackpad. It stays one bought pack: four identical cells (same part number) joined by the pack maker,
  with one 2S protection board, balance lead, NTC and one connector, as laptop packs are made. Model its real shape
  around the trackpad; the board only needs the pack connector and the charger's battery sense.
- **Charging: real 45-65 W.** Use one buck-boost charger that takes 20 V USB-C PD and charges 2S (BQ25798 class:
  3.6-24 V input, 1S-4S, 5 A charge, NVDC power path), sized for at least 45 W from a 20 V / 2.25-3.25 A contract.
  Keep one autonomous PD sink that asks for 20 V (CH224 class); no I2C PD controller unless the design needs it.
- **No battery bypass.** Remove the Q_BAT1/Q_BAT2 bypass stage. At 2S the system current fits through the charger's
  own battery FET; check that against the charger datasheet at peak CM5 + display + speaker load.
- **5 V rail from 2S.** Make +5 V (CM5 at 5 A) with a buck from VSYS (6-8.4 V), not a boost.
- **Bottom shell.** No through-cutouts that expose parts: use pockets on the inside of the shell for tall components.
- **Lid.** The lid-sensor magnet sits in a blind pocket; no hole through the lid's outer skin.
