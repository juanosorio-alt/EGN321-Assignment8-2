# Calculation and Recovery Verification

## Original artifact and traceability
The original workbook is preserved byte-for-byte in `original/`. Its SHA-256 and cell ranges are recorded in `original/manifest.json`. Sample inputs come from Inventory!A4:G9. Expected baseline outputs come from the saved calculated values in Reorder Logic!A4:F9. This build inspected formulas and caches; it did not rerun Excel. The earlier Assignment 3.2 audit records separate recalculation scenarios. The application does not use cached expected results as its calculation implementation.

## Known-correct cases
| SKU | Demand (items) | Point (items) | Stock (items) | Reorder | Order (items) |
|---|---:|---:|---:|---|---:|
| P-100 | 24 | 34 | 38 | NO | 0 |
| P-110 | 24 | 30 | 24 | YES | 36 |
| P-120 | 12 | 16 | 9 | YES | 23 |
| P-130 | 10 | 15 | 22 | NO | 0 |
| P-140 | 10 | 13 | 7 | YES | 19 |
| P-150 | 20 | 28 | 42 | NO | 0 |

All six baseline cases match in unit tests and a real HTTP review. Independently, P-110 gives demand 8 items/week × 3 weeks = 24 items, point 24 + 6 = 30, reorder because 24 ≤ 30, and quantity 2 × 30 − 24 = 36. Tests compare the SKU and every original output column.

## Problem or edge case
Change P-130 safety stock from 5 to 20 and retain stock 22, weekly use 5 and lead time 2. Original C7 is `=B7+5`, so it still gives point 15, NO and quantity 0. Under the chosen universal-input policy, demand is 10, point is 30 and quantity is 60 − 22 = 38. This deliberate difference fixes consistency with the editable input, but does not prove the original exception was an unauthorized business rule. Its intent remains unknown.

## Invalid input
For P-110, stock −1 would yield a legacy workbook quantity of 61 under the formula. The new policy excludes backorders and refuses negative stock. It returns HTTP 400 with a field-specific explanation and saves no partial review. Tests also reject nonnumeric, missing, nonfinite, oversized and fractional count values, unsupported units and duplicate SKUs.

## Additional test
Add a new unique SKU and reverse the item order. Recommendations keyed by SKU remain identical. This tests the proposal's risk around row-dependent associations without alleging a production sorting incident. Boundary tests exercise stock below, equal to and above the point. Fractional demand explicitly rounds an order upward to whole items.

## Actual execution evidence
`evidence/unit_tests.txt` contains the executed automated suite. `evidence/live/` includes actual HTTP JSON responses, saved dashboard HTML, file logs, supervisor logs, an SQLite backup and a UTC timeline. HTML is captured output, not a screenshot. Browser screenshots in `evidence/` are from a later UI walkthrough against the same running application, so review IDs/counts may differ from the earlier immutable backup.

The controlled storage marker caused HTTP 503, FAILED state and a refusal to save. Removing only the marker restored HEALTHY. Before/after histories matched exactly. A new review then saved successfully. SQLite integrity_check returned `ok`. This proves the application-level simulation and preservation assertions, not resilience to physical disk damage.

The supervisor then killed its own child through an explicitly enabled local control. PID 45386 changed to 45429, and a healthy response arrived approximately 1.44 seconds after the request. Earlier review IDs persisted. The separate automated SQLite-lock test uses a real write lock and verifies recovery after rollback.

An earlier verification attempt completed the storage phase but could not signal the child directly because of the execution environment's process permission boundary. It was retained in the local work area and excluded from the successful evidence set. The repeat used the documented supervisor control and a fresh runtime. The live evidence is not a classmate handoff.
