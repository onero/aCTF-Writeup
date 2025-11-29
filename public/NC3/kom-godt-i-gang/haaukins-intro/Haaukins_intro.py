from pwn import *

context.log_level = "warn"

IP = "intro.nc3"

flag = [32] * len("################################################")
while 32 in flag:
    with remote(IP, 6346) as io:
        io.recvline()
        line = io.recvline()

    for i, c in enumerate(line):
        if c != 32:
            flag[i] = c
            print(bytes(flag).decode())
            break
