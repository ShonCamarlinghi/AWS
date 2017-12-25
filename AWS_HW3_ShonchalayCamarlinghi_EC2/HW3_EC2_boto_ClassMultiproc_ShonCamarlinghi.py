import time
import boto.vpc
import multiprocessing, subprocess, sys, os
from multiprocessing import Process, Queue, Pool


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
    # q = Queue()
    # pool = Pool(processes=4)
    # pool.map(q_function(q), range(3))
    # # res = pool.apply_async(q_function(q))
    q = Queue()
    for z in xrange(4):
        z = multiprocessing.Process(name=z, target=q_function, args=(q,))
        z.daemon = True
        z.start()
        time.sleep
        z.join()

#  regex pattern in bash stdout  (see q_function, commented out line)  and finish process'
    # if 'Heroku' in q.get():
    #     print 'Heroku launched!'
    #     Heroku.join()

# class instance(conn, amiid, group, sn1, keypairname):
class instance(object):

    def __init__(self):
        self.reservation = conn.run_instances(amiid,
                                          instance_type='t2.micro',
                                          security_group_ids=[group.id],
                                          subnet_id=sn1.id,
                                          key_name=keypairname,
                                          # min_count = 1,
                                          # max_count =4
                                          )

        time.sleep(30)
        self.reservation = conn.get_all_reservations(filters={'instance-state-name': 'running'})
        for x in self.reservation:  #type(x) == 'class'; type self.i == 'unicode'
            self.i = x.instances[0].id
        if True:
            # print "Instance ID %s is up and running, type %s" % (self.i, type(self.i))
            print "Instance ID %s is up and running, type %s" % (self.i, type(self.i))
        else:
            "Instance failed to start, please restart/debug your script..."

    def statusChangeCheck(self,status):
        # *.update(), *.state() works only for type(*) == class
        for x in self.reservation:
            pass
        while True:
            time.sleep(2)
            #print type(x.instances[0]) will print <class 'boto.ec2.instance.Instance'>
            x.instances[0].update()
            if x.instances[0].state == status:
                print x.instances[0].id + ' ' + status
            break

    def stop(self):
        conn.stop_instances(self.i)
        print "Stopping instance: %s" % self.i

    def terminate(self):
        conn.terminate_instances(self.i)
        print "Terminating instances: %s" % self.i

def s_function(): # managing EC@ instances: start, check status, stop, terminate.
    s = instance()
    s.stop()
    s.statusChangeCheck('stopped')
    s.terminate()
    s.statusChangeCheck('terminated')

def q_function(q): # multiprocessing function, q = Queue() defined in main()
    p = multiprocessing.current_process()
    print '\nStarting: ', p.name, p.pid
    sys.stdout.flush()
    #q.put(subprocess.call((''.join([r'RAW BASH SHELL COMMAND WITH ARGS AND OPTIONS'])), stderr=subprocess.STDOUT, shell=True))
    q.put(s_function())  #actual function to be run in parallel, in queue
    print '\nFinished: ', p.name, p.pid


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
