start-server:
	../google_appengine/dev_appserver.py --datastore_path=store/data.db --history_path=store/data.db.history ./

upload: update-indexes
	../google_appengine/appcfg.py update ./

update-indexes:
	../google_appengine/appcfg.py update_indexes ./

commit:
	git commit -m 'Update of generated files' index.yaml

clean:
	find . -name '*~' -exec rm {} ';'

.PHONY: start-server upload update-indexes
