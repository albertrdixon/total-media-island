#!/usr/bin/env python
import transmissionrpc
import logging
import sys
from getopt import getopt
from threading import Thread, Event
from time import sleep


class TorrentCleanerThread(Thread):
  """Really naive transmission torrent cleaner"""
  def __init__(self, host="localhost", port=9091, ratio=1.0, logger=logging.getLogger()):
    super(TorrentCleanerThread, self).__init__()
    self._clean = Event()
    self._quit = Event()
    self.host = host
    self.port = port
    self.log = logger

  def clean(self):
    self._clean.set()

  def stop(self):
    self._quit.set()

  def run(self):
    while not self._quit.is_set():
      self._clean.wait()
      if self._quit.is_set():
        exit(0)

      try:
        tc = transmissionrpc.Client(self.host, port=self.port)
        logging.getLogger('transmissionrpc').setLevel(logging.INFO)
        tc = transmissionrpc.Client(self.host, port=self.port)
        logging.getLogger('transmissionrpc').setLevel(logging.INFO)
        self.log.info("Cleaning time! Getting list of torrents.")
        torrents = tc.get_torrents()
        for torrent in torrents:
          if torrent_finished(torrent, self.ratio):
            self.log.info("Torrent '{}' is finished, removing.".format(torrent.name))
            tc.remove_torrent(torrent.id, delete_data=True)
            return
          if torrent.isStalled:
            self.log.info("Torrent '{}' is stalled, removing.".format(torrent.name))
            tc.remove_torrent(torrent.id, delete_data=True)
        self._clean.clear()
      except Exception, e:
        pass
      finally:
        self._clean.clear()

    exit(0)


def torrent_finished(torrent, ratio):
  if torrent.isFinished:
    return True
  if torrent.progress == 100 and torrent.ratio >= ratio:
    return True
  return False


def main(argv):
  usage = "cleaner.py -H <transmission_host> [ -p <transmission_port> ] [ -f <clean_frequency_in_seconds> ] [ -r <ratio_limit> ]"
  host, port, frequency, ratio = None, 9091, 3600, 1.0
  opts, args = getopt(argv, "hH:p:f:r:", ["host=", "port=", "frequency=", "ratio="])
  for opt, arg in opts:
    if opt == '-h':
      print(usage)
      sys.exit(2)
    elif opt in ('-H', '--host'):
      host = arg
    elif opt in ('-p', '--port'):
      port = arg
    elif opt in ('-f', '--frequency'):
      frequency = arg
    elif opt in ('-r', '--ratio'):
      ratio = arg

  if host is None:
    print("Must specify transmission host!")
    print(usage)
    sys.exit(1)

  log = logging.getLogger()
  log.setLevel(logging.INFO)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.INFO)
  formatter = logging.Formatter('[%(asctime)s] [%(module)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
  ch.setFormatter(formatter)
  log.addHandler(ch)

  log.info("Cleaner started against {}:{}".format(host, port))
  log.info("Will try to clean every {} seconds".format(frequency))
  cleaner = TorrentCleanerThread(host=host, port=port, ratio=ratio, logger=log)
  cleaner.start()

  try:
    while True:
      sleep(int(frequency))
      cleaner.clean()
  except (KeyboardInterrupt, SystemExit):
    log.info("Caught interrupt, quitting")
    cleaner.stop()
    sys.exit()


if __name__ == "__main__":
  main(sys.argv[1:])
