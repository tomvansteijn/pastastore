=================
Connector objects
=================
The structure and some background on the different types of Connectors is
detailed below.

Each connector makes a distinction between the following datasets:

* observation timeseries (the series to be simulated)
* stresses timeseries (the forcing series on the system)
* models (the timeseries models)

In-memory
---------
The :ref:`DictConnector` is a very simple object that stores all
data and models in dictionaries. The data is stored in-memory and not on disk
and is therefore not persistent, i.e. you cannot pick up where you left off
last time. Once you exit Python your data is lost. For small projects, this
connector can be useful as it is extremely simple.

Arctic
------
The :ref:`ArcticConnector` is an object that creates a
connection with a MongoDB database. This can be an existing or a new database.
For each of the datasets a collection or library is created. These are named
using the following convention: `<database name>.<collection name>`.

The Arctic implementation uses the following structure:

.. code-block:: bash

   +-- database
   |   +-- collections or libraries (i.e. oseries, stresses, models)
   |   |   +-- documents... (i.e. individual timeseries or models)

The data is stored within these libraries. Observations and stresses timeseries
are stored as pandas.DataFrames. Models are stored in JSON (actually binary
JSON) and *do not* contain the timeseries themselves. These are picked up from
the other libraries when the model is loaded from the database.

The `ArcticConnector` object allows the user to add different versions for
datasets, which can be used to keep a history of older models for example.

Pystore
-------
The :ref:`PystoreConnector` is an object that links
to a location on disk. This can either be an existing or a new Pystore. A new
store is created with collections that hold the different datasets:

* observation timeseries
* stresses timeseries
* models

The Pystores have the following structure:

.. code-block:: bash

   +-- store
   |   +-- collections... (i.e. oseries, stresses, models)
   |   |   +-- items... (i.e. individual timeseries or models)


The timeseries data is stored as Dask DataFrames which can be easily converted
to pandas DataFrames. The models are stored as JSON (not including the
timeseries) in the metadata file belonging to an item. The actual data in the
item is an empty DataFrame serving as a placeholder. This slightly 'hacky'
design allows the models to be saved in a PyStore. The timeseries are picked
up from their respective stores when the model is loaded from disk.

PyStore supports so-called snapshots (which store the current state of the
store) but this has not been actively implemented in this module. Pystore does
not have the same versioning capabilities as Arctic.

Custom Connectors
-----------------
It should be relatively straightforward to write your own custom connector
object. The :ref:`Base` submodule contains the
`BaseConnector` class that defines which methods and properties *must*
be defined. The `ConnectorUtil` mix-in class contains some general methods that
are used by each connector. Each Connector object should inherit from these
classes.

The `BaseConnector` class also shows the expected call signature for each
method. Following the same call signature should ensure that your new connector
works directly with `PastaStore`. Though extra keyword arguments can be
added in the custom class.

Below is a small snippet showing a custom Connector class::

   class MyCustomConnector(BaseConnector, ConnectorUtil):
      """Must override each method and property in BaseConnector, e.g."""

      def get_oseries(self, name, progressbar=False):
         # your code to get oseries from database here
         pass
