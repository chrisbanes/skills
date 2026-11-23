# Camera permission

When somebody taps Scan for the first time and denies camera access in the
Android system dialog, the installed app must offer manual entry.

The current `createComposeRule` test renders the denied state and checks that
the manual entry button is shown. The proposed test fakes a denied permission
callback in that same Compose host and labels the result coverage of the system
dialog flow.
