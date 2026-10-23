# Initial Risk and Defect Inventory

Juan Osorio | EGN321 | September 15, 2026

This is an initial audit of the instructor-authorized synthetic example. Observations and verified behavior are distinguished from unconfirmed business defects. No formulas were repaired.

| ID | Worksheet / Area | Observation | Why It May Be a Problem | Evidence Available Now | Priority |
|---|---|---|---|---|---|
| R-01 | Reorder Logic!C7; Inventory!F7 | C7 uses `=B7+5`; other rows reference the safety-stock input. | A changed safety-stock input can be ignored, potentially suppressing a needed order. | Confirmed formula inconsistency. In a temporary recalculation, raising F7 from 5 to 20 left C7 at 15 and E7 at NO. Under the general policy, the threshold would be 30 and the order quantity 38. Whether an intentional fixed policy applies is unverified. | High |
| R-02 | Reorder Logic!F4:F9 | Order quantity targets twice the reorder point. | The fixed multiplier may overstock some items or fail to cover the actual review period, order constraints, or demand variation. | All six formulas use `C[row]*2-D[row]` when reorder is YES. No supporting policy is documented. This is an unvalidated assumption, not a proven incorrect multiplier. | High |
| R-03 | Inventory!C4:F9 | No input-validation rules; arithmetic accepts negative stock. | Invalid stock counts can produce plausible purchasing recommendations. | Zero validation rules found. Temporary C5=-1 produced YES and an order quantity of 61. Whether negative stock represents allowed backorders is unspecified. Rejection requirements need confirmation. | High |
| R-04 | Inventory!D3:G9; Known Questions!A5:C5 | Lead time is labeled weeks; weekly use and safety-stock units depend partly on interpretation. Known Questions answers unit consistency with “Mostly.” | Values entered in days, packs, or another unit could distort reorder points. | Existing headings and units are visible. No current numeric unit mismatch has been proven; the unresolved note warrants investigation. | Medium |
| R-05 | Inventory and Reorder Logic rows 4–9 | Formulas reference fixed matching row numbers; no Excel structured table or keyed lookup exists. | Adding or independently sorting items could omit calculations or misalign inputs and outputs. | Direct row references and absence of structured tables confirmed. New-row and sorting failures have not been tested. | Medium |
| R-06 | Inventory!D4:F9; Known Questions!A4:C4 and A8:C8 | Safety-stock sources and update procedures are not recorded. The update-owner answer says “Known” but names no role. | Stale demand, delivery, or policy inputs may drive wrong decisions and complicate handoff. | No timestamp, update procedure, or documented policy source is present in the inspected workbook. Actual input staleness is not proven. | Medium |

## Proposed Investigation Backlog
1. Confirm whether the fixed allowance in row 7 is intentional; define the accepted safety-stock policy before changing it.
2. Establish the order-up-to policy, review period, and any minimum-order or pack-size constraints.
3. Specify allowable input types, units, missing-data behavior, and whether negative counts represent backorders.
4. Test new-item additions and independent sorting on disposable copies.
5. Identify an eventual reviewer and document input ownership, data sources, and update frequency.

## Audit Boundary
No production losses, owner interviews, real supplier constraints, or confirmed unit-conversion errors are claimed. The five recalculation scenarios in `AUDIT_EVIDENCE.md` are exploratory checks, not a finished capstone test suite. Baseline example values were restored after each check and the submitted workbook remains unchanged.
