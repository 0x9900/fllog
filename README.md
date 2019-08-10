# fllog

## Log fldigi QSO on MacLoggerDX

This simple program is called from an flgigi macro to log your QSO on
MacLoggerDX. The program name is `fllog`. It communicates with the
logging software through UDP. In order to work the logging software
needs to be running. You also need to enable UDP on the logging
software.


# Installation

```
$ sudo ./install.sh
```

To complete the installation, you need to create a log macro in
fldigi.  Right click on the macro button you use for logging and copy
the following line at the end.

```
<EXEC>/usr/local/bin/fllog</EXEC>
```

As an example, here is the macro I use to end my QSO:

```
<NAME>, Thank you for the QSO on <BAND> / <MODE>.
I look forward to seeing your signal on my waterfall, 73.
QSL: LoTW, DIRECT
<ZDT> <CALL> de <MYCALL> sk
<RX>
<EXEC>/usr/local/bin/fllog</EXEC>
<LOG>
```
