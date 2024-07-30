#!/bin/bash

# Variables
AWS_REGION="eu-south-2"
SECURITY_GROUP_ID="sg-073fdb0f830844861"
RULE_DESCRIPTION="automatedMyCurrentLocation"
RULE_ID="sgr-030624572d1f86638"

# Get the current public IP
CURRENT_IP=$(curl -s https://myip.dk/)
CURRENT_IP_CIDR="${CURRENT_IP}/32"

# Get the rule details
RULE=$(aws ec2 describe-security-group-rules --region $AWS_REGION --filters Name=security-group-rule-id,Values=$RULE_ID)
echo $RULE
if [ -z "$RULE" ]; then
  echo "No matching rule found."
  exit 1
fi

# Extract protocol, from port, and to port
IP_PROTOCOL=$(echo $RULE | jq -r '.SecurityGroupRules[0].IpProtocol')
FROM_PORT=$(echo $RULE | jq -r '.SecurityGroupRules[0].FromPort')
TO_PORT=$(echo $RULE | jq -r '.SecurityGroupRules[0].ToPort')

# Update the rule with the new IP
aws ec2 modify-security-group-rules --region $AWS_REGION --group-id $SECURITY_GROUP_ID --security-group-rules "SecurityGroupRuleId=$RULE_ID,SecurityGroupRule={IpProtocol=$IP_PROTOCOL,FromPort=$FROM_PORT,ToPort=$TO_PORT,CidrIpv4=$CURRENT_IP_CIDR,Description=$RULE_DESCRIPTION}"

echo "Updated the rule $RULE_ID with IP $CURRENT_IP_CIDR"
