# Resto_client: a client to access resto servers

[![PyPI license](https://img.shields.io/pypi/l/resto_client.svg)](https://pypi.org/project/resto_client/)
[![Python versions](https://img.shields.io/pypi/pyversions/resto_client.svg)](https://pypi.org/project/resto_client/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/resto_client.svg)](https://pypi.org/project/resto_client/)
[![PyPI - Format](https://img.shields.io/pypi/format/resto_client)](https://pypi.org/project/resto_client/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/resto_client)](https://pypi.org/project/resto_client/)
[![GitHub contributors](https://img.shields.io/github/contributors/CNES/resto_client)](https://github.com/CNES/resto_client/graphs/contributors)

**resto_client** is a python package which gives you access to several remote sensing image servers which are based on the [resto](https://github.com/jjrom/resto/tree/2.x) open source server.

Once you have installed it, **resto_client** offers the possibility to interact with these servers by issuing commands from a simple terminal.
Currently implemented commands allow to:
- define and manage a list of well known servers,
- select one of them and browse its collection and their characteristics,
- **search** a collection by criteria for retrieving features (images for instance) and display their characteristics,
- **show** : retrieve and display feature metadata when you know its identifier,
- **download** files composing the feature: the product itself, but also its quicklook, thumbnail or annexes,
- authentication is supported to provide access to restricted features or sign product licenses when necessary.

### Well known resto servers

**resto_client** comes with a list of well known servers already configured, which can be accessed out of the box:

* [kalideos : CNES Kalideos platform](https://www.kalideos.fr)
* [ro : CEOS Recovery Observatory](https://www.recovery-observatory.org)
* [peps : The French Sentinel Data Processing center](https://peps.cnes.fr)
* [theia : The French Space Agency, THEIA land data center](https://theia.cnes.fr)
* [creodias : Copernicus DIAS CREODIAS](https://www.creodias.eu)


This list is augmented regularly, but you can of course add your own server by providing its configuration through **resto_client**.

### Supported environment

**resto_client** runs on the following configurations:
- Python 3.6, 3.7 or 3.8
- Any Operating System supporting the above versions of Python (Windows, Linux, MacOS, etc.)

resto_client tests are done on Windows and Linux using the supported python versions.


### Resto_client installation

The recommended way to intall `resto_client` is to simply use [`pip`](https://pypi.org/project/pip/) which will install the package available from [Python Package Index](https://pypi.org/project/requests/) in your python environment:

```console
$ pip install resto_client
```

Once **resto_client** package is installed you can test it by issuing the following command in a terminal:

```console
$ resto_client --help
```


### How to use resto_client?

Firstly you can select the server to be used for all subsequent commands. This selection is not 
mandatory and you may prefer to specify the server to use in each subsequent commands. 
But it is more convenient if you are using the same server for a long time. 

You can use a well known server:

```console
$ resto_client set server kalideos
```
Or configure a new one and set it:

```console
$ resto_client configure_server create new_kalideos https://www.kalideos.fr/resto2 dotcloud https://www.kalideos.fr/resto2 default
$ resto_client set server new_kalideos
```

You can then show the server synthetic characteristics:

```console
$ resto_client show server
Server URL: https://www.kalideos.fr/resto2/
+-----------------+--------+---------------------+------------+--------------+
| Collection name | Status |        Model        | License Id | License name |
+-----------------+--------+---------------------+------------+--------------+
|     KALCNES     | public | RestoModel_dotcloud | unlicensed |  No license  |
|     KALHAITI    | public | RestoModel_dotcloud | unlicensed |  No license  |
+-----------------+--------+---------------------+------------+--------------+
```
This shows you the server URL as well as its collection and their main characteristics. If you want the details of a collection, you can type in:

```console
$ resto_client show collection KALCNES
+----------------------------------------------------------------------------+
|                        Collection's Characteristics                        |
+-----------------+--------+---------------------+------------+--------------+
| Collection name | Status |        Model        | License Id | License name |
+-----------------+--------+---------------------+------------+--------------+
|     KALCNES     | public | RestoModel_dotcloud | unlicensed |  No license  |
+-----------------+--------+---------------------+------------+--------------+

STATISTICS for KALCNES
+------------+-------------+
| collection | Nb products |
+------------+-------------+
| KALCNES    |        2599 |
| Total      |        2599 |
+------------+-------------+
+---------------+-------------+
| continent     | Nb products |
+---------------+-------------+
| Europe        |        2594 |
| North America |           1 |
| Total         |        2595 |
+---------------+-------------+
.

```
In fact the collection description contains much more statistics, but we have truncated the result for brevity.

You can search the collection for the features it contains, either by identifiers or by criteria. For instance:

```console
$ resto_client search --criteria platform:"PLEIADES 1A" resolution:[0,1.5] startDate:2018-01-01 completionDate:2018-01-31 --collection=KALCNES
['1926127184714545', '6589984032241814', '1926091543104317', '1926059176484529']
4 results shown on a total of  4 results beginning at index 1
```

And you can get the details of some feature by specifying its **identifier**:

```console
$ resto_client show feature 1926127184714545
Metadata available for product 1926127184714545
+--------------------+-------------------------------------------------------------------------------------------+
| Property           | Value                                                                                     |
+--------------------+-------------------------------------------------------------------------------------------+
| collection         | KALCNES                                                                                   |
| productIdentifier  | 1926127184714545                                                                          |
| parentIdentifier   | None                                                                                      |
| title              | PLEIADES 1A PAN L1A 2018-01-23 10:37:39Z                                                  |
| description        | L1A PAN image acquired by PLEIADES 1A on[...]                                             |
.
```
Here we have also truncated the result but there are much more metadata available for each feature.

Finally you may want to download some file associated to that feature : product, quicklook, thumbnail, annexes.
The following example is for its quicklook:

```console
$ resto_client download quicklook 1926127184714545
downloading file: c:\Users\xxxxxxx\Downloads\1926127184714545_ql.jpg
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 128k/128k [00:09<00:00, 13.3kB/s]
```

Obviously you can also download the product, provided that you have the right credentials to access it if it is protected

```console
$ resto_client download product 1926127184714545 --username=known_user
Please enter your password:***********
...
```

Every command has several options and there are also more commands to set different **resto_client** parameters or to define servers.
You can discover their function and syntax by exploring the help on **resto_client** and on its subcommands
:

```console
$ resto_client --help
usage: resto_client [-h] {set,unset,show,download,search,configure_server} ...

A commmand line client to interact with resto servers.

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  For more help: resto_client <sub_command> -h

  {set,unset,show,download,search,configure_server}
    set                 set application parameters: server, account,
                        collection, download_dir, region, verbosity
    unset               unset application parameters: server, account,
                        collection, download_dir, region, verbosity
    show                show resto_client entities: settings, server,
                        collection, feature
    download            download features files: product, quicklook, thumbnail
                        or annexes
    search              search feature(s) in collection
    configure_server    configure servers known by resto_client: create, edit,
                        delete.
$ resto_client show --help
usage: resto_client show [-h] {settings,server,collection,feature} ...

Show different resto_client entities.

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  For more help: resto_client show show <entity> -h

  {settings,server,collection,feature}
    settings            Show application settings
    server              Show the server details
    collection          Show the details of a collection
    feature             Show feature details

```


### Documentation

More documentation available soon.
