#!/bin/bash

# AI Therapy Platform - IAM Setup Script
# Creates IAM roles and policies for Lambda functions

set -e

REGION="us-west-2"
ROLE_NAME="ai-therapy-lambda-execution-role"
POLICY_NAME="ai-therapy-lambda-execution-policy"

echo "Setting up IAM roles for AI Therapy Platform..."

# Create Lambda execution role
echo "Creating Lambda execution role: $ROLE_NAME"
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://backend/iam/lambda-execution-role.json \
    --region $REGION || echo "Role may already exist"

# Create and attach custom policy
echo "Creating custom policy: $POLICY_NAME"
POLICY_ARN=$(aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://backend/iam/lambda-execution-policy.json \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || \
    aws iam list-policies \
    --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" \
    --output text)

echo "Policy ARN: $POLICY_ARN"

# Attach custom policy to role
echo "Attaching custom policy to role"
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn $POLICY_ARN

# Attach AWS managed policy for basic Lambda execution
echo "Attaching AWS managed Lambda basic execution policy"
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "IAM setup completed successfully!"
echo "Role ARN: arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$ROLE_NAME"