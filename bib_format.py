with open("citations.txt", "r") as f:
    with open("citations2.txt", "w") as g:
        g.write("Recorded use cases\n")
        g.write("=========\n\n")
        for x in f:
            g.write(x)
            g.write('\n\n')
