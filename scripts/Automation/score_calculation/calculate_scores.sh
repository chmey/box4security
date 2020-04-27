#!/bin/bash

DIR=$(echo "/home/amadmin/box4s/scripts/Automation/score_calculation")

# Get the data for the alert score
curl -s -H "Content-type: application/json" -X POST http://localhost:9200/_sql --data-binary @$DIR/res/alert_score.json > $DIR/alert_score_result.json

# Get the data for the vuln score
curl -s -H "Content-type: application/json" -X POST http://localhost:9200/_sql --data-binary @$DIR/res/vuln_score.json > $DIR/vuln_score_result.json

# Calculate the alertscore and post it to elasticsearch
EPOCHTIMESTAMP=$(($(date +%s%N)/1000000))
ALERTSCORE=$(python3 $DIR/calculate_alert_score.py)
VULNSCORE=$(python3 $DIR/calculate_vuln_score.py)
ITSECSCORE=$(echo "scale=2; ($ALERTSCORE + $VULNSCORE) / 2" | bc)

echo "Alertscore: $ALERTSCORE"
echo "Vulnscore: $VULNSCORE"
echo "IT-Sec-Score $ITSECSCORE"

cp $DIR/res/insert_template.json $DIR/insert_alert_score.json
sed -i 's/%1/alert_score/g' $DIR/insert_alert_score.json
sed -i "s/%2/$ALERTSCORE/g" $DIR/insert_alert_score.json
sed -i "s/%3/$EPOCHTIMESTAMP/g" $DIR/insert_alert_score.json
curl -s -H "Content-type: application/json" -X POST http://localhost:9200/scores/_doc --data-binary @$DIR/insert_alert_score.json

cp $DIR/res/insert_template.json $DIR/insert_vuln_score.json
sed -i 's/%1/vuln_score/g' $DIR/insert_vuln_score.json
sed -i "s/%2/$VULNSCORE/g" $DIR/insert_vuln_score.json
sed -i "s/%3/$EPOCHTIMESTAMP/g" $DIR/insert_vuln_score.json
curl -s -H "Content-type: application/json" -X POST http://localhost:9200/scores/_doc --data-binary @$DIR/insert_vuln_score.json

cp $DIR/res/insert_template.json $DIR/insert_itsec_score.json
sed -i 's/%1/itsec_score/g' $DIR/insert_itsec_score.json
sed -i "s/%2/$ITSECSCORE/g" $DIR/insert_itsec_score.json
sed -i "s/%3/$EPOCHTIMESTAMP/g" $DIR/insert_itsec_score.json
curl -s -H "Content-type: application/json" -X POST http://localhost:9200/scores/_doc --data-binary @$DIR/insert_itsec_score.json

# Delete all temp data
rm $DIR/alert_score_result.json
rm $DIR/vuln_score_result.json
rm $DIR/insert_alert_score.json
rm $DIR/insert_vuln_score.json
rm $DIR/insert_itsec_score.json
