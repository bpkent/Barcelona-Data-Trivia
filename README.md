Barcelona Data Trivia
=========

Welcome! We post a daily factoid on BlueSky about the city of Barcelona, derived from data from the Barcelona Open Data portal.

https://bsky.app/profile/bcndatatrivia.bsky.social


Big picture to do's
-----------
* Implement an LLM gateway (e.g. LiteLLM) to be able to toggle between LLM providers more easily.

* "Info-gathering phase"
    - LLM should generate queries to collect info it needs to answer the final query
    - Needs a little structure in the output to be able to say "done, proceed to final query".
    - Can a reasoning model plan this autonomously??

* Logo on the BSky account
* Explanatory text on the BSky account
    - Including that the info is AI-generated but human curated and reviewed.

* LLM to generate the motivating question too.
    - What context would it need for this?
        - Examples
        - List of table names, descriptions, and field names/descriptions
    
* Explore agent frameworks to see if they make it easier
    - This *is* an agentic flow, after all.
    - LangGraph, PydanticAI, etc.
    - Maybe better branded as "build an agent from scratch"?

* Evaluations

* Ultimately want a fully automated solution.
