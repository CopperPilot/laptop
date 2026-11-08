# Build film review

A separate agent watches the build film frame by frame and says what would confuse a viewer: parts passing through each other or flying the wrong way, the product resting upside down or with its face hidden, flicker, a camera inside a part. It can change the film's direction (how the product rests, where the viewer stands, which way parts back out), and the film is re-rendered and watched again. Automatic checks replay every frame against the 3D models as well.

**Verdict:** pass (round 1). A clear, well-framed build film of the 13-inch aluminum CM5 laptop that opens and closes in a natural desktop orientation and cleanly shows the exploded layers, main board population, internal battery and sub-board layout, cable routing, and final reassembly.

| Severity | Time | Shot | What a viewer sees | Fix |
|---|---|---|---|---|
| P2 | 40.2 s | close_up | As the top deck, keyboard, and trackpad descend back into place, the orange trackpad ribbon cable remains briefly visible through the keyboard and trackpad until the trackpad finishes settling at 40.9s. | Clip or hide internal cables under the top deck once the top deck settles, or lower the trackpad cable routing Z height slightly. |

