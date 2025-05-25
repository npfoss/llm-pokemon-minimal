import io
import base64

from google import genai
from google.genai import types

from keys import GEMINI_API_KEY


client = genai.Client(api_key=GEMINI_API_KEY)

def get_llm_response(system_prompt, screenshots, prompt, prefill):
    # Convert images to base64
    base64_screenshots = []
    for screenshot in screenshots:
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        base64_screenshots.append(base64.standard_b64encode(buffered.getvalue()).decode())

    message = client.models.generate_content(
        # model='gemini-2.5-flash-preview-05-20',
        model='gemini-2.5-pro-preview-05-06',
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,
            max_output_tokens=2100, # tricky because it spends tokens thinking and then runs out before outputting
            # config=types.GenerateContentConfig(
            #     thinking_config=types.ThinkingConfig(thinking_budget=512)
            # ), # this is supposed to work and doesn't for some reason, idk https://ai.google.dev/gemini-api/docs/thinking#set-budget
            stop_sequences=["\n\nN", "\nA", "\nN", "\n#", "."],
        ),
        contents=[
            types.Part.from_bytes(
                data=img,
                mime_type='image/jpeg',
            ) for img in base64_screenshots
        ] + [{"text": prompt + '\n' + prefill}],
    )
    output = message.text[len(prefill):] if message.text.startswith(prefill) else message.text
    print('[system] model output:', output)
    return output



