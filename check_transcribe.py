#!/usr/bin/env python3
"""
Check if Transcribe is working
"""
import boto3
import json

transcribe = boto3.client('transcribe', region_name='us-west-2')

# List recent transcription jobs
try:
    response = transcribe.list_transcription_jobs(MaxResults=5)
    
    print("Recent Transcription Jobs:")
    print("=" * 60)
    
    if 'TranscriptionJobSummaries' in response:
        for job in response['TranscriptionJobSummaries']:
            print(f"Job: {job['TranscriptionJobName']}")
            print(f"Status: {job['TranscriptionJobStatus']}")
            print(f"Created: {job['CreationTime']}")
            if 'FailureReason' in job:
                print(f"Failure: {job['FailureReason']}")
            print("-" * 60)
    else:
        print("No transcription jobs found")
        
except Exception as e:
    print(f"Error: {e}")
