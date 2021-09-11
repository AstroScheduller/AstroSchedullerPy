![astro_scheduller_logo](src/astro_scheduller.jpg)

# Preparations

## Environment

**Python Version** >= 3.8 *(Highly Recommended)*

**Required Python Packages:** :

```
astropy
matplotlib
numpy
Tkinter
```

**See [requirements.txt](https://github.com/xiawenke/AstroScheduller/blob/main/requirements.txt)*.

**The default Anaconda environment includes all of the above required runtime libraries.*



## Preparation: Observation Parameters & Sources

This is the “input parameter” of the AstroScheduller, which is a text file in JSON format. **Please save the file in the directory where the script is located.** 

### List of Observation Objects

This is a list of all the objects (observation targets/sources) that you want to observe in one observation.

| **Name**                              | **Parameter** | **Format**                | **Required**        |
| :------------------------------------ | :------------ | :------------------------ | :------------------ |
| Identifier of the object              | identifier    | list(str, str, ... , str) | True                |
| Duration of the observation (in sec.) | dur           | int.                      | True                |
| Weight*                               | weight        | float (0-1)               | False  (Default: 1) |
| Force to observe**                    | force         | bool (False=0 / True=1)   | False  (Default: 0) |

\* Higher weights means higher priority to be observe. 

\*\* Observations of the source will be scheduled immediately when can be observed (even though this is not an optimal possibility).

### Observation Parameters

| **Name**                               | **Parameter** | **Format**                                                   | **Required** |
| :------------------------------------- | :------------ | :----------------------------------------------------------- | :----------- |
| Observation starts                     | obs_start     | YYYY.MM.DD hh:mm:ss                                          | True         |
| Observation ends                       | obs_end       | YYYY.MM.DD hh:mm:ss                                          | True         |
| Telescope location                     | tele_loc      | [Lat., Lon., Hei.]                                           | True         |
| Range of altitude/elevation* (in deg.) | elev_range    | [min., max.]                                                 | True         |
| Smallest angle to the sun** (in deg.)  | escape_sun    | int. *(Deg. From Sun)*                                       | True         |
| List of observation objects            | sources       | The JSON format text created in the last part (List of Observation Objects) of the documentation. | True         |

\* Range of altitude/elevation: the maximum and minimum elevation angle of the observation that the object can be observed.

\*\* Smallest angle to the sun: the minimum angle from the Sun that the telescope can operate to observe.

### Example

```json
{
    "obs_start": "2021.07.24 02:00:00", #Format: "YYYY.MM.DD hh:mm:ss"
    "obs_end": "2021.07.24 11:00:00", #Format: "YYYY.MM.DD hh:mm:ss"
    "tele_loc": [32.701500, -109.891284, 3185], 
                #Format: [Lat., Lon., Hei.] (AZ Tele.)
    "elev_range": [30, 80], #Format: [min., max.] (AZ Tele.)
    "escape_sun": 10, #Format: [Deg. From Sun]
    "sources":
        [
            {"identifier": "G005.88-00.39", "dur": 1200, "weight": 1},                
            {"identifier": "J1935+2154", "dur": 1200, "weight": 0.1},            
            {"identifier": "J1935+2154", "dur": 1200, "force": 1},
            ...
            {"identifier": "G160.14+03.15", "dur": 1200}
            #Object identifiers (e.g. "J1935+2154")           observation duration(e.g. 1200)
        ]
} # The script supports adding comments starting with "#" to the JSON file entered in the script.
```

Another example: [psr_list_debug.txt](https://github.com/xiawenke/AstroScheduller/blob/main/test/psr_list_debug.txt)



## Offline Source Coordinates Database

The source coordinates database is a solution to the problem that the Astropy package needs to be connected to the Internet to get the pulsar coordinates (for some computers are not connected to the Internet). Similar to the source table, the source database is an array file in JSON format, which needs to be **saved in the same directory as the script under the file name "sources.db"**.

The structure of the source database is as follows.

```bash
[
    {
        "RA": "[坐标R.A.]",
        "DEC": "[坐标Dec.]",
        "IDENTIFIER": [
            "[源名1]", "[源名2]", ...
        ]
    },
    ...
    {
        "RA": "00:06:04.8",
        "DEC": "+18:34:59",
        "IDENTIFIER": [
            "J0006+1834"
        ]
    },
    {
        "RA": "00:07:01.7",
        "DEC": "+73:03:07.4",
        "IDENTIFIER": [
            "J1807-0847", "B1804-08"
        ]
    },
]
```

Source coordinates can be generated automatically. When the script runs online and encounters a source that is not defined in the database, it downloads the data from SIMBAD via the Astropy package and appends it to end of the database. See instructions in "Generate an offline database" in the "Tips and Tricks" section of the documentation for more details.

