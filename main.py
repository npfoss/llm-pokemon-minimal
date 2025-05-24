from pyboy import PyBoy

max_steps = 5


class PBWrapper:
    def __init__(self):
        self.pyboy = PyBoy(
            "pokemon.gb",
            cgb=True,
            sound_emulated=False,
        )

    def tick(self, frames):
        """Advance the emulator by the specified number of frames."""
        for _ in range(frames):
            self.pyboy.tick()

    def initialize(self):
        """Initialize the emulator."""
        # Run the emulator for a short time to make sure it's ready
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

    def press_buttons(self, buttons):
        if any([b not in ["a", "b", "start", "select", "up", "down", "left", "right"] for b in buttons]):
            raise ValueError(f"Invalid button(s) provided: {buttons}")

        for button in buttons:
            self.pyboy.button_press(button)
            self.tick(10)   # Press briefly
            self.pyboy.button_release(button)
            self.tick(120) # Wait longer after button release
        

def main():
    game = PBWrapper()
    game.initialize()

    steps = 0
    while steps < max_steps:
        steps += 1
        try:
            print("next move?", end=' ')
            move = input()
            game.press_buttons([move])
        except Exception as e:
            print(f"An error occurred: {e}")



if __name__ == "__main__":
    main()
