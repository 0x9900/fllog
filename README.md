# fllog

## Log fldigi QSO on MacLoggerDX

This simple program is called from a fldigi macro to log your QSO on
MacLoggerDX.

The program `fllog` can log QSOs to MacLoggerDX locally or through the network.

For more information on how to use that program, go to
https://0x9900.com/logging-on-macloggerdx-with-fldigi/

## Installation

```
$ pip install fllog
```

Once the program is installed, you must create a [macro][1] in fldigi to log the QSO.

```
<EXEC>/usr/local/bin/fllog pipe</EXEC>
```
 > Replace `/usr/local/bin` with the path to the program.

## Usage

Running the program `fllog` with the option `--help` will give you the
complete list of options.

```bash
$ fllog --help
usage:
fllog [pipe | udp]

This program is a companion program to log from fldigi to MacLoggerDX.

Create a macro "LOG" in fldigi with the following line:
<EXEC>/usr/local/bin/fllog [mode]</EXEC>

 > Replace /usr/local/bin with the path to the program.

The mode can be either "udp" or "pipe"
For more information, call "fllog --help" on a terminal

For example:
<EXEC>/usr/local/bin/fllog udp --ipaddress 127.0.0.1 --port 2237</EXEC>

fldigi to MacLoggerDX logger

positional arguments:
  {pipe,udp}
    pipe                The log will be sent using a pipe command
    udp                 The log will be sent using UDP

options:
  -h, --help            show this help message and exit
  -a ADIF, --adif ADIF  Backup the log entries into an AIDF file
  -d, --debug           Dump the fldigi environment variables

```

The arguments for the subcommand udp are:

```bash
options:
  -h, --help            show this help message and exit
  -i IPADDRESS, --ipaddress IPADDRESS
                        Macloggerdx ip address [default: 127.0.0.1]
  -p PORT, --port PORT  Macloggerdx port number [default: 2237]
```

## Macro example

```
<NAME>, Thank you for the QSO on <BAND> / <MODE>.
I look forward to seeing your signal on my waterfall, 73.
QSL: LoTW, DIRECT
<ZDT> <CALL> de <MYCALL> sk
<RX>
<EXEC>/usr/local/bin/fllog pipe</EXEC>
<LOG>
```

The following example is the macro I use on my Linux machine to log the fldigi contact to MacLoggerDX running on my Mac.

In the following example, `fldigi` logs the contact to the machine `192.168.10.175`, using the default port, and also saves the contacts into the file `/home/fred/logbook.adif`.

 > _Note:_ The arguments `--adif` and `--debug` are global arguments and need to be placed before the mode (pipe|udp).

```
<NAME>, Thank you for the QSO on <BAND> / <MODE>.
I look forward to seeing your signal on my waterfall, 73.
QSL: LoTW, DIRECT
<ZDT> <CALL> de <MYCALL> sk
<RX>
<EXEC>/usr/local/bin/fllog --adif /home/fred/logbook.adif udp --ipaddress 192.168.10.175</EXEC>
<LOG>
```


[1]: http://www.w1hkj.com/FldigiHelp/macros_sub_page.html
