import os
import sys
import threading
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.types import ConversationConfig

load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("API_KEY")

user_name = "Frank"
schedule = "Coffee Chat at 12:00 PM; Assignment A8 due at 11:59 PM"
prompt = f"You are a helpful assistant. Your interlocutor has the following schedule: {schedule}."
first_message = f"Hello {user_name}, what can I help with today?"

conversation_override = {
    "agent": {
        "prompt": {"prompt": prompt},
        "first_message": first_message,
    },
}

config = ConversationConfig(
    conversation_config_override=conversation_override,
    extra_body={},
    dynamic_variables={},
    user_id="fx58",
)

client = ElevenLabs(api_key=API_KEY)

stop_event = threading.Event()

def print_agent_response(response):
    print(f"Agent: {response}")
    if "goodbye" in response.lower() or "see you" in response.lower():
        stop_event.set()
        conversation.end_session()
        sys.exit(0)

def print_interrupted_response(original, corrected):
    print(f"Agent interrupted, truncated response: {corrected}")

def print_user_transcript(transcript):
    print(f"User: {transcript}")
    if transcript.strip().lower() in ["quit", "exit", "goodbye", "bye", "stop"]:
        print("Assistant shutting down after goodbye...")
        conversation.send_text("Goodbye!")
        stop_event.set()
        conversation.end_session()
        sys.exit(0)

conversation = Conversation(
    client,
    AGENT_ID,
    config=config,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=print_agent_response,
    callback_agent_response_correction=print_interrupted_response,
    callback_user_transcript=print_user_transcript,
)

try:
    conversation.start_session()
except KeyboardInterrupt:
    print("\nManual interrupt detected. Closing session...")
    conversation.end_session()
    sys.exit(0)
