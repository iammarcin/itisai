#!/bin/bash

# Set the region
REGION="eu-south-2"

# List all EC2 instances in the region and capture the instance ID
INSTANCE_ID=$(aws ec2 describe-instances --region $REGION --query "Reservations[*].Instances[*].InstanceId" --output text)

# Check if INSTANCE_ID is not empty
if [ -z "$INSTANCE_ID" ]; then
  echo "No instances found in region $REGION."
else
  echo "Instance ID: $INSTANCE_ID"

  # Restart the EC2 instance
  aws ec2 reboot-instances --region $REGION --instance-ids $INSTANCE_ID

  echo "Instance $INSTANCE_ID has been restarted."
fi
