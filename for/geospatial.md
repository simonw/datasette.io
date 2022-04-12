---
title: Datasette for geospatial analysis
summary: Combining Datasette with SpatiaLite provides a powerful set of tools for analyzing and visualizing geospatial data.
order: 5
---

The [SpatiaLite](https://www.gaia-gis.it/fossil/libspatialite/index) extension for SQLite can be used with Datasette to enable a full suite of geospatial SQL functions.

![A screenshot of Datasette running some geospatial plugins](https://camo.githubusercontent.com/56a2ed7e65e28e726d4c3abfbe56bd7960524e6af6512fc2cee083bdd7fcd863/68747470733a2f2f7374617469632e73696d6f6e77696c6c69736f6e2e6e65742f7374617469632f323032312f6461746173657474652d6c6561666c65742d66726565647261772e706e67)

Datasette has a number of plugins and tools that can be used to work with geospatial data.

Geospatial plugins include:

- [datasette-cluster-map](https://datasette.io/plugins/datasette-cluster-map) renders a map of markers for any table or query with `latitude` and `longitude` columns
- [datasette-geojson](https://datasette.io/plugins/datasette-geojson) adds a `.geojson` extension which can export SpatiaLite geometries as [GeoJSON](https://geojson.org/)
- [datasette-geojson-map](https://datasette.io/plugins/datasette-geojson-map) renders that GeoJSON output on a map
- [datasette-leaflet-freedraw](https://datasette.io/plugins/datasette-leaflet-freedraw) adds an interface to filter geometries by drawing a shape on a map
- [datasette-leaflet-geojson](https://datasette.io/plugins/datasette-leaflet-geojson) shows maps inline for any column that includes GeoJSON
- [datasette-tiles](https://datasette.io/plugins/datasette-tiles) allows Datasette to serve map tile images stored using the [MBTiles](https://github.com/mapbox/mbtiles-spec) format

Tools for working with geospatial data include:

- [geojson-to-sqlite](https://datasette.io/tools/geojson-to-sqlite), a command line utility for loading GeoJSON data into a SQLite or SpatiaLite database
- [shapefile-to-sqlite](https://datasette.io/tools/shapefile-to-sqlite), a command line utility for loading shapefiles into SQLite or SpatiaLite
- [download-tiles](https://datasette.io/tools/download-tiles) can be used to download map tiles and store them in MBTiles, suitable for use with [datasette-tiles](https://datasette.io/plugins/datasette-tiles)

The following tutorials provide more detail on how Datasette can be used for geospatial processing:

- [GUnion to combine geometries in SpatiaLite](https://til.simonwillison.net/spatialite/gunion-to-combine-geometries) shows how to load Amtrak data using `geojson-to-sqlite` and render it using `datasette-geojson-map`
- [KNN queries with SpatiaLite](https://til.simonwillison.net/spatialite/knn) shows how to use the KNN feature to run queries showing the nearest geometries to a point
- [Natural Earth in SpatiaLite and Datasette](https://til.simonwillison.net/gis/natural-earth-in-spatialite-and-datasette) shows how to use the 791MB [Natural Earth](https://www.naturalearthdata.com/) SQLite vector database with Datasette
- [Drawing shapes on a map to query a SpatiaLite database](https://simonwillison.net/2021/Jan/24/drawing-shapes-spatialite/) introduces the `datasette-leaflet-freedraw` plugin