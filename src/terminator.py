import os
import sys
import textwrap
import shutil

from . import colours

if os.name == "nt":
    import msvcrt

else:
    import tty
    import termios

TERMINAL_WIDTH = shutil.get_terminal_size((80, 20))


def get_char():
    """
    Gets a single character from standard input.

    Returns: str
    """
    # Windows method returns empty string if no character is waiting to be read.
    if os.name == "nt":
        if msvcrt.kbhit():
            return msvcrt.getch()

        else:
            return ""

    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


def find_closest(text, values, closest=False):
    """
    Finds closest match to text in values.

    Args:
        text (str): the string to find matches for.
        values (iterable): iterable containing possible matches.
        closest (bool): if False only returns exact matches.

    Returns: str
    """
    new_text = text.lstrip().lower()
    
    inside = []
    for value in values:
        if new_text in value:
            inside.append(value)
    
    if len(inside) == 0:
        def find_similarities(text, list1):
            num = 0
            chars_done = {}
            for char in text:
                if char in list1:
                    if char in chars_done.keys():
                        if list1.count(char) > chars_done[char]:
                            num += 1
                            chars_done[char] += 1
                    
                    else:
                        chars_done[char] = 1
                        num += 1
            
            return num
                    
        if closest:
            most = [values[0], find_similarities(text, values[0])]
            for value in values[1:]:
                similarities = find_similarities(text, value)
                if similarities > most[1]:
                    most = [value, similarities]
                
                elif similarities == most[1]:
                    if len(value) < len(most[0]):
                        most = [value, similarities]
            
            return most[0]
            
        else:
            return text
    
    elif len(inside) == 1:
        return inside[0]
    
    else:
        smallest = inside[0]
        for match in inside:
            if len(match) < len(smallest):
                smallest = match
        
        return smallest


def index_from_end(list1, value):
    """
    Finds the index of the first match of value in list starting from the end and working backwards.

    Args:
        list1 (iterable): iterable to find match in.
        value:

    Returns: int
    """
    list1.reverse()
    return -(list1.index(value) + 1)


class DrawQueue(object):
    def __init__(self, window):
        """
        Initialises the object.

        Args:
            window (TerminalWindow): window object to draw to.

        Returns: None
        """
        assert isinstance(window, TerminalWindow)
        self.window = window

        self.queue = []

    def add_draw(self, func, args=()):
        """
        Add a draw call to the queue.
        
        Args:
            func (callable or str): the function to call or string to print.
            args (tuple): the arguments to give the function when it is called.

        Returns: None
        """
        self.queue.append((func, args))
        self.next()

    def next(self):
        """
        Attempts to make the next draw call in the queue.

        Returns: None
        """
        if self.window.lock is not None or id(self.queue[0][0]) == self.window.lock:
            try:
                if isinstance(self.queue[0][0], str):
                    self.window.print(self.queue[0][0])

                else:
                    self.queue[0][0](*self.queue[0][1])

                self.window.lock = None

            except IndexError:
                # No draw calls currently exist.
                pass


class TerminalWindow(object):
    """
    Flexible terminal interface that gives greater control over how text is displayed.
    """
    def __init__(self, wrap=False, wrap_width=TERMINAL_WIDTH):
        """
        Initialises the TerminalWindow object.

        Args:
            wrap (bool): determines whether text being printed should be wrapped. Uses the TERMINAL_WIDTH global variable.
        """
        if os.name == "nt":
            self._CLEAR_COMMAND = "cls"
        
        else:
            self._CLEAR_COMMAND = "clear"

        self.wrap = wrap
        self.wrap_width = wrap_width
            
        self._screen = []
        self._writer = colours.ColouredWriter()
        self._VALID_COLOURS = [None, "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

        self.draw_queue = DrawQueue(self)

        # Lock is the id of the drawing function which has obtained the lock
        self.lock = None

    def __setattr__(self, key, value):
        # Goes to the next item in self.draw_queue whenever self is unlocked.
        try:
            if key == "lock" and value is None and self.lock is not None:
                self.draw_queue.next()

        except AttributeError:
            #Occurs in __init__
            pass

        super().__setattr__(key, value)

    def lock(self, the_id):
        """
        Locks the TerminalWindow object to prevent other threads from changing the screen.
        This is not enforced - it is either used by the Screen class or implemented by the user.

        Args:
            the_id (int): the id of the function obtaining the lock.

        Returns: None
        """
        self.lock = the_id

    def unlock(self):
        """
        Unlocks the TerminalWindow.

        Returns: None
        """
        self.lock = None

    def fg_colour(self, colour):
        """
        Changes the colour of future text.

        Args:
            colour (str): the colour to change the text colour to. Must exist in self._VALID_COLOURS.

        Returns: None
        """
        assert colour in self._VALID_COLOURS
        self._writer.colour = colour

    def bg_colour(self, colour):
        """
        Changes the background colour of future text.

        Args:
            colour (str): the colour to change the background colour to. Must exist in self._VALID_COLOURS.

        Returns: None
        """
        assert colour in self._VALID_COLOURS
        self._writer.on_colour = colour

    def set_colours(self, the_colours):
        """
        Set foreground and background colours simultaneously.

        Args:
            the_colours (tuple): 2-element tuple containing the foreground and background text colours respectively.

        Returns: None
        """
        self.fg_colour(the_colours[0])
        if len(the_colours) > 1:
            self.bg_colour(the_colours[1])
    
    def print(self, text="", end="\n"):
        """
        Displays text to the terminal. The text is added to the screen data so that if the terminal is re-drawn the
        text will still be displayed.

        Args:
            text (str): the text to be displayed.
            end (str): additional string to display at the end of a line. This is not added to the screen data.

        Returns: None
        """
        if self.wrap:
            text = "\n".join(textwrap.wrap(text, width=self.wrap_width))

        if "\n" not in end:
            try:
                self._screen[-1] += text

            except IndexError:
                self._screen.append(text)

        else:
            for i in range(text.count("\n")):
                self._screen.append("")
                self._screen[-1] += text

        self._writer.write(text, end=end)
    
    def clear_buffer(self):
        """
        Clears screen data so it will be clear if the terminal is redrawn.

        Returns: None
        """
        self._screen = []
    
    def clear_terminal(self):
        """
        Clears the terminal window. Screen data is not affected.

        Returns: None
        """
        os.system(self._CLEAR_COMMAND)
    
    def clear_screen(self):
        """
        Clears the terminal and screen data.

        Returns: None
        """
        self.clear_buffer()
        self.clear_terminal()
    
    def redraw(self):
        """
        Clear the terminal then re-writes screen data.

        Returns: None
        """
        self.clear_terminal()
        for line in self._screen:
            self._writer.write(line)
    
    def delete_previous(self):
        """
        Removes the previous line in screen data.

        Returns: None
        """
        try:
            the_index = index_from_end(self._screen[-1], "\n")
            self._screen = self._screen[:-1].extend(self._screen[-1][:the_index])
            
        except ValueError:
            self._screen = self._screen[:-1]
        
        self.redraw()

    def count_lines(self):
        """
        Counts the number of lines in the screen data.

        Returns: int
        """
        return self._screen.count("\n")

    def insert(self, text, xy):
        """
        Insert the text at position xy, where the greater the y value, the lower the height.

        Args:
            text (str): the text to insert.
            xy (tuple): tuple containing x and y integer coordinates.

        Returns: None
        """
        num_lines = self.count_lines()
        if num_lines < xy[1]:
            self._screen += "\n" * (xy[1] - num_lines)
            self._screen += (" " * xy[0]) + text

        else:
            def find_nth(iterable, item, n):
                start = iterable.index(item)
                while start >= 0 and n > 1:
                    start = iterable.index(item, start+len(item))
                    n -= 1
                return start

            index = find_nth(self._screen, "\n", xy[1]) + 1
            self._screen = self._screen[:index] + (" " * xy[0]) + text + self._screen[index:]

    def input(self, text="", keep_input=True):
        """
        Gets user input.

        Args:
            text (str): the text to prompt user input.
            keep_input (bool): if true, the user input is added to the screen data (stays on redraw).

        Returns: str
        """
        params = ()
        try:
            # If there is a space at the end of text, prevent a newline from being printed.
            if text[-1] == " ":
                params = (text[:-1], " ")

            else:
                params = (text, "")

        except IndexError:
            pass

        self.print(*params)
        the_input = input()

        if keep_input:
            # Add the input to the screen so it will stay on redraw.
            try:
                self._screen[:-1].extend(self._screen[-1] + the_input)

            except IndexError:
                self._screen = [the_input,]

        return the_input
