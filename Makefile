all:
	echo "Please specify a target"

start-server:
	~/google_appengine/dev_appserver.py --datastore_path=store/data.db --history_path=store/data.db.history ./

next-release:
	cil summary --is-open --label=Milestone-v0.05

open:
	cil summary --is-open

closed:
	cil summary --is-closed

clean:
	find . -name '*~' -exec rm {} ';'

.PHONY: start-server next-release open closed clean
