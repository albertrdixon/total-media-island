require 'clockwork'
module Clockwork
  configure do |config|
    logger = Logger.new(STDOUT)
    logger.formatter = Logger::Formatter.new
    config[:logger]         = logger
    config[:sleep_timeout]  = 10
    config[:tz]             = 'UTC'
    config[:thread]         = true
    config[:max_threads]    = 2
  end

  every(1.day, 'plex.update', at: String(ENV['UPDATE_TIME'])) do
    system '/usr/local/bin/plexupdate.sh'
  end
end