"""Operator judgement prompts: proposals only, not attributed Human statements."""
def prompts():
 return {"status":"HUMAN_REVIEW_REQUIRED","entries":[
  {"id":"J01","topic":"Why B-002 was not advanced to production D","evidence_to_check":"C qualification and D production gate","human_statement":None},
  {"id":"J02","topic":"Why released C strategy logic was preserved during runner optimization","evidence_to_check":"strategy release hash and bounded-history equivalence status","human_statement":None},
  {"id":"J03","topic":"Why D/E sandbox outcomes cannot authorize production","evidence_to_check":"D/E sandbox evidence and governance checks","human_statement":None},
  {"id":"J04","topic":"Why expensive validation was interrupted or deferred","evidence_to_check":"C run log and recorded Human decision","human_statement":None}
 ],"note":"Topics are prompts derived from project work, not verified Human decisions. Human must approve or rewrite."}
