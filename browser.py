import tkinter.font
# from url import lex

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100   

def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c=="<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    
    if not in_tag and buffer:
        out.append(Text(buffer))
    
    return out

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        


    def load(self, url):
        body = url.request()
        tokens = lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, f in self.display_list:
            if y>self.scroll + HEIGHT: continue
            if y + VSTEP<self.scroll: continue

            self.canvas.create_text(x, y - self.scroll, text=c, font=f)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()

class Layout:
    def __init__(self, tokens: str):
        self.display_list = []
        self.line = []
        self.cursor_x: int = HSTEP
        self.cursor_y: int = VSTEP
        self.weight: str = "normal"
        self.style: str = "roman"
        self.size: int = 12
        for tok in tokens:
            self.token(tok)
        self.flush()

    def token(self, tok) -> list[str]:
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word=word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight == "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small": 
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP


        return self.display_list
    
    def word(self, word: str):
 
        font = tkinter.font.Font(
            size=self.size,
            weight=self.weight,
            slant=self.style,
        )
        w = font.measure(word)
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(" ")
        if self.cursor_x + w >= WIDTH - HSTEP:
            self.flush()
        # if self.cursor_x + w >= WIDTH - HSTEP:
        #     self.cursor_y += font.metrics("linespace") * 1.25
        #     self.cursor_x = HSTEP 

        self.line.append((self.cursor_x, word, font))

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + (1.25 * max_descent)
        self.cursor_x = HSTEP
        self.line = []

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag