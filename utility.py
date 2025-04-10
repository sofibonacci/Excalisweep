###########use in all wizards##########

def print_list_enumerate(response, title="", indent=0):
    if not response:
        print(f"\nNo {title} found.")
        return

    prefix = "  " * indent

    if indent == 0 and title:
        print(f"\n{title}:")

    if isinstance(response, list):
        for i, item in enumerate(response, start=1):
            print(f"{prefix}{i}. ", end="")
            if isinstance(item, (dict, list)):
                print_list_enumerate(item, "", indent + 1)
            else:
                print(item)

    elif isinstance(response, dict):
        for key, value in response.items():
            print(f"{prefix}- {key}")
            if isinstance(value, (list, dict)):
                print_list_enumerate(value, "", indent + 1)
            else:
                print(f"{prefix}   - {value}")


def print_columns(items, title="", col_width=25):
    if title:
        print(f"\n{title}:\n")

    terminal_width = shutil.get_terminal_size(fallback=(80, 20)).columns
    num_cols = max(1, terminal_width // col_width)

    for i, item in enumerate(items):
        print(f"{item:<{col_width}}", end="")
        if (i + 1) % num_cols == 0:
            print()
    print("\n")
    
def select_from_list(item_list, prompt_message, allow_all=True): # function to select one or multiple items from a list
    """
    allow_all:
        * `False` -> Select only one item.
        * `True`  -> Allows selecting all, multiple, or a single item.
        
    """
    print(f"\n{prompt_message}")
    choice = input("\nYour choice: ").strip().lower()
    
    if allow_all and choice == "all":
        return item_list 
    
    try:
        indexes = [int(i.strip()) - 1 for i in choice.split(",")]
        selected_items = [item_list[i] for i in indexes if 0 <= i < len(item_list)]

        if not allow_all and len(selected_items) > 1:
            print("\nYou can only select one item.")
            return []

        return selected_items

    except ValueError:
        print("\n❌ Invalid input. Please enter valid numbers separated by commas.")
        return []