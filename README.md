# fllog

## Log fldigi QSO on MacLoggerDX

This simple program is called from a flgigi macro to log your QSO on
MacLoggerDX. The program name is `fllog`. It communicates with the
logging software through UDP. To work the logging software
needs to be running. You also need to enable UDP on the logging
software.

For more information on how to use that program go to
https://0x9900.com/logging-on-macloggerdx-with-fldigi/

## Installation

```
$ sudo ./install.sh
```

To complete the installation, you need to create a logging macro in
fldigi.  Right-click on the macro button you use for logging and copy
the following line at the end.

```
<EXEC>/usr/local/bin/fllog</EXEC>
```

## Usage

Running the program fllog with the option `--help` will give you the
complete list of options.

`--ipaddress <ipaddr> | -i <ipaddr>` Specify the IP address of the
computer running MacLoggerDX. By default the IP is 127.0.0.1.

`--port <portnum> | -p <portnum>` Specify the port number where
MacLoggerDX is listening for adif packets. By default the port is
2237.

`--debug | -d` This option is only for debugging purpose. All the
fldigi variable will dump in the fldigi input the screen. Be careful
playing with this option since you might send all your environment
over the air. As an example, here is the macro I use to end my QSO:


## Macro example

```
<NAME>, Thank you for the QSO on <BAND> / <MODE>.
I look forward to seeing your signal on my waterfall, 73.
QSL: LoTW, DIRECT
<ZDT> <CALL> de <MYCALL> sk
<RX>
<EXEC>/usr/local/bin/fllog</EXEC>
<LOG>
```
