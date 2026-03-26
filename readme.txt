
cluster-health-monitor

The script call-api-and-run-script-2.py fetch the clutser's health status 
from health api endpoint api/v1/cloud/healthreport,
analyzes received json and detect weather any of microservices is not healthy.
If status is not healthy the script invokes the script shell-script-red.sh
which prints error content.
If status changes from healthy to unhealthy or from unhealty to healthy it invokes the script shell-script-for-statuschange-2.sh
which sends notifications via email, using mailsend-go binary (from https://github.com/muquit/mailsend-go)
The script call-api-and-run-script.sh can be invoked every 1 minute from cron


Python3 Requirements:
pip3 install requests
pip3 install configobj
