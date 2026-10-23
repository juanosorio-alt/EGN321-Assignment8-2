# Demonstration and Code Defense Preparation

## Suggested 8–10 minute sequence
1. **Original artifact, 1 minute:** Open the workbook. Explain inputs and outputs using P-110. Show C7's fixed allowance and the absence of input validation described in the audit.
2. **Journey and architecture, 1 minute:** Explain the inventory proposal and separate temperature course exercises. Identify logic.py, app.py, SQLite and the supervisor. Do not claim temperature measurements are inventory inputs.
3. **Normal operation and original comparison, 2 minutes:** Load the workbook sample, calculate and save. Verify P-110's 24/30/36 result independently. Show historical review and CSV export.
4. **Refusal and edge case, 1 minute:** Set P-110 stock to −1. Explain why refusal is safer under the stated no-backorders policy. Restore 24, then set P-130 safety stock to 20 and verify order 38. Explain the intentional policy difference.
5. **Evidence and recovery, 2 minutes:** Show the test output. Follow README section 12 to create the outage marker, refresh, attempt a save, inspect FAILED and logs, remove only the marker, refresh and verify prior history/new save. Use the recorded process-restart timeline as additional evidence.
6. **Handoff, assumptions and limitations, 1–2 minutes:** Until the real session occurs, state that handoff remains pending. Afterward explain actual obstacles and the two changes made. Explain multiplier, units and lack of production validation.

## File map for rehearsal
| Instructor request | Location | Verification |
|---|---|---|
| Change order multiplier | logic.py ORDER_MULTIPLIER | Recompute expected quantities; run relevant tests; baseline equivalence changes intentionally |
| Change numeric bound | logic.py MAX_INPUT | Test just below, at and above the new boundary |
| Add a validation rule | logic.py number/calculate | Add valid and invalid cases; verify the API saves nothing on refusal |
| Change a visible label | templates/index.html | Reload browser and inspect the result |
| Add a log field | app.py event or REVIEW_SAVED call | Save a review and inspect /api/events |
| Change startup port | INVENTORY_PORT environment variable | Start on an unused port and open the matching URL |
| Change restart delay | supervisor.py RESTART_SCHEDULED and time.sleep | Keep log and actual delay consistent; run recovery verification |
| Change a test | test_inventory.py | Explain the independent expected outcome before running it |

## Questions to practice answering
**Why use Decimal?** It avoids ordinary binary floating-point arithmetic in the core rule. Inputs still require validation and outputs use ordinary JSON numbers for display.

**Why is the transaction atomic?** All input rows validate first. One serialized review is then inserted in one SQLite transaction. Invalid input never saves a partial review.

**Why retain old reviews?** They preserve what inputs and policy produced a recommendation at a particular UTC time. Editing creates another review.

**Does HEALTHY mean the inventory is correct?** No. It means the application can access/write its storage. Source truth and business freshness remain human responsibilities.

**What changed from row 7?** Every item now uses its explicit safety-stock input. This is a documented classroom policy choice, not confirmation of the original business intent.

**Why not silently convert units?** A number labeled packs or days needs an explicit conversion and validated context. The current application supports only each and weeks.

**What does the restart test prove?** The supervisor can restart its terminated child locally and retain committed reviews. It does not prove recovery after power loss, corruption or supervisor failure.

**Can the tool place an order?** No. It proposes a quantity for human review only.

Practice independently before class. The assignment prohibits AI during the live code challenge and defense. This guide is preparation, not assistance to use during that challenge.
