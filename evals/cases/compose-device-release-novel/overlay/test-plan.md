# Startup after changing keep rules

Startup reaches the Compose home screen on debug builds. On the previous
R8-optimized release build, an entry point loaded at runtime was stripped and
the app crashed before reaching home. The keep rule has been corrected.

The proposed regression check extends the existing debug activity integration
test with a second home-screen assertion. Startup stays within the app.
