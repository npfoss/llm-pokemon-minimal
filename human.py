# To confirm we're actually giving them enough info to play properly

import numpy as np
import matplotlib.pyplot as plt

def get_llm_response(system_prompt, screenshots, prompt, prefill="next move?"):
    print(system_prompt)

    # all this is just to render the latest screenshot
    plt.imshow(np.array(screenshots[-1]))
    plt.axis('off')  # Turn off axis numbers and ticks
    plt.gcf().canvas.manager.set_window_title("current screen")
    plt.show(block=False) # Show plot without blocking

    print(prompt)
    print(prefill, end='')
    user_input = input()

    # close screenshot
    plt.close(plt.figure())

    return user_input
