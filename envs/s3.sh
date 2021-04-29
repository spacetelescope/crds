# export CRDS_MAPPING_URL=https://s3.us-east-1.amazonaws.com/account/crds_cache/mappings/jwst
# export CRDS_REFERENCE_URL=https://s3.us-east-1.amazonaws.com/account/crds_cache/references/jwst

export CRDS_SERVER_URL=https://jwst-serverless.stsci.edu
export CRDS_PATH=$HOME/crds_cache

export CRDS_S3_ENABLED=1
export CRDS_S3_RETURN_URI=0
export CRDS_MAPPING_URI=s3://account/crds_cache/mappings/jwst
export CRDS_REFERENCE_URI=s3://account/crds_cache/references/jwst
# export CRDS_REFERENCE_URI=https://s3.us-east-1.amazonaws.com/account/crds_cache/references/jwst
export CRDS_CONFIG_URI=s3://account/crds_cache/config/jwst

# To use pickled contexts,  set CRDS_S3_ENABLED=0 and CRDS_USE_PICKLED_CONTEXTS=1
export CRDS_USE_PICKLED_CONTEXTS=0
export CRDS_PICKLE_URI=s3://account/crds_cache/pickles/jwst

export CRDS_DOWNLOAD_MODE=plugin
export CRDS_DOWNLOAD_PLUGIN='crds_s3_get ${SOURCE_URL} ${OUTPUT_PATH} --file-size ${FILE_SIZE} --file-sha1sum ${FILE_SHA1SUM}'
