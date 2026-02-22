import pandas as pd
import os
import shutil
from tabulate import tabulate


def clear_test_results():
    """
    Clears all files and folders from the Test_results directory.
    Creates the folder if it doesn't exist.
    """
    test_results_folder = os.path.join(os.getcwd(), "Test_results")
    os.makedirs(test_results_folder, exist_ok=True)
    
    # Clear all files from Test_results folder
    for filename in os.listdir(test_results_folder):
        file_path = os.path.join(test_results_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def game_state_as_df_to_text(game_state, output_file=None):
    """
    Converts game state into formatted dataframes and text, 
    optionally saving to file.
    
    Args:
        game_state: Dictionary containing deck, discardpile, meadow, 
        locations, players
        output_file: Optional filename to save the output as a text file 
        (saves to Test_results folder)
                    Auto-increment counter is added to prevent overwriting
        
    Returns:
        Dictionary containing formatted output:
        - 'deck_size': Text with deck size
        - 'locations_df': DataFrame with locations and workers (vertical)
        - 'meadow_discardpile_df': DataFrame with meadow and discard pile cards
        - 'players_df': DataFrame with player information
        - 'full_text': Complete formatted text output
        - 'saved_file_path': Path where file was saved
    """
    
    # Extract game state components
    deck = game_state["deck"]
    discardpile = game_state["discardpile"]
    meadow = game_state["meadow"]
    locations = game_state["locations"]
    players = game_state["players"]
    
    # ============================================
    # TEXT FIELDS
    # ============================================
    
    deck_size_text = f"DECK SIZE: {len(deck.cards)}"
    
    # ============================================
    # LOCATIONS DATAFRAME (VERTICAL)
    # ============================================

    location_data = []
    for loc in locations:
        # Format workers as "Player 0: 2, Player 1: 1" etc.
        workers_str = (", ".join([f"Player {p.index}: {count}" for 
                                  p, count in loc.workers.items()]))
        location_data.append({
            "Location": loc.name,
            "Workers": workers_str
        })
    
    locations_df = pd.DataFrame(location_data)
    
    # ============================================
    # MEADOW + DISCARDPILE DATAFRAME
    # ============================================
    
    # Split meadow into two halves (1-4 and 5-8)
    meadow_cards = [card.name for card in meadow.cards]
    meadow_first_half = meadow_cards[:4] if len(meadow_cards) > 0 else []
    meadow_second_half = meadow_cards[4:] if len(meadow_cards) > 4 else []
    
    # Split discard pile into two halves (1-4 and 5-8)
    discard_cards = [card.name for card in discardpile.cards]
    discard_first_half = discard_cards[:4] if len(discard_cards) > 0 else []
    discard_second_half = discard_cards[4:] if len(discard_cards) > 4 else []
    
    # Create dataframe with flexible row count
    max_rows = max(len(meadow_first_half), len(meadow_second_half), 
                   len(discard_first_half), len(discard_second_half))
    
    meadow_discard_data = {
        "Meadow 1-4": [meadow_first_half[i] 
                       if i < len(meadow_first_half) 
                       else "" for i in range(max_rows)],
        "Meadow 5-8": [meadow_second_half[i] 
                       if i < len(meadow_second_half) 
                       else "" for i in range(max_rows)],
        "Discardpile 1-4": [discard_first_half[i] 
                            if i < len(discard_first_half) 
                            else "" for i in range(max_rows)],
        "Discardpile 5-8": [discard_second_half[i] 
                            if i < len(discard_second_half) 
                            else "" for i in range(max_rows)],
    }
    
    meadow_discardpile_df = pd.DataFrame(meadow_discard_data)
    
    # ============================================
    # PLAYERS DATAFRAME
    # ============================================
    
    all_rows = []
    row_labels = []
    
    # Workers row
    row_labels.append("Workers")
    all_rows.append([p.workers for p in players])
    
    # Season row
    row_labels.append("Season")
    all_rows.append([p.season.capitalize() for p in players])
    
    # Finished row
    row_labels.append("Finished")
    all_rows.append([str(p.finished) for p in players])
    
    # Points row (comma-separated with label)
    row_labels.append("Points (card, token,\npros., jour., event)")
    all_rows.append([", ".join([str(p.points[pt]) 
                for pt in ["card", "token", "prosperity", "journey", "event"]])
                for p in players])
    
    # Resources row (comma-separated with label)
    row_labels.append("Resources (twig,\nresin, pebble, berry)")
    all_rows.append([", ".join([str(p.resources[rt]) 
                for rt in ["twig", "resin", "pebble", "berry"]]) 
                for p in players])
    
    # City row (newline-separated)
    row_labels.append("City")
    city_row_data = []
    for player in players:
        city_cards = (
            "\n".join([card.name for card in player.city]) 
            if player.city else "")
        city_row_data.append(city_cards)
    all_rows.append(city_row_data)
    
    # Hand row (newline-separated)
    row_labels.append("Hand")
    hand_row_data = []
    for player in players:
        hand_cards = (
            "\n".join([card.name for card in player.hand]) 
            if player.hand else "")
        hand_row_data.append(hand_cards)
    all_rows.append(hand_row_data)
    
    # Create dataframe
    players_df = pd.DataFrame(
        all_rows,
        columns=[f"Player {p.index}" for p in players],
        index=row_labels)
    
    # ============================================
    # CREATE FULL TEXT OUTPUT WITH BORDERS
    # ============================================
    
    text_output = []
    text_output.append(deck_size_text)
    text_output.append("")
    
    # Locations dataframe with borders
    text_output.append("LOCATIONS:")
    text_output.append(tabulate(locations_df, 
                        headers='keys', tablefmt='grid', showindex=False))
    text_output.append("")
    
    # Meadow + Discardpile dataframe with borders
    text_output.append("MEADOW & DISCARDPILE:")
    text_output.append(tabulate(meadow_discardpile_df, 
                        headers='keys', tablefmt='grid', showindex=False))
    text_output.append("")
    
    # Players dataframe with borders
    text_output.append("PLAYERS:")
    text_output.append(tabulate(players_df, 
                        headers='keys', tablefmt='grid', showindex=True))
    
    full_text = "\n".join(text_output)
    
    # ============================================
    # SAVE TO FILE IF SPECIFIED
    # ============================================
    
    saved_file_path = None
    if output_file:
        # Create Test_results folder if it doesn't exist
        test_results_folder = os.path.join(os.getcwd(), "Test_results")
        os.makedirs(test_results_folder, exist_ok=True)
        
        # Add auto-increment counter to filename
        filename_blank = os.path.splitext(output_file)[0]
        file_extension = os.path.splitext(output_file)[1] or ".txt"
        
        counter = 1
        count_filename = f"{filename_blank}_{counter}{file_extension}"
        saved_file_path = (
            os.path.join(test_results_folder, count_filename))
        
        # Find next available filename if it exists
        while os.path.exists(saved_file_path):
            counter += 1
            count_filename = f"{filename_blank}_{counter}{file_extension}"
            saved_file_path = (
                os.path.join(test_results_folder, count_filename))
        
        # Save to file in Test_results folder
        with open(saved_file_path, 'w') as f:
            f.write(full_text)
    
    # ============================================
    # RETURN RESULTS
    # ============================================
    
    return {
        'deck_size': deck_size_text,
        'locations_df': locations_df,
        'meadow_discardpile_df': meadow_discardpile_df,
        'players_df': players_df,
        'full_text': full_text,
        'saved_file_path': saved_file_path
    }
