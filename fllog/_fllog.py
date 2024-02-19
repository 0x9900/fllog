#!/usr/bin/env python3
#
# (C) 2019-2024 Fred C. (W6BSD)
# https://github.com/0x9900/fllog
#

"""
%(prog)s [options]

This program is a companion program to log from fldigi to MacLoggerDX.

Create a macro "LOG" in fldigi with the following line:
<EXEC><path where the program has been installed>fllog [mode]</EXEC>

The mode can be either "udp" or "pipe"
For more information call "fllog --help" on a terminal

For example:
<EXEC>/usr/local/bin/fllog udp --ipaddress 127.0.0.1 --port 2237</EXEC>

"""
import logging
import os
import re
import socket
from argparse import ArgumentParser, Namespace
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from subprocess import Popen
from tempfile import NamedTemporaryFile

from fllog import wsjtx

try:
  from datetime import UTC        # python 3.12 and up
except ImportError:
  from datetime import timezone   # python 3.10
  UTC = timezone.utc

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M:%S', level=logging.INFO)

TMP_PATH = '/var/tmp'

IPADDR = '127.0.0.1'
PORTNUM = 2237

ADIF_VER = "3.1.0"
PROGRAM_ID = "FLDIGI / FLLOG"

# MacLoggerDX will accept anything for mode. This mapping for the
# modes accepted by lotw.
ADIFMAP = {
  'CLOVER': 'CLOVER',
  'AM': 'AM',
  'AMTOR': 'AMTOR',
  'AMTORFEC': 'AMTOR',
  'ARDOP': 'ARDOP',
  'ASCI': 'RTTY',
  'ATV': 'ATV',
  'BPSK125': 'PSK125',
  'BPSK31': 'PSK31',
  'BPSK63': 'PSK63',
  'C4FM': 'C4FM',
  'CHIP': 'CHIP',
  'CHIP128': 'CHIP',
  'CHIP64': 'CHIP',
  'CONTESTI': 'CONTESTI',
  'CONTESTI4125': 'CONTESTI',
  'CONTESTI4250': 'CONTESTI',
  'CONTESTI4500': 'CONTESTI',
  'CONTESTI8125': 'CONTESTI',
  'CONTESTI8250': 'CONTESTI',
  'CONTESTI8500': 'CONTESTI',
  'CONTESTI16500': 'CONTESTI',
  'CW': 'CW',
  'DATA': 'DATA',
  'DIGITALVOICE': 'DIGITALVOICE',
  'DOMINO': 'DOMINO',
  'DOMINOEX': 'DOMINO',
  'DOMINOF': 'DOMINO',
  'DSTAR': 'DSTAR',
  'FAX': 'FAX',
  'FM': 'FM',
  'FMHELL': 'HELL',
  'FSK31': 'FSK31',
  'FSK441': 'FSK441',
  'FSKHELL': 'HELL',
  'FSQCALL': 'DATA',
  'FT8': 'FT8',
  'GTOR': 'GTOR',
  'HELL': 'HELL',
  'HELL80': 'HELL',
  'HFSK': 'HFSK',
  'ISCAT': 'ISCAT',
  'ISCATA': 'ISCAT',
  'ISCATB': 'ISCAT',
  'JS8': 'DATA',
  'JT4': 'JT4',
  'JT4A': 'JT4',
  'JT4B': 'JT4',
  'JT4C': 'JT4',
  'JT4D': 'JT4',
  'JT4E': 'JT4',
  'JT4F': 'JT4',
  'JT4G': 'JT4',
  'JT65': 'JT65',
  'JT65A': 'JT65',
  'JT65B': 'JT65',
  'JT65B2': 'JT65',
  'JT65C': 'JT65',
  'JT65C2': 'JT65',
  'JT6M': 'JT6M',
  'JT9': 'JT9',
  'JT91': 'JT9',
  'JT910': 'JT9',
  'JT92': 'JT9',
  'JT930': 'JT9',
  'JT95': 'JT9',
  'JT9A': 'JT9',
  'JT9B': 'JT9',
  'JT9C': 'JT9',
  'JT9D': 'JT9',
  'JT9E': 'JT9',
  'JT9EFAST': 'JT9',
  'JT9F': 'JT9',
  'JT9FFAST': 'JT9',
  'JT9G': 'JT9',
  'JT9GFAST': 'JT9',
  'JT9H': 'JT9',
  'JT9HFAST': 'JT9',
  'LSB': 'SSB',
  'MFSK11': 'MFSK11',
  'MFSK128': 'DATA',
  'MFSK16': 'MFSK16',
  'MFSK22': 'DATA',
  'MFSK31': 'DATA',
  'MFSK32': 'DATA',
  'MFSK4': 'DATA',
  'MFSK64': 'DATA',
  'MFSK8': 'MFSK8',
  'MSK144': 'MSK144',
  'MT63': 'MT63',
  'OLIVIA': 'OLIVIA',
  'OLIVIA161000': 'OLIVIA',
  'OLIVIA16500': 'OLIVIA',
  'OLIVIA321000': 'OLIVIA',
  'OLIVIA4125': 'OLIVIA',
  'OLIVIA4250': 'OLIVIA',
  'OLIVIA8250': 'OLIVIA',
  'OLIVIA8500': 'OLIVIA',
  'OPERA': 'OPERA',
  'OPERABEACON': 'OPERA',
  'OPERAQSO': 'OPERA',
  'PAC2': 'PACTOR',
  'PAC3': 'PACTOR',
  'PAC4': 'PACTOR',
  'PACKET': 'PACKET',
  'PACTOR': 'PACTOR',
  'PAX': 'PAX',
  'PAX2': 'PAX',
  'PCW': 'CW',
  'PSK10': 'PSK10',
  'PSK1000': 'DATA',
  'PSK125': 'PSK125',
  'PSK250': 'DATA',
  'PSK2K': 'PSK2K',
  'PSK31': 'PSK31',
  'PSK500': 'DATA',
  'PSK63': 'PSK63',
  'PSK63F': 'PSK63F',
  'PSKAM10': 'PSKAM',
  'PSKAM31': 'PSKAM',
  'PSKAM50': 'PSKAM',
  'PSKFEC31': 'PSKFEC31',
  'PSKHELL': 'HELL',
  'Q15': 'Q15',
  'QPSK125': 'PSK125',
  'QPSK250': 'DATA',
  'QPSK31': 'PSK31',
  'QPSK500': 'DATA',
  'QPSK63': 'PSK63',
  'QRA64': 'QRA64',
  'QRA64A': 'QRA64',
  'QRA64B': 'QRA64',
  'QRA64C': 'QRA64',
  'QRA64D': 'QRA64',
  'QRA64E': 'QRA64',
  'ROS': 'ROS',
  'ROSEME': 'ROS',
  'ROSHF': 'ROS',
  'ROSMF': 'ROS',
  'RTTY': 'RTTY',
  'RTTYM': 'RTTYM',
  'SIM31': 'DATA',
  'SSB': 'SSB',
  'SSTV': 'SSTV',
  'T10': 'T10',
  'THOR': 'THOR',
  'THOR4': 'THOR',
  'THOR5': 'THOR',
  'THOR8': 'THOR',
  'THOR11': 'THOR',
  'THOR16': 'THOR',
  'THRBX': 'THROB',
  'THROB': 'THROB',
  'USB': 'SSB',
  'VOI': 'VOI',
  'WINMOR': 'WINMOR',
  'WSPR': 'WSPR',
}


class ADIFMap(Mapping):
  def __init__(self):
    self._clean = re.compile('[^A-Z0-9]+')
    self._map = ADIFMAP

  def clean(self, value):
    return self._clean.sub('', value.upper())

  def __getitem__(self, key, default='DATA'):
    key = self.clean(key)
    if key in self._map:
      return self._map[self.clean(key)]
    return default

  def __iter__(self):
    return iter(self._map)

  def __len__(self):
    return len(self._map)


# Create an global instance
adifmap = ADIFMap()


class ADIF(Mapping):

  def __init__(self, data=None):
    self._data = data

    # Fldigi does weird things with the date and often likes to put a
    # date far in the past.
    # Log today's
    self.gmtnow = datetime.now(UTC)

  def __getitem__(self, key):
    if key in self._data:
      return self._data[key]
    return ''

  def __iter__(self):
    return iter(self._data)

  def __len__(self):
    return len(self._data)

  def who(self):
    return self['FLDIGI_LOGBOOK_CALL']

  def __str__(self):
    return '\n'.join([self.header, self.record])

  def _get_time(self, field):
    _tm = self.get(field)
    _time = datetime.strptime(_tm, '%H:%M:%S') if _tm else self.gmtnow
    return _time.strftime('%H%M%S')

  def _get_date(self, field):
    _dt = self.get(field)
    _date = datetime.strptime(_dt, '%Y%m%d') if _dt else self.gmtnow
    return _date.strftime('%Y%m%d')

  @property
  def header(self):
    head = (
      self._gen_field('adif_ver', ADIF_VER).rstrip(),
      self._gen_field('programid', PROGRAM_ID).rstrip(),
      "<eoh>"
    )
    return '\n'.join(head)

  @property
  def record(self):
    attrs = (
      'call', 'mode', 'freq', 'gridsquare', 'rst_rcvd', 'rst_sent',
      'qso_date', 'qso_date_off', 'time_on', 'time_off',
      'serno_in', 'serno_out', 'comments'
    )
    fields = []
    for attr in attrs:
      try:
        fields.append(self._gen_field(attr, getattr(self, attr)))
      except KeyError as err:
        logging.debug(err)
    fields.append(self.eor)
    return ''.join(fields)

  @property
  def eor(self):
    return "<eor>"

  @property
  def call(self):
    return self['FLDIGI_LOGBOOK_CALL']

  @property
  def mode(self):
    return adifmap.get(self['FLDIGI_MODEM_ADIF_NAME'])

  @property
  def gridsquare(self):
    return self['FLDIGI_LOGBOOK_LOCATOR']

  @property
  def freq(self):
    return str(float(self['FLDIGI_FREQUENCY']) / 1_000_000)

  @property
  def tx_pwr(self):
    return self['FLDIGI_LOGBOOK_TX_PWR']

  @property
  def station_callsign(self):
    return self['FLDIGI_MY_CALL']

  @property
  def my_gridsquare(self):
    return self['FLDIGI_MY_LOCATOR']

  @property
  def rst_rcvd(self):
    return self['FLDIGI_LOGBOOK_RST_IN']

  @property
  def rst_sent(self):
    return self['FLDIGI_LOGBOOK_RST_OUT']

  @property
  def qso_date(self):
    dt_on = self.datetime_on
    return dt_on.strftime('%Y%m%d')

  @property
  def qso_date_off(self):
    dt_off = self.datetime_off
    return dt_off.strftime('%Y%m%d')

  @property
  def time_on(self):
    dt_on = self.datetime_on
    return dt_on.strftime('%H%M%S')

  @property
  def time_off(self):
    dt_off = self.datetime_off
    return dt_off.strftime('%H%M%S')

  @property
  def serno_in(self):
    return self.get('FLDIGI_LOGBOOK_SERNO_IN', '')

  @property
  def serno_out(self):
    return self.get('FLDIGI_LOGBOOK_SERNO_OUT', '')

  @property
  def datetime_on(self):
    _time = self._get_time('FLDIGI_LOGBOOK_TIME_ON')
    _date = self._get_date('FLDIGI_LOGBOOK_DATE')
    _datetime = _date + _time
    return datetime.strptime(_datetime, '%Y%m%d%H%M%S')

  @property
  def datetime_off(self):
    _time = self._get_time('FLDIGI_LOGBOOK_TIME_OFF')
    _date = self._get_date('FLDIGI_LOGBOOK_DATE_OFF')
    _datetime = _date + _time
    return datetime.strptime(_datetime, '%Y%m%d%H%M%S')

  @property
  def comments(self):
    fields = (
      self['FLDIGI_MODEM_LONG_NAME'],
      self['FLDIGI_LOGBOOK_NOTES'],
      PROGRAM_ID,
    )
    fields = [f for f in fields if f]
    comments = ' - '.join(fields)
    return comments

  @staticmethod
  def _gen_field(label, value):
    return f"<{label}:{len(value):d}>{value}"


def dump_env(env, adif):
  debug_file = Path('/tmp/fllog.debug')
  try:
    with open(debug_file, 'a+', encoding='utf-8') as fdd:
      for key, val in sorted(env.items()):
        val = val.replace('"', '\"')
        fdd.write(f'export {key}="{val}"\n')
      fdd.write("#" + "-" * 76 + "\n")
      fdd.write(str(adif))
      fdd.write("\n#" + "=" * 76 + "\n")
  except IOError as err:
    logging.error(err)


def save_log(adif, logfile):
  write_header = False
  filename = Path(logfile).expanduser()
  if not filename.exists():
    write_header = True

  with open(filename, 'a', encoding='utf-8') as fdl:
    if write_header:
      fdl.write(adif.header + '\n')
    fdl.write(adif.record)
    fdl.write('\n')


def send_adif_udp(adif, opts):
  packet = wsjtx.WSLogged()

  packet.DateTimeOff = adif.datetime_off
  packet.DXCall = adif.call
  packet.DXGrid = adif.gridsquare
  packet.DialFrequency = int(float(adif.freq) * 1_000_000)
  packet.Mode = adif.mode
  packet.ReportSent = adif.rst_sent
  packet.ReportReceived = adif.rst_rcvd
  packet.TXPower = adif.tx_pwr
  packet.Comments = adif.comments
  packet.DateTimeOn = adif.datetime_on

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.sendto(packet.raw(), (opts.ipaddress, opts.port))


def send_adif_pipe(adif, _):
  try:
    with NamedTemporaryFile(mode='w', dir=TMP_PATH, prefix='fldigi-', suffix='.adi',
                            encoding='utf-8', delete=False) as temp:
      temp.write(str(adif))
      temp.write('\n')
  except IOError as err:
    logging.error(err)
    return

  try:
    cmd = ['/usr/bin/open', '-b', 'com.dogparksoftware.MacLoggerDX', temp.name]
    with Popen(cmd, shell=False) as proc:
      proc.wait()
  except IOError as err:
    logging.error(err)


def parse_arguments():
  """Parse the command arguments"""
  parser = ArgumentParser(description="fldigi to macloggerdx logger",
                          usage=__doc__)
  parser.add_argument('-a', '--adif',
                      help="Backup the log entries into an AIDF file")
  parser.add_argument('-d', '--debug', action="store_true", default=False,
                      help='Dump the fldigi environment variables')

  subp = parser.add_subparsers(required=True)
  p_pipe = subp.add_parser('pipe', help='The log will be sent using a pipe command')
  p_pipe.set_defaults(func=send_adif_pipe)

  p_netw = subp.add_parser('udp', help='The log will be sent using UDP')
  p_netw.set_defaults(func=send_adif_udp)
  p_netw.add_argument('-i', '--ipaddress', default=IPADDR,
                      help="Macloggerdx ip address [default: %(default)s]")
  p_netw.add_argument('-p', '--port', default=PORTNUM,
                      help="Macloggerdx port number [default: %(default)s]")
  opts = parser.parse_args()
  return opts


def read_env():
  env = {k: v for k, v in os.environ.items() if k.startswith('FLDIGI')}
  if not env:
    logging.error(
      'FLDIDI environement variable not set.\n\t\tFor more information '
      'go to https://0x9900.com/logging-on-macloggerdx-with-fldigi/'
    )
    raise SystemExit('Envirnment not set')
  return env


def main():
  opts = parse_arguments()

  env = read_env()

  adif = ADIF(env)
  if opts.debug:
    dump_env(env, adif)
  if opts.adif:
    save_log(adif, opts.adif)

  opts.func(adif, opts)
  logging.info('Contact with `%s` logged', adif.who())


if __name__ == "__main__":
  main()
