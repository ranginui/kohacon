#!/bin/bash

if [ -z "$1" ]; then
    echo 'Please provide an app to deploy'
    exit 2
fi

if [ -z "$2" ]; then
    echo 'Please specify a command:'
    echo ' - update'
    echo ' - update_indexes'
    echo ' - vacuum_indexes'
    echo ' - update_queues'
    echo ' - update_cron'
    exit 2
fi

APP="$1"
COMMAND="$2"

echo "Performing '$COMMAND' on '$APP'"

case "$APP" in
    chilts)
        echo "Hi Chilts"
        APP=website-chilts-org
        ;;
    lollysite)
        echo "Main Lollysite site"
        ;;
    *)
       echo "Unknown site"
       exit 2
       ;;
esac

# setup the app.yaml for this application
sed -i.orig "1,1s/^application: lollysite$/application: $APP/" app.yaml

case "$COMMAND" in
    update|update_indexes|update_queues|update_cron)
        echo "Doing $COMMAND"
        ~/google_appengine/appcfg.py $COMMAND ./
        ;;
    request-logs)
        echo "Doing update"
        ~/google_appengine/appcfg.py request_logs ./ logs/access-$APP.log
        ;;
    *)
        echo "Unknown command"
        ;;
esac

# put the normal app.yaml back
sed -i.last "1,1s/^application: .*$/application: lollysite/" app.yaml
