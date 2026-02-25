# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog principles.
Versioning is lightweight and incremental.

---

## [0.2.0] - RF Engine & Requirement-Based Architecture Sweep

### Added
- VDE-SAT uplink RF model
- `is_vdes_sat_uplink_available()` access criterion
- `single_access_vdes.py`
- `local_availability_vdes.py`
- `architecture_sweep_local_rf.py`
- Requirement filtering:
  - `--max-gap`
  - `--min-availability`
- Automatic CSV export to `results/`
- Metadata header in CSV outputs

### Improved
- Architecture sweep now supports RF-based evaluation
- Default station set to sternula (57.02868, 9.94350)
- CLI consistency across examples

### Internal
- Refactored sweep to avoid dependency on GroundStation internals
- Added RF module structure under `sat_sim/rf/`
- Added `vdes_access.py` access layer abstraction

---

## [0.1.0] - Initial Orbital Engine

### Added
- Two-body propagation
- J2 perturbation
- Classical orbital elements (COE)
- Walker constellation generator
- Geometric access computation
- Gap and revisit metrics
- Architecture sweep (geometric)
- Basic CSV export
