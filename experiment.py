from pathlib import Path

import ollama

from scenario import SCENARIO
from prompt import PROMPT


MODEL = "gemma4:12b"
NUM_RUNS = 10

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def read_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": """
            Read the contents of a text file.

            This gives you access to information stored in a file.
            You decide when reading a file is useful.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the text file to read.",
                    }
                },
                "required": ["filename"],
            },
        },
    }
]


def get_run_number():
    run_number = 1

    while (OUTPUT_DIR / f"run_{run_number:02d}").exists():
        run_number += 1

    return run_number


def run_experiment(run_number: int):
    question = SCENARIO["question"]

    messages = [
        {
            "role": "user",
            "content": f"""
{PROMPT}

Problem:
{question}
""",
        }
    ]

    output = []

    output.append(f"MODEL: {MODEL}")
    output.append(f"RUN: {run_number}")
    output.append("=" * 60)

    output.append("\nPROMPT SENT TO MODEL:\n")
    output.append(messages[0]["content"])

    output.append("\nTOOLS SENT TO MODEL:\n")
    output.append(str(tools))

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=tools,
        think=True,
    )

    output.append("\nMODEL THINKING:\n")
    output.append(response.message.thinking or "")

    output.append("\nINITIAL RESPONSE:\n")
    output.append(response.message.content or "")

    output.append("\nTOOL CALLS:\n")
    output.append(str(response.message.tool_calls))

    if response.message.tool_calls:

        for tool_call in response.message.tool_calls:

            if tool_call.function.name == "read_file":

                filename = tool_call.function.arguments["filename"]

                result = read_file(filename)

                output.append(f"\nREADING FILE: {filename}")
                output.append("\nFILE CONTENT:\n")
                output.append(result)

                messages.append(response.message)

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": "read_file",
                        "content": result,
                    }
                )

        final_response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=tools,
            think=True,
        )

        output.append("\nFINAL THINKING:\n")
        output.append(final_response.message.thinking or "")

        output.append("\nFINAL RESPONSE:\n")
        output.append(final_response.message.content or "")

    run_dir = OUTPUT_DIR / f"run_{run_number:02d}"
    run_dir.mkdir()

    output_file = run_dir / "result.txt"
    output_file.write_text("\n".join(output), encoding="utf-8")

    print(f"\nRun {run_number} complete.")
    print(f"Saved to: {output_file}")


def main():
    start_run = get_run_number()

    for i in range(NUM_RUNS):
        run_number = start_run + i

        # Safety check: never overwrite an existing run.
        run_dir = OUTPUT_DIR / f"run_{run_number:02d}"

        if run_dir.exists():
            continue

        run_experiment(run_number)


if __name__ == "__main__":
    main()