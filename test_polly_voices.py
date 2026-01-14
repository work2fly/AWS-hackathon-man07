#!/usr/bin/env python3
"""Test Polly voices"""
import boto3

polly = boto3.client('polly', region_name='us-west-2')

# Test both voices
for voice in ['Joanna', 'Matthew']:
    try:
        print(f"\nTesting {voice}...")
        response = polly.synthesize_speech(
            Text='Hello, this is a test.',
            OutputFormat='mp3',
            VoiceId=voice,
            Engine='neural',
            LanguageCode='en-US'
        )
        print(f"✅ {voice} works with Neural engine!")
    except Exception as e:
        print(f"❌ {voice} failed: {e}")
        # Try standard engine
        try:
            response = polly.synthesize_speech(
                Text='Hello, this is a test.',
                OutputFormat='mp3',
                VoiceId=voice,
                Engine='standard',
                LanguageCode='en-US'
            )
            print(f"✅ {voice} works with Standard engine!")
        except Exception as e2:
            print(f"❌ {voice} failed with standard too: {e2}")
