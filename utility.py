import shutil

########### use in all wizards ##########

# -----------------------------------------
# Function: print_list_enumerate --> use them in all 
# -----------------------------------------
# Description: --> use it in all wizards inside listing functions
#   Recursively prints lists or dictionaries in a clean, enumerated format.
#   Useful for structured CLI output, especially for debugging or user wizards.
# Parameters:
#   - response: list or dict to print
#   - title: title of the section
#   - indent: internal use for recursive indentation
# Usage:
#   print_list_enumerate(data, "My Data")
#   data can be a list, dict, or nested structure
# -----------------------------------------

def print_list_enumerate(response, title, indent=0):  
    if not response:
        print(f"\nNo {title} found.")
        return

    prefix = "  " * indent  

    if indent == 0:  
        print(f"\n{title}:\n")

    if isinstance(response, list):
        for i, item in enumerate(response, start=1):
            if indent == 0:  
                print(f"{prefix}{i}. ", end="")
            else:
                print(prefix, end="")

            if isinstance(item, (dict, list)):
                print_list_enumerate(item, title, indent + 1)
            else:
                print(item)

            if indent == 0: 
                print()  # Adds a blank line between top-level items

    elif isinstance(response, dict):
        for i, (key, value) in enumerate(response.items(), start=1):
            if indent == 0:  
                print(f"{prefix}{i}. {key}")
            else:
                print(f"{prefix}- {key}")

            if isinstance(value, (list, dict)):
                print_list_enumerate(value, title, indent + 1)
            else:
                print(f"{prefix}   - {value}")

            if indent == 0: 
                print()  # Adds a blank line between top-level items


# -----------------------------------------
# Function: print_columns
# -----------------------------------------
# Description: --> use in others for printing all aws services
#   Prints a flat list of items in a multi-column format based on terminal width.
#   Useful for compact presentation of options or data.
# Parameters:
#   - items: list of items (str/int/any)
#   - title: optional title printed above the list
# Usage:
#   print_columns(["Option A", "Option B", "Option C"], title="Available Options")
# -----------------------------------------

def print_columns(items, title=""):
    if title:
        print(f"\n{title}:\n")

    if not items:
        print("No items to display.\n")
        return

    max_item_length = max(len(str(item)) for item in items) + 2  # Padding
    terminal_width = shutil.get_terminal_size(fallback=(100, 20)).columns
    num_cols = max(1, terminal_width // max_item_length)

    for i, item in enumerate(items):
        print(f"{str(item):<{max_item_length}}", end="")
        if (i + 1) % num_cols == 0:
            print()
    if len(items) % num_cols != 0:
        print()  # Final line break if last row isn't complete


# -----------------------------------------
# Function: select_from_list
# -----------------------------------------
# Description: --> use it in all wizards inside delete functions
#   Prompts the user to select one or more items from a list by entering indices.
# Parameters:
#   - item_list: list of items to choose from
#   - prompt_message: message displayed to the user
#   - allow_all (bool): 
#       * True  = allow selecting multiple or "all"
#       * False = allow selecting only one item
# Returns:
#   A list of selected items or an empty list on invalid input
# Usage:
#   selected = select_from_list(options, "Select an option:", allow_all=False)
#   selected = select_from_list(options, "Choose items (1,2,3 or 'all'):", allow_all=True)
# -----------------------------------------

def select_from_list(item_list, prompt_message, allow_all=True): 
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
