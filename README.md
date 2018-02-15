# Proof of work exercise

Write two methods, one called `mint` and one called `verify`.

* `mint`
  - Mint should take two arguments: a `challenge` (random integer) and a `work_factor` (number of leading 0s in the hash).
  - It should return a `token`, which is a random string such that SHA2(`challenge` || `token`) starts with at least `work_factor` many 0s.
  - Use hex encoding rather than binary encoding for simplicity. (You'll want no more than 4 for your work factor.)
* `verify`
  - This should take three arguments: the `challenge`, the `work_factor`, and the `token`.
  - It should return `true` or `false` based on whether the token is valid.

Bonus: if you have extra time, add timestamping and implement a cache of recent tokens so that that double-spends are rejected.


<hr>

# Merkle tree exercise

* Generate a Merkle tree given the following body of data, using SHA-2 as your hashing algorithm
  - Your data is the following blocks:
  - "We", "hold", "these", "truths", "to", "be, "self-evident", "that"
* In the internal stages, concatenate blocks as so "#{blockA.hash}||#{blockB.hash}" <b><-Be sure to use this exact string format</b>
* Do not use any special padding for leaf vs internal nodes
* The merkle root should be equal to `c4f66b2f97c9fb2fcb58b08b4f260d396b5c972ff4948c7deccc81fa34db1a44`

Bonus: create a padding scheme so that arbitrary numbers of blocks can be Merkleized.

Bonus 2: add different padding to the leaves as opposed to internal nodes, so that preimage attacks are impossible.

Bonus 3: implement an interface for Merkle proofs. Have a `prove_inclusion(block)` function and a `verify_inclusion(proof, merkle_root)` function.
