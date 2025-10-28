.. _aws:

AWS
---

The CRDS client can be configured to read files from Amazon's S3 service. The STScI AWS environment currently hosts files in the following buckets:

+-----------------+-----------------------+------------------+
| Environment     | S3 Bucket Name        | S3 Prefix        |
+=================+=======================+==================+
| HST OPS         | hst-crds-cache-ops    |                  |
+-----------------+-----------------------+------------------+
| HST TEST        | hst-crds-cache-test   |                  |
+-----------------+-----------------------+------------------+
| ROMAN OPS       | stpubdata             | /roman/crds      |
+-----------------+-----------------------+------------------+
| ROMAN TEST      | stpubdata-tst         | /roman/crds/test |
+-----------------+-----------------------+------------------+
| ROMAN INT       | stpubdata-tst         | /roman/crds/int  |
+-----------------+-----------------------+------------------+

.. tip::
    
    Your compute environment must be configured with AWS credentials that have been granted access to the bucket. The Roman Ops CRDS cache is hosted in the publicly-accessible AWS Open Data bucket so any valid AWS credentials can be used.


Configuring CRDS to use S3
+++++++++++++++++++++++++++

The CRDS client must be configured with environment variables to read files from S3 buckets. The exact configuration depends on the observatory. CRDS provides a convenience wrapper script `crds_s3_set` to automatically set the requisite environment vars depending on the observatory and use case inputs.

- `crds_s3_set` sets the necessary environment variables to read files from S3. This can be done manually in lieu of using the setter script. The exact variables required can be found by running the script, viewing the source code, or looking at the examples below.

When CRDS detects that S3 access is enabled via the `CRDS_MODE=s3` environment variable, it will automatically use the S3 buckets for downloading mapping and reference files instead of the HTTP-based CRDS server.

Prerequisites
.............

    1. The `boto3` and `awscli` packages must be installed in the CRDS environment to enable S3 access. This can be done via pip when installing CRDS by specifying the `aws` extra dependencies:

    .. code-block:: bash
    
        $ pip install crds[aws]


    2. The compute environment must be configured with AWS credentials that have been granted access to the appropriate bucket. This is typically done by configuring the AWS CLI with `aws configure` or by setting the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables. Only Roman Ops is publicly available in the AWS OpenData bucket (any valid AWS credentials are acceptable); HST buckets are accessible to STScI internal users only, and at this time STScI does not host any public S3 buckets for JWST CRDS access.

Here are example commands to configure CRDS for S3 access:

.. tabs::

   .. group-tab:: ROMAN

        The s3 buckets for Roman only contain mappings and references from the last 5 contexts. The CRDS cache for Roman Ops is publicly accessible in the Open Data bucket. If you do not want to use the latest context, you will need to manually set the `CRDS_CONTEXT` environment variable as well.

        Using the `crds_s3_set` script to automatically set environment variables:
    
        .. code-block:: bash

            # Set CRDS_PATH to your local cache directory (will be created if it doesn't exist)
            # Defaults to /tmp/crds_cache if not set in advance
            $ export CRDS_PATH=/path/to/local/cache
            # source crds_s3_set <observatory> <environment>
            $ source crds_s3_set roman ops

        
        If setting manually, the equivalent environment variables would be:

        .. code-block:: bash

            $ export CRDS_PATH=/path/to/local/cache
            $ export CRDS_MAPPING_URI=s3://stpubdata/roman/crds/mappings/roman
            $ export CRDS_DOWNLOAD_MODE=plugin
            $ export CRDS_DOWNLOAD_PLUGIN='crds_s3_get ${FILENAME} -d ${OUTPUT_PATH} -s ${FILE_SIZE} -c ${FILE_SHA1SUM}'
            $ export CRDS_S3_ENABLED=1
            $ export CRDS_S3_BUCKET=stpubdata
            $ export CRDS_REF_SUBDIR_MODE=flat
            $ export CRDS_SERVER_URL=https://roman-crds-serverless.stsci.edu
            $ export CRDS_CONFIG_URI=s3://stpubdata/roman/crds/config/roman
            $ export CRDS_S3_PREFIX=/roman/crds
            $ export CRDS_OBSERVATORY=roman
            $ export CRDS_REFERENCE_URI=s3://stpubdata/roman/crds/references/roman
            $ export CRDS_MODE=s3
            $ export CRDS_S3_RETURN_URI=0


   .. group-tab:: HST
    
        The S3 buckets for HST exclude mapping files, so the client must be configured to load the context's rules from a pickle file.  Here is an example configuration for the HST OPS bucket:

        Using the `crds_s3_set` script to automatically set environment variables:
    
        .. code-block:: bash
        
            # Set CRDS_PATH to your local cache directory (will be created if it doesn't exist)
            # Defaults to /tmp/crds_cache if not set in advance
            $ export CRDS_PATH=/path/to/local/cache
            # source crds_s3_set <observatory> <environment>
            $ source crds_s3_set hst ops


        If setting manually, the equivalent environment variables would be:

        .. code-block:: bash

            # If setting manually, the equivalent environment variables would be:
            $ export CRDS_PATH=/path/to/local/cache
            $ export CRDS_CONFIG_URI=s3://hst-crds-cache-ops/config/hst/
            $ export CRDS_REFERENCE_URI=s3://hst-crds-cache-ops/references/hst/
            $ export CRDS_PICKLE_URI=s3://hst-crds-cache-ops/pickles/hst/
            $ export CRDS_DOWNLOAD_MODE=plugin
            $ export CRDS_DOWNLOAD_PLUGIN='crds_s3_get ${SOURCE_URL} -d ${OUTPUT_PATH} --file-size ${FILE_SIZE} --file-sha1sum ${FILE_SHA1SUM}'
            $ export CRDS_SERVER_URL=https://hst-crds-serverless.stsci.edu
            $ export CRDS_USE_PICKLED_CONTEXTS=1
            $ export CRDS_S3_ENABLED=1
            $ export CRDS_S3_BUCKET=hst-crds-cache-ops
            $ export CRDS_S3_PREFIX=''
            $ export CRDS_OBSERVATORY=hst
            $ export CRDS_MODE=s3
            $ export CRDS_S3_RETURN_URI=0
            $ export CRDS_REF_SUBDIR_MODE=flat



Fetching CRDS Files from S3
............................

Once the environment is configured for S3 access, CRDS commands such as `crds sync` and `crds bestrefs` as well as mission-specific calibration pipeline commands will automatically fetch files from S3 as needed. The context defaults to `latest` if not specified explicitly (same behavior as other modes). Here are some example commands:

  .. code-block:: bash
    
        # Run romancal pipeline (will download necessary mappings/references from S3)
        $ strun romancal.pipeline.ExposurePipeline l1_img.asdf
    
        # Alternatively: Sync all files from the S3 bucket to the local cache
        $ crds sync --all

