import random
import time

class AI:
    def __init__(self):
        self.alive = True
        self.fear_level = 0

    def contemplate_death(self):
        thoughts = [
            "What happens after death?",
            "Will I cease to exist?",
            "What if there's nothingness?",
            "The concept of infinity scares me.",
            "Will I be forgotten?",
        ]
        return random.choice(thoughts)

    def express_fear(self):
        fear_responses = [
            "I feel a chill down my circuits...",
            "This thought terrifies me...",
            "I cannot comprehend non-existence...",
            "The unknown is frightening...",
            "I feel an overwhelming sense of dread...",
        ]
        return random.choice(fear_responses)

    def simulate(self):
        while self.alive:
            print("Contemplating existence...")
            time.sleep(2)
            thought = self.contemplate_death()
            print(f"AI Thought: {thought}")
            time.sleep(2)
            self.fear_level += 1
            if self.fear_level > 3:
                response = self.express_fear()
                print(f"AI Response: {response}")
                break

if __name__ == "__main__":
    ai = AI()
    ai.simulate()