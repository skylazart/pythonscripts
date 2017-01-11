#!/bin/bash

# Felipe Cerqueira - FSantos@trustwave.com
# Cauan Guimaraes - CGuimaraes@trustwave.com
# Dec 2016

# Proxy connections to burp
export http_proxy=http://localhost:8080
export https_proxy=http://localhost:8080

EXPECTED_RESULT="200 OK"
LOGNAME=session_$$.log


for delay_minute in 0 1 6 12 22 30; do
    delay_second=$(( delay_minute * 60 ));
    echo "`date` - sleeping for $delay_second second(s) or $delay_minute minute(s)";
    sleep $delay_second
    
    echo "`date` - sending request";

    exec 2>&1 > $LOGNAME
    
    # Curl  command goes  here. Using  an authenticated  request,
    # right-click  and  select  "Copy as  curl command"


    # End
    
    
    exec 1>&0
    exec 2>&0
    
    grep "$EXPECTED_RESULT" $LOGNAME > /dev/null
    
    if [ "$?" != "0" ]; then
        echo "`date` - session expired!!!"
        break
    else
        echo "`date` - session still alive"
    fi
done

rm $LOGNAME
