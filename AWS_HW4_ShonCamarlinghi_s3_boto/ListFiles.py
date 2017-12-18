# -*- coding: utf-8 -*-
"""03) ListFiles.py will have these command line arguments:
user-name password
For example: python ListFiles.py MtCat NiceCat
For each user file stored, this Python script prints one line to the console:
file-key
example:
a) So if you ran the CreateUser, followed by running the UploadFile.py script twice:
python CreateUser.py MyUserName MyPassword
python UploadFile.py MyUserName MyPassword CatPicture .\cat.png
python UploadFile.py MyUserName MyPassword DogPicture .\dog.png
b) Followed by a call to ListFiles:
python ListFiles.py MyUserName MyPassword
you will see this output:
CatPicture
DogPicture"""

import boto
import boto.vpc
import subprocess
import sys, os
sys.path.append(os.getcwd())
import CreateUser

region = 'us-west-1'
conn = boto.ec2.connect_to_region(region)
vpccon = boto.vpc.connect_to_region(region)
vpcid = 'vpc-a52044c1'   #get vpc-id from VPC Dashboard
vpc = vpccon.get_all_vpcs(vpc_ids=[vpcid])[0];
secgrpid = 'sg-19f4167f'  #get security group id, from "Security Groups" section of EC2 mngmnt console
group = conn.get_all_security_groups(group_ids=[secgrpid])[0]
sn = vpccon.get_all_subnets(filters={'vpcId':[vpcid]})  #get subnet from VPC
sn1 = sn[0]
# # get KeyPair from Keypairs in region, must be on machine to use ssh
keypairname = 'myEC2instance' #name only, not actually key itself
key = conn.get_all_key_pairs(keynames=[keypairname])[0]
amiid = 'ami-327f5352' # free tier Linux AMI from EC2 > LaunchInstance
s3 = boto.connect_s3()

def main():
    user = str(sys.argv[1])
    pswd = str(sys.argv[2])
    b = s3.get_bucket(user)
    for o in b:
        print o.name





def bashcmd(cmd):
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


if __name__ == '__main__':
    main()