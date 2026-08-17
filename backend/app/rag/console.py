"""REPL de consola para probar la cadena RAG sin pasar por la API.

Uso (desde /backend, con el venv activado, DB y Ollama corriendo):
    python -m app.rag.console
"""

from app.rag.chain import build_chain

EXIT_COMMANDS = {"salir", "exit", "quit"}


def main() -> None:
    print("Copiloto de Kardex — escribi una pregunta (o 'salir' para terminar)\n")
    chain = build_chain()
    while True:
        question = input("> ").strip()
        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            break
        answer = chain.invoke(question)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
