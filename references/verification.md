# Verification record · 0.1.0

Local verification date: 2026-10-22. This record describes observed results, not universal compatibility.

## Supported and exercised environment

- Windows x64, logged-in WeChat 4.1.15.56 x64.
- WSL Python 3.12 invoking Windows PowerShell, built-in Framework64 C# compiler, and system winsqlite3.dll.
- Full source copied to a new install directory on the Linux filesystem. Build stages only the named sources into the private Windows build directory; no developer paths are required.
- New private root separate from the legacy implementation. Existing legacy config/data/source were left unchanged.
- Native Windows Python, arbitrary Linux/macOS capture, other WeChat versions and other Agent installers were **not** live-validated.

## Observed results

- 45 Python synthetic tests passed, including pre-existing linked output rejection, refusal of a nonprivate saved-snapshot output root, clipped report coverage, >500-message traversal, name ambiguity, exact time bounds, mutation/hash failure, version rollback, cross-scope rejection, CLI invocation from another working directory and runtime setup/build checks.
- Actual Windows compile and both bundled native fixture executables succeeded: six crypto/capture checks and four security regression checks. These are synthetic, not live key/process compatibility tests.
- Fresh live capture in the separately initialized root succeeded for one previously owner-authorized contact/time interval: three matching messages.
- Keyword search, two evidence chunks, current authorized AI analysis, and local report registration succeeded. Report cited all three scoped message IDs. Personal account, name, message bodies, IDs and paths are excluded from this public record.
- Repeating live capture for the same scope returned added=0, updated=0, unchanged=3, missing=0.
- Main-only provenance, nonzero-page HMAC and SQLite integrity are required by the adapter. WAL is intentionally excluded; the three-message result does not prove complete history.
- Fresh dependency installation succeeded with a configured alternate Python package index after the default download timed out. This is an environment/network issue; no alternate model or chat upload was used.

## Clean local installation

The actual Hermes quarantine → community scan → install implementation installed the complete 31-file release manifest into an isolated test home. The installed file set exactly matched the manifest. All 45 synthetic Python tests passed again from the installed location with a different working directory. The fixed installed package also repeated the original live scope successfully (three unchanged messages), created two evidence chunks and registered a hash-verified report with explicit coverage metadata. This exercises local installation; remote GitHub fetch is separately checked after upload.

## Installation scanner

Hermes community-source static scan returned SAFE / ALLOWED after narrowing config access to a named environment variable and isolating the test environment mock. No scanner rules, allowlists, ignores or force overrides were changed. Eight medium informational findings remain: explicit subprocess execution for local compiler/helper/test/package installation and the standard Zstandard magic-byte literal. They are visible rather than suppressed. A passing scanner is not a sandbox, runtime no-egress proof or complete native-code security audit.

All private configuration, captures, evidence and reports remain outside the public package. See security.md for retention and processing boundaries.
