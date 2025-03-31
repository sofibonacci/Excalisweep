###########use in all wizards##########

def print_list_enumerate(response, title, enumerate_keys=True, indent=0):
    # Check if the response is empty
    if not response:
        print(f"\nNo {title} found.")
        return

    # Prefix for indentation
    prefix = "  " * indent

    # Print the title only once
    if indent == 0:
        print(f"\n{title}:")

    # If the response is a list, process it
    if isinstance(response, list):
        _print_list(response, enumerate_keys, prefix, indent)

    # If the response is a dictionary, process its keys and values
    elif isinstance(response, dict):
        _print_dict(response, enumerate_keys, prefix, indent)


def _print_list(response, enumerate_keys, prefix, indent):
    """Handles printing when the response is a list, without recursion."""
    for i, item in enumerate(response, start=1):
        if enumerate_keys:
            print(f"{prefix}{i}. ", end="")
        else:
            print(prefix, end="")

        # If the item is a list or dictionary, print it as a string without recursion
        if isinstance(item, (dict, list)):
            print(str(item))
        else:
            print(item)


def _print_dict(response, enumerate_keys, prefix, indent):
    """Handles printing when the response is a dictionary, without recursion."""
    for i, (key, value) in enumerate(response.items(), start=1):
        # If enumeration is enabled, print the index and the key
        if enumerate_keys:
            print(f"{prefix}{i}. {key}")
        else:
            print(f"{prefix}- {key}")

        # If the value is a list or dictionary, print it in a single line
        if isinstance(value, (list, dict)):
            print(f"{prefix}   - {str(value)}")
        else:
            print(f"{prefix}   - {value}")


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