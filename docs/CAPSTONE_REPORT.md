# Capstone Delivery
## Juan Pablo Osorio

## 1. What I inherited
The instructor-authorized inventory workbook represents a fictional six-item replenishment process. Inputs are stock, weekly use, lead time and safety stock. Outputs are demand during lead time, reorder point, YES/NO and proposed order quantity. The source artifact and original audit are preserved in `original/`.

## 2. What I built
The final application implements this inventory workflow in reusable Python logic and a local Flask interface. It validates inputs before computing, keys records by SKU, stores complete dated reviews in SQLite and exports CSV. The temperature-monitoring assignments were separate exercises. They contributed architecture experience rather than inventory measurements or a directly equivalent calculation.

## 3. Calculation proof
All six original saved workbook cases match the application. P-110 independently gives demand 24, point 30 and order 36. The edge case changes P-130 safety stock to 20: the new policy yields point 30 and quantity 38, while the fixed-5 workbook formula remains at point 15. Negative stock is refused. Added/reordered items retain their SKU associations. `VERIFICATION.md` provides the complete table and evidence paths.

## 4. Normal operation
The operator loads the workbook sample, edits inputs if needed and selects Calculate and save review. The interface displays calculation components and the quantity, records a review ID and timestamp, and supports inspection of earlier reviews. Recommendations require human review before a purchase.

## 5. Refusal
A negative count produces a field-specific refusal and no partial record. Other unsupported values or units are rejected. Refusal prevents a plausible-looking quantity from masking an invalid assumption, particularly because this policy does not support backorders.

## 6. System evidence
The automated suite, HTTP results, database backup and browser captures are included. Evidence is generated from this application. The source baseline uses preserved cached workbook results plus independently checked arithmetic; no fresh Excel-engine recalculation is claimed for this build.

## 7. Failure and recovery
The controlled storage outage blocks saves and reports FAILED. Removing only the marker restores HEALTHY without deleting reviews. A real SQLite-lock automated test verifies that a write conflict is also refused and can recover. A separate supervised child termination changes PID and preserves history, with approximately 1.44 seconds to a healthy response in the recorded run. These checks have bounded scope and do not establish physical storage reliability.

## 8. Handoff
The partner test is intentionally deferred until the final application and guide are ready. No partner results or post-handoff improvements are reported. The inventory-specific handoff procedure is provided. At least two changes based on actual observations and the reflection remain necessary after the session.

## 9. Assumptions
Amounts use each, items/week and weeks. Demand is deterministic. The multiplier 2 is retained as a stated classroom assumption. Every item uses its supplied safety stock. Orders round upward to whole items. Backorders are excluded. These choices need review before real business use.

## 10. Limitations
There is no physical stock verification, supplier integration, live inventory feed, authentication, purchase execution or demonstrated multi-user deployment. Stock snapshots can become outdated without the system knowing it. Technical bounds do not establish economically appropriate quantities. Production-grade deployment and retention policies remain outside scope.

## 11. AI usage
Codex assisted code, tests, documentation and presentation preparation. `AI_LOG.md` records tasks, accepted work, modifications and verification. The student must understand the code and independently complete the live defense.

## 12. Presentation
The eight-slide PowerPoint includes speaker notes and the application's actual screen output. `DEMO_AND_DEFENSE.md` provides the 8–10 minute sequence covering normal operation, original comparison, refusal, evidence and recovery. The handoff slide accurately states the pending status and must be revised after that session.

## 13. Live code challenge
Preparation maps likely changes to calculation policy, validation, labels, logging and configuration. Tests should change only when their expected behavior intentionally changes; passing tests alone is not an explanation of correctness. The live challenge has not occurred and must be performed without AI under the instructor's rules.
