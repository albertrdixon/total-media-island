### Total Media Island

You want to watch movies and tv shows, right? So do I!

Of course that means downloading them. Which means setting up bittorrent. Which means setting up something like [Sickrage](http://sickrage.tv) to go out and find those torrents. Which means setting up a VPN so you don't get laughed at by everyone.

That sounds like a lot. Why not just use [Docker](http://docker.com) to just do everything for us? Good idea!

Install docker and docker-compose. Set up your secrets in .env files under each directory. Run `docker-compose up -d`. Congrats, you now have a publicly accessible media downloader & [Plex](http://plex.tv) server!
