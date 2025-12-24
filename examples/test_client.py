#!/usr/bin/env python3
"""
Simple example client for testing Linphone Caller API
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"


def main():
    print("Linphone Caller - Test Client")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Checking health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   Linphone Available: {health['linphone_available']}")
        
        if not health['linphone_available']:
            print("\n   ERROR: Linphone is not available!")
            print("   Please ensure linphone-cli is installed.")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Could not connect to API: {e}")
        sys.exit(1)
    
    # 2. Get destination from user
    print("\n2. Enter call details:")
    destination = input("   SIP Destination (e.g., sip:1234567890@sip.example.com): ").strip()
    
    if not destination.startswith("sip:"):
        destination = f"sip:{destination}"
    
    duration_input = input("   Call Duration in seconds (default 120): ").strip()
    duration = int(duration_input) if duration_input else 120
    
    # 3. Start call
    print(f"\n3. Starting call to {destination}...")
    try:
        response = requests.post(f"{BASE_URL}/call/start", json={
            "destination": destination,
            "duration": duration
        })
        response.raise_for_status()
        call = response.json()
        call_id = call['call_id']
        print(f"   Call ID: {call_id}")
        print(f"   Status: {call['status']}")
        
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Could not start call: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        sys.exit(1)
    
    # 4. Wait for call to establish
    print("\n4. Waiting for call to establish...")
    time.sleep(5)
    
    # 5. Check status
    print("\n5. Checking call status...")
    try:
        response = requests.get(f"{BASE_URL}/call/{call_id}/status")
        response.raise_for_status()
        status = response.json()
        print(f"   Status: {status['status']}")
        print(f"   Duration: {status['duration']}s")
        
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Could not get status: {e}")
    
    # 6. Ask about audio injection
    inject = input("\n6. Do you want to inject audio? (y/n): ").strip().lower()
    
    if inject == 'y':
        audio_file = input("   Audio file name (e.g., greeting.wav): ").strip()
        
        print(f"   Injecting audio: {audio_file}...")
        try:
            response = requests.post(
                f"{BASE_URL}/call/{call_id}/inject-audio",
                json={"audio_file_name": audio_file}
            )
            response.raise_for_status()
            result = response.json()
            print(f"   {result['message']}")
            
        except requests.exceptions.RequestException as e:
            print(f"   ERROR: Could not inject audio: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text}")
    
    # 7. Ask about ending call
    print(f"\n7. Call will automatically end after {duration} seconds.")
    end_now = input("   Do you want to end the call now? (y/n): ").strip().lower()
    
    if end_now == 'y':
        print("   Ending call...")
        try:
            response = requests.post(f"{BASE_URL}/call/{call_id}/end")
            response.raise_for_status()
            result = response.json()
            print(f"   {result['message']}")
            print(f"   Final Duration: {result['duration']}s")
            
        except requests.exceptions.RequestException as e:
            print(f"   ERROR: Could not end call: {e}")
    else:
        print("   Call will continue until duration expires.")
    
    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

