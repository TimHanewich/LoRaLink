# LoRaLink Changelog
|Version|Commit|Description|
|-|-|-|
|0.2.0|6c481a10d2eadfe740f8955398c9f0ca9cea7fb5|Base program, fully functional|
|0.2.1|9bad8855b373c5c762ff2538a125f9ff9f09fa84|Improved boot loading, fatal error handling|
|0.2.2|76d6973755a1986c27564778f274e58d74fda3c6|Introduced bug fixes to reyax module, improving stability in scenarios where a received LoRa message may interupt a command & response pair over UART|
|0.3.0|bbd22852eec663a11648f75136914e3bd01e1315|OperationalCommands are only sent to the rover if the control input has changed since the most recent OperationalCommand was sent (should reduce current consumption by RYLR998 constantly sending repetitive commands unnecessarily)|