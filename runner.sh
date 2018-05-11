#!/bin/bash
osascript -e 'tell app "Terminal"
    do script "cd /Users/r3m1x/Developer/OS_multi && python3 mysql_insert.py"
end tell'

osascript -e 'tell app "Terminal"
    do script "cd /Users/r3m1x/Developer/OS_multi && python3 main.py"
end tell'
