#!/bin/sh
#
# (C) 2019 Fred C. (W6BSD)
# https://github.com/0x9900/fllog
#

if [[ $(id -u) != 0 ]]; then
    echo "Error: this install script need to be run with root privileges"
    echo "Enter the following line at the prompt to install fllog"
    echo "sudo ./install.sh"
    exit 1
fi

echo
echo "Installing fllog into /usr/local/bin"
/bin/mkdir -p /usr/local/bin
/bin/cp ./fllog.py /usr/local/bin/fllog
/bin/chmod a=rwx,og=rx /usr/local/bin/fllog

cat <<EOF

To complete the installation, you need to create a log macro
containing the following line:

<EXEC>/usr/local/bin/fllog</EXEC>

As an example, here is the macro I use when I am done with my QSO:

<NAME>, Thank you for the QSO on <BAND> / <MODE>.
I look forward to seeing your signal on my waterfall, 73.
QSL: LoTW, DIRECT
<ZDT> <CALL> de <MYCALL> sk
<RX>
<EXEC>/usr/local/bin/fllog</EXEC>
<LOG>

EOF

exit
