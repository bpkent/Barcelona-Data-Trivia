
Evaluations for the LLM-based parts of the Barcelona Data Trivia Bot
===========

Brainstorm
--------
- Need real inputs: natural language question, table metadata
    - Maybe use the questions I've already done so far?
    - Maybe collect these as I go?
    - But old results could be wrong, so need to compute myself.
        - (I can be wrong too!)
- Evaluate:
    - Is the SQL valid?
    - Is the SQL valid after removing markdown backticks?
    - Does the SQL execute?
    - Is the answer correct? (accuracy)
        - Need a per-field definition of correctness
        - And aggregation to a single accuracy
- To get the correct answer, I'll need to write SQL as well. Any point in comparing the LLM SQL to my SQL?

- Start with 5 test cases
    - For now, assume all happy path because no input from outside sources, only me.

- Need to start logging the runs
    - To log file, JSON, or DB? Log file easiest to write, JSON probably easiest to access programmatically.

- Does the table info need to be part of the test cases or can it be computed from the table on the fly?
    - Risky to compute on the fly, if the metadata changes.
    - But the table can change too...
    - Maybe simpler to start by computing on the fly, then think about freezing when the test case is written.