import os
import colours
import sys
import tty

if os.name == "nt":
    import msvcrt

else:
    import termios


def get_char():
    """Returns a single character from standard input."""

    #Windows method returns empty string if no character is waiting to be read.
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
    Finds the closest match to text in values.

    :param text:
    :param values:
    :param closest:
    :return:
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


def suggest_closest(msg, the_list, the_window, closest=True):
    input1 = input(msg)
    if input1 == "":
        return input1
    while True:
        the_closest = find_closest(input1, the_list, closest=closest)
        if the_closest == input1:
            return input1
            
        the_window.redraw()
        print("Did you mean " + the_closest + "? Press \"Enter\" to confirm.")
        input2 = input()
        if input2.strip() == "":
            return the_closest
        
        else:
            input1 = input2

def index_from_end(list1, value):
    list1.reverse()
    return -(list1.index(value) + 1)


class TerminalWindow(object):
    def __init__(self):
        if os.name == "nt":
            self._CLEAR_COMMAND = "cls"
        
        else:
            self._CLEAR_COMMAND = "clear"
            
        self._screen = []
        self._writer = colours.ColoredWriter()
    
    def print(self, text="", end="\n"):
        self._screen.append(text)
        self._writer.write(text, end=end)
    
    def clear_buffer(self):
        self._screen = []
    
    def clear_terminal(self):
        os.system(self._CLEAR_COMMAND)
    
    def clear_screen(self):
        self.clear_buffer()
        self.clear_terminal()
    
    def redraw(self):
        self.clear_terminal()
        for line in self._screen:
            self._writer.write(line)
    
    def delete_previous(self):
        try:
            the_index = index_from_end(self._screen[-1], "\n")
            self._screen = self._screen[:-1].extend(self._screen[-1][:the_index])
            
        except ValueError:
            self._screen = self._screen[:-1]
        
        self.redraw()
    
    def input(self, text="", keep_input=True):
        """
        Gets user input.

        keep_input [True]: determines whether the input is added to the text buffer (stays on redraw).
        """

        params = ()
        try:
            #If there is a space at the end of text, prevent a newline from being printed.
            if text[-1] == " ":
                params = (text[:-1], " ")

            else:
                params = (text, "")

        except IndexError:
            pass

        self.print(*params)
        the_input = input()

        if keep_input:
            #Add the input to the screen so it will stay on redraw.
            self._screen = self._screen[:-1].extend(self._screen[-1] + the_input)

        return the_input


if __name__ == "__main__":
    """
    window = TerminalWindow()
    
    list1 = ["hello", "hello sir", "something", "weird"]
    while True:
        window.print(find_closest(input(), list1, True) + "\n\n")
        window.redraw()
    """
    writer = colours.ColoredWriter()
    
    options = [None, "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    
    for text in options:
        for background in options:
            try:
                writer.write("Hello world!", text, "on_" + background)
            
            except TypeError:
                writer.write("Hello world!", text, None)
                
            print("")
    
