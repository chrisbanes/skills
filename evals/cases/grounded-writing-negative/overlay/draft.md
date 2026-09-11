# Adaptive quality technical report

The device matrix covers Pixel 8, Pixel 6, and a low-end reference device. For
each device, capture p50 and p95 frame time during the scrolling trace.

Adaptive uses minimum-pixel interpolation, a CPU mask for backdrop sampling,
and a 250 ms cooldown before restoring Full. Retain these details so a
regression can be traced to the implementation stage that changed.
