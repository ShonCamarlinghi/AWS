# -*- coding: utf-8 -*-
'''user-name password file-key path-to-file-to-upload

user-name = the user-name from CreateUser.py
password = the user's password from CreateUser
file-key = is a tag/string that the user can associate with an uploaded file
path-to-file-to-upload = the path to a file on your machine to save in S3
The file-key and path-to-file-to-upload may have spaces
For example:
python UploadFile.py MrCat NiceCat My-Favorite-Dog-Picture .\dog1.jpg
You must handle typical errors like: user does not exist, bad password, cannot find file'''

# -*- coding: utf-8 -*-
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
    tag = str(sys.argv[3])
    picture = str(sys.argv[4])
    directoryContent = os.listdir('./')
    print directoryContent
    if picture[3:] in directoryContent:
        b = s3.get_bucket(user)
        anothernewkey = b.new_key(tag)
        anothernewkey.set_contents_from_filename(picture)
        anothernewkey.set_acl('public-read')
        uploadURL = 'https//s3.amazonaws.com/%s/%s' % (user,tag)
        print uploadURL

    else:
        print 'Picture your are trying to upload does not exist in your current directory..'
        sys.exit()






def bashcmd(cmd):
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


if __name__ == '__main__':
    main()



