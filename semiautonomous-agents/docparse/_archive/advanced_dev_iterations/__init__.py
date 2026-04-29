"""Advanced precision techniques held out of the default pipeline.

Each module here implements one technique the research recommended but that
the default pipeline doesn't use, because the cost/benefit only makes sense
when the cheaper validators in `docparse.validators` aren't catching enough.

To enable them you can either:
  - Import + call directly from a custom orchestrator, or
  - Run the alternative pipeline `pipeline_premium.py` which wires them all
    together for benchmark / A-B testing.

Modules:
  - judge.py       : render extracted chart back via Vega-Lite, ask a
                     different model family "do these match?"
  - multivote.py   : run the value pass N times, take median per cell
  - setofmark.py   : overlay numbered marks on chart elements before sending
                     to the value pass (anchors VLM attention)
  - pipeline_premium.py : wires everything together for evaluation runs
"""
