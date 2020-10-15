ObjectID
========

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


:License: MIT

Team Members
------------
Stephen du Plesis: stephendups@gmail.com

Johannes Wolmarans: u17043540@tuks.co.za

Luke Greenberg: lukegreen.pc@gmail.com

Zoe Schnetler: zoe.schnetler@gmail.com

Thembinkosi Isaac Mtsweni: u16205457@tuks.co.za

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy objectid

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Software Requirements Specification Document
---------

The SRS documnet for the ObjectID system can be found at:
https://www.overleaf.com/read/jkftvtyxvbfr


Technical_Installation_Manual
----------

https://drive.google.com/file/d/1uQm2RkXZDLwHv0GS1vLEEMzHtZE-1YR1/view?usp=sharing

User Manual:
----------

https://www.overleaf.com/read/fxqswyzrhpkb

ObjectID Front-end link:
----------

https://github.com/COS301-SE-2020/Object-ID-Frontend

Testing Policy:
----------

https://drive.google.com/file/d/1IjHSEzLkrTo9t98l5Vown3-w8pvmaby4/view?usp=sharing

Postman Tests:
----------

https://drive.google.com/file/d/1SiLnPqtZqNCDNEja1fGKKERlk57hUAam/view?usp=sharing

Deployment To Production:
----------

Deployment to production has been made as easy as possible by use of Docker and docker-compose.

Ensure that you have Docker and docker-compose installed on your system:

https://docs.docker.com/get-docker/
https://docs.docker.com/compose/install/

After installation of docker use git to clone the repository where you want the volumes to be installed:
::
  $ git clone <git_repo_url>

We also need to make sure that you have AI model weights. Since these are particularly large files you need to use git lfs.
To install git lfs on Linux you can use:
::
  $ sudo apt-get install git-lfs

Then to download the weights, from inside the repository location execute:
::
  $ git lfs pull

Now that your SSL certificates are setup and your repo cloned you can spin up the instance simply by running:
::
  $ docker-compose up -d --build

This uses docker-compose to build multiple images configuring your instance to run as needed.
"up" tells docker-compose to spin up the instances
"-d" tells docker-compose to run the instances in detached mode allowing for you to resume terminal control after the spin up
"--build"" tells docker-compose to build the images using the specified docker files and commands

If this is your first time running the system there is a bit more setup required.
First we must check that the correct database exists:
To check execute:
::
  $ docker-compose logs db

If you see the following message:
::
  [FATAL]: Database 'objectid' does not exist

Then the database does not exist so we must create it by doing the following:
::
  $ docker-compose exec db sh
  $ su - postgres
  $ psql
  $ CREATE DATABASE objectid;
  $ \q
  $ logout
  $ logout


Now our database has been created.
Now we must check the django instance to see if it has spun up correctly.
Let's do this by creating a super user that will allow you to connect to the admin panel.
Execute:
::
  $ docker-compose exec web python /code/manage.py createsuperuser

This should prompt you to create a user.
If an error is thrown it means that our Django instance has not migrated or spun up correctly.
To fix this execute:
::
  $ docker-compose up -d web

This tells docker-compose to relaunch the Django instance.

Now execute the "createsuperuser" command again and follow the prompts.

If everything has worked you should be able to goto the following address:
::
  $ localhost/<admin_url>

Where <admin_url> is replaced by the admin URL described in the /.envs/.django file.
Inside that file you will find something similar to:
::
  $ DJANGO_ADMIN_URL=some_hash/

The area described by "some_hash" is the "admin_url"

If you are directed to the Django admin panel and presented with a login screen you are ready to go.

There are two way of stopping the system at this point:
::
     $ docker-compose down -v
This stops the system but at the same time removes the volumes and deletes the built images meaning that you will need to use the "--build"
flag when starting the system again

::
     $ docker-compose down
This stops the system but does not remove the images and volumes meaning that to spin up the system again you will only need to execute:
::
     $ docker-compose up -d

Updating a deployment:
----------
Updating the deployment is easy. Firstly run:
::
     $ git pull
This will get you the new code base and then you can simply re-launch the Django image without a rebuild to have the new code:
::
     $ docker-compose up -d web

Configuring a deployment:
----------
## SSL:
Currently the SSL certificates are self-signed certificates linked to this repository and no domain.
If you wish to change the certificate files do so by:

- Rename your files in the following manner:
::
  objectid.crt
  objectid.key

- Replace the files located inside: `` /nginx/ ``

## Domains:
To configure the system to run on your domain you need to update the file location inside:
::
     /nginx/nginx.conf
To configure your domains you must change the conf file to match your domain name.
To put it simply that means changing the lines that say:
::
     server_name localhost;
To your domain. i.e:
::
     server_name <domain_name>;

To make these changes take effect simply execute:
::
     $ docker-compose up -d nginx
