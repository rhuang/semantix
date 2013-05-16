Semantix
========

The Semantix crawler.

Installation
------------

1. Get Python 2.7.3.
2. Install [Flask](http://flask.pocoo.org/docs/installation/ "Flask"). Make sure `virtualenv` is 
installed. Follow the instructions to install to activate the virtual environment and flask install.
3. Install [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/ "BeautifulSoup").

Run
---

1. Run `. venv/bin/activate`. Everytime you want to deploy the project, you have to activate the 
virtual environment.
2. Run `python run.py`.

Notes
-----

We activate a virtual environment to ensure our project runs on the enclosed Python version and is 
not affected by the other Python versions installed on the machine. Flask is also installed into 
the virtual environment, and not globally on our machine.

