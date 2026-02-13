import os
from agent import AppointmentAgent
from dotenv import load_dotenv

def main():
    """Main terminal loop for the appointment scheduling agent."""
    
    # Get API keys from environment variables
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")  # Optional
    
    if not openai_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize agent
    agent = AppointmentAgent(openai_key, google_maps_key)
    
    # Print intro message
    print("\n" + "="*60)
    print("🏥 Welcome to the AI Appointment Scheduling Assistant!")
    print("="*60)
    print("\nType 'quit' or 'exit' at any time to end the conversation.")
    print("\nI'm here to help you schedule a medical appointment.")
    print("How can I help?")
    print("-"*60 + "\n")
    
    # Main conversation loop
    while not agent.get_state().is_complete:
        try:
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Your appointment was not completed.")
                print("Feel free to come back anytime to schedule.\n")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Process input and get response
            response = agent.process_input(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your appointment was not completed.")
            print("Feel free to come back anytime to schedule.\n")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or type 'quit' to exit.\n")
    
    # Print completion message if appointment was successfully scheduled
    if agent.get_state().is_complete:
        print("\n" + "="*60)
        print("✅ APPOINTMENT SUCCESSFULLY SCHEDULED!")
        print("="*60)
        print("\nThank you for using our scheduling system.")
        print("\n👋 Have a great day!\n")


if __name__ == "__main__":
    main()