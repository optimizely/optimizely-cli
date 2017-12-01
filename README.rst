==============
optimizely-cli
==============

optimizely-cli is a command-line interface for Optimizely projects.

It aims to give you quick access to your experiment data as well as store a
local copy of your data so that you can manage and track changes in the version
control system of your choice.

-------------------
System Requirements
-------------------

optimizely-cli runs on Linux and Mac OS X, and requires Python 2.7.x+. It may
work on other versions of Python.

------------
Installation
------------

Install optimizely-cli using `pip`_::

    $ pip install git+ssh://git@github.com/optimizely/optimizely-cli.git

Or to upgrade:

    $ pip install --upgrade git+ssh://git@github.com/optimizely/optimizely-cli.git

---------------
Getting Started
---------------

To use optimizely-cli, you need to link it to your Optimizely account.  You
can do this in several ways:

* Environment variables
* Shared credentials file
* Config file
* IAM Role

The quickest way to get started is to run the ``opti init`` command and follow
the instructions::

    $ opti init
	First visit https://app.optimizely.com/v2/profile/api to create a new access token
	Enter the token you created here:
	Verifying token...
	Token is valid
	Credentials written to .optimizely-credentials.json
	Do not add this file to version control!
	It should stay private

	Checking for an existing project...
	Successfully created project (id: <project_id>)
	Config file written to .optimizely.json

It is a good idea to add the following to your .gitignore file:

	$ echo .optimizely-credentials.json >> .gitignore

Don't commit your credentials to version control!

------------------
Command Completion
------------------

The ``opti`` utility can complete your commands. Just add the following to your .bashrc:

    eval "$(_OPTI_COMPLETE=source opti)"

^^^^^^^^
Examples
^^^^^^^^

Get a list of projects ::

    $ opti project list

Create a new project ::

    $ opti project create

Get a list of events ::

    $ opti event list
