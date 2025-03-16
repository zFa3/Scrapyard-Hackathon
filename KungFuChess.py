# KFChess - zFa3
# inspiration: kfchess.com

class KFChess:
    
    # init
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):

        self.WHITE, self.BLACK = True, False

        # the symbols on the board
        self.PADDING = "."
        self.PLACEHOLDER = "-"
        self.EMPTY = " "
        self.PIECES = {
            "k":"♔", "q":"♕", "r":"♖", "b":"♗", "n":"♘", "p":"♙", "K":"♚", "Q":"♛", "R":"♜", "B":"♝", "N":"♞", "P":"♟", ".":" "
        }
        # set the fen of the board
        self.ROWS, self.COLS = 12, 10
        # initialize the board
        self.board = [self.PLACEHOLDER for _ in range(self.ROWS * self.COLS)]
        # set the castling rights for both sides
        self.white_castle, self.black_castle = [True, True], [True, True]
        # cardinal direction constants
        self.U, self.D, self.L, self.R = (-self.COLS, self.COLS, -1, 1)
        # set the fen
        try: self.set_fen(fen)
        except: self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    # set the board based of an input fen
    def set_fen(self, fen: str) -> None:
        fen = fen.replace("/", "")
        fen_index = 0
        for row in range(12):
            for col in range(10):
                index = row * self.COLS + col
                if self.board[index] != self.PLACEHOLDER: continue
                if row < 2 or row > 9 or col < 1 or col > 8:
                    self.board[index] = self.PADDING; continue
                elif fen[fen_index].isnumeric():
                    for _ in range(int(fen[fen_index])):
                        self.board[index + _] = self.EMPTY
                else: self.board[index] = fen[fen_index]
                fen_index += 1

    # reset the game board
    def reset_game(self):
        self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.white_castle, self.black_castle = [True, True], [True, True]
    
    # prints the current game board to the console
    def print_board(self):
        show_index = False
        for row in range(2, 10):
            for col in range(1, 9):
                index = row * self.COLS + col
                if self.board[index] == self.EMPTY:
                    if show_index: print(index, end = " ")
                    else: print(self.EMPTY, end = " ")
                else: print(self.PIECES[self.board[index]], end = " " + (" " if show_index else ""))
            print()

    # generates pseudolegal moves for a position, returns a 'list' of pairs of indicies (From, To)
    def generate_pseudo_legal_moves(s, white: bool) -> list[tuple[int, int]]:
        if not s.is_game_over(): return [] # there are no legal moves
        pseudo_legal_moves = []
        pieces = ("kqrbnp", "KQRBNP")
        for index, item in enumerate(s.board):
            if item in pieces[white]:
                item = item.upper()
                if item == "N":
                    for loc in (s.U + s.U + s.L, s.U + s.U + s.R, s.L + s.L + s.U, s.L + s.L + s.D, s.R + s.R + s.U, s.R + s.R + s.D, s.D + s.D + s.L, s.D + s.D + s.R):
                        if s.board[index + loc] == s.EMPTY or s.board[index + loc] in pieces[not white]:
                            pseudo_legal_moves.append((index, index + loc))
                elif item == "B":
                    for dir in (s.U + s.L, s.U + s.R, s.D + s.L, s.D + s.R):
                        for ray in range(1, 9):
                            if s.board[index + dir * ray] == s.EMPTY:
                                pseudo_legal_moves.append((index, index + dir * ray))
                            elif s.board[index + dir * ray] in pieces[not white]:
                                pseudo_legal_moves.append((index, index + dir * ray))
                                break
                            else: break
                elif item == "R":
                    for dir in (s.U, s.D, s.L, s.R):
                        for ray in range(1, 9):
                            if s.board[index + dir * ray] == s.EMPTY:
                                pseudo_legal_moves.append((index, index + dir * ray))
                            elif s.board[index + dir * ray] in pieces[not white]:
                                pseudo_legal_moves.append((index, index + dir * ray))
                                break
                            else: break
                elif item == "Q":
                    for dir in (s.U + s.L, s.U + s.R, s.D + s.L, s.D + s.R, s.U, s.D, s.L, s.R):
                        for ray in range(1, 9):
                            if s.board[index + dir * ray] == s.EMPTY:
                                pseudo_legal_moves.append((index, index + dir * ray))
                            elif s.board[index + dir * ray] in pieces[not white]:
                                pseudo_legal_moves.append((index, index + dir * ray))
                                break
                            else: break
                elif item == "K":
                    for loc in (s.U + s.L, s.U + s.R, s.D + s.L, s.D + s.R, s.U, s.D, s.L, s.R):
                        if s.board[index + loc] == s.EMPTY or s.board[index + loc] in pieces[not white]:
                            pseudo_legal_moves.append((index, index + loc))
                    # left side castling
                    if (white and s.white_castle[0] and index == 95 and all([s.board[castle_squares] == s.EMPTY for castle_squares in range(92, 95)])):
                        pseudo_legal_moves.append((95, 93))
                    elif (not white and s.black_castle[0] and index == 25 and all([s.board[castle_squares] == s.EMPTY for castle_squares in range(22, 25)])):
                        pseudo_legal_moves.append((25, 23))
                    
                    # right side castling
                    if (white and s.white_castle[1] and index == 95 and all([s.board[castle_squares] == s.EMPTY for castle_squares in range(96, 98)])):
                        pseudo_legal_moves.append((95, 97))
                    elif (not white and s.black_castle[1] and index == 25 and all([s.board[castle_squares] == s.EMPTY for castle_squares in range(26, 28)])):
                        pseudo_legal_moves.append((25, 27))
                elif item == "P":
                    pawn_direction = (s.U if white else s.D)
                    if s.board[index + pawn_direction] == s.EMPTY:
                        pseudo_legal_moves.append((index, index + pawn_direction))
                        if ((white and 80 < index < 89) or (not white and 30 < index < 39)) and s.board[index + (pawn_direction * 2)] == s.EMPTY:
                        # if (white and 80 < index < 89) or (not white and 30 < index < 39) and s.board[index + (pawn_direction * 2)] == s.EMPTY:
                            pseudo_legal_moves.append((index, index + pawn_direction * 2))
                    for target in (pawn_direction + s.R, pawn_direction + s.L):
                        if s.board[index + target] in pieces[not white]:
                            pseudo_legal_moves.append((index, index + target))
        return pseudo_legal_moves
    
    # make a move on the board, accounts for castling and promotion
    def make_move(self, move: tuple[int, int], player: bool) -> bool:
        if move in self.generate_pseudo_legal_moves(player):
            self.board[move[1]] = self.board[move[0]]
            self.board[move[0]] = self.EMPTY
            
            self.white_castle[0] = move[0] != 91 and self.white_castle[0]
            self.white_castle[1] = move[0] != 98 and self.white_castle[1]
            self.black_castle[0] = move[0] != 21 and self.black_castle[0]
            self.black_castle[1] = move[0] != 28 and self.black_castle[1]
            
            self.white_castle = [move[0] != 95 and self.white_castle[0], move[0] != 95 and self.white_castle[1]]
            self.black_castle = [move[0] != 25 and self.black_castle[0], move[0] != 25 and self.black_castle[1]]
            
            if self.board[move[1]] == "P" and 20 < move[1] < 29: self.board[move[1]] = "Q"
            if self.board[move[1]] == "p" and 90 < move[1] < 99: self.board[move[1]] = "q"

            if move[0] == 95 and move[1] == 93: self.board[91] = self.EMPTY; self.board[94] = "R"; self.white_castle = [False, False]
            if move[0] == 95 and move[1] == 97: self.board[98] = self.EMPTY; self.board[96] = "R"; self.white_castle = [False, False]

            if move[0] == 25 and move[1] == 23: self.board[21] = self.EMPTY; self.board[24] = "r"; self.black_castle = [False, False]
            if move[0] == 25 and move[1] == 27: self.board[28] = self.EMPTY; self.board[26] = "r"; self.black_castle = [False, False]
            return True
        return False
    
    def make_illegal_move(self, move: tuple[int, int]) -> None:
        self.board[move[1]] = self.board[move[0]]
        self.board[move[0]] = self.EMPTY
        
        self.white_castle[0] = move[0] != 91 and self.white_castle[0]
        self.white_castle[1] = move[0] != 98 and self.white_castle[1]
        self.black_castle[0] = move[0] != 21 and self.black_castle[0]
        self.black_castle[1] = move[0] != 28 and self.black_castle[1]
        
        self.white_castle = [move[0] != 95 and self.white_castle[0], move[0] != 95 and self.white_castle[1]]
        self.black_castle = [move[0] != 25 and self.black_castle[0], move[0] != 25 and self.black_castle[1]]
        
        if self.board[move[1]] == "P" and 20 < move[1] < 29: self.board[move[1]] = "Q"
        if self.board[move[1]] == "p" and 90 < move[1] < 99: self.board[move[1]] = "q"

    def format_indicies(self, index: int) -> int:
        row, col = index // 8, index % 8
        return (row + 2) * self.COLS + (col + 1)
    
    # checks if the index is out of bounds
    def in_bounds(self, square: int) -> bool:
        return 1 < square // self.COLS < 10 and 0 < square % self.COLS < 9
    
    def return_board(self) -> list[str]:
        return [item for index, item in enumerate(self.board) if self.in_bounds(index)]
    
    # format from 8x8 to 12x10 or vice versa
    def format_index(self, index: int, to_8x8: bool) -> int:
        row, col = index // (self.COLS if to_8x8 else 8), index % (self.COLS if to_8x8 else 8)
        return ((row + (-2 if to_8x8 else 2)) * (8 if to_8x8 else self.COLS) + col + (-1 if to_8x8 else 1))
    
    def format_move(self, move: tuple[int, int], to_8x8: bool) -> tuple[int, int]:
        return (self.format_index(move[0], to_8x8), self.format_index(move[1], to_8x8))
    
    def captured_piece_type(self, move: tuple[int, int]) -> None | str:
        return self.board[move[1]] if self.board[move[1]] != self.EMPTY else None
    
    def add_padding(self, board: list[str]) -> list[str]:
        new_board = [self.PADDING for _ in range(self.COLS * self.ROWS)]
        for index, item in enumerate(board):
            row, col = index // 8, index % 8
            new_board[(row + 2) * self.COLS + col + 1] = item
        return new_board
    
    def is_game_over(self) -> bool:
        return self.board.count("k") == 1 and self.board.count("K") == 1

if __name__ == "__main__":
    kf_chess = KFChess()
    plm_list = kf_chess.generate_pseudo_legal_moves(True)
    print([kf_chess.format_move(i, True) for i in plm_list])