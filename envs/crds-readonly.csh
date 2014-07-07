# Normally /grp/crds/cache is readonly anyway.   In the case of CRDS server users,
# readonly is enforced in CRDS software,  not OS permissions, because the server user
# has permissions to write to the cache.
setenv CRDS_SERVER_URL https://crds-serverless-mode.stsci.edu
setenv CRDS_PATH /grp/crds/cache
setenv CRDS_READONLY_CACHE  1

