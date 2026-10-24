from app.agents.base_agent import SpecialistAgent


class SecurityAgent(SpecialistAgent):
    name = "security"
    prompt_file = "security_prompt.txt"
    focus = "secrets, injection, authorization, unsafe data handling, and vulnerable patterns"
