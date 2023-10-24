#! /bin/bash
export DTT_VC_API_APP_DIR=$PWD
export DTT_VC_API_TAG=0.0.82
export DTT_VC_API_IMAGE=idlaborg/dtt-vc-api:$DTT_VC_API_TAG

docker build -t $DTT_VC_API_IMAGE .
docker push $DTT_VC_API_IMAGE

cd ../helm
helm upgrade \
    --install dtt-vc-api . \
    --namespace dtt-vc-api \
    --set vc_api.image=$DTT_VC_API_IMAGE \
    --create-namespace

cd $DTT_VC_API_APP_DIR