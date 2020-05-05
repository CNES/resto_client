.. _resto_servers_db_description:

###########################
resto servers database
###########################

**resto_client** provides access to *resto servers* which are defined in a json database.


Server definition
=================

Identification
-------------------

Each *resto server* is identified by a unique case unsensitive name.
Once created and validated, you can use a server just by specifying its name.

Predefined and user defined servers
-----------------------------------------

**resto_client** comes with a set of predefined *resto servers* which can be used out of the box.
But it also allows to define new *resto servers* which are not (yet) known by the maintainance team.
This is useful for instance if you have setup a resto server for testing purposes and want to use **resto_client** with it.
Both predefined and user defined servers can then be used indifferently by **resto_client**.

However two principles apply to servers editing:

- predefined servers cannot be deleted,
- a server name being unique, a user defined server cannot reuse the name of a predefined resto server,

Should you find that a *resto server* that you have defined would deserve to be included in the predefined servers list,
please feel free to `fill in a project issue <https://github.com/CNES/resto_client/issues/new>`_, and we will consider its inclusion.


Definition details
------------------

Each *resto server* is composed of 2 services:

- the **authentication service** which is in charge of the user authentication,
- the **application service** which handles the application requests.

In our wording, a service corresponds to a single Internet endpoint which is able to process a set of fully specified requests in order to provide the expected service.
Each service is described by what we call a 'service access':

- the base URL at which the service can be reached, 
- the name of the protocol it supports.


.. note:: A protocol is designated by a unique name and describes the set of requests which are supported by the services implementing it.
          It also describes the responses which can be received for each request sent to the service.
          
          For the moment the protocols definitions are contained in the python package directly.
          Therefore they cannot be configured by the user and adding or removing or modifying a protocol implies a new release
          of the package.



Dynamic management
=========================

Server status
-------------

When created in the database either as a predefined or a user defined one, a given server is not necessarily available.
Moreover a server can be down for some time for instance when it is under maintenance.

To tackle these problems we manage a server status to track its availability with the following meaning:

.. csv-table:: 
   :header: "Server status", "Meaning"
   :widths: 30, 50

   "Never reached", "The server has been correctly created but all attempts (if any) to request it have failed."
   "Unavailable", "The server has once been reached successfully, but the last attempts to request it have failed."
   "Running", "The last request to the server has been successfully answered."
   
   
Here "successful" means that the response received from the server was one of the expected ones, including applicative errors (wrong id, no result, etc.).
Failures are only detected when protocol errors occur.

Depending on this status, the error messages will be different (TBC).

Server cache
------------

Some requests to the server send a response which is not changing very often: server description, list of collections for instance.
However these results are needed at different places in **resto_client** and we cannot define them as static information.

In order to avoid resubmiting these requests again and again we keep these results in a cache within the servers database. These cached results are used as the primary source of information.
And to stay nearly up-to-date with the server content we update them when they are older than a predefined period of time (typically 24h).


Database lifecycle
===================

Creation
-----------------

*resto servers* database is created at the first launch of **resto_client** following its installation. It is located in the following directory:

.. csv-table:: 
   :header: "Operating System", "Servers database location"
   :widths: 30, 50

   "Windows", "%USERPROFILE%\\AppData\\Local\\CNES\\resto_client"
   "Linux", "$HOME/.local/share/resto_client"
   

Upgrade
----------------

When upgrading **resto_client** to a newer version, it may happen that the database format has changed or that the predefined servers have been modified.
Both conditions imply that the database need to be upgraded. The upgrading process is different for predefined and user defined servers:

- existing predefined servers are removed from the database and newly predefined servers are created.
  This may lead to the addition of new predefined servers, but also to the removal of previously predefined servers, which can be desirable when a server has been shutdown for instance.

- user defined servers are kept unchanged, provided that their stored definitions are compatible in terms of format and semantics with the new definition format.
  If it is not the case, the previous servers definitions are copied in a backup file and they are deleted from the database.
  A message warns the user that these servers have been deleted and must be redefined.

During this process, servers names can be deleted and naming conflicts may happen.
Firstly we guarantee that the name of existing predefined servers will not change after an upgrade. Secondly, if a predefined server is deleted we will keep track of this
name and will not allow its use for creating new user defined servers (but we could reuse it for reactivating the said predefined server).
Finally if a newly predefined server has a name which conflicts with a user defined server,
this latter is renamed by appending '_user_defined' to its name, and the former replaces it.
Then the user defined server is processed as described above.

Deletion
----------------

Uninstalling **resto_client** does not remove the database. You should delete it manually after uninstallation by removing the whole folder containing the database.


