import sys
from .libs import ansitowin32, termcolor


class ColouredWriter(object):
    """
    Simplifies the use of coloured text and highlighting in a terminal.
    """
    def __init__(self):
        """
        Initialises the ColouredWriter object.
        """
        self.converter = ansitowin32.AnsiToWin32(sys.stdout)

        self.colour = None
        self.on_colour = None
        self.attrs = None

    def write(self, text, colour=None, on_colour=None, attrs=None, end="\n"):
        """
        Write text to the terminal.

        Args:
            text (str): the text to write.
            colour (str): the colour of the text.
            on_colour (str): the colour of the text background/highlighting.
            attrs (str): extra properties such as bold or italics.
            end (str): added to the end of text.

        Returns: None
        """
        the_colour = self.colour
        the_on_colour = self.on_colour
        the_attrs = self.attrs

        if colour is not None:
            the_colour = colour

        if on_colour is not None:
            the_on_colour = on_colour

        if attrs is not None:
            the_attrs = attrs

        self.converter.write_and_convert(termcolor.colored(text, the_colour, the_on_colour, the_attrs) + end)


if __name__ == "__main__":
    writer = ColouredWriter()
    
    options = [None, "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    
    for text in options:
        for background in options:
            try:
                writer.write("Hello world!", text, "on_" + background)
            
            except TypeError:
                writer.write("Hello world!", text, None)
                
            print("")
