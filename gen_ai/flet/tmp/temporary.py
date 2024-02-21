import flet

# Create a dropdown menu with the options "Option 1", "Option 2", and "Option 3".
dropdown = flet.Dropdown(
    options=["Option 1", "Option 2", "Option 3"]
)

# Display the dropdown menu to the user.
dropdown.display()

# Get the user's selection from the dropdown menu.
selection = dropdown.get_selection()

# Print the user's selection to the console.
print(f"The user selected {selection}.")