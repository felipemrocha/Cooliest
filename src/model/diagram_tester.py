from channel_diagram import diagram

with open('diagram.tex', 'w') as f:
    w      = 3
    h      = .8
    l_in   = .2
    l_chip = 3
    l_out  = 1
    t_in   = 69
    t_chip = 250
    t_out  = 420
    diagram(f, w, h, l_in, l_chip, l_out, t_in, t_chip, t_out)
    print('Done!')
