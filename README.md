# ngsidekick-server

Http endpoints to supplement neuroglancer scenes.

This little project is still in the experimental/prototyping stage.

## Segment property transformations

The `/segprops/...` API processes an existing `precomputed` segment properties source and filters/transforms it according to expressions you provide as arguments in the URL.

Overview:

- Define a custom format for the segment labels:
    - `.../label/{superclass} - {type}`
- Reduce UI clutter by showing just a subset of tags from the source data:
    - `.../tags/superclass/class/somaSide`
- Query for subsets of segments by defining your own tags:
    - `.../tags/mytag = (trumanHl == "01A" or trumanHl == "01B")`

[Here's an example.](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.103606.337212.json) Details below.

## API

There are two supported API calls (`label` and `tags`):

- `precomputed://https://<ngsidekick-server>/segprops/<dataset>/label/...`
- `precomputed://https://<ngsidekick-server>/segprops/<dataset>/tags/...`

**Note**: Although it's common to include all segment properties in a single `source` URL, neuroglancer allows you to provide separate sources for labels, tags, and numeric segment properties (one source for each type of data).


### Using `.../label/...`

To provide a custom label segment property (appearing in the neuroglancer segment list), provide a Python format string as a template to combine one or more properties from the source data into a single string.

Example ([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.093051.846407.json)): `{type} ({somaSide}) [{group}]`

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/label/{type} ({somaSide}) [{group}]
```

Results in labels like `AN01A006 (L) [53588]`

You can define more than one property by appending more components to the URL and using `=` to name the properties.  Such properties are not shown in neuroglancer, but they CAN be referenced in the final label expression.

For example, to avoid having empty `type` strings appear at the top of the segment list, replace them with `~` before constructing the label:

Example ([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.094641.067798.json)):

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/label/type2 = type.replace("", "~") / {type2} ({somaSide}) [{group}]
```


### Using `.../tags/...`

You can filter/combine any properties from the source data to show as tags in the UI.  Examples below.

Select (only) the tags from the source you want to see ([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.094838.732871.json)):

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/superclass/class/somaSide
```

Or define your own tag with a boolean expression:

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.095757.381530.json))

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/mytag = (trumanHl == "01A" or trumanHl == "01B")
```

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.095856.830318.json))

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/mytag = (trumanHl in ("01A", "01B") and somaSide == "R")
```

Your expressions are evaluated using pandas [`DataFrame.eval()`][eval], which [allows various helper functions][eval-syntax] such as `str.startswith()`, etc. (but is not a full python interpreter).

[eval]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.eval.html
[eval-syntax]: https://pandas.pydata.org/docs/user_guide/enhancingperf.html#enhancingperf-eval

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.100052.674517.json))

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/kenyon = type.str.startswith("KC")
```

You can define your own tags and pass through existing tags at the same time:

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.100541.308440.json))


```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/superclass/class/somaSide/kenyon = type.str.startswith("KC")
```

#### Convenience subsets

To pass through **all** tags from the input, use the special name `_all_tags`:

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.100714.370555.json))


```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/_all_tags/kenyon = type.str.startswith("KC")
```

Or use `_default_tags` to exclude tag categories with more than 1000 options (to avoid UI clutter when the source data includes tags like `supertype`).

([link](https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/2025-10-27.100811.371893.json))


```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/_default_tags/kenyon = type.str.startswith("KC")
```

### Named datasets

In API calls such as `<ngsidekick-server>/segprops/<dataset>/label/...`, the `<dataset>` argument must be one of the following:

- One of the hard-coded dataset names [listed in the `ngsidekick-server` code][datasets].
- A path to a neuroglancer `precomputed` segment properties directory, beginning with `gs://` or `https://`
    - Example:
        ```
        precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/gs://flyem-male-cns/v0.9/segmentation/combined_properties/label/{type} ({somaSide})
        ```

[datasets]: https://github.com/janelia-flyem/ngsidekick-server/blob/main/src/ngsidekick_server/app.py#L10


**Note:** The datasource for `male-cns-v0.9` doesn't include all properties from neuprint.  A more comprehensive set of properties is available via `male-cns-0.9-all`, which includes less commonly used properties like `mancGroup, mancSerial, mcnsSerial` and a few others.  It's a bigger file, so it results in slower queries.


### Limitations

Since arguments are delmited by `/` in the URL, your template strings and expressions can't use `/` internally.  In tag expressions (or numeric properties), you can use pandas `.div()` as a workaround:

```
# (The `/label/` API can also produce numeric properties, but your expression must avoid producing `NaN` values.)
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/label/average_tbar_fanout = syn_downstream.div(syn_pre.clip(lower=1))
```

For template strings, there is currently no workaround for `/` characters.  You must avoid them in your segment labels.

## Future development

- This server reads from `precomputed` segment properties, which makes it compatible with many existing neuroglancer scenes.  However, that's not a particularly efficient format for reading.  In a future version, it wouldn't be hard to read from Apache Feather data sources or Parquet sources, which would be faster.  (It would be possible to read only the columns the user has referenced in their query, for example.)

- It might be possible to support more sophisticated template string expressions using jinja templates or Pythion f-strings, but there are significant security considerations.

## Running the Development Server

```bash
# Option 1: Run directly
python src/ngsidekick_server/app.py

# Option 2: Use Flask CLI
export FLASK_APP=src/ngsidekick_server/app.py
export FLASK_ENV=development
flask run
```

The server will start on http://localhost:8000

## Docker Deployment

```
gcloud auth login
gcloud auth configure-docker us-east4-docker.pkg.dev  # first time only

docker build --platform linux/amd64 . -t us-east4-docker.pkg.dev/flyem-private/ngsidekick/ngsidekick-server
docker push us-east4-docker.pkg.dev/flyem-private/ngsidekick/ngsidekick-server
```

