import json

def read_file(filepath):
    """Reads the content of a file and returns it."""
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def write_to_json(problems, output_filepath):
    """Writes a list of dictionaries to a JSON file."""
    with open(output_filepath, 'w', encoding='utf-8') as file:
        json.dump(problems, file, indent=4)

def parse_problems(text):
    """Parses the text containing multiple problems and returns a list of problem dictionaries."""
    problems = []
    current_problem = {}
    lines = text.split('\n')
    current_key = None

    for line in lines:
        if line.startswith('User'):
            if current_problem:
                problems.append(current_problem)
            current_problem = {'instruction': '', 'input': '', 'output': ''}
            current_key = 'input'
            current_problem[current_key] = line
        elif line.startswith('Assistant'):
            current_key = 'output'
            current_problem[current_key] = ''
        elif current_key:
            if current_key not in current_problem:
                current_problem[current_key] = ''
            current_problem[current_key] += line + '\n'

    if current_problem:
        problems.append(current_problem)

    return problems

def main():
    # Read the dataset file
    text = read_file("test.txt")
    problems = parse_problems(text)
    
    # Convert and write to JSON
    write_to_json(problems, "data1.json")
    print("Problems parsed and written to data1.json")

if __name__ == "__main__":
    main()
