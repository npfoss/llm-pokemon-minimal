from pyboy import PyBoy
from PIL import Image
from time import sleep

# *** choose which LLM you want to test ***
from human import get_llm_response # this is you
# from claude import get_llm_response
# from gemini import get_llm_response

max_steps = 20
num_screenshots = 30


# lightweight wrapper around the emulator
class PBWrapper:
    def __init__(self):
        self.pyboy = PyBoy(
            "pokemon.gb",
            cgb=True,
            sound_emulated=False,
        )

    # advance the emulator by the specified number of frames.
    def tick(self, frames):
        for _ in range(frames):
            self.pyboy.tick()

    # initialize the emulator and skip through the startup sequence
    def initialize(self):
        self.pyboy.set_emulation_speed(0)
        for _ in range(9):
            self.tick(1000)
        for _ in range(18):
            self.press_buttons(['a'])
            self.tick(10)
        self.press_buttons(['down'])
        self.tick(10)
        for _ in range(7):
            self.press_buttons(['a'])
            self.tick(10)
        self.press_buttons(['down'])
        self.tick(10)
        for _ in range(9):
            self.press_buttons(['a'])
            self.tick(10)
        self.pyboy.set_emulation_speed(1)

    # send input to the emulator
    def press_buttons(self, buttons):
        if any([b not in ["a", "b", "start", "select", "up", "down", "left", "right"] for b in buttons]):
            raise ValueError(f"Invalid button(s) provided: {buttons}")

        for button in buttons:
            self.pyboy.button_press(button)
            self.tick(10)   # Press briefly
            self.pyboy.button_release(button)
            self.tick(10)

        # give some time for the moves to propagate
        self.tick(120)

    def get_screenshot(self):
        return Image.fromarray(self.pyboy.screen.ndarray)

def clean_action_string(stng):
    return [s.strip(' "\'[]') for s in stng.split(',')]

def main():
    game = PBWrapper()
    game.initialize()

    # start the agent's action history with a few actions and screenshots just to show it what's possible (seems to help a little)
    log = [
        '["left"]',
        '["right"]',
        '["down", "up"]',
        '["right", "up", "up"]', # uncomment if you want to give a hint (bring in vision range of the real stairs). ...doesn't seem to help though
    ]
    screenshots = []
    for a in log:
        screenshots.append(game.get_screenshot())
        game.press_buttons(clean_action_string(a))

    steps = 0 # number of LLM calls
    while steps < max_steps:

        screenshots.append(game.get_screenshot())
        if len(screenshots) > num_screenshots:
            screenshots.pop(0)

        system_prompt="""<gameplay_instructions>
This is a log of screenshots and button pressess in a strong playthrough of an unreleased Pokemon game.
The player alternates between exploring and progressing through the game.
Sometimes the player gets stuck or makes mistakes, but they always realize this and correct it.
The player never attempts the same action again if it doesn't do anything on the previous try.
All of the player's moves are based entirely on the screenshots shown.

Valid actions are gameboy buttons "a", "b", "start", "select", "up", "down", "left", or "right", or any sequence thereof.
Multiple actions in one line are preferred when possible, for speed (up to 5 at most).
</gameplay_instructions>
"""
        # generate current prompt from log
        def get_prompt():
            return '<info>Once the log begins, nothing else will be printed besides the sequence of actions taken.</info>\n\n<action_log>\n' + "\n".join(log)

        print('[system] starting next loop. prompts:')
        print(system_prompt)
        print(get_prompt())
        try:
            steps += 1
            action_prefill = '["'
            action_response = get_llm_response(
                system_prompt=system_prompt,
                screenshots=screenshots,
                prompt=get_prompt(),
                prefill=action_prefill
            )
            move = clean_action_string(action_response)
            print('[system] making moves:', move)
            game.press_buttons(move)
            log.append(str(move).replace("'", '"'))
        except Exception as e:
            print(f"An error occurred: {e}")
            sleep(5)


if __name__ == "__main__":
    main()
