## Rendering quality

`Full` keeps the complete Glass treatment. Choose it when visual fidelity is
the priority. `Adaptive` reduces the effect during sustained interaction to
trade some visual detail for steadier performance. Both settings preserve the
same public API; Adaptive remains experimental on Android backdrops.

Adaptive chooses its interpolation from a minimum-pixel threshold, combines a
CPU mask with the backdrop, and restores Full after a 250 ms cooldown.
