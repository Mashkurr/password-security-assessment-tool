# Common-password blocklist

`common_passwords.txt` is the `10k-most-common.txt` corpus from the SecLists
project maintained by Daniel Miessler and contributors:

https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt

- Retrieved: 12 November 2026
- Non-empty entries: 10,001
- Unique entries after case-insensitive normalization: 10,001
- Licence: MIT, as distributed by the SecLists repository

The application loads the file at startup, removes blank lines, normalizes
entries with Unicode-aware `casefold()`, and performs an exact local match.
The file is not supplied or endorsed by NIST. NIST SP 800-63B-4 defines the
types of values that verifiers should block, while the implementer is
responsible for selecting and maintaining an appropriate corpus.

## Update procedure

Before a release, retrieve the current upstream file, replace
`common_passwords.txt`, verify the source and licence, record the retrieval
date above, run `pytest -q`, and review any expected-score cases affected by
the updated corpus. A larger or organization-specific blocklist may be used,
but its source, size and update date must be documented.
