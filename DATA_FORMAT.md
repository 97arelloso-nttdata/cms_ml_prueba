# CMS-ML Data Format

## Input

The input for CMS-ML is a table of FFT Timeseries, which contains the following 4 fields:

  * `turbine_id`: Unique identifier of the turbine to which this value relates.
  * `signal_id`: Unique identifier of the signal to which this value belongs.
  * `timestamp (datetime)`: Time at which this reading was taken.
  * `values (array)`: Array containing the values of the FFT spectrum of the signal at the
    indicated timestamp.

| turbine_id   | signal_id   | timestamp           |             values |
|--------------|-------------|---------------------|--------------------|
| T1           | S1          | 2001-01-01 00:00:00 |  [0.1, 1.5, 2.3..] |
| T1           | S1          | 2001-01-01 12:00:00 |  [0.0, 0.5, 1.2..] |
| T1           | S1          | 2001-01-02 00:00:00 |  [0.4, 3.3, 4.9..] |
| T1           | S1          | 2001-01-02 12:00:00 |  [0.1, 2.5, 5.5..] |
| T1           | S2          | 2001-01-01 00:00:00 |  [0.1, 1.2, 2.3..] |
| T1           | S2          | 2001-01-01 12:00:00 |  [1.0, 1.5, 2.3..] |
| T1           | S2          | 2001-01-02 00:00:00 |  [2.0, 1.5, 2.3..] |
| T1           | S2          | 2001-01-02 12:00:00 |  [3.5, 0.5, 2.3..] |
| ...          | ...         | ...                 |                ... |

Optionally, an arbitrary number of additional fields can be included as contextual metadata:

| turbine_id   | signal_id   | timestamp           |             values |  Measured RPM | ... |
|--------------|-------------|---------------------|--------------------|---------------|-----|
| T1           | S1          | 2001-01-01 00:00:00 |  [0.1, 1.5, 2.3..] |      1421.991 | ... |
| T1           | S1          | 2001-01-01 12:00:00 |  [0.0, 0.5, 1.2..] |       434.132 | ... |
| T1           | S1          | 2001-01-02 00:00:00 |  [0.4, 3.3, 4.9..] |      1021.210 | ... |
| T1           | S1          | 2001-01-02 12:00:00 |  [0.1, 2.5, 5.5..] |      1312.596 | ... |
| T1           | S2          | 2001-01-01 00:00:00 |  [0.1, 1.2, 2.3..] |      1219.249 | ... |
| T1           | S2          | 2001-01-01 12:00:00 |  [1.0, 1.5, 2.3..] |       850.810 | ... |
| T1           | S2          | 2001-01-02 00:00:00 |  [2.0, 1.5, 2.3..] |       995.543 | ... |
| T1           | S2          | 2001-01-02 12:00:00 |  [3.5, 0.5, 2.3..] |      4592.991 | ... |
| ...          | ...         | ...                 |                ... |           ... | ... |

## JSON Format

CMS-ML is also prepared to load and work with data stored as a collection of JSON files.

The input JSONs files need to have the following keys and subkeys:

- details
    - name, type, sensorName, sensorType, sensorSerial, ...
- location
    - siteName, turbineName, turbineSerial, configurationName, softwareVersion, ...
- data
    - context
        - timeStamp, rpm, rpmStatus, alarmStatus, duration, condition, maskTime, ...
        - extra
            - Mask Status, ...
        - binningParameters
            - WPS-ActivePower-Average, WPS-ActivePower-Minimum, WPS-ActivePower-Maximum, WPS-ActivePower-Deviation, WPS-ActivePower-StartTime, WPS-ActivePower-StopTime, WPS-ActivePower-Counts, ...
        - operationalValues
            - Measured RPM, WPS-ActivePower, WPS-Gearoiltemperature, WPS-GeneratorRPM, WPS-PitchReference, WPS-RotorRPM, WPS-Windspeed, WPS-YawAngle, overload warning, bias warning, bias voltage, ...
    - set
        - xValueOffset, xValueDelta, xValueUnit, yValueUnit, yValues

```jsonld=
{
   "data" : {
      "context" : {
         "extra" : [
            {
               "value" : "",
               "name" : "Mask Status"
            }
         ],
         "binningParameters" : [
            {
               "name" : "WPS-ActivePower-Average",
               "value" : "1145.5"
            },
            ...
         ],
         "maskTime" : "",
         "condition" : "WPS-ActivePower 1151-1403",
         "rpm" : 1000,
         "rpmStatus" : "",
         "operationalValues" : [
            {
               "name" : "Measured RPM",
               "value" : 1419.991
            },
            ...
         ],
         "alarmStatus" : "",
         "timeStamp" : "2019-05-24T16:23:44+00:00",
         "duration" : 5
      },
      "set" : [
         {
            "xValueDelta" : 0.0001245678,
            "yValues" : [
               0,
               0.373824,
               0.406339,
               0.202908,
               0.213631,
               0.117062,
               0.141085,
               0.0677467,
               0.125728,
               0.0314338,
               0.082759,
               0.0540856,
               0.0638158,
               0.0430439
            ],
            "xValueOffset" : 0,
            "xValueUnit" : "s",
            "yValueUnit" : "1"
         }
      ]
   },
   "details" : {
      "sensorSerial" : "234567",
      "name" : "signal_1",
      "type" : "",
      "sensorName" : "Sensor_1",
      "sensorType" : "M-channel"
   },
   "location" : {
      "turbineName" : "T001",
      "configurationName" : "1.2 MW VS M-sys5 - i=98.765",
      "siteName" : "Site 1",
      "turbineSerial" : "2345678",
      "softwareVersion" : "m1.2.3.2019-11-14"
   }
}
```

### Extract FFT Timeseries from JSON files

CMS-ML provides a function to parse a collection of JSON files stored with the format
indicated above and extract FFT Timeseries from them.

This is done with the function `extract_cms_jsons`, which recieves the following arguments:

* `jsons_path (str)`: The path to a directory that contains the raw JSON files or the path to
a single JSON file.
* `output_path (str, optional)`: The output path where the generated FFT timeseries will be stored
as `csv` files. If not specified, a `pandas.DataFrame` will be returned.
* `start_time (str, datetime, optional)`: The minimum timestamp, inclusive. If None, the
timestamps have no minimum. Default is None.
* `end_time (str, datetime, optional)`: The maximum timestamp, exclusive. If None, the timestamps
have no maximum. Default is None.
* `turbines (list, optional)`: The turbines to include in the output. If None, all turbines in the
extracted dataframe are included. Default is None.
* `signals (list, optional)`: Names of the signals to process. If None, all signals in the
extracted data are included. Default is None.
* `context_fields (bool or list)`: If ``bool`` whether or not to parse the context columns from
the jsons. If ` `list`` parse only the given list of fields from the context. Defaults to ``True``.

### Example

Let's start by generating a JSON file to work with by calling the `cms_ml.make_demo_jsons`
function:

```python3
from cms_ml import make_demo_jsons

make_demo_jsons(path='data', force=True)
```

This will create a folder named `data` with a `demo.json` file inside with the format explained
above.

Now you can use the `cms_ml.cms_jsons.extract_cms_jsons` function to parse the generated JSON
file and extract FFT Timeseries from it:

```python
from cms_ml.cms_jsons import extract_cms_jsons

df = extract_cms_jsons(jsons_path='data/', context_fields=True)
```

The output will be a `pandas.DataFrame` with the format described [in the readme](
README.md#data-fromat)

```
 turbine_id             signal_id_x timestamp_x                                             values      signal_id_y         timestamp_y sensorName turbineName  xValueDelta  xValueOffset xValueUnit yValueUnit
0       T001  Sensor1_signal1_values  2020-01-01  [8.544281799811039, -2.0076341772953614, 2.422...  Sensor1_signal1 2020-01-01 00:00:00    Sensor1        T001       0.0025           0.0         Hz          1
1       T001  Sensor1_signal1_values  2020-01-01  [8.544281799811039, -2.0076341772953614, 2.422...  Sensor1_signal1 2020-01-01 01:00:00    Sensor1        T001       0.0025           0.0         Hz          1
2       T001  Sensor1_signal1_values  2020-01-01  [8.544281799811039, -2.0076341772953614, 2.422...  Sensor1_signal1 2020-01-01 02:00:00    Sensor1        T001       0.0025           0.0         Hz          1
3       T001  Sensor1_signal1_values  2020-01-01  [8.544281799811039, -2.0076341772953614, 2.422...  Sensor1_signal1 2020-01-01 03:00:00    Sensor1        T001       0.0025           0.0         Hz          1
4       T001  Sensor1_signal1_values  2020-01-01  [8.544281799811039, -2.0076341772953614, 2.422...  Sensor1_signal1 2020-01-01 04:00:00    Sensor1        T001       0.0025           0.0         Hz          1
```

#### Storing the output as a CSV

If you want this process to automatically save the extracted data as a `csv` file, you can specify
an output path where the extracted FFT Timeseries will be saved:

```python
extract_cms_jsons(jsons_path='data/', output_path='fft_timeseries.csv')
```
