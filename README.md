![Image 1](./docs/github.gif)

This project provides an easy-to-use set of tools for visual processing of your GPS data. For now, GPX and FIT formats are supported. The maps are sourced from Mapbox.com and in order to use it you need to create a free account there first. Then, you can create your own custom map styles using the Mapbox Studio which provides you with the last two neccessary pieces: your token ID and your custom map style ID. These credentials along with your Mapbox username are then passed to the tools provided here and rendering of image frame sequences may begin.

Downloaded map tiles are cached/saved on local disk by your specification to minimze the number of prompts.

Output consists of two image sequences: map-image frame sequence and timestamp image sequence. Those can be then processed in a software like DaVinci Resolve to create videos or animations along with your GoPro camera footage, for example. An example of such use can be found here: https://youtu.be/QCelI4TwC4U



