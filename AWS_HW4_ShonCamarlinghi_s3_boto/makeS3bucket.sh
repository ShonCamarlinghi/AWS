#!/bin/bash

bucketname='ucscawscli'
bucketname="s3://"$bucketname"$(echo $RANDOM)"
echo bucket name is :$bucketname
aws s3 mb $bucketname
sleep 10

echo "$(aws s3 ls | grep ucscawscli)"


echo "BlaBlaBlaCommandLine" > Isfile.txt
cat Isfile.txt

aws s3 sync . $bucketname
sleep 5
aws s3 ls $bucketname

aws s3 cp $bucketname/Isfile.txt IsfileFromS3.txt

sleep 5

aws s3 rb $bucketname --force
