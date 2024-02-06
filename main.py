import random

import numpy
import numpy as np
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QMessageBox
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPainter, QColor, QAction, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
import threading


class connect_four:
    def __init__(self):
        self.height = 6
        self.width = 7
        self.board = self.init_board()
        self.num_of_coins = 0

    def init_board(self):
        board = np.zeros((self.height, self.width), dtype=int)
        return board

    def init_game(self):
        self.board = self.init_board()
        self.num_of_coins = 0

    def make_move(self, player, col, board):
        if not self.check_move(col, board):
            return False

        height = len(board) - 1
        while board[height][col] == 0:
            if height == -1:
                break
            height -= 1
        board[height + 1][col] = player
        self.num_of_coins += 1
        return True

    def check_move(self, col, board):
        if not 0 <= col < len(board[0]):
            return False
        if board[len(board) - 1][col] != 0:
            return False
        return True

    def remove_player(self, col, board):
        height = len(board) - 1
        while board[height][col] == 0:
            if height == 0:
                break
            height -= 1

        if height == len(board) - 1:
            return
        board[height][col] = 0

    def check_win(self, player, board):
        # Check horizontal
        for row in range(len(board)):
            for col in range(len(board[row]) - 3):
                if all(board[row][col + i] == player for i in range(4)):
                    return True

        # Check vertical
        for col in range(len(board[0])):
            for row in range(len(board) - 3):
                if all(board[row + i][col] == player for i in range(4)):
                    return True

        # Check diagonal (bottom-left to top-right)
        for row in range(3, len(board)):
            for col in range(len(board[row]) - 3):
                if all(board[row - i][col + i] == player for i in range(4)):
                    return True

        # Check diagonal (top-left to bottom-right)
        for row in range(len(board) - 3):
            for col in range(len(board[row]) - 3):
                if all(board[row + i][col + i] == player for i in range(4)):
                    return True

        return False

    def check_tie(self, board):
        last_row = board[len(board) - 1]
        if 0 in last_row:
            return False
        else:
            return True


class com_ai:
    def __init__(self, game, sign, win, open_two, open_three, seven_trap, center):
        self.sign = sign
        self.opponent = 2 if sign == 1 else 1
        self.game = game

        self.score_win = win
        self.score_open_two = open_two
        self.score_open_three = open_three
        self.score_seven_trap = seven_trap
        self.score_center = center

    def minimax(self, board, depth, player, alpha, beta):
        if self.game.check_win(player, board):
            if player == self.sign:
                return self.score_win * depth
            else:
                return self.score_win * depth * -1

        if self.game.check_tie(board):
            return 0

        if depth == 0:
            return self.get_score(board)

        if self.sign == player:  # maximizing
            best_score = -float("inf")
            new_board = numpy.copy(board)
            for cols in range(len(board[0])):
                if self.game.make_move(player, cols, new_board):
                    score = self.minimax(new_board, depth - 1, self.opponent, alpha, beta)
                    self.game.remove_player(cols, new_board)
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
            return best_score

        else:  # minimizing
            best_score = float("inf")
            new_board = numpy.copy(board)
            for cols in range(len(board[0])):
                if self.game.make_move(player, cols, new_board):
                    score = self.minimax(new_board, depth - 1, self.sign, alpha, beta)
                    self.game.remove_player(cols, new_board)
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if alpha >= beta:
                        break
            return best_score

    def best_move(self, board):
        best_move = self.check_if_can_win(board, self.sign)
        if best_move is not None:
            return best_move

        best_move = self.check_if_can_win(board, self.opponent)
        if best_move is not None:
            return best_move

        if self.check_if_going_to_tie():
            print("check this out")

        best_score = -float("inf")
        new_board = numpy.copy(board)
        for cols in range(len(board[0])):
            if self.game.make_move(self.sign, cols, new_board):
                score = self.minimax(new_board, 4, self.opponent, -float("inf"), float("inf"))
                self.game.remove_player(cols, new_board)
                if score > best_score:
                    best_score = score
                    best_move = cols
        print(best_score)

        if best_move is None:
            print(best_move)
        return best_move

    def get_score(self, board):
        score = 0

        score += (self.check_lines(board, self.sign, 2) - self.check_lines(board, self.opponent,
                                                                           2)) * self.score_open_two

        score += (self.check_lines(board, self.sign, 3) - self.check_lines(board, self.opponent,
                                                                           3)) * self.score_open_three

        score += (self.check_7_traps(board, self.sign) - self.check_7_traps(board,
                                                                            self.opponent)) * self.score_seven_trap

        score += (self.check_center(board, self.sign) - self.check_center(board, self.opponent)) * self.score_center

        return score

    def check_lines(self, board, player, num):
        count = 0
        # Check horizontal lines
        for row in board:
            if self.check_opens(row, player, num):
                count += 1

        # Check vertical lines
        for col in range(len(board[0])):
            if self.check_opens([row[col] for row in board], player, num):
                count += 1

        # Check diagonal lines (bottom-left to top-right)
        for i in range(len(board) - 3):
            for j in range(len(board[0]) - 3):
                if self.check_opens([board[i + k][j + k] for k in range(4)], player, num):
                    count += 1

        # Check diagonal lines (top-left to bottom-right)
        for i in range(3, len(board)):
            for j in range(len(board[0]) - 3):
                if self.check_opens([board[i - k][j + k] for k in range(4)], player, num):
                    count += 1

        return count

    def check_opens(self, line, player, num):
        # Check if there is an open three-in-a-row in a list
        for i in range(len(line) - 3):
            four_pieces = [line[i + j] for j in range(4)]
            empty_count = four_pieces.count(0)
            player_count = four_pieces.count(player)

            if player_count == num and empty_count == 4 - num:
                return True

        return False

    def check_7_traps(self, board, player):
        count = 0

        for rows in range(len(board)):
            for cols in range(len(board[rows])):

                if rows < len(board) - 2 and cols < len(board[rows]) - 2:
                    if board[rows][cols] == board[rows + 1][cols + 1] == board[rows + 2][cols + 2] == player:
                        if board[rows][cols + 1] == board[rows][cols + 2]:
                            count += 1
                        if board[rows + 2][cols] == board[rows + 2][cols + 1]:
                            count += 1
                        if board[rows + 1][cols] == board[rows + 2][cols]:
                            count += 1
                        if board[rows][cols + 2] == board[rows + 1][cols + 2]:
                            count += 1

                if rows < len(board) - 2 and cols < len(board[rows]) - 2:
                    if board[rows + 2][cols] == board[rows + 1][cols + 1] == board[rows][cols + 2] == player:
                        if board[rows][cols] == board[rows][cols + 1]:
                            count += 1
                        if board[rows + 2][cols + 1] == board[rows + 2][cols + 2]:
                            count += 1
                        if board[rows][cols] == board[rows + 1][cols]:
                            count += 1
                        if board[rows + 1][cols + 2] == board[rows + 2][cols + 2]:
                            count += 1
        return count

    def check_center(self, board, player):
        count = 0
        for rows in range(len(board)):
            for cols in range(2, 5):
                if board[rows][cols] == player:
                    count += 1
        return count

    def check_if_can_win(self, board, player):
        for col in board[0]:
            self.game.make_move(player, col, board)
            if self.game.check_win(player, board):
                self.game.remove_player(col, board)
                return col
            self.game.remove_player(col, board)
        return None

    def check_if_going_to_tie(self):
        if self.game.num_of_coins + 1 == self.game.height * self.game.width:
            return True
        return False

    def change_sign(self, sign):
        self.sign = sign
        self.opponent = 2 if sign == 1 else 1

    def __str__(self):
        return f"Stats: win: {self.score_win}, two: {self.score_open_two}, three: {self.score_open_three}, seven: {self.score_seven_trap}, center: {self.score_center}"


class tournament:
    def __init__(self, com):
        self.game = connect_four()
        self.best_ai = com

    def play_a_game(self, player1, player2):
        self.game.init_game()
        player1.change_sign(1)
        player2.change_sign(2)
        player = 1
        while True:
            if player == 1:
                self.game.make_move(player1.sign, player1.best_move(self.game.board), self.game.board)

            else:
                self.game.make_move(player2.sign, player2.best_move(self.game.board), self.game.board)

            if self.game.check_win(player, self.game.board):
                print(f'Player {player} Won!')
                if player == 1:
                    return player1
                else:
                    return player2

            if self.game.check_tie(self.game.board):
                return random.choice([player1, player2])
            if player == 1:
                player += 1
            else:
                player -= 1

    def make_player(self):
        win = random.randint(2000, 5000)
        center = random.randint(1, 1000)
        two = random.randint(1, 1000)
        three = random.randint(1, 1000)
        seven = random.randint(1, 1000)
        player = com_ai(self.game, 2, win, two, three, seven, center)
        return player

    def play_tournament(self):
        print('q1')
        first_quarter = self.play_a_game(self.best_ai, self.make_player())
        print('q2')
        second_quarter = self.play_a_game(self.make_player(), self.make_player())
        print('q3')
        third_quarter = self.play_a_game(self.make_player(), self.make_player())
        print('q4')
        fourth_quarter = self.play_a_game(self.make_player(), self.make_player())
        print('h1')
        first_half = self.play_a_game(first_quarter, second_quarter)
        print('h2')
        second_half = self.play_a_game(third_quarter, fourth_quarter)
        print('f')
        final = self.play_a_game(first_half, second_half)
        print(final.__str__())


class ConnectFourGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.playable = True
        self.game = connect_four()
        self.ai = com_ai(self.game, 2, 4639, 206, 882, 55, 140)
        self.menu_choice = 1
        self.player = 1
        self.buttons = None
        self.status_label = None
        self.grid = None
        self.layout = None
        self.central_widget = None
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a menu bar
        menu_bar = self.menuBar()
        game_menu = menu_bar.addMenu('Game')

        play_with_friend_action = QAction('Play with a Friend', self)
        play_with_friend_action.triggered.connect(self.play_with_friend)
        game_menu.addAction(play_with_friend_action)

        play_vs_computer_action = QAction('Play against Computer', self)
        play_vs_computer_action.triggered.connect(self.play_vs_computer)
        game_menu.addAction(play_vs_computer_action)

        play_vs_computer_action = QAction('Enhance computer', self)
        play_vs_computer_action.triggered.connect(self.tourn)
        game_menu.addAction(play_vs_computer_action)

        self.status_label = QLabel("Connect Four")
        self.layout.addWidget(self.status_label)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.layout.addLayout(self.grid)

        # Create the game board
        self.buttons = []
        for row in range(self.game.height - 1, -1, -1):  # Start from the last row and go to the first row
            row_buttons = []
            for col in range(self.game.width):  # Start from the last column and go to the first column
                button = QPushButton()
                button.setFixedSize(100, 100)
                row_buttons.append(button)
                self.grid.addWidget(button, row, col)
                button.clicked.connect(lambda _, row=self.game.height - 1 - row, col=col: self.cell_clicked(row, col))
            self.buttons.append(row_buttons)
        self.print_board()

    def cell_clicked(self, row, col):
        if self.buttons[row][col].text() != "":
            return
        if not self.playable:
            return
        self.friendly_game(col)
        if self.menu_choice == 2:
            self.playable = False
            self.vs_computer()

    def print_board(self):
        # Update the button labels based on the current board state
        icon = ""
        for row in range(self.game.height):
            for col in range(self.game.width):
                if self.game.board[row][col] == 0:
                    icon = "White.jpeg"
                elif self.game.board[row][col] == 1:
                    icon = "Red.jpeg"  # Player 1's piece
                elif self.game.board[row][col] == 2:
                    icon = "Yellow.jpeg"  # Player 2's piece

                pixmap = QPixmap(icon)
                self.buttons[row][col].setIcon(QIcon(pixmap))
                self.buttons[row][col].setIconSize(QSize(100, 95))

    def play_with_friend(self):
        self.playable = True
        self.player = 1
        self.menu_choice = 1
        self.game.init_game()
        self.print_board()

    def play_vs_computer(self):
        self.playable = True
        self.player = 1
        self.menu_choice = 2
        self.game.init_game()
        self.print_board()

    def friendly_game(self, col):
        self.game.make_move(self.player, col, self.game.board)
        self.print_board()
        if self.game.check_win(self.player, self.game.board):
            self.playable = False
            self.announce_winner(self.player)
        else:
            self.player = 3 - self.player

    def vs_computer(self):
        self.game.make_move(self.player, self.ai.best_move(self.game.board), self.game.board)
        self.print_board()
        if self.game.check_win(self.player, self.game.board):
            self.playable = False
            self.announce_winner(self.player)
        else:
            self.player = 3 - self.player
            self.playable = True

    def announce_winner(self, winner):
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"Player {winner} wins!")

        # Add a button to close the message box
        msg.addButton('Ok', QMessageBox.ButtonRole.YesRole)

        # Execute the message box
        msg.exec()

    def tourn(self):
        tourni = tournament(self.ai)
        tourni.play_tournament()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ConnectFourGame()
    ex.show()
    sys.exit(app.exec())



