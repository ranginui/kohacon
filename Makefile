start-server:
	~/google_appengine/dev_appserver.py --datastore_path=store/data.db --history_path=store/data.db.history ./

next-release:
	cil summary --is-open --label=Milestone-v0.05

open:
	cil list --is-open

closed:
	cil list --is-open --label=Milestone-v0.05

clean:
	find . -name '*~' -exec rm {} ';'

.PHONY: start-server next-release open closed clean
