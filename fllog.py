#!/usr/bin/env python
#
# (C) 2019-2020 Fred C. (W6BSD)
# https://github.com/0x9900/fllog
#

"""
%(prog)s [options]

Create a macro "LOG" in fldigi with the following line:
<EXEC><path where the program has been installed>fllog</EXEC>

For example:
<EXEC>/usr/local/bin/fllog</EXEC>

"""
import logging
import os
import re
import socket
import struct
import sys
import time

from argparse import ArgumentParser
from collections import Mapping

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%H:%M:%S', level=logging.INFO)


IPADDR = '127.0.0.1'
PORTNUM = 2237

# enter the data content of the UDP packet as hex
ADIF_VER = "3.1.0"
PROGRAM_ID = "FLDIGI"

MAGIC_NUMBER = 0XADBCCBDA         # Magic number never changes.
SCHEMA_NUMBER = 0x2
MESSAGE_TYPE = 0xC
MESSAGE_ID = 0x57534a542d580000

PACKET_STRUCT = '!LLLLQH%ds'


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
    self.gmtnow = time.gmtime()

  def __getitem__(self, key):
    if key in self._data:
      return self._data[key]
    return ''

  def __iter__(self):
    return iter(self._data)

  def __len__(self):
    return len(self._data)

  def who(self):
    return self['FLDIGI_LOG_CALL']

  def __str__(self):
    attrs = (
      'call', 'mode', 'freq', 'gridsquare', 'rst_rcvd', 'rst_sent',
      'qso_date', 'qso_date_off', 'time_on', 'time_off',
      'serno_in', 'serno_out', 'comment'
    )
    fields = [self.header, '\n']
    for attr in attrs:
      try:
        fields.append(getattr(self, attr))
      except KeyError:
        pass
    fields.append(self.eor)
    return ''.join(fields)

  @property
  def header(self):
    head = (
      self._gen_field('adif_ver', ADIF_VER).rstrip(),
      self._gen_field('programid', PROGRAM_ID).rstrip(),
      "<eoh>"
    )
    return '\n'.join(head)

  @property
  def eor(self):
    return "<eor>"

  @property
  def call(self):
    return self._gen_field('call', self['FLDIGI_LOG_CALL'])

  @property
  def mode(self):
    return self._gen_field('mode', adifmap.get(self['FLDIGI_MODEM_ADIF_NAME']))

  @property
  def gridsquare(self):
    return self._gen_field('gridsquare', self['FLDIGI_LOG_LOCATOR'])

  @property
  def freq(self):
    return self._gen_field('freq', str(float(self['FLDIGI_FREQUENCY']) / 1000000))

  @property
  def station_callsign(self):
    return self._gen_field('station_callsign', self['FLDIGI_MY_CALL'])

  @property
  def my_gridsquare(self):
    return self._gen_field('my_gridsquare', self['FLDIGI_MY_LOCATOR'])

  @property
  def rst_rcvd(self):
    return self._gen_field('rst_rcvd', self['FLDIGI_LOG_RST_IN'])

  @property
  def rst_sent(self):
    return self._gen_field('rst_sent', self['FLDIGI_LOG_RST_OUT'])

  @property
  def qso_date(self):
    return self._gen_field('qso_date', time.strftime('%Y%m%d', self.gmtnow))

  @property
  def qso_date_off(self):
    return self._gen_field('qso_date_off', time.strftime('%Y%m%d', self.gmtnow))

  @property
  def time_on(self):
    return self._gen_field('time_on', time.strftime('%H%M%S', self.gmtnow))

  @property
  def time_off(self):
    return self._gen_field('time_off', time.strftime('%H%M%S', self.gmtnow))

  @property
  def serno_in(self):
    if self['FLDIGI_LOG_SERNO_IN']:
      return self._gen_field('serno_in', self['FLDIGI_LOG_SERNO_IN'])
    else:
      return ''

  @property
  def serno_out(self):
    if self['FLDIGI_LOG_SERNO_OUT']:
      return self._gen_field('serno_out', self['FLDIGI_LOG_SERNO_OUT'])
    else:
      return ''

  @property
  def comment(self):
    fields = (
      PROGRAM_ID,
      self['FLDIGI_MODEM_LONG_NAME'],
      self['FLDIGI_LOG_NOTES']
    )
    fields = [f for f in fields if f]
    comment = ': '.join(fields)
    return self._gen_field('comment', comment)

  @staticmethod
  def _gen_field(label, value):
    return "<{}:{:d}>{}".format(label, len(value), value)


def make_udp_packet(adif):
  count = time.time() % 0xFFFF
  adif_data = str(adif)
  data_struct = PACKET_STRUCT % len(adif_data)

  packet = struct.pack(data_struct, MAGIC_NUMBER, SCHEMA_NUMBER,
                       MESSAGE_TYPE, 0x06, MESSAGE_ID, count, adif_data)

  return packet

def send_log(ipaddr, portnum, udp_packet):
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    sock.sendto(udp_packet, (ipaddr, portnum))
  except socket.error as err:
    logging.error(err)


def dump_env(env, adif):
  try:
    with open('/tmp/fllog.debug', 'ab+') as fdd:
      for key, val in sorted(env.items()):
        fdd.write('export {}="{}"\n'.format(key, val.replace('"', '\"')))
      fdd.write("#" + "-" * 76 + "\n")
      fdd.write(str(adif))
      fdd.write("\n#" + "=" * 76 + "\n")

  except IOError as err:
    logging.error(err)


def parse_arguments():
  """Parse the command arguments"""
  parser = ArgumentParser(description="fldigi to macloggerdx logger",
                          usage=__doc__)
  parser.add_argument('-d', '--debug', action="store_true", default=False,
                      help='Dump the fldigi environment variables')
  parser.add_argument('-i', '--ipaddress', default=IPADDR,
                      help="Macloggerdx ip address [default: %(default)s]")
  parser.add_argument('-p', '--port', default=PORTNUM,
                      help="Macloggerdx port number [default: %(default)s]")
  opts = parser.parse_args()
  return opts


def main():
  opts = parse_arguments()

  env = {k: v for k, v in os.environ.items() if k.startswith('FLDIGI')}
  if not env:
    logging.error(
      'FLDIDI environement variable not set. For more info\n'
      'go to https://0x9900.com/logging-on-macloggerdx-with-fldigi/'
    )
    sys.exit(os.EX_USAGE)

  adif = ADIF(env)

  if opts.debug:
    dump_env(env, adif)

  packet = make_udp_packet(adif)
  send_log(opts.ipaddress, opts.port, packet)
  logging.info('Contact with `%s` logged', adif.who())

if __name__ == "__main__":
  main()
