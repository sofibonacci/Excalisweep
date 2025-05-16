import shutil

########### use in all wizards ##########

# -----------------------------------------
# Function: print_list_enumerate --> use it in all
# -----------------------------------------
# Description: Use it in all wizards inside listing functions.
#   Cleanly prints lists or dictionaries with enumeration.
#   Useful for displaying AWS resources or structured CLI output.
# Parameters:
#   - data: list or dict to print
#   - title: title of the printed section
# Usage:
#   print_list_enumerate(my_data, "EC2 Instances")
#   my_data can be a list, dict, or nested structure.
# -----------------------------------------

def print_list_enumerate(data, title):  
    if not data:
        print(f"\nNo {title} found.")
        return

    print(f"\n🔹 {title}:\n")

    if isinstance(data, dict):
        for i, (key, value) in enumerate(data.items(), start=1):
            print(f"{i}. {key}")
            if isinstance(value, dict):
                for subkey, subval in value.items():
                    print(f"   - {subkey}: {subval}")
            else:
                print(f"   - {value}")
            print()  

    elif isinstance(data, list):
        for i, item in enumerate(data, start=1):
            print(f"{i}. {item}")
        print()


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
    
    if choice == "exit":
        print("\nExiting selection.")
        return []
    
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


# -----------------------------------------
# Function: run_interactive_menu            
# -----------------------------------------
# Description: --> use it in all wizards inside main menu
#   Displays an interactive menu with options and executes the corresponding actions.
# Parameters:
#   - title: title of the menu
#   - options: list of tuples (label, action, exit_flag)
#       * label: displayed name of the option
#       * action: function to execute when selected
#       * exit_flag: boolean indicating if this option exits the menu
# Usage:
#   run_interactive_menu("Main Menu", [
#       ("Option 1", action1, False),
#       ("Option 2", action2, False),
#       ("Exit", exit_action, True)
#   ])                  
# ----------------------------------------- 

def run_interactive_menu(title, options):
    print(f"""
    *****************************************
    *   {title}   *
    *****************************************
    """)

    while True:
        print("\nMain Menu:")
        for idx, (label, _, _) in enumerate(options, 1):
            print(f"{idx}. {label}")
        choice = input("Enter your choice: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            _, action, exit_flag = options[int(choice) - 1]
            if exit_flag:
                print("\n🔚 Exiting. Have a great day!")
                break
            action()
        else:
            print(f"\nInvalid choice. Please enter a number between 1 and {len(options)}.")
