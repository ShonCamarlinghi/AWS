# -*-coding: utf-8-*-
import boto.vpc
import boto.vpc.vpc
import paramiko
import string
import urllib2
import multiprocessing, subprocess, sys, os, time
from multiprocessing import Process, Queue, Pool


#see 04_EC2_ProgrammingExamples.ppt.pdf in Classes/UCSC/AWS/ppts/

#PARAMS
amiid = 'ami-31490d51' # free tier Linux AMI from EC2 > LaunchInstance
region = 'us-west-1'
ec2 = boto.ec2.connect_to_region(region)
vpccon = boto.vpc.connect_to_region(region)

vpcid = 'vpc-a52044c1'   #get vpc-id from VPC Dashboard
vpc = vpccon.get_all_vpcs(vpc_ids=[vpcid])[0]

secgrpid = 'sg-19f4167f'  #get security group id, from "Security Groups" section of EC2 mngmnt console
group = ec2.get_all_security_groups(group_ids=[secgrpid])[0]

sn = vpccon.get_all_subnets(filters={'vpcId':[vpcid]})  #get subnet from VPC
sn1 = sn[0]
# # get KeyPair from Keypairs in region, must be on machine to use ssh
keylocation = '/Users/...'
keyfilename = 'myEC2instance' #name only, not actually key itself
sshkeyfilename = keylocation + '/' + keyfilename + '.pem'
key = ec2.get_all_key_pairs(keynames=[keyfilename])[0]





def main():
    # q = Queue()
    # pool = Pool(processes=4)
    # pool.map(q_function(q), range(3))
    # # res = pool.apply_async(q_function(q))
    q = Queue()
    for z in xrange(3):  # 3 instances
        z = multiprocessing.Process(name=z, target=q_function, args=(q,))
        z.daemon = False
        z.start()
        z.join()


class instance(object):

    def __init__(self):
        self.reservation = ec2.run_instances(amiid,
                                          instance_type='t2.micro',
                                          security_group_ids=[group.id],
                                          subnet_id=sn1.id,
                                          key_name=keyfilename,
                                          # min_count = 1,
                                          # max_count = 3
                                          )

        time.sleep(60)

        self.reservation = ec2.get_all_reservations(filters={'instance-state-name': 'running'})
        for x in self.reservation:  #type(x) == 'class'; type self.i == 'unicode'
            self.i = x.instances[0].id
            self.ip_address = x.instances[0].ip_address
        if True:
            # print "Instance ID %s is up and running, type %s" % (self.i, type(self.i))
            print "Instance ID: %s is up and running, IP:  %s" % (self.i, self.ip_address)
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
        ec2.stop_instances(self.i)
        print "Stopping instance: %s" % self.i

    def terminate(self):
        ec2.terminate_instances(self.i)
        print "Terminating instances: %s" % self.i


    def installServer(self, sshkeyfilename, keylocation):
        global ip
        ip = self.ip_address
        sshuser = 'ec2-user' #http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html
        # when you connect to linux ec2 instance, whoami returns 'ec2-user'
        os.chdir(keylocation)
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=sshuser, key_filename=sshkeyfilename)

        stdin, stdout, stderr = ssh.exec_command("sudo yum install tomcat6 tomcat6-webapps")
        stdin.flush()
        data = stdout.read().splitlines()
        for line in data:
            print line
        # print data[-1]

        stdin, stdout, stderr = ssh.exec_command("sudo service tomcat6 start")
        stdin.flush()
        data = stdout.read().splitlines()
        # print data[-1]
        for line in data:
            print line

        stdin, stdout, stderr = ssh.exec_command("sudo service tomcat6 status")
        stdin.flush()
        data = stdout.read().splitlines()
        # print data[-1]
        for line in data:
            print line
        ssh.close()

    def bashcmd(self, cmd):
        process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
        out, err = process.communicate()
        return out

def s_function(): # managing EC@ instances: start, check status, stop, terminate.
    s = instance()
    s.stop()
    s.statusChangeCheck('stopped')
    s.terminate()
    s.statusChangeCheck('terminated')

def startEC2_install2(sshkeyfilename,keylocation):
    s = instance()
    s.statusChangeCheck('running')
    time.sleep(60)
    s.installServer(sshkeyfilename, keylocation)
    print 'Attempting to confirm Tomcat is installed on: ', ip
    cmd = r"wget -t 1 --timeout=1 -q -O /dev/stdout hXp://"+ str(ip) +":8080 | head -n 2| grep -o 'Apache'"
    response = s.bashcmd(cmd)
    if response != 'Apache':
        print 'Trying again with longer timeout'
        cmd = r"wget -t 1 --timeout=3 -q -O /dev/stdout hXp://" + str(ip) + ":8080 | head -n 2| grep -o 'Apache'"
        response = s.bashcmd(cmd)
        print response
        if response == 'Apache':
            print "Apache installed!"
        else:
            print 'Apache installation is not confirmed, debugging needed'

    # s.stop()
    # s.statusChangeCheck('stopped')
    # s.terminate()
    # s.statusChangeCheck('terminated')



def q_function(q): # multiprocessing function, q = Queue() defined in main()
    p = multiprocessing.current_process()
    print '\nStarting: ', p.name, p.pid
    sys.stdout.flush()
    #q.put(subprocess.call((''.join([r'RAW BASH SHELL COMMAND WITH ARGS AND OPTIONS'])), stderr=subprocess.STDOUT, shell=True))
    # q.put(s_function())  #actual function to be run in parallel, in queue
    q.put(startEC2_install2(sshkeyfilename,keylocation))

    print '\nFinished: ', p.name, p.pid




if __name__ == '__main__':
    main()



#****************************************************************************************
    #INSTRUCTION
#
# Using the notes and example code from section 08_ParamikoBash do the following:
#
# a) programmatically create 3 EC2 instances using the Amazon Linux AMI (free tier) in us-west-1
#
# b) on each EC2 instance programmatically install and run Tomcat
#
# c) programmatically confirm that Tomcat is running on each instance
#
# d) programmatically terminate each EC2 instance
#
# Next:.
#
# 1) in a text editor create a simple "hello world" web page - named MyPage.html
#
# .2) look up how to install a web-site/app into Tomcat. Call this MyWebApp
#
# .3) between steps 'c' and 'd' above,
#
# programmatically create and install MyWebApp, with MyPage.html as the default and only page in MyWebApp, on Tomcat in each EC2 instance
#
# programmatically confirm that http://..../MyWebApp/MyPage.html (Links to an external site.)Links to an external site. is running on each EC2 instance
#
# ------------
#
# To turn in  email to: lpsihw@gmail.com
#
# Subject Line: AWS, #7, Your Name
#
# zip-up and attach code files and screen shots that show the EC2 instances running and confirms that Tomcat is running on each instancezip-up and attach code files and screen shots that show the EC2 instances running and confirms that Tomcat is running on each instance, and confirms your web-site page is running
#
# NOTE: you can complete the assignment without extra credit first and send it in first. If you have time, add the extra credit portions and send that in afterwards. You do NOT need to notify me you are doing this. When I see an email with 7, followed by an email with 7EC - I will just look at the 7EC email.
#
# Points: 3 points without extra credit, 5 points with Extra Credit

                # print 'instance: %s is running', reservations.instances[0].id
# ec2.terminate_instances(instance_ids=[reservations.instances[0].id])

#===================================== boto API trials from  http://boto.cloudhackers.com/en/latest/ec2_tut.html ====================================
#import boto.ec2


#conn = boto.ec2.connect_to_region("us-west-1",
                                  #aws_access_key_id='',
                                 # aws_secret_access_key='')

# reservations = ec2.get_all_reservations(
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
