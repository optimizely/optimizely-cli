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

Install or upgrade optimizely-cli using pip:

    $ pip install --upgrade git+git://github.com/optimizely/optimizely-cli

If you get some sort of error about TLS versions like this:

    "There was a problem confirming the ssl certificate: [SSL: TLSV1_ALERT_PROTOCOL_VERSION]"

Then install a newer version of pip and then install again:

    $ curl https://bootstrap.pypa.io/get-pip.py | python

---------------
Getting Started
---------------

To use optimizely-cli, you need to link it to your Optimizely account.
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

You can move ``.optimizely-credentials.json`` to your home directory (the
``opti`` tool will look there as long as your project is under your home):

	$ mv .optimizely-credentials.json ~/

Or add it to your .gitignore file like this:

	$ echo .optimizely-credentials.json >> .gitignore

Don't commit your credentials to version control!

^^^^^
Usage
^^^^^

For a full list of commands, just type ``opti`` at the command line. Here are some examples of available sub-commands:

===========  ===================================================
attribute    Manage Audience Attributes
audience     Manage Optimizely audiences
environment  Manage Environments
event        List, create, and manage Optimizely events
experiment   List, create, and manage Optimizely experiments
feature      Manage Features
group        Manage Optimizely exclusion groups
init         Link an Optimizely project with your repository
project      List, create, and manage Optimizely projects
pull         Pull down the current state of an Optimizely project
push         Push back local data to an Optimizely project
===========  ===================================================

^^^^^^^^
Examples
^^^^^^^^

Get a list of projects ::

    $ opti project list

Create a new project ::

    $ opti project create

Get a list of events ::

    $ opti event list

Create a new event ::

    $ opti event create new_event

Pull all Optimizely experiment data and write them to a local ``optimizely/`` directory ::

    $ opti pull

Collect changes to your local ``optimizely/`` directory and apply them your data in Optimizely ::

    $ opti push

------------------
Command Completion
------------------

The ``opti`` utility can complete your commands. Just add the following to your .bashrc:

    eval "$(_OPTI_COMPLETE=source opti)"

------------
Contributing
------------

Please see `contributing`_.

.. _contributing: CONTRIBUTING.md
.. _additional_code: ADDITIONAL_CODE.md
.. _terms: http://www.optimizely.com/terms

---------------
Additional Code
---------------

Please see `additional_code`_.

Any use of the Optimizely Service is subject to our `Terms of Service <terms_>`_ or the separate, written agreement between your company and Optimizely (if any).
