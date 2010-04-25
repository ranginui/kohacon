all:
	echo "Please specify a target"

start-chilts:
	~/google_appengine/dev_appserver.py --datastore_path=store/chilts.db --history_path=store/chilts.db.history ./

start-fact-finder:
	~/google_appengine/dev_appserver.py --datastore_path=store/fact-finder.db --history_path=store/data.db.history ./

next-release:
	cil summary --is-open --label=Milestone-v0.05

open:
	cil summary --is-open

closed:
	cil summary --is-closed

clean:
	find . -name '*~' -exec rm {} ';'

.PHONY: start-server next-release open closed clean
