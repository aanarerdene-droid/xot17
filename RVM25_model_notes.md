# RVM25 PET reverse vending machine concept

Concept model dimensions: **760 mm wide × 700 mm deep × 1,850 mm high**. The front face points toward negative Y; the floor is Z = 0. Units are millimetres.

## Use in Autodesk Fusion

1. In Fusion, choose **Insert → Insert Mesh** and select `RVM25_reverse_vending_machine_color.3mf`.
2. If Fusion overrides the imported colors, open **Preferences → Material** and turn off **Apply a Different Appearance**.
3. The 3MF is a faceted color mesh. The `.stl` is a monochrome fallback; the `.scad` source includes the colored design and QR panel.

The front QR panel is also provided as `RVM25_machine_QR.svg`. Its QR payload is the demo machine ID `LW-024`. It marks where phone pairing belongs, but it is not a live connection yet: the rewards app needs a hosted URL or installed-app link and a backend before phones can pair with a real machine. Replace the machine-ID payload with the deployed pairing URL when that service exists.

The model shows a PET intake, screen and controls, collection-bin window, service door, status light, vents, header, feet, and QR panel. It is a visual concept, not a manufacturing drawing; internal conveyor, compactor, electrical parts, and structural details are not modeled.
