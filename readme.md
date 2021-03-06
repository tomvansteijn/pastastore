[![Build Status](https://travis-ci.org/pastas/pastastore.svg?branch=master)](https://travis-ci.org/pastas/pastastore)
[![Documentation Status](https://readthedocs.org/projects/pastastore/badge/?version=latest)](https://pastastore.readthedocs.io/en/latest/?badge=latest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/81b1e0294f5247cfa4eca657a8eebc61)](https://www.codacy.com/gh/pastas/pastastore?utm_source=github.com&utm_medium=referral&utm_content=pastas/pastastore&utm_campaign=Badge_Grade)

# pastastore

This module contains a tool to manage
[Pastas](https://pastas.readthedocs.io/en/latest/) timeseries and models in a
database.

The implementation is similar to pastas.Project, but in addition to managing 
timeseries and models in-memory, it allows storage of data in a 
database or on disk. Storing timeseries and models in a database gives the user 
a simple way to manage Pastas projects with the added bonus of allowing the user 
to pick upwhere they left off, without having to (re)load everything into memory.

The connection to database/disk/memory is managed by a connector object.
Currently, three connectors are included. The first implementation is an 
in-memory connector. The other two store data in a database. Both of these 
implementations are designed to have fast read/write operations, while also 
compressing the stored data.

-   In-memory: uses dictionaries to hold timeseries and pastas Models in-memory.
      Does not require any additional packages to use. 

-   [Arctic](https://arctic.readthedocs.io/en/latest/) is a timeseries/dataframe
      database that sits atop [MongoDB](https://www.mongodb.com). Arctic supports
      pandas.DataFrames.

-   [PyStore](https://github.com/ranaroussi/pystore) is a datastore (inspired
      by Arctic) created for storing pandas dataframes (especially timeseries) on
      disk. Data is stored using fastparquet and compressed with Snappy.

## Dependencies

This module has several dependencies (depending on which connector is used):

If using in-memory connector:

-   No additional dependencies are required.

If using Arctic:

-   Arctic requires MongoDB, e.g. install the Community edition
    ([Windows](https://fastdl.mongodb.org/win32/mongodb-win32-x86_64-2012plus-4.2.1-signed.msi),
    [MacOS](https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-4.2.1.tgz)).

-   OR, if you wish to use Docker for running MongoDB see the installation instructions [here](https://github.com/pastas/pastastore/tree/master/dockerfiles#running-mongodb-from-docker).

If using Pystore:

-   PyStore uses [Snappy](http://google.github.io/snappy/), a fast and
    efficient compression/decompression library from Google. You'll need to
    install Snappy on your system before installing PyStore. See links for
    installation instructions here:
    <https://github.com/ranaroussi/pystore#dependencies>

## Installation

Install the module by typing `pip install .` from the module root directory.
Please note that pystore is _not_ automatically installed as a dependency
because it requires Snappy to be (manually) installed first (see previous
section)!

_For installing in development mode, clone the repository and install by
typing `pip install -e .` from the module root directory._

## Usage

The following snippets show typical usage. The general idea is to first define
the connector object. Then, the next step is to pass that connector to
`PastaStore`.

### Using in-memory dictionaries

```python
import pastastore as pst

# define connector
conn = pst.DictConnector("my_connector")

# create project for managing Pastas data and models
store = pst.PastaStore("my_project", conn)
```

### Using Arctic

```python
import pastastore as pst

# define arctic connector
connstr = "mongodb://localhost:27017/"
conn = pst.ArcticConnector("my_connector", connstr)

# create project for managing Pastas data and models
store = pst.PastaStore("my_project", conn)
```

### Using Pystore

```python
import pastastore as pst

# define pystore connector
path = "./data/pystore"
conn = pst.PystoreConnector("my_connector", path)

# create project for managing Pastas data and models
store = pst.PastaStore("my_project", conn)
```

The database read/write/delete methods can be accessed through the reference
to the connector object. For easy access, the
most common methods are registered to the `store` object. E.g.

```python
series = store.conn.get_oseries("my_oseries")
```

is equivalent to:

```python
series = store.get_oseries("my_oseries")
```

## Types of Connectors

The structure and some background on the different types of Connectors is
detailed below.

### DictConnector

The `DictConnector` is a very simple object that stores all
data and models in dictionaries. The data is stored in-memory and not on disk
and is therefore not persistent, i.e. you cannot pick up where you left off
last time. Once you exit Python your data is lost. For small projects, this
connector can be useful as it is extremely simple.

### ArcticConnector

The ArcticConnector is an object that creates a connection with a MongoDB
database. This means there must be a running MongoDB instance available. 
This can be an existing or a new database. A database is created
to hold the different datasets: observation timeseries, stresses timeseries
and models. For each of these datasets a collection or library is created.
These are named using the following convention:
`<database name>.<collection name>`.

The Arctic implementation uses the following structure:
`database / collections or libraries / documents`. The data is stored within
these libraries. Observations and stresses timeseries are stored as
pandas.DataFrames. Models are stored in JSON (actually binary JSON) and
_do not_ contain the timeseries themselves. These are picked up from the
other libraries when the model is loaded from the database.

The ArcticPastas object allows the user to add different versions for datasets,
which can be used to keep a history of older models for example. This functionality is still in an experimental stage.

### PystoreConnector

The PystoreConnector is an object that links to a location on disk. This can
either be an existing or a new Pystore. A new store is created with collections
that hold the different datasets: observation timeseries, stresses timeseries,
and models.

The Pystores have the following structure: `store / collections / items`. The
timeseries data is stored as Dask DataFrames which can be easily converted to
pandas DataFrames. The models are stored as JSON (not including the timeseries)
in the metadata file belonging to an item. The actual data in the item is an
empty DataFrame serving as a placeholder. This slightly 'hacky' design allows
the models to be saved in a PyStore. The timeseries are picked up from their
respective stores when the model is loaded from disk.

PyStore supports so-called snapshots (which store the current state of the
store) but this has not been actively implemented in this module. Pystore does
not have the same versioning capabilities as Arctic.

### Custom Connectors

It should be relatively straightforward to write your own custom connector
object. The `pastastore.base` module contains the `BaseConnector` class
that defines which methods and properties _must_ be defined. Each Connector
object should inherit from this class. The `BaseConnector` class also shows
the expected call signature for each method. Following the same call signature
should ensure that your new connector works directly with `PastaStore`.
Extra keyword arguments can be added in methods in the custom class as long as 
these are defined after the expected call signature as defined in the 
`BaseConnector`.

```python
class MyCustomConnector(BaseConnector, ConnectorUtil):
    """Must override each method and property in BaseConnector, e.g."""

    def get_oseries(self, name, progressbar=False):
        # your code to get oseries from database here
        pass
```
