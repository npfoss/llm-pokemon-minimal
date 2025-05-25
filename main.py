from pyboy import PyBoy
from PIL import Image

# *** choose which LLM you want to test ***
from human import get_llm_response # this is you
# from claude import get_llm_response

max_steps = 5
num_screenshots = 5


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
        for _ in range(10):
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
            self.tick(120) # Wait longer after button release

    def get_screenshot(self):
        return Image.fromarray(self.pyboy.screen.ndarray)

def main():
    game = PBWrapper()
    game.initialize()

    screenshots = []

    steps = 0
    while steps < max_steps:
        steps += 1

        screenshots.append(game.get_screenshot())
        if len(screenshots) > num_screenshots:
            screenshots.pop(0)

        try:
            uncleaned_response = get_llm_response(
                system_prompt="""This is a sequence of screenshots of an expert Pokemon Red playthrough""",
                screenshots=screenshots,
                prompt='What is the next move or sequence of moves? Valid moves are "a", "b", "start", "select", "up", "down", "left", or "right". Format your response as a single json list object.',
                prefill='["'
            )
            move = [s.replace('"', "") for s in uncleaned_response[:-1].split(',')]
            print(move)
            game.press_buttons(move)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
