Deployment
------------

[Reference](https://aws.amazon.com/blogs/mt/manage-custom-aws-config-rules-with-remediations-using-conformance-packs/)

[Alternative for single account](https://aws.amazon.com/blogs/security/how-to-automatically-revert-and-receive-notifications-about-changes-to-your-amazon-vpc-security-groups/)

[Alternative using Security Hub](https://aws.amazon.com/solutions/implementations/aws-security-hub-automated-response-and-remediation/)


1. [Enable AWS Config](https://docs.aws.amazon.com/config/latest/developerguide/getting-started.html) in all accounts in your AWS Organization.


1. Deploy the AWS CloudFormation template in the master account. It creates two Lambda functions, one for the AWS Config rule and one for remediation, as well as the appropriate IAM roles for cross-account execution in member accounts.
    * sg_auto_remediation_cf.yaml


1. Deploy the StackSet to create IAM roles in the member accounts that are assumed by the Lambda functions in the master account.
    * sg_auto_remediation_roles_cf_stack_set.yaml


1. Upload an SSM automation document that defines the remediation step for the custom AWS Config rule.

    1. Go to AWS Systems Manager and choose Automation, then Execute Automation, and then Create Automation. Name the remediation document SecurityGroupAutomation.
    2. Change the mode to Editor and choose Edit. Paste the json into the content section.
        * ssm_automation_doc.json


1. Share the SSM document with the member accounts in your AWS Organization.

    1. Go to Systems Manager, then Shared Resources - Documents, then go to the Automation Document you created for remediation.
    2. Choose the Details
    3. In the Permissions section, add the account IDs of all member accounts into which you are deploying the conformance packs, choose Add, and choose Save.

1. Add permissions for AWS Config to invoke Lambda
    * Run the following command to allow the AutomationSecurityGroupConformance function to be invoked by the AutomationRole in the member accounts. Change the Member Account ID to your member account (for multiple member accounts, run this command for each account number):
        ```
        aws lambda add-permission --function-name AutomationSecurityGroupConformance --statement-id "AllowExecutionFromAutomation" --action "lambda:InvokeFunction" --principal "arn:aws:iam::{MemberAccount}:role/AutomationRole"
        ```

1. Set up the prerequisites for conformance packs.
    * [Prerequisites](https://docs.aws.amazon.com/config/latest/developerguide/cpack-prerequisites.html)
    * Make sure to name the Amazon S3 bucket as specified in the Prerequisites for Organization Conformance Packs section.


1. Deploy the conformance pack in your AWS Organization to create rule.
    * Deploy the conformance pack through AWS CLI.
        * Open the conformance pack and change the Account ID to your Master Account ID in the three locations specified in the code, then save the conformance pack.
            * sg_conformance_pack.yaml
        * Copy the following command, and change the location of the template-body to the same location in which you saved the conformance packs template. Change the Amazon S3 bucket to the one you set up in the conformance pack prerequisites. Change the Region and Account ID to the Master Account ID for the Lambda function.
            ```
            aws configservice put-organization-conformance-pack --organization-conformance-pack-name="conformancePack" --template-body=file://sg_conformance_pack.yaml --delivery-s3-bucket={S3-bucket-for-conformance-pack} --conformance-pack-input-parameters=ParameterName=SecurityGroupMaskLambdaArn,ParameterValue="arn:aws:lambda:{region}:{MasterAccountID}:function:ConformancePackSecurityGroup"
            ```

        * Run the command after you make these changes. In all the member accounts in your AWS Organization, you are able to see the rule that you created.

    * Every time your member accounts make a change to a Security Group, the change is evaluated by the AWS Config rule. If it doesn’t comply with the /16 or smaller CIDR block range rule you built, the non-compliant rule is removed.

1. Test
    * Trigger a configuration change to a Security Group in a member account to test your rule. Add a Security Group rule that has a source of 10.0.0.0/12, which doesn’t comply with your rule since it has a larger CIDR block range than /16.

1. Clean Up
    * To remove all resources created as a part of this example, delete the following resources:
        * The AWS CloudFormation Stack in the master account
        * The StackSet in the master account
        * The SSM automation document

    * Run the following command to delete the conformance pack:
        ```
        aws configservice delete-organization-conformance-pack --organization-conformance-pack-name conformancePack
        ```
