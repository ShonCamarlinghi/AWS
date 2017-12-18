# -*- coding: utf-8 -*-
'''05) DeleteFile.py will have there command line parameters:
user-name password file-key
For example:
python DeleteFile.py MrCat NiceCat Bird01
where MrCat is a user-name and NiceCat is the password from a previous running of the CreateUser.py script'''


import os
import subprocess
import sys
from boto.s3.key import Key
import boto.vpc

sys.path.append(os.getcwd())

region = 'us-west-1'
conn = boto.ec2.connect_to_region(region)
vpccon = boto.vpc.connect_to_region(region)
vpcid = 'vpc-a52044c1'  # get vpc-id from VPC Dashboard
vpc = vpccon.get_all_vpcs(vpc_ids=[vpcid])[0];
secgrpid = 'sg-19f4167f'  # get security group id, from "Security Groups" section of EC2 mngmnt console
group = conn.get_all_security_groups(group_ids=[secgrpid])[0]
sn = vpccon.get_all_subnets(filters={'vpcId': [vpcid]})  # get subnet from VPC
sn1 = sn[0]
# # get KeyPair from Keypairs in region, must be on machine to use ssh
keypairname = 'myEC2instance'  # name only, not actually key itself
key = conn.get_all_key_pairs(keynames=[keypairname])[0]
amiid = 'ami-327f5352'  # free tier Linux AMI from EC2 > LaunchInstance
s3 = boto.connect_s3()


def main():
    user = str(sys.argv[1])
    pswd = str(sys.argv[2])
    tag = str(sys.argv[3])


    b = s3.get_bucket(user)
    for o in b:
        print o.key
        if str(o.key) == tag:
            o.delete()
            print 'Deleted %s from %s' % (o.key, b)


def bashcmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


if __name__ == '__main__':
    main()