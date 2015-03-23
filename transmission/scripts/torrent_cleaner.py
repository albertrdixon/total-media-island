#!/usr/bin/env python
import transmissionrpc
import logging
import sys
from getopt import getopt
from threading import Thread, Event
from time import sleep


class TorrentCleanerThread(Thread):
  """Really naive transmission torrent cleaner"""
  def __init__(self, host="127.0.0.1", port=9091, ratio=1.0, logger=logging.getLogger()):
    super(TorrentCleanerThread, self).__init__()
    self._clean = Event()
    self._quit = Event()
    self.host = host
    self.port = port
    self.ratio = ratio
    self.log = logger
    self.finished = False
    self.client = None

  def clean(self):
    self._clean.set()

  def stop(self):
    self._quit.set()
    self._clean.set()
    self.finished = True

  def should_quit(self):
    if self._quit.is_set():
      self.log.info("Cleaner shutting down")
      exit(0)

  def run(self):
    while not self._quit.is_set():
      self.log.info("Waiting for 'clean' event")
      self._clean.wait()
      self.should_quit()

      self.log.info("Running torrent cleaner")
      self.finished = False

      for i in range(1, 5):
        self.should_quit()
        if self.finished:
         break
        self.log.debug("Clean attempt {}".format(i))
        try:
          self.log.debug("Acquiring client.")
          self.client = self.client or transmissionrpc.Client(self.host, port=self.port)
          logging.getLogger('transmissionrpc').setLevel(self.log.getEffectiveLevel())
          self.log.debug("Getting list of torrents.")
          torrents = self.client.get_torrents()
          if not torrents:
            self.log.info("No torrents to process!")
            self.finished = True
          else:
            for torrent in torrents:
              self.should_quit()
              remove = False
              self.log.info("Torrent #{}: {}".format(torrent.id, torrent))
              if torrent_finished(torrent, self.ratio):
                self.log.info("Torrent #{} ({}) is finished, removing.".format(torrent.id, torrent))
                remove = True
              if torrent.isStalled or torrent.status == "stopped":
                self.log.info("Torrent #{} ({}) is stalled, removing.".format(torrent.id, torrent))
                remove = True
              if remove:
                self.client.remove_torrent(torrent.id, delete_data=True)
              else:
                self.log.info("Torrent #{} ({}) is still active, skipping.".format(torrent.id, torrent))
            else:
              self.finished = True
        except Exception, e:
          self.log.error("ERROR: {}".format(e))
          if i < 4:
            sleep(i * 3)
          continue
      self.log.info("Cleaning run complete!")
      self._clean.clear()
    self.should_quit()


def torrent_finished(torrent, ratio):
  done = False
  if torrent.isFinished or (torrent.progress == 100 and torrent.ratio >= ratio):
    done = True
  return done


def main(argv):
  usage = "cleaner.py -H <transmission_host> [ -p <transmission_port> ] [ -f <clean_frequency_in_seconds> ] [ -r <ratio_limit> ]"
  host, port, frequency, ratio, debug = None, 9091, 3600, 1.0, False
  opts, args = getopt(argv, "hdH:p:f:r:", ["host=", "port=", "frequency=", "ratio="])
  for opt, arg in opts:
    if opt == '-h':
      print(usage)
      sys.exit(2)
    elif opt == '-d':
      debug = True
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

  level = logging.INFO
  if debug:
    level = logging.DEBUG
  log = logging.getLogger("torrent_cleaner")
  log.setLevel(level)

  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(level)
  formatter = logging.Formatter('[%(asctime)s] [%(module)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
  ch.setFormatter(formatter)
  log.addHandler(ch)

  log.info("Cleaner started against {}:{}".format(host, port))
  log.info("Will try to clean every {} minutes".format(frequency / 60))
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
