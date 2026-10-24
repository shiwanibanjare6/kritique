from app.agents.base_agent import SpecialistAgent


class StyleAgent(SpecialistAgent):
    name = "style"
    prompt_file = "style_prompt.txt"
    focus = "readability, maintainability, naming, error handling, and accidental debug or placeholder code"
