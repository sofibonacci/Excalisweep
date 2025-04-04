###########use in all wizards##########

def print_list_enumerate(response, title): #function to print enumerated lists  
    if not response:
        print(f"\nNo {title} found.")
        return
    
    print(f"\n{title}:")
    for i, item in enumerate(response, start=1):
        print(f"{i}. {item}")


def select_from_list(item_list, prompt_message, allow_all=False): # function to select one or multiple items from a list
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