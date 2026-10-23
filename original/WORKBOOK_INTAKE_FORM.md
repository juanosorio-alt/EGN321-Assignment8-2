# Workbook Intake Form

## Student
- Name: Juan Osorio
- Course / Section: EGN321
- Date: September 15, 2026

## Workbook
- Original workbook name: `INVENTORY_REORDER_SANITIZED_EXAMPLE.xlsx`
- Sanitized submission name: `INVENTORY_REORDER_SANITIZED_JUAN_OSORIO.xlsx`
- File type: .xlsx
- Number of worksheets: 4, all visible.
- Formula cells: 36, all in `Reorder Logic!A4:F9`.
- Macros present? No. No VBA or macro-sheet parts are present.
- External links present? No external relationships or external workbook links were found.
- Protected sheets/workbook? No.

## Source
- Source: the instructor-provided Assignment 3.2 student package, `examples` folder.
- Organization/process: a fictionalized small family retail/service business managing six stocked items. This is a classroom example, not a workbook collected from my own employer or family business.
- Permission to use a sanitized copy for class? Yes. I confirmed that the instructor allows this supplied example for the assignment. This records my confirmation, not an independently obtained permission letter.
- Primary user: store manager in the supplied scenario. The purchasing assistant prepares orders using the recommendations.
- Real-user limitation: no operational owner was interviewed and no future replacement tester has been identified. These facts must be resolved for a real deployment; the example is being used under the instructor's authorization.

## Purpose
- Process: recurring inventory review and replenishment planning.
- Question: which stocked items should be reordered, and in what quantities?
- Decision: whether to order each item and the proposed quantity to purchase.
- Frequency: weekly in the supplied `EXAMPLE_ONE_PAGE_ANALYSIS.docx`; this was not established through an owner interview.
- Consequences: underordering can cause stockouts and service delays; overordering can tie up cash and storage. These are scenario consequences, not measured losses.

## Inputs

| Input | Meaning | Unit | Source |
|---|---|---|---|
| SKU and item | Item identifier and description | Text | Inventory!A4:B9; fictional course data |
| On Hand | Current available stock | Each/item count | Inventory!C4:C9 |
| Weekly Use | Average consumption rate | Items/week, inferred from heading and workflow | Inventory!D4:D9 |
| Lead Time | Delivery delay | Weeks, explicitly labeled | Inventory!E4:E9 |
| Safety Stock | Additional stock allowance | Items, inferred from additive formula | Inventory!F4:F9 |
| Unit | Item counting unit | Each | Inventory!G4:G9 |

The course package supplies the values. In an operational version they would need stock counts, usage records, supplier lead times, and an approved safety-stock policy. Those operational sources are not documented here.

## Outputs

| Output | Meaning | Unit | Who Uses It |
|---|---|---|---|
| Demand During Lead Time | Weekly use multiplied by lead time | Items | Store manager |
| Reorder Point | Lead-time demand plus stock allowance | Items | Store manager |
| On Hand | Linked available stock for comparison | Items | Manager and purchasing assistant |
| Reorder? | YES when available stock is at or below reorder point | YES/NO | Purchasing assistant |
| Order Qty | Twice reorder point minus available stock when reorder is YES; otherwise zero | Items | Purchasing assistant |

Outputs are in `Reorder Logic!B4:F9`, linked to item identifiers in column A.

## Workflow and Dependencies
Review stock, consumption, lead-time, and safety-stock inputs; inspect the reorder recommendations; prepare purchase orders. Input updates and purchasing actions are manual workflow steps; no automation or order transmission is embedded in this file.

Most rows calculate `reorder point = weekly use * lead time + safety stock`. Row 7 instead adds the fixed number 5. Selection uses direct row references and IF conditions; there are no VLOOKUP, INDEX/MATCH, or other keyed lookups. No SUM/AVERAGE aggregation ranges were found. The two other sheets provide explanatory text and questions.

## Initial Concerns
- Difficult to understand: no rationale for the order-up-to multiplier of 2 or the supplied safety stocks.
- Fragile: row-linked formulas, a hard-coded allowance in C7, and no structured table for adding new items.
- Potentially wrong: changing Inventory!F7 does not affect the row-7 reorder point. The behavior is verified; whether the fixed allowance is intentional remains unknown.
- Validation concern: negative stock is not rejected by the formulas. No worksheet data-validation rules were found.
- Desired improvement: I want to understand how to avoid stockouts and unnecessary purchases through clearer policies, units, input validation, and later testing.

See `INITIAL_RISK_AND_DEFECT_INVENTORY.md` and `AUDIT_EVIDENCE.md` for evidence and limitations.
