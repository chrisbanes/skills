Fix navigation delivery for exactly one UI consumer. An event emitted while that consumer is briefly absent must wait for it rather than disappear; broadcast delivery is not required.
