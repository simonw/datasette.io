---
title: Datasette for exploratory analysis
summary: Import data from CSVs, JSON, database connections and more. Datasette will automatically show you patterns in your data and help you share your findings with your colleagues.
order: 1
---

Your first step with any new data set should be to start exploring it. Datasette provides multiple tools for doing this.

## Start browsing the data

Datasette's table interface lets you start scrolling through data straight away.

![Screenshot of the table interface](/static/datasette-screenshot.png)

## Facets

Datasette automatically identifies columns with less than twenty unique values and gives you the option to facet by them - seeing the most common values, and selecting those to filter the set. This provides a powerful way to start spotting patterns in the data.

![Screenshot of the facet interface](/static/screenshots/facets.png)

## Visualization

Plugins such as [datasette-vega](https://github.com/simonw/datasette-vega) and [datasette-cluster-map](https://github.com/simonw/datasette-cluster-map) provide tools for interactively visualizing data directly within the Datasette interface.

![Screenshot of datasette-cluster-map](/static/screenshots/datasette-cluster-map.png)
