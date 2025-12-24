import socket
import ssl
import browser
import tkinter

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1) # the 1 is the max splits
        assert self.scheme in ["http", "https"]
        if "/" not in url:
            url = url +"/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)


    def request(self):
        s = socket.socket(
            family=socket.AF_INET, #IPV4
            type=socket.SOCK_STREAM, #can send continuos data
            proto=socket.IPPROTO_TCP, 
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)


        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n" #CRUCIAL, or else the receiving server will wait for eternity, this makes it end
        s.send(request.encode("utf8")) #sends request and encodes it into bytes
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip() #casefold handles a wider range than lower
        
        assert "transfer-encoding" not in response_headers #we dont want these
        assert "content-encoding" not in response_headers
        
        content = response.read()
        s.close()

        return content
    

def lex(body):
    in_tag = False
    text = ""
    for c in body:
        if c=="<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text+= c
    
    return text




if __name__ == "__main__":
    import sys
    browser.Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
    # load(URL(sys.argv[1]))