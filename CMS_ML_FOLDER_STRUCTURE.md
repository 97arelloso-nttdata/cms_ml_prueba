# Raw Data Format

The **Raw Data Format** consists on a collection of CSV files stored in a single folder with the
following structure:

## Folder Structure

* All the data from all the turbines is inside a single folder, which here we will call `readings`.
* Inside the `readings` folder, one folder exists for each turbine, named exactly like the turbine:
    * `readings/T001`
    * `readings/T002`
    * ...
* Inside each turbine folder one CSV file exists for each month, named `%Y-%m.csv`.
    * `readings/T001/2010-01.csv`
    * `readings/T001/2010-02.csv`
    * `readings/T001/2010-03.csv`
    * ...

## CSV Contents

* Each CSV file contains three columns:
    * `signal_id`: name or id of the signal.
    * ``timestamp``: timestamp of the reading formatted as ``%m/%d/%y %H:%M:%S``.
    * `values`: array with values of the reading.

This is an example of what a CSV contents look like:

|    | signal_id   | timestamp         |    values |
|----|-------------|-------------------|-----------|
|  0 | S1          | 01/01/01 00:00:00 | [1, 2,..] |
|  1 | S1          | 01/01/01 12:00:00 | [3, 4,..] |
|  2 | S1          | 01/02/01 00:00:00 | [5, 6,..] |
|  3 | S1          | 01/02/01 12:00:00 | [7, 8,..] |
|  4 | S1          | 01/03/01 00:00:00 | [9, 2,..] |
|  5 | S1          | 01/03/01 12:00:00 | [1, 2,..] |
|  6 | S2          | 01/01/01 00:00:00 | [3, 4,..] |
|  7 | S2          | 01/01/01 12:00:00 | [5, 6,..] |
|  8 | S2          | 01/02/01 00:00:00 | [7, 8,..] |
|  9 | S2          | 01/02/01 12:00:00 | [9, 5,..] |
| 10 | S2          | 01/03/01 00:00:00 | [8, 4,..] |
| 11 | S2          | 01/03/01 12:00:00 | [7, 3,..] |
