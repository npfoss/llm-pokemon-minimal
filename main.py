from pyboy import PyBoy
from PIL import Image
from time import sleep

# *** choose which LLM you want to test ***
from human import get_llm_response # this is you
# from claude import get_llm_response
# from gemini import get_llm_response

max_steps = 30
num_screenshots = 8


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

def main():
    game = PBWrapper()
    game.initialize()

    screenshots = []

    log = [
        'Note: start screen',
        'Action(s): ["start"]',
        'Note: welcome dialogue',
        'Action(s): ["a"]',
        'Note: more welcome dialogue',
        'Action(s): ["a", "a"]',
        'Note: explaining pokemon background info I already know',
        'Action(s): ["a", "a", "a", "a"]',
        'Note: more background',
        'Action(s): ["a", "a", "a", "a"]',
        'Note: name choice screen',
        'Action(s): ["down", "a"]',
        'Note: my name is now "RED"',
        'Action(s): ["a"]',
        'Note: partial dialogue',
        'Action(s): ["a"]',
        'Note: I have a rival',
        'Action(s): ["a"]',
        'Note: partial dialogue',
        'Action(s): ["a"]',
        'Note: choosing the name of my rival',
        'Action(s): ["down", "a"]',
        'Note: my rival is named "BLUE"',
        'Action(s): ["a"]',
        'Note: partial dialogue',
        'Action(s): ["a"]',
        'Note: says I should explore the town',
        'Action(s): ["a"]',
        'Note: game is about to start',
        'Action(s): ["a"]',
    ]

    steps = 0 # number of LLM calls
    while steps < max_steps:

        screenshots.append(game.get_screenshot())
        if len(screenshots) > num_screenshots:
            screenshots.pop(0)

        system_prompt="""This is the transcript and notes of a Pokemon Blue expert playing through Pokemon Red for the first time, including their last several game screens.
They are very unfamiliar with the details of the game at first, but doing their best to progress through it efficiently despite occasional mistakes and inaccurate notes in the past.
Sometimes they don't know what to do next, and simply wander around to understand the world better for a little while.

Their text notes always follow the following format:
Note: [brief note on their immediate scene any anything relevant or noteworthy that happened. Never more than ~25 words at most, usually shorter.]
Action(s) taken: [list of actions they took immediately after recording the note above]

These notes are based purely on the screenshots included with the log, and pertain exactly and solely to what they can see at the time of the note, nothing else. They never write what they expect the state to be or wish it was, only what they currently see on the screen, if it's noteworthy, or nothing at all.
Sometimes past notes are inaccurate, and they may correct themselves in future notes, or just keep going.
Their notes often express uncertainty, like "don't know how to get to the destination" or "what is this thing?", as they never assume they know what's going on until they see it in a screenshot.
When the screenshots conflict with the logs, they ignore the logs and listen to the screenshots only.

Valid actions are gameboy buttons "a", "b", "start", "select", "up", "down", "left", or "right", or any sequence thereof."""
        # generate current prompt from log
        def get_prompt():
            return '#### BEGIN PLAYTHROUGH LOG ####\n' + "\n".join(log)

        print('[system] starting next loop. prompts:')
        print(system_prompt)
        print(get_prompt())
        try:
            steps += 1
            note_prefill = 'Note:'
            note_response = get_llm_response(
                system_prompt=system_prompt,
                screenshots=screenshots,
                prompt=get_prompt(),
                prefill=note_prefill
            )
            if(len(note_response) > 280):
                raise Exception('note too long', note_response)
            if(note_response.startswith("####")):
                raise Exception('gemini tried to end the log again', note_response)
            log.append(note_prefill + note_response)

            # retry actions in case of failure
            while steps < max_steps:
                try:
                    steps += 1
                    action_prefill = 'Action(s): ["'
                    action_response = get_llm_response(
                        system_prompt=system_prompt,
                        screenshots=screenshots,
                        prompt=get_prompt(),
                        prefill=action_prefill
                    )
                    move = [s.strip(' "\'') for s in action_response[:-1].split(',')]
                    print('[system] making moves:', move)
                    game.press_buttons(move)
                    log.append(action_prefill + action_response)
                    break
                except Exception as e:
                    print(f"An error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
            sleep(5)


if __name__ == "__main__":
    main()
