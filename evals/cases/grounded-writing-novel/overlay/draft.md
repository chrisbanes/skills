## Rendering quality

`Full` uses the complete effect. `Adaptive` samples every 12 pixels, builds a
CPU mask for the backdrop, and waits for a 250 ms cooldown before restoring
Full. It is experimental on Android backdrops.
