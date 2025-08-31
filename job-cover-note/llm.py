import ollama

class OllamaLLM:
    def __init__(self, model: str = "llama3.1:latest", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": self.temperature}
        )
        # Ollama returns a dict with 'message' containing {'role', 'content'}
        return response["message"]["content"]
