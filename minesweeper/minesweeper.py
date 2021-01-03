import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # This command checks if the "cell" parameter is in the sentence.
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # This command checks if the "cell" parameter is in the sentence.
        if cell in self.cells:
            self.cells.remove(cell)

    def infer_from(self, other):
        """
        Returns inferred sentence from this and other sentence.
        If it can't make any inference returns None.
        """
        if other.cells.issubset(self.cells):
            return Sentence(self.cells - other.cells, self.count - other.count)
        elif self.cells.issubset(other.cells):
            return Sentence(other.cells - self.cells, other.count - self.count)
        else:
            return None

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the current cell as a move
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)

        new = Sentence(self.nearby_cells(cell), count)

        # Loop over all the known mines
        for mine in self.mines:
            new.mark_mine(mine)

        # Loop over all the known safe cells
        for safe in self.safes:
            new.mark_safe(safe)

        # Append the new "Sentence" to the original Knowledge Base
        self.knowledge.append(new)

        # Create 2 new data sets, "new_mines" and "new_safe"
        new_mines = set()
        new_safes = set()

        # Loop over every sentence in the Knowledge Base
        for sentence in self.knowledge:

            # Mark any additional Mines using the new, updated KB
            for cell in sentence.known_mines():
                new_mines.add(cell)

            # Mark any additional Safes using the new, updated KB
            for cell in sentence.known_safes():
                new_safes.add(cell)

        for cell in new_mines:
            self.mark_mine(cell)
        for cell in new_safes:
            self.mark_safe(cell)

        # Add new sentences if they can be inferred from existing knowledge
        more = []

        for sentenceA, sentenceB in itertools.combinations(self.knowledge, 2):
            inference = sentenceA.infer_from(sentenceB)
            if inference is not None and inference not in self.knowledge:
                more.append(inference)

        # Add all elements of the list, "more" to the end of KB
        self.knowledge.extend(more)

        # Loop over every sentence in the KB
        for sentence in self.knowledge:

            # Remove any empty sentences from the knowledge base
            if sentence == Sentence(set(), 0):
                self.knowledge.remove(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if (move not in self.moves_made) and (move not in self.mines):
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if (move not in self.moves_made) and (move not in self.mines):
                    return move
        return None

    def nearby_cells(self, cell):
        
        # Creates a blank set, called "cells"
        cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                
                # If (i,j) happens to be current cell, ignore it and move on
                if (i, j) == cell:
                    continue

                # Add as neighbour if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells.add((i, j))
        return cells