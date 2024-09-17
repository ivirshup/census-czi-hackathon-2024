# census with anndata + zarr

This repo contains work for trying to build a lighter weight census using features in anndata + zarr for the CZI 2024 hackathon.

## Tasks

The initial two tasks for this project will be:

* Create a bucket with zarr formatted versions of the census
* Creating a data loader that will read data from the census
* Create a website that exposes features the explorer on top of the same s3 bucket 


## Resources

### Bucket

The bucket we'll be working with is: `s3://tmp-census-zarr` on `us-west-2`.

### AnnData queries

* [OOC Dataframes for anndata](https://github.com/scverse/anndata/pull/1247)

### Vitessce

* [Docs](https://python-docs.vitessce.io/index.html)
    * [AWS S3 Example](https://python-docs.vitessce.io/notebooks/data_export_s3.html#4.-Create-a-boto3-resource-with-S3-credentials)
* [vitessce-python repo](https://github.com/vitessce/vitessce-python)

### Zarr

* https://zarr.readthedocs.io/en/stable/
