from app.agents.base_agent import SpecialistAgent


class ArchitectureAgent(SpecialistAgent):
    name = "architecture"
    prompt_file = "architecture_prompt.txt"
    focus = "architectural consistency, module boundaries, performance, and long-term behavior"
