#!/usr/bin/env python3
"""
MVP test suite for AI Scrum Master.
Tests core standup functionality and integrations.
"""

import asyncio
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEAM_ID = 1

def test_api_health():
    """Test if the API is running."""
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False

def test_ai_health():
    """Test AI services health."""
    try:
        response = requests.post(f"{BASE_URL}/ai/health-check")
        if response.status_code == 200:
            data = response.json()
            print("✅ AI services health check passed")
            print(f"   AI Service: {data.get('ai_service', 'unknown')}")
            print(f"   Vector Service: {data.get('vector_service', 'unknown')}")
            print(f"   OpenAI Configured: {data.get('openai_configured', False)}")
            return True
        else:
            print(f"❌ AI health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI health check error: {e}")
        return False

def test_standup_generation():
    """Test standup summary generation."""
    print("\n🧪 Testing Standup Summary Generation...")
    
    # Sample standup data
    standup_request = {
        "team_id": TEAM_ID,
        "include_jira_updates": True,
        "slack_channel_id": None  # Will use sample data
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/standup/teams/{TEAM_ID}/generate-summary",
            json=standup_request
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Standup summary generated successfully!")
            print(f"\n📋 Summary:")
            print(f"   {data.get('summary', 'No summary')}")
            
            if data.get('key_achievements'):
                print(f"\n🏆 Key Achievements:")
                for achievement in data['key_achievements']:
                    print(f"   • {achievement}")
            
            if data.get('blockers'):
                print(f"\n🚫 Blockers:")
                for blocker in data['blockers']:
                    if isinstance(blocker, dict):
                        print(f"   • {blocker.get('description', 'Unknown blocker')}")
                    else:
                        print(f"   • {blocker}")
            
            if data.get('action_items'):
                print(f"\n📝 Action Items:")
                for item in data['action_items']:
                    if isinstance(item, dict):
                        print(f"   • {item.get('action', 'Unknown action')}")
                    else:
                        print(f"   • {item}")
            
            print(f"\n🎭 Team Sentiment: {data.get('team_sentiment', 'Unknown')}")
            return True
        else:
            print(f"❌ Standup generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Standup generation error: {e}")
        return False

def test_backlog_analysis():
    """Test AI backlog analysis feature."""
    print("\n🧪 Testing Backlog Analysis...")
    
    sample_backlog_item = {
        "title": "User login system",
        "description": "Users need to be able to log in",
        "item_type": "story"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/analyze-backlog",
            json=sample_backlog_item
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backlog analysis completed!")
            print(f"\n📊 Analysis Results:")
            print(f"   Clarity Score: {data.get('clarity_score', 0):.2f}/1.0")
            print(f"   Estimated Complexity: {data.get('estimated_complexity', 'Unknown')}")
            
            if data.get('suggested_improvements'):
                print(f"\n💡 Suggested Improvements:")
                for improvement in data['suggested_improvements']:
                    print(f"   • {improvement}")
            
            if data.get('potential_risks'):
                print(f"\n⚠️ Potential Risks:")
                for risk in data['potential_risks']:
                    print(f"   • {risk}")
            
            return True
        else:
            print(f"❌ Backlog analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backlog analysis error: {e}")
        return False

def test_slack_integration():
    """Test Slack integration."""
    print("\n🧪 Testing Slack Integration...")
    
    try:
        # Test collecting Slack messages (will use sample data in MVP)
        response = requests.post(
            f"{BASE_URL}/standup/slack/collect/{TEAM_ID}",
            params={"channel_id": "C1234567890", "hours_back": 24}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Slack message collection test passed!")
            print(f"   Collected {len(data.get('entries', []))} standup entries")
            return True
        else:
            print(f"❌ Slack integration test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Slack integration error: {e}")
        return False

def test_vector_database():
    """Test vector database functionality."""
    print("\n🧪 Testing Vector Database...")
    
    try:
        response = requests.get(f"{BASE_URL}/ai/vector-stats")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Vector database is operational!")
            print(f"   Total Documents: {data.get('total_documents', 0)}")
            print(f"   Collection: {data.get('collection_name', 'Unknown')}")
            return True
        else:
            print(f"❌ Vector database test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Vector database error: {e}")
        return False

def main():
    """Run all MVP tests."""
    print("🚀 AI Scrum Master MVP Test Suite")
    print("=" * 50)
    
    # Track test results
    tests = [
        ("API Health", test_api_health),
        ("AI Services", test_ai_health),
        ("Vector Database", test_vector_database),
        ("Standup Generation (Core MVP)", test_standup_generation),
        ("Backlog Analysis", test_backlog_analysis),
        ("Slack Integration", test_slack_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📍 Running: {test_name}")
        print("-" * 30)
        
        success = test_func()
        results.append((test_name, success))
        
        if not success and test_name == "API Health":
            print("\n❌ Cannot continue without API. Please start the backend server.")
            break
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your AI Scrum Master MVP is working correctly.")
        print("\nNext steps:")
        print("1. Configure your OpenAI API key in .env")
        print("2. Set up Slack and Jira integrations")
        print("3. Access the API docs at http://localhost:8000/api/v1/docs")
    else:
        print("\n⚠️ Some tests failed. Check the configuration and dependencies.")
        print("\nTroubleshooting:")
        print("1. Ensure all services are running (docker-compose up)")
        print("2. Check your .env configuration")
        print("3. Verify OpenAI API key is valid")

if __name__ == "__main__":
    main()