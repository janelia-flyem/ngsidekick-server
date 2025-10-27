# ngsidekick-server

Http endpoints to supplement neuroglancer scenes.

## Segment property transformations

The `/segprops/...` API processes an existing `precomputed` segment properties source and filters/transforms it according to expressions you provide as arguments in the URL.

There are two supported API calls (`label` and `tags`):

- `precomputed://https://<ngsidekick-server>/segprops/<dataset>/label/...`
- `precomputed://https://<ngsidekick-server>/segprops/<dataset>/tags/...`

### Using `.../label/...`

To provide a custom label segment property (appearing in neuroglancer in the neuroglancer segment list), provide a Python format string as a template to combine one or more properties from the source data into a single string.

Example: `{type} ({somaSide}) [{group}]`

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/label/{type} ({somaSide}) [{group}]
```

Results in labels like `AN01A006 (L) [53588]`

You can define more than one property by appending more components to the URL and using `=` to name the properties.  Such properties are not shown in neuroglancer, but they CAN be referenced in the final label:

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/label/myprop = ({somaSide})/myprop2 = [{group}]/{type} {myprop} {myprop2}
```

### Using `.../tags/...`

You can filter/combine any properties from the source data into tags to be shown in the UI.

Select (only) the tags from the source you want to see:

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/superclass/class/somaSide
```

Or define your own tag with a boolean expression:

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/mytag = trumanHL == "01A" and somaSide == "R"
```

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/mytag = trumanHL in ("01A", "01B") and somaSide == "R"
```

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/kenyon = type.str.startswith("KC")
```

Or both: select a subset and define a new tag:

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/superclass/class/somaSide/kenyon = type.str.startswith("KC")
```

To define a new tag and also pass through all tags from the input, use the special name `_all_tags`

```
precomputed://https://ngsidekick-server-833853795110.us-east4.run.app/segprops/male-cns-v0.9/tags/_all_tags/kenyon = type.str.startswith("KC")
```

Or use `_default_tags` to exclude tags with more than 1000 options (to avoid UI clutter):

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





### Limitations

Since arguments are delmited by `/` in the URL, your template strings and expressions can't use `/` internally.  In tag expressions, you can use pandas `.div()` as a workaround.  For template strings, there is currently, no workaround.



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

