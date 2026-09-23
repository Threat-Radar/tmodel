# spec/vectors/

Published example threat models and test vectors — the interop and regression
contract. A vector is a concrete, worked threat model (or a fragment of one)
expressed in our schema: an asset with a trust boundary, a threat, an attack
path/chain, a mapped CWE/CVE, a mitigation, and its review state.

Vectors are how we prove:

- an imported external format round-trips into our model,
- a risk metric computes the same score everywhere,
- a threat chain renders the same graph everywhere,
- a UI or exporter reads the model without a private side agreement.

Empty until the object model has a first draft (increment I2).
