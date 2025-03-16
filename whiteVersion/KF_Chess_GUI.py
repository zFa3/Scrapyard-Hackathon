import pygame as p
import KungFuChess as kfc
import time as tm

import serial

#Open serial communication with Arduino 2 (connected to Computer 2)
arduino2 = serial.Serial('/dev/tty.usbmodem1101', 9600, timeout=0.05)  # Change COM port based on your setup
tm.sleep(2)  # Give some time to establish connection

#Send a value to Arduino 2
#arduino2.write(b'Hello from Computer 2\n')

#Read response from Arduino 2 (which gets forwarded from Arduino 1)

width = height = 1000
dimension = 8
square_size = height // dimension

DELIMETER = ("|", "~")
images = {}
PLAYER = True
kf_chess = kfc.KFChess()
pieces = [
    "bB", "bK", "bN", "bP", "bQ", "bR",
    "wB", "wK", "wN", "wP", "wQ", "wR",
]

HIGHLIGHT_COLOR = (155, 231, 135)
COOLDOWN_COLOR = (216, 67, 95)
SELECT_COLOR = (0, 0, 0)

cooldown = 5 # in seconds

times = [tm.perf_counter() for _ in range(64)]

def change_notation(inp: str) -> str:
    return ("b" if inp.islower() else "w") + inp.upper()

def loadImages():
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("ChessPieces/" + piece + ".png"), (square_size, square_size))

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    # clock = p.time.Clock()
    screen.fill((0, 0, 0, 0))
    loadImages()
    click = -1
    index = -1
    while kf_chess.is_game_over():
        for e in p.event.get():
            if e.type == p.QUIT:
                break
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // square_size
                row = location[1] // square_size
                p.draw.rect(screen, p.Color(52, 158, 235), p.Rect(row, col, square_size, square_size))
                index = row * 8 + col
                if click == -1 or (tm.perf_counter() - times[click]) < cooldown:
                    click = index
                else:
                    # print(kf_chess.format_move((click, (index)), False))
                    if not kf_chess.make_move(kf_chess.format_move((click, (index)), False), PLAYER):
                        if not is_all_pieces_frozen():
                            if kf_chess.make_move(kf_chess.format_move((click, (index)), False), not PLAYER):
                                arduino2.write(send(("0" if len(str(click)) == 1 else "") + str(click) + ("0" if len(str(index)) == 1 else "") + str(index)))
                                set_all_pieces_cooldown()
                            else: click = index
                        else: click = index
                    else:
                        times[index] = tm.perf_counter()
                        arduino2.write(send(("0" if len(str(click)) == 1 else "") + str(click) + ("0" if len(str(index)) == 1 else "") + str(index)))
                        click = -1

        drawBoard(screen)
        drawPieces(screen, kf_chess.return_board(), click, [kf_chess.format_index(move[1], True) if kf_chess.format_index(move[0], True) == click else -1 for move in kf_chess.generate_all_plm()])
        # clock.tick(max_fps)
        p.display.flip()
        if arduino2.in_waiting > 0:
            message = arduino2.readline().decode().strip()
            recieve(message)
            arduino2.flushInput()
            #break
        # recv(send())

def set_all_pieces_cooldown():
    br = kf_chess.return_board()
    for i, t in enumerate(times):
        if (str(br[i]).isupper() and PLAYER) or (str(br[i]).islower() and not PLAYER):
            times[i] = tm.perf_counter()

def is_all_pieces_frozen():
    res = True
    br = kf_chess.return_board()
    for i, t in enumerate(times):
        if (str(br[i]).isupper() and PLAYER) or (str(br[i]).islower() and not PLAYER):
            res = res and (tm.perf_counter() - times[i] < cooldown)
    return res

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*square_size, r*square_size, square_size, square_size))

def drawPieces(screen, board, click, moves):
    for r in range(dimension):
        for c in range(dimension):
            piece = change_notation(board[r * 8 + c])
            if piece in pieces:
                screen.blit(images[piece], p.Rect(c*square_size, r*square_size, square_size, square_size))
                if (tm.perf_counter() - times[r * 8 + c] < cooldown):
                    percentage = ((tm.perf_counter() - times[r * 8 + c]) / cooldown) * square_size
                    sf = p.Surface((width, height))
                    sf.set_alpha(200)
                    sf.fill((0, 0, 0, 0))
                    p.draw.rect(sf, COOLDOWN_COLOR, p.Rect(c * square_size, r * square_size + percentage, square_size, square_size - percentage))
                    screen.blit(sf, (0, 0))
            if click == r * 8 + c:
                sf = p.Surface((width, height))
                sf.set_alpha(200)
                sf.fill((0, 0, 0, 0))
                p.draw.rect(sf, SELECT_COLOR, p.Rect(c * square_size, r * square_size, square_size, square_size))
                screen.blit(sf, (0, 0))
            for item in moves:
                if item == r * 8 + c:
                    sf = p.Surface((width, height))
                    sf.set_alpha(200)
                    sf.fill((0, 0, 0, 0))
                    p.draw.rect(sf, HIGHLIGHT_COLOR, p.Rect(c * square_size, r * square_size, square_size, square_size))
                    screen.blit(sf, (0, 0))

def send(a) -> str:
    print("send", a)
    return bytes(a + "\n", "utf-8")

def recv(info: str) -> None:
    global kf_chess, times
    parsed = info.split(DELIMETER[0])
    kf_chess.board = parsed[0].split(DELIMETER[1])
    times = list(map(float, parsed[1].split(DELIMETER[1])))

def recieve(string: str) -> None:
    global times, kf_chess
    print("recv", string)
    move1, move2 = int(string[:2]), int(string[2:])
    kf_chess.make_illegal_move((kf_chess.format_index(move1, False), kf_chess.format_index(move2, False)))
    times[move2] = tm.perf_counter()

if __name__ == "__main__":
    main()