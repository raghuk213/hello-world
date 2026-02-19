import sys

def count_characters(name):
    name = name.strip()
    if not name:
        return "Please enter a name!"
    count = len(name)
    no_space = len(name.replace(" ", ""))
    if " " in name:
        return f'"{name}" has {count} characters (with spaces), or {no_space} without spaces.'
    return f'"{name}" has {count} character{"s" if count != 1 else ""}.'

def get_bot_response(user_text):
    text  = user_text.strip()
    lower = text.lower()
    if lower in ("hi", "hello", "hey", "hii"):
        return "Hello! I am CharBot. Type any name and I will count its characters!"
    if lower in ("bye", "goodbye", "exit", "quit"):
        return "Goodbye! Have a great day!"
    if lower in ("help", "?"):
        return "Just type any name!\nExample: Raghu\nOr type: my name is Raghu"
    for phrase in ("how many characters in ", "count ", "characters in "):
        if lower.startswith(phrase):
            return count_characters(text[len(phrase):])
    if lower.startswith("my name is "):
        return "Nice to meet you! " + count_characters(text[len("my name is "):])
    return count_characters(text)

def main():
    print("=" * 45)
    print("        Welcome to CharBot!")
    print("  Type a name to count its characters.")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 45)
    print()
    print("CharBot: Hi! I am CharBot.")
    print("         Type any name and I will count its characters!")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCharBot: Goodbye! Have a great day!")
            break

        if not user_input:
            continue

        response = get_bot_response(user_input)
        print(f"\nCharBot: {response}\n")

        if user_input.lower() in ("bye", "goodbye", "exit", "quit"):
            break

if __name__ == "__main__":
    main()
