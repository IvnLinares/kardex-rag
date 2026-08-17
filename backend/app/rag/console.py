"""REPL de consola para probar la cadena RAG sin pasar por la API.

Uso (desde /backend, con el venv activado, DB y Ollama corriendo):
    python -m app.rag.console
"""

from app.rag.chain import answer_question

EXIT_COMMANDS = {"salir", "exit", "quit"}


def main() -> None:
    print("Copiloto de Kardex — escribi una pregunta (o 'salir' para terminar)\n")
    while True:
        question = input("> ").strip()
        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            break
        result = answer_question(question)
        print(f"\n{result.text}")
        if result.sources:
            citados = ", ".join(f"{s.nombre} ({s.producto_id})" for s in result.sources)
            print(f"[Fuentes: {citados}]")
        print()


if __name__ == "__main__":
    main()
