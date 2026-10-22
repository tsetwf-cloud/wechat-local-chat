# Sources and license boundary

The Python business selection/archive/request implementation and this package's orchestration are local implementations. No source or text from the noncommercial `mcncarl/yichen-skills/yichen-wechat-local-vault` was bundled; its Windows detached-snapshot design was surveyed but is not a runtime dependency.

The Config.Cipher runtime layout traversal is adapted from:

- Repository: https://github.com/TANGandXUE/wcdb-key-tool
- Fixed reviewed commit: `79f1b5b92e12c66aa281b4a60a3c478b5f547dfa`
- License: MIT; original notice retained in `THIRD_PARTY_LICENSE.txt`.
- Derived area: `scripts/native/src/Runtime.cs` (memory object discovery/layout); refactored read-only handle use, buffer lifetime, process gates and capture/archive work belong to this package.

The .NET Framework compiler and `winsqlite3.dll` are Windows system components, not redistributed binaries. `zstandard==0.25.0` is obtained separately during setup under its own distribution license; its code/wheels are not vendored here.

SQLite main-database/WAL behavior reference: https://sqlite.org/wal.html . This package intentionally does not merge WAL and makes no fixed-delay completeness claim.

Hermes install/Skill reference: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/ . Installation should retrieve the complete directory including support files, not just the frontmatter document.
