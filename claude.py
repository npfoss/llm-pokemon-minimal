import io
import base64

import anthropic

from keys import ANTHROPIC_API_KEY


client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_llm_response(system_prompt, screenshots, prompt, prefill):
    # Convert images to base64
    base64_screenshots = []
    for screenshot in screenshots:
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        base64_screenshots.append(base64.standard_b64encode(buffered.getvalue()).decode())

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        temperature=0.0,
        max_tokens=10,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    *[{
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img
                        }
                    } for img in base64_screenshots],
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            },
            {"role": "assistant", "content": prefill},
        ]
    )
    print(message.content)
    if len(message.content) > 1:
        raise Exception("haven't implementated a way to handle multiple contents returned yet! oh no")
    return message.content[0].text
