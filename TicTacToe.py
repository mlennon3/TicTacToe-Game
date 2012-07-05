import copy

class Board(object):

    def __init__(self, board = [], board_size = 3):
        self.board_size = board_size
        self.game_pieces = []

        # Has ability to accept different board-sizes
        for i in xrange(1, board_size):
            self.game_pieces.append(['_']*self.board_size)
        self.game_pieces.append([' ']*self.board_size)

        self.corners = [1, board_size, board_size**2 - board_size + 1,
                         board_size**2]
        # Does not accept different board-sizes(like most of this file)
        self.sides = [2, 4, 6, 8]
        self.computer_token = 'O'
        self.human_token = "x"
        self.whos_turn = "x"


    def draw_board(self):
        board = '\n'
        for row in self.game_pieces:
            board += row[0]
            for spot in row[1:]:
                board += '|' + spot
            board += '\n'
        return board


    def find_board_index(self, spot):
        # Has future use capibility
        if spot not in range(1, 1 + self.board_size**2):
            return "find_board_index had an error"
        row = (spot-1)/self.board_size
        column = (spot - 1) % self.board_size
        return row, column


    def get_empty_spots(self):
        empty_spots = []
        for choice in range(1, 1 + self.board_size**2):
            if self.is_empty_spot(choice):
                empty_spots.append(choice)
        return empty_spots
        

    def is_empty_spot(self, choice):
        choice_location = self.find_board_index(choice)
        row, column = choice_location[0], choice_location[1]

        # Not a spot on the board
        if choice not in range(1, 1 + self.board_size**2):
            return False
        elif (self.game_pieces[row][column] == '_'
             or self.game_pieces[row][column] == ' '):
            return True
        else:
            return False

    # Sets the token into the gameboard
    def place_token(self, token, spot):
        spot_location = self.find_board_index(spot)
        self.game_pieces[spot_location[0]][spot_location[1]] = '%s' % token


    def who_won_and_how(self):
        # Checks across
        for row in self.game_pieces:
            if row[0] == row[1] == row[2]:

                if row[0] != ' ' and row[0] != '_':
                    return row[0], "Across"

        # Checks down
        for i in range(0, self.board_size):
            if (self.game_pieces[i][i] == self.game_pieces[i-1][i] == 
                self.game_pieces[i-2][i]):

                if self.game_pieces[i] != ' ' and self.game_pieces[i] != '_':
                    return self.game_pieces[i][i], "Down"
        
        # Checks diagonals
        if (self.game_pieces[1][1] != ' ' and self.game_pieces[1][1] != '_'):
            if (self.game_pieces[0][0] == self.game_pieces[1][1] ==
                                        self.game_pieces[2][2]):
                return self.game_pieces[0][0], "Diagonal"

            elif (self.game_pieces[0][2] == self.game_pieces[1][1] ==
                                        self.game_pieces[2][0]):
                return self.game_pieces[0][2], "Diagonal"

        # Checks if game-board is full
        if len(self.get_empty_spots()) == 0:
            return "Cat's Game", None


    def find_opposite_corner(self, corner):
        opposite_corners = {self.corners[0]: self.corners[3],
                            self.corners[1]: self.corners[2],
                            self.corners[2]: self.corners[1],
                            self.corners[3]: self.corners[0]}
        return opposite_corners[corner]


class Game(object):
    def __init__(self, board, who_starts):
        self.board = board
        self.who_starts = who_starts


    def play(self):
        if self.who_starts == 'x':
            print board.draw_board()
            while True:
                self.human_turn()
                if board.who_won_and_how():
                    break
                print "================="
                self.computer_turn()
                if board.who_won_and_how():
                    break

        elif self.who_starts == 'O':
            while True:
                self.computer_turn()
                if board.who_won_and_how():
                    break
                print "================="
                self.human_turn()
                if board.who_won_and_how():
                    break

        print "Game over, %s" % (board.who_won_and_how()[0])
        if board.who_won_and_how()[1]:
            print "Wins %s" % board.who_won_and_how()[1]
        print board.draw_board()


    # For computer to check moves against an independant copy
    def temp_board(self, board_choice):
        temp_board = copy.deepcopy(board_choice)
        return temp_board


    def get_human_choice(self):
        empty_spot = False
        while not empty_spot:
            choice = raw_input("Where do you want to play? 1-9\n>>>")
            try:
                choice = int(choice)
            except ValueError:
                continue
            # Try again if the spot is already taken
            empty_spot = board.is_empty_spot(choice)
        return choice


    def human_turn(self):
        move = self.get_human_choice()
        board.place_token(board.human_token, move)
        print board.draw_board()


    def computer_turn(self):
        move = self.best_computer_move(board)
        board.place_token(board.computer_token, move)
        print board.draw_board()


    def best_computer_move(self, which_board):
        temp_board = self.temp_board(which_board)
        empty_spots = temp_board.get_empty_spots()
        # Strategy taken from http://en.wikipedia.org/wiki/Tic-tac-toe#Strategy
        # Checks if a move is a winning move, a blocking move, a forking move,
        # or a move to block an opponents fork, and executes that move
        # according to the given hiearchy.
        # If no move will do those things, it will play the center, play a
        # corner opposite of its opponent, or play an available side.

        # Trys to get a winning move
        for choice in empty_spots:
            if self.is_winning_move(temp_board, choice,
                                    temp_board.computer_token):
                return choice


        # Trys to get a blocking move
        for choice in empty_spots:
            if self.is_winning_move(temp_board, choice,
                                    temp_board.human_token):
                return choice


        # Trys to get a forking move
        for choice in empty_spots:
            if self.is_forking_move(temp_board, choice,
                                    temp_board.computer_token):
                return choice


        # Trys to get a fork-blocking move
        fork_blocking_move = self.is_fork_blocking_move(temp_board)
        if fork_blocking_move:
            return fork_blocking_move


        # Plays center
        if 5 in temp_board.get_empty_spots():
            return 5


        # Plays the corner opposite of opponent
        for corner in temp_board.corners:
            spot = board.find_board_index(corner)
            if (temp_board.game_pieces[spot[0]][spot[1]] ==
                                        temp_board.human_token):
                opp_corner = temp_board.find_opposite_corner(corner)
                if opp_corner in temp_board.get_empty_spots():
                    return opp_corner


        # Plays first open corner
        for corner in temp_board.corners:
            if corner in temp_board.get_empty_spots():
                return corner


        # Plays first available side
        for side in temp_board.sides:
            if side in temp_board.get_empty_spots():
                return side

        #Could not find anywhere
        raise NameError("Could not find a place to play")


    def is_winning_move(self, which_board, choice, token):
        temp_board = self.temp_board(which_board)
        temp_board.place_token(token, choice)
        if temp_board.who_won_and_how():
            return True


    def is_forking_move(self, which_board, choice, token):
        temp_board = self.temp_board(which_board)
        temp_board.place_token(token, choice)
        possible_wins = 0

        for second_choice in temp_board.get_empty_spots():
            temp_temp_board = self.temp_board(temp_board)
            temp_temp_board.place_token(token, second_choice)

            if temp_temp_board.who_won_and_how():
                possible_wins += 1

        return possible_wins >= 2


    # Trys to get a fork-block
    def is_fork_blocking_move(self, which_board):
        temp_board = self.temp_board(which_board)

        Has_Fork = False
        forking_spot = 0
        for choice in temp_board.get_empty_spots():
            if self.is_forking_move(temp_board, choice, board.human_token):
                forking_spot = choice
                Has_Fork = True

        if not Has_Fork:
            return False

        else:
            # Trys to get a move that forces the opponent to block
            # and that won't give opponent a future fork
            for choice in temp_board.get_empty_spots():
                if self.is_forcing_and_forking_move(temp_board, choice,
                                                 board.computer_token):
                    return choice

            # Will block the fork, but without forcing opponent to block
            return forking_spot


    def is_forcing_and_forking_move(self, which_board, choice, token):
        temp_board = self.temp_board(which_board)
        temp_board.place_token(token, choice)

        if self.exists_block_forcing_move(temp_board, token):
            # Plays the next two turns.
            # Now, if user does not have winning move, and does not have
            # a fork, the move is considered block-forcing and fork-blocking

            # Finds and places next best possible play for human player
            human_move = self.best_computer_move(temp_board)
            temp_board.place_token(temp_board.human_token, human_move)

            # Finds and places next best possible play for computer
            comp_move = self.best_computer_move(temp_board)
            temp_board.place_token(temp_board.computer_token, comp_move)

            # After the hypothetical plays, the human player has
            # neither a winning move nor a forking move available
            if not self.has_winning_move(temp_board, temp_board.human_token):
                return True
        return False


    # Checks to see if in the next two moves there is a winning spot
    def has_winning_move(self, which_board, token):
        temp_board = self.temp_board(which_board)

        for choice in temp_board.get_empty_spots():
            if self.is_winning_move(temp_board, choice, token):
                return True
            elif self.is_forking_move(temp_board, choice, token):
                return True
        return False


    # Checks to see if the player given by 'token' has two in a row
    def exists_block_forcing_move(self, which_board, token):
        temp_board = self.temp_board(which_board)

        for choice in temp_board.get_empty_spots():
            if self.is_winning_move(temp_board, choice, token):
                return True
        



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
board = Board()
game = Game(board, 'x')
game.play()


Again = True
players = ['x', 'O']
# To keep a loop of more games
i = 1
while Again:
    if raw_input("Do you want to play again? Y/N\n>>>").lower() != 'y':
        Again = False
        print "Goodbye"
        break
    else:
        board = Board()
        game = Game(board, players[i%2])
        game.play()
        i += 1