# -*- coding: utf-8 -*-
import os, sys, time, boto, boto.vpc, subprocess, re, boto, string, random, math
from boto.s3.key import Key


#PARAMS
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
    prefix = 'camarlinghi_'
    ran = random_generator()
    user = prefix + str(sys.argv[1]) + '_' + ran
    pswd = str(sys.argv[2]) + '_' + ran
    email =  ran + '@' + str(sys.argv[3]) #enter only email service domain
    mainBucket = 'intero6'

    sys.stdout.flush()
    time.sleep(5)

    makeIntero(mainBucket)

    makeUserBucket(user, email, pswd)

    key_value(mainBucket, email, pswd)

    return user, email, pswd


def makeIntero(x):
    global interoB
    lookupS3(x)
    if x not in stringBucketlist:
        print 'Main bucket is missing, making main bucket'
        x = s3.create_bucket(x)
        time.sleep(5)
        print x, type(x)
    else:
        pass

def makeUserBucket(user, email, pswd):
    lookupS3(user)
    print stringBucketlist
    if user in stringBucketlist:
        print 'BUCKET EXISTS: ', user
        print 'Updating pswd and email for: ', user
        key_value(user, email, pswd)
    else:
        print 'BUCKET DOES NOT EXIST: ', user
        # try:
        s3.create_bucket(user)
        time.sleep(10)
        lookupS3(user)
        print stringBucketlist
        if user in stringBucketlist:
            print 'BUCKET EXISTS: ', user
            print 'Updating pswd and email for: ', user
            key_value(user, email, pswd)
        # except boto.exception.S3CreateError: str(409)
        # print 'Username already taken, please try running createUser.py with a different username'
        # sys.exit()


def bashcmd(cmd):
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out

def random_generator():
    size = 4
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))

def lookupS3(x):
    global stringBucketlist
    global classBucketlist
    stringBucketlist = []
    classBucketlist = s3.get_all_buckets()
    for b in classBucketlist:
        stringBucketlist.append(str(b.name))

def key_value(user, email, pswd):
    b = s3.get_bucket(user)  # get boto class object
    newkey = b.new_key(user)
    newkey.set_metadata('email', pswd)
    newkey.set_metadata('pswd', email)


def instanceStatusChangeCheck(i, status):
    while True:
        time.sleep(2)
        i.instances[0].update()
        if i.instances[0].state == status:
            print i.instances[0].id + ' ' + status
            break



if __name__ == '__main__':
    main()










