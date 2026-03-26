#!/bin/sh

thearg=$1

#-----------------------------------------------------------
#reading variables:
VARFILE="./shell-script-for-statuschange-config.sh"
if [ ! -f "$VARFILE" ]; then
    echo "Config file $VARFILE missing. Exiting right away."
    exit 1
fi
echo "Reading variables from ${VARFILE}"
. ${VARFILE}
#-----------------------------------------------------------



result="Orchid vw-mwtde cluster health statuschange: arg=${thearg}"
message=`tail -1 logfile.log`
echo ${result}

subj="${result}"
uuid=`uuidgen`

echo -n "/usr/local/bin/mailsend-go -smtp ${SMTPSERVER} -port ${SMTPPORT} -t ${TO} -bcc ${BCC} -f ${FROM} -fname \"${ROBOTNAME}\" -sub \"${subj}\" body -msg \"${message}\" auth -user ${SMTPUSER} -pass ${SMTPPASS} header -name Message-ID -value \"<${uuid}@${MESSIDDOMAIN}\" -log mailsend.log" > mailcmd.sh
/bin/sh mailcmd.sh
rm -f mailcmd.sh
