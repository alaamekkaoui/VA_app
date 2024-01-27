import google.generativeai as genai
import textwrap


def configure_api(api_key):
    genai.configure(api_key=api_key)

def initialize_genai(api_key):
    configure_api(api_key)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)

def summarize_email_content(model, email_text,bard_prompt):
    try:
        bard_prompt = "Summarize the following email in 30 words:\n\n"
        # Combine the email text and Bard prompt
        input_text = f"{email_text}\n\n{bard_prompt}"

        # Generate a summary using the combined text
        summary = model.generate_content(input_text).text
        return summary
    except Exception as e:
        print(f"Error generating content: {e}")
        return "Error summarizing email"

def generate_confirmation_response(sender_name, meeting_date):
    response = f"Dear {sender_name},\n\nThank you for the meeting details. I have noted the following:\n- Meeting Date: {meeting_date}\n\nLooking forward to our collaboration.\n\nBest regards."
    return response

def to_markdown(text):
    bullet_character = '•'
    replacement = '  *'
    indentation = ' | '

    formatted_text = text.replace(bullet_character, replacement)
    indented_text = textwrap.indent(formatted_text, indentation, predicate=lambda _: True)

    return indented_text

def process_email(user_input, model,bard_prompt):
    summary = summarize_email_content(model, user_input , bard_prompt)
    return summary

def generate_email_response(sender_name, meeting_date):
    confirmation_response = generate_confirmation_response(sender_name, meeting_date)
    print("Response: Working.")
    print("Confirmation Response:\n", to_markdown(confirmation_response))

def generate_short_description(prompt):
    api_key = 'AIzaSyCbPhOCx7wcrm_Y_z6FtR5lMKYhKkPSOsk'
    try:
        model = initialize_genai(api_key)
        bard_prompt = f"{prompt}\n\n"
        
        # Generate a short description using the prompt
        short_description = model.generate_content(bard_prompt).text
        print("Short Description: ", short_description)
        return short_description
    except Exception as e:
        print(f"Error generating short description: {e}")
        return "Error generating short description"

print("|---------Starting Bard api script--------|")
