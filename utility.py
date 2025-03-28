###########use in all wizards##########

def print_list_enumerate(response, title, indent=0, enumerate_keys=True):  
    if not response:
        print(f"\nNo {title} found.")
        return

    prefix = "  " * indent  

    if indent == 0:  
        print(f"\n{title}:")

    if isinstance(response, list):
        for i, item in enumerate(response, start=1) if enumerate_keys else enumerate(response, start=0):
            if enumerate_keys:
                print(f"{prefix}{i}. ", end="")
            else:
                print(prefix, end="")

            if isinstance(item, (dict, list)):
                print()
                print_list_enumerate(item, title, indent + 1, enumerate_keys)  
            else:
                print(item)

    elif isinstance(response, dict):        
        for i, (key, value) in enumerate(response.items(), start=1) if enumerate_keys else response.items():
            if enumerate_keys:
                print(f"{prefix}{i}. {key}")
            else:
                print(f"{prefix}- {key}")

            if isinstance(value, (list, dict)):
                print_list_enumerate(value, title, indent + 1, enumerate_keys)  
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