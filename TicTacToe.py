import copy
import random

def play():
    game_pieces = [['_', '_', '_'], ['_', '_', '_'], [' ', ' ', ' ']]
    user_token = 'x'
    computer_token = 'O'
    Game_Is_Over = False
    Cats_Game = False
    user_turns_played = 0

    while not Game_Is_Over:
        # Human goes first
        game_pieces = one_turn(game_pieces, user_token)
        Game_Is_Over = did_player_win(game_pieces, user_token)
        if Game_Is_Over:
            break
        user_turns_played += 1

        # Five user turns and four computer turns have been played,
        # therefore the gameboard is filled.
        if user_turns_played >= 5: 
            Cats_Game, Game_Is_Over = True, True
            break

        print "=============================================="

        # Computer's turn
        game_pieces = computer_turn(game_pieces, computer_token, user_token)
        Game_Is_Over = did_player_win(game_pieces, computer_token)

    # Game is over
    who_won(game_pieces, computer_token, user_token, Cats_Game)
    

def one_turn(game_pieces, user_token):
    print draw_board(game_pieces)
    user_turn = get_user_turn(game_pieces)
    game_pieces[user_turn[0]][user_turn[1]] = '%s' % user_token
    print draw_board(game_pieces)
    return game_pieces


def computer_turn(game_pieces, computer_token, user_token):
    empty_spots = get_empty_spots(game_pieces)
    return best_computer_move(game_pieces, computer_token, user_token)


def best_computer_move(game_pieces, computer_token, user_token):
    # Strategy taken from http://en.wikipedia.org/wiki/Tic-tac-toe#Strategy
    # Checks if a move is a winning move, a blocking move, a forking move,
    # or a move to block an opponents fork, and executes that move
    # according to the given hiearchy.
    # If no move will do those things, it will play the center, play a corner
    # opposite of its opponent, or play an available side.

    # Trys to get a winning move
    empty_spots = get_empty_spots(game_pieces)
    for choice in empty_spots:
        if is_winning_move(game_pieces, choice, computer_token):
            return place_choice(game_pieces, choice, computer_token)

    # Trys to get a blocking move
    for choice in empty_spots:
        if is_winning_move(game_pieces, choice, user_token):
            return place_choice(game_pieces, choice, computer_token)

    # Trys to get a forking move
    for choice in empty_spots:
        if is_forking_move(game_pieces, choice, computer_token):
            return place_choice(game_pieces, choice, computer_token)

    # Trys to get a fork-blocking move that also forces the opponent to block
    # then trys to get play a fork-block that doesn't force opponent to block
    fork_blocking_move = exists_fork_blocking_move(game_pieces, computer_token, user_token)
    if fork_blocking_move:
        return fork_blocking_move

    # Plays center
    if 5 in empty_spots:
        return place_choice(game_pieces, 5, computer_token)

    # Plays the corner opposite of opponent
    corner = player_in_corner(game_pieces, user_token)
    if corner:
        opposite_corner = find_opposite_corner(corner)
        if is_empty_spot(game_pieces, opposite_corner):
            return place_choice(game_pieces, opposite_corner, computer_token)

    # Plays first available corner
    corners = [1, 3, 7, 9]
    for choice in corners:
        if choice in empty_spots:
            return place_choice(game_pieces, choice, computer_token)

    # Plays first available side
    sides = [2, 4, 6, 8]
    for choice in empty_spots:
        if choice in sides:
            return place_choice(game_pieces, choice, computer_token)

    # Could not find anywhere to play
    raise NameError('Could not find a place to play.')


def is_winning_move(game_pieces, choice, token):
    temp_game_pieces = copy.deepcopy(game_pieces)
    place_choice(temp_game_pieces, choice, token)

    if did_player_win(temp_game_pieces, token):
        return True
    return False


def is_forking_move(game_pieces, choice, token):
    temp_game_pieces, empty_spots = temp_game_situation(game_pieces)
    place_choice(temp_game_pieces, choice, token)

    possible_wins = 0

    for second_choice in empty_spots:
        temp_temp_game_pieces = copy.deepcopy(temp_game_pieces)
        place_choice(temp_temp_game_pieces, second_choice, token)

        if did_player_win(temp_temp_game_pieces, token):
            possible_wins += 1

    return possible_wins >= 2


def exists_fork_blocking_move(game_pieces, computer_token, user_token):
    # Trys to get fork-blocking
    temp_game_pieces, empty_spots = temp_game_situation(game_pieces)

    has_fork = False
    forking_spot = 0
    for choice in empty_spots:
        if is_forking_move(game_pieces, choice, user_token):
            forking_spot = choice
            has_fork = True
    if not has_fork:
        return False

    else:
        # Trys to get a move that forces the opponent to block
        # instead of creating a fork for them
        for choice in empty_spots:
            if is_block_forcing_and_fork_blocking(game_pieces, choice,
                                     computer_token, user_token):
                return place_choice(game_pieces, choice, computer_token)

        # Will block the fork, without forcing making opponent block
        return place_choice(game_pieces, forking_spot, computer_token)


def is_block_forcing_and_fork_blocking(game_pieces, choice, 
                                        computer_token, user_token):
    temp_game_pieces, empty_spots = temp_game_situation(game_pieces)

    place_choice(temp_game_pieces, choice, computer_token)

    if is_block_forcing_move(temp_game_pieces, computer_token):
        # Plays the next two turns.
        # Now, if user does not have winning move, and does not have a fork,
        # the move is considered block-forcing and fork-blocking.

        # Finds and places best hypothetical play for the human player
        temp_game_pieces = best_computer_move(temp_game_pieces, user_token,
                                             computer_token)

        # Finds and places best hypothetical play for the computer
        temp_game_pieces = best_computer_move(temp_game_pieces,
                                             computer_token, user_token)

        # After the hypothetical plays, the human player has neither
        # a winning move nor a forking move available
        if not has_winning_move(temp_game_pieces, user_token):
            return True

    return False


def has_winning_move(game_pieces, token):
    temp_game_pieces, empty_spots = temp_game_situation(game_pieces)

    for choice in empty_spots:
        if is_winning_move(temp_game_pieces, choice, token):
            return True
        elif is_forking_move(temp_game_pieces, choice, token):
            return True
    return False


def is_block_forcing_move(game_pieces, computer_token):
    temp_game_pieces, empty_spots = temp_game_situation(game_pieces)

    for choice in empty_spots:
        if is_winning_move(temp_game_pieces, choice, computer_token):
            return True
    return False


def player_in_corner(game_pieces, token):
    # Finds if a player with the inputted token is in any of the corners.
    # If he is, returns the board position of the occupied corner
    corners = [1, 3, 7, 9]
    for i in corners:
        spot = find_board_index(i)
        if game_pieces[spot[0]][spot[1]] == token:
            return i
    return False


def find_opposite_corner(corner):
    opposite_corners = {1:9, 3:7, 7:3, 9:1}
    return opposite_corners[corner]


def did_player_win(game_pieces, token):
    # Checks across
    for row in game_pieces:
        if token == row[0] == row[1] == row[2]:
            return "Across", row[0]

    # Checks down
    for i in range(0, len(game_pieces[0])):
        if token == game_pieces[i][i] == (game_pieces[i-1][i] == 
                                                game_pieces[i-2][i]):
            return "Down", game_pieces[i][i]

    # Checks diagonals
    if token == game_pieces[0][0] == game_pieces[1][1] == game_pieces[2][2]:
        return "Diagonal", game_pieces[0][0]
    elif token == game_pieces[0][2] == game_pieces[1][1] == game_pieces[2][0]:
        return "Diagonal", game_pieces[0][2]

    # No win
    return None


def draw_board(game_pieces):
    board = '\n'
    for row in game_pieces:
        board += row[0]
        for spot in row[1:]:
            board += '|' + spot
        board += '\n'
    return board


def get_user_turn(game_pieces):
    empty_spot = False
    while not empty_spot:
        choice = raw_input("Where do you want to play? 1-9\n>>>")
        try:
            choice = int(choice)
        except ValueError:
            continue
        empty_spot = is_empty_spot(game_pieces, choice)

    return find_board_index(choice)


def is_empty_spot(game_pieces, choice):
    choice_location = find_board_index(choice)
    row, column = choice_location[0], choice_location[1]
    if choice not in range(1, 10):
        return False
    # Checks if no piece has played there
    elif (game_pieces[row][column] == '_' or game_pieces[row][column] == ' '):
        return True
    else:
        return False


def find_board_index(spot):
    row = None
    column = None
    if spot in range(1, 4):
        row =  0
    elif spot in range(4, 7):
        row =  1
    elif spot in range(7, 10):
        row =  2
    else:
        return "find_board_index had an error"
    column = (spot - 1) % 3

    return row,column


def get_empty_spots(game_pieces):
    empty_spots = []
    for choice in range(1, 10):
        if is_empty_spot(game_pieces, choice):
            empty_spots.append(choice)
    return empty_spots


def place_choice(game_pieces, choice, token):
    spot_location = find_board_index(choice)
    game_pieces[spot_location[0]][spot_location[1]] = "%s" % token
    return game_pieces


def who_won(game_pieces, computer_token, user_token, Cats_Game=None):
    if Cats_Game:
        print 'Cats Game'
        print 'Game Over'

    elif did_player_win(game_pieces, user_token):
        print user_token, 'wins'
        print draw_board(game_pieces)
        # What kind of win
        print did_player_win(game_pieces, user_token)[0]

    elif did_player_win(game_pieces, computer_token):
        print computer_token, 'wins'
        # What kind of win
        print did_player_win(game_pieces, computer_token)[0]
        print draw_board(game_pieces)



def temp_game_situation(game_pieces):
    temp_game_pieces = copy.deepcopy(game_pieces)
    empty_spots = get_empty_spots(temp_game_pieces)
    return temp_game_pieces, empty_spots

print '''\n
   /= = = = = = = = = = = = = = = = = = = = = = =\\
  /= = = = = = = = = = = = = = = = = = = = = = = =\\
 ||                                               ||
 ||            Welcome to TicTacToe!              ||
 ||                                               ||
 ||              The controls are:                ||
 ||                                               ||
 ||                   1 2 3                       ||
 ||                   4 5 6                       ||
 ||                   7 8 9                       ||
 ||                                               ||
 ||                 Good Luck!                    ||
 ||                                               ||
  \= = = = = = = = = = = = = = = = = = = = = = = =/
   \= = = = = = = = = = = = = = = = = = = = = = =/
'''

play()