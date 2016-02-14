# README #

### Domain-Expiration ###

* This application is made to store all your domains whois in a DB using:
** <a href="https://docs.python.org/3/whatsnew/3.5.html">Python 3.5</a>
** <a href="https://github.com/KeepSafe/aiohttp">aiohttp</a>
** <a href="https://www.mongodb.org/">MongoDB</a>

### How do I get set up? ###

* Clone the repo
* Be sure that you have the Linux <a href="http://www.computerhope.com/unix/uwhois.htm">Whois command</a>
* Create a virtualenv and install the requirements.txt
* ``$ python3.5 ./main.py`
* Serve the static folder into /static/ path.
* In order to run the collector, enable linux cron and put main_collector.py into /var/www/

### License ###

``Domain-expiration`` is offered under the Apache 2 license.

### Contribution guidelines ###

* Albert Palenzuela albert.palenzuela@gmail.com
