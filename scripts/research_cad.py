import argparse
import os
import re
import sys

from openai import OpenAI

SYSTEM_PROMPT = """You are a CAD engineer AI. Your task is to generate Python code using the `cadquery` library based on the user's prompt. 
You must output ONLY valid Python code inside a markdown code block (```python ... ```).
The code should:
1. Import cadquery as cq.
2. Create the geometry according to the user's instructions.
3. Save the resulting shape to a file named 'generated_cad.stl' using cq.exporters.export().

Example:
```python
import cadquery as cq

# Create a simple box
result = cq.Workplane("front").box(5, 5, 5)

# Export to STL
cq.exporters.export(result, "generated_cad.stl")
```
"""

def generate_cad_code(prompt: str) -> str:
    # Initialize OpenAI client
    # It assumes OPENAI_API_KEY is set in the environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set. Using mock LLM response for demonstration.")
        return """```python
import cadquery as cq
result = cq.Workplane("front").box(10, 10, 10)
cq.exporters.export(result, 'generated_cad.stl')
```"""
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        sys.exit(1)

    print(f"Sending prompt to LLM: '{prompt}'...")
    response = client.chat.completions.create(
        model="gpt-4o",  # or whichever default model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content
    return content

def extract_and_run_code(llm_response: str):
    # Extract python code
    match = re.search(r'```python\n(.*?)\n```', llm_response, re.DOTALL)
    if not match:
        print("No Python code block found in LLM response:")
        print(llm_response)
        sys.exit(1)
    
    code = match.group(1)
    print("--- Generated Code ---")
    print(code)
    print("----------------------")
    
    print("Executing code...")
    try:
        # Execute the code in a new namespace
        exec(code, {})
        print("Execution complete. Check for generated_cad.stl")
    except Exception as e:
        print(f"Error executing generated CAD code: {e}")

def main():
    parser = argparse.ArgumentParser(description="Research CAD Generation using LLM and CadQuery")
    parser.add_argument("--prompt", type=str, default="A simple cube of side 10", help="Prompt for CAD generation")
    args = parser.parse_args()

    llm_output = generate_cad_code(args.prompt)
    extract_and_run_code(llm_output)

if __name__ == "__main__":
    main()
