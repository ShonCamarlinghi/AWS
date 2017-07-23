import boto.ec2
import boto.vpc
import time


#see 04_EC2_ProgrammingExamples.ppt.pdf in Classes/UCSC/AWS/ppts/

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


def main():
    for x in xrange(3):
        reservations = conn.run_instances(amiid,
                                      instance_type = 't2.micro',
                                      security_group_ids=[group.id],
                                      subnet_id=sn1.id,
                                      key_name=keypairname
                                        )
    time.sleep(60)
    print 'Checking what instances are running and stop them:'
    reservations = conn.get_all_reservations(
        filters={'instance-state-name': 'running'})  # other filter names: stopped, pending,
    print reservations

    ids = []
    for i in reservations:
       # print i.instances  # print running instances one-by-one
       # print i.instances[0].id  #extract running instance ids and uppend to a list for futher stop ans suspending
        ids.append(i.instances[0].id)
    print "Running instances"
    print ids  # instance_ids = ['instance-id-1','instance-id-2', ...]

     # conn.stop_instances(instance_ids=['instance-id-1','instance-id-2', ...])
    conn.stop_instances(ids)
    for i in reservations:
        print "Stopping instance: " + i.instances[0].id
        instanceStatusChangeCheck(i, 'stopped')  #other status values: stopped, pending, terminated,


    conn.terminate_instances(ids)
    for i in reservations:
        print "Terminating instances: " + i.instances[0].id
        instanceStatusChangeCheck(i, 'terminated')



def instanceStatusChangeCheck(i, status):
    while True:
        time.sleep(2)
        i.instances[0].update()
        if i.instances[0].state == status:
            print i.instances[0].id + ' ' + status
            break

if __name__ == '__main__':
    main()



                # print 'instance: %s is running', reservations.instances[0].id
# ec2.terminate_instances(instance_ids=[reservations.instances[0].id])

#===================================== boto API trials from  http://boto.cloudhackers.com/en/latest/ec2_tut.html ====================================
#import boto.ec2


#conn = boto.ec2.connect_to_region("us-west-1",
                                  #aws_access_key_id='',
                                 # aws_secret_access_key='')

# reservations = conn.get_all_reservations(
#     filters={'instance-state-name': 'stopped'})  # other filter names: stopped, pending,
# print reservations
#
#
#
# print 'Checking what instances are running:'
# ids = []
# for i in reservations:
#     print i.instances   # print instances one-by-one
#     print i.instances[0].id  # extracting instance id
#     ids.append(i.instances[0].id)
#
# print ids