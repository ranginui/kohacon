start-server:
	google_appengine/dev_appserver.py --datastore_path=store/data.db --history_path=store/data.db.history ./

issue-summary:
	cil summary --is-open --label=Milestone-v0.04

issue-list:
	cil list --is-open --label=Milestone-v0.04

clean:
	find . -name '*~' -exec rm {} ';'

.PHONY: start-server upload update-indexes issue-summary issue-list
