# Workbook Audit Evidence

Juan Osorio | EGN321 | September 15, 2026

## Source and Preservation
- Source: `examples/INVENTORY_REORDER_SANITIZED_EXAMPLE.xlsx` in the instructor package.
- Submission: `INVENTORY_REORDER_SANITIZED_JUAN_OSORIO.xlsx`.
- Source SHA-256: `6ed094b93f98e53fadb401db660a3001a3aa8750d426e13fda52c791edae5b42`
- Submission SHA-256: `6ed094b93f98e53fadb401db660a3001a3aa8750d426e13fda52c791edae5b42`
- Result: identical bytes. Original workbook, inputs, formulas, formatting, and caches are preserved.

## Structural and Safety Audit

| Area | Finding |
|---|---|
| Sheets | Read Me, Inventory, Reorder Logic, Known Questions; all visible |
| Data | Six fictional item records, Inventory!A4:G9 |
| Formulas | 36, Reorder Logic!A4:F9; all cell values and formula text inspected |
| Hidden rows/columns | None |
| Sheet/workbook protection | None |
| External workbook links and external relationships | None |
| Cell hyperlinks and named ranges | None |
| VBA/macros, embedded objects, connections | No corresponding package parts |
| Comments/notes | No comment/note parts or attached cell comments; visible comments inspected |
| Data validation | No rules on any worksheet |
| Excel structured tables | None |
| Metadata | No docProps core/custom parts; actual ZIP parts inspected rather than treating library-generated defaults as stored metadata |
| Lookups | Direct cross-sheet references and IF comparisons; no keyed lookup functions |
| SUM/AVERAGE ranges | None; no aggregation cutoff issue identified |
| Privacy | Generic role descriptions and fictional item data only; no sensitive content identified |

All sheets were rendered and reviewed. The workbook's visible descriptions and the package's example analysis supplied scenario context; actual usage was not independently established.

## Independent Baseline Reconciliation
For each item: lead-time demand = weekly use × lead time; reorder point = demand + safety stock, except row 7 uses fixed 5; reorder = on hand <= reorder point; quantity = 2 × reorder point − on hand when YES, otherwise 0.

| SKU | Lead-time demand | Reorder point | On hand | Reorder? | Order quantity |
|---|---:|---:|---:|---|---:|
| P-100 | 24 | 34 | 38 | NO | 0 |
| P-110 | 24 | 30 | 24 | YES | 36 |
| P-120 | 12 | 16 | 9 | YES | 23 |
| P-130 | 10 | 15 | 22 | NO | 0 |
| P-140 | 10 | 13 | 7 | YES | 19 |
| P-150 | 20 | 28 | 42 | NO | 0 |

All 36 formula outputs, including the six SKU links, matched both the stored workbook values and a fresh Artifact Tool recalculation. No formula errors were observed in those outputs. This verifies consistency with the supplied formulas, not that the purchasing policies are operationally correct.

## Temporary Input Checks
Each check changed only an in-memory input and restored it afterward. The source and submission files were never overwritten by the calculation engine.

| Check | Change | Observed result | Interpretation |
|---|---|---|---|
| A | Inventory!F7: 5 → 20 | C7=15, E7=NO, F7=0 on Reorder Logic | The row-7 formula ignores that input. Under the general safety-stock policy the values would be 30, YES, and 38; policy intent still needs confirmation. |
| B | Inventory!F5: 6 → 20 | C5=44, E5=YES, F5=64 on Reorder Logic | A normal row responds to the safety-stock change. |
| C | Inventory!C5: 24 → 30 | E5=YES, F5=30 | Equality at the reorder point triggers replenishment. |
| D | Inventory!C5: 24 → 31 | E5=NO, F5=0 | Stock above the reorder point does not trigger replenishment. |
| E | Inventory!C5: 24 → -1 | E5=YES, F5=61 | Negative stock produces a number instead of refusal; acceptable-domain policy is undocumented. |

All five checks matched the predicted formula behavior; the full baseline was rechecked after restoration.

## Scope and Limits
These checks used Artifact Tool, with read-only Python/OOXML inspection and independent arithmetic. They were not run in desktop Excel. No current-row arithmetic mismatch was identified. Business-policy correctness, actual input freshness, new-item insertion, independent sorting, and a real-user handoff remain future investigation topics. No workbook repair, interface, or final Python tool was required or created for Assignment 3.2.
