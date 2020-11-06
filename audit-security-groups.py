import boto3

client = boto3.client('rds')
ec2 = boto3.resource('ec2')


### Security Groups
security_groups = list(ec2.security_groups.all())
all_sgs = set([security_group.group_id for security_group in security_groups])

print("Total SGs:", len(all_sgs))

### EC2
instances = list(ec2.instances.all())
all_inst_sgs = set([sg['GroupName'] for inst in instances for sg in inst.security_groups])

print("SGS attached to EC2 instances:", len(all_inst_sgs))


### RDS
rds_instances = client.describe_db_instances()
rds_inst_sg_ids = set([sg['VpcSecurityGroupId'] for inst in rds_instances['DBInstances'] for sg in inst['VpcSecurityGroups']])

print("SGS attached to RDS instances:", rds_inst_sg_ids)

### Unused 
unused_sgs = all_sgs - all_inst_sgs.union(rds_inst_sg_ids)
print("Total Unattached SGs:", len(unused_sgs))
print('Unattached SGs:', unused_sgs)
