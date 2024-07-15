import numpy as np

class Node:
    def __init__(self, x, y, z):
        self.x = x - z/(2**0.5)
        self.y = y - z/(2**0.5)

class Bar:
    def __init__(self, node1, node2):
        self.n1 = node1
        self.n2 = node2
        self.l  = ((node1.x - node2.x)**2 + (node1.y - node2.y)**2)**0.5

def diagram(f, w, h, l_in, l_chip, l_out, t_in, t_chip, t_out):
    ### PREAMBLE
    f.write('\\documentclass{standalone}\n')
    f.write('\\usepackage{tikz}\n')
    f.write('\\usetikzlibrary{arrows.meta,arrows}\n')
    f.write('\\begin{document}\n')
    f.write('\\begin{tikzpicture}\n')
    f.write('\\tiny\n')
    ### DIAGRAM
    # 
    #  l -> x, h -> y, w -> z 
    #
    #           INLET           CHIP         OUTLET
    #
    #      B*-------------F*------------J*-----------N*  
    #       |\             |\            |\           |\
    #      A*-\-----------E* \----------I* \---------M* \
    #        \C*-------------G*------------K*-----------O*
    #         \|             \|            \|           \|
    #         D*-------------H*------------L*-----------P*
    #
    A = Node(0,0,0);                 B = Node(0,h,0);                 C = Node(0,h,w);                 D = Node(0,0,w)
    E = Node(l_in,0,0);              F = Node(l_in,h,0);              G = Node(l_in,h,w);              H = Node(l_in,0,w)
    I = Node(l_in+l_chip,0,0);       J = Node(l_in+l_chip,h,0);       K = Node(l_in+l_chip,h,w);       L = Node(l_in+l_chip,0,w)
    M = Node(l_in+l_chip+l_out,0,0); N = Node(l_in+l_chip+l_out,h,0); O = Node(l_in+l_chip+l_out,h,w); P = Node(l_in+l_chip+l_out,0,w)
    AB = Bar(A,B); AD = Bar(A,D); AM = Bar(A,M); BC = Bar(B,C); BN = Bar(B,N); CD = Bar(C,D); CO = Bar(C,O); DP = Bar(D,P); MN = Bar(M,N); MP = Bar(M,P); NO = Bar(N,O); OP = Bar(O,P)
    EF = Bar(E,F); EH = Bar(E,H); EI = Bar(E,I); FG = Bar(F,G); FJ = Bar(F,J); GH = Bar(G,H); GK = Bar(G,K); HL = Bar(H,L); IJ = Bar(I,J); IL = Bar(I,L); JK = Bar(J,K); KL = Bar(K,L)
    outer = [AB, AD, AM, BC, BN, CD, CO, DP, MN, MP, NO, OP]
    inner = [EF, EH, FG, GH, IJ, IL, JK, KL]
    ### CHIP
    f.write('\\fill [opacity=0.75, fill=red!15!white] (' + f'{A.x}' + ',' + f'{A.y}' + ') -- (' + f'{D.x}' + ',' + f'{D.y}' + ') -- (' + f'{H.x}' + ',' + f'{H.y}' + ') -- (' + f'{E.x}' + ',' + f'{E.y}' + ') -- cycle;\n')
    f.write('\\fill [opacity=0.75, fill=red!90!white] (' + f'{E.x}' + ',' + f'{E.y}' + ') -- (' + f'{H.x}' + ',' + f'{H.y}' + ') -- (' + f'{L.x}' + ',' + f'{L.y}' + ') -- (' + f'{I.x}' + ',' + f'{I.y}' + ') -- cycle;\n')
    f.write('\\fill [opacity=0.75, fill=red!15!white] (' + f'{I.x}' + ',' + f'{I.y}' + ') -- (' + f'{L.x}' + ',' + f'{L.y}' + ') -- (' + f'{P.x}' + ',' + f'{P.y}' + ') -- (' + f'{M.x}' + ',' + f'{M.y}' + ') -- cycle;\n')
    left  = [Node(np.linspace(EH.n1.x,EH.n2.x,9)[i],np.linspace(EH.n1.y,EH.n2.y,9)[i],0) for i in range(9)] + [Node(np.linspace(HL.n1.x,HL.n2.x,9)[i],np.linspace(HL.n1.y,HL.n2.y,9)[i],0) for i in range(9)]
    right = [Node(np.linspace(EI.n1.x,EI.n2.x,9)[i],np.linspace(EI.n1.y,EI.n2.y,9)[i],0) for i in range(9)] + [Node(np.linspace(IL.n1.x,IL.n2.x,9)[i],np.linspace(IL.n1.y,IL.n2.y,9)[i],0) for i in range(9)]
    for l, r in zip(left, right):
        f.write('\\draw [black] (' + f'{l.x}' + ',' + f'{l.y}' + ') -- (' + f'{r.x}' + ',' + f'{r.y}' + ');\n')
    ### EDGES + INFO
    f.write('\\draw [red, -Latex] (' + f'{(A.x + D.x)/2 - 0.5*(l_in+l_chip+l_out)}' + ',' + f'{(B.y + D.y)/2}' + ') -- (' + f'{(A.x + D.x)/2}' + ',' + f'{(B.y + D.y)/2}' + ');\n')
    f.write('\\node [red, label=above:{$T_{in}=' + f'{t_in:.02f}' + 'K$}] at (' + f'{(A.x + D.x)/2 - 0.25*(l_in+l_chip+l_out)}' + ',' + f'{(B.y + D.y)/2}' + ') {};\n')
    for bar in outer:
        f.write('\\draw [black] (' + f'{bar.n1.x}' + ',' + f'{bar.n1.y}' + ') -- (' + f'{bar.n2.x}' + ',' + f'{bar.n2.y}' + ');\n')
    for bar in inner:
        f.write('\\draw [black, dotted] (' + f'{bar.n1.x}' + ',' + f'{bar.n1.y}' + ') -- (' + f'{bar.n2.x}' + ',' + f'{bar.n2.y}' + ');\n')
    f.write('\\draw [red, -Latex] (' + f'{(M.x + P.x)/2}' + ',' + f'{(N.y + P.y)/2}' + ') -- (' + f'{(M.x + P.x)/2 + 0.5*(l_in+l_chip+l_out)}' + ',' + f'{(N.y + P.y)/2}' + ');\n')
    f.write('\\node [red, label=above:{$T_{out}=' + f'{t_out:.02f}' + 'K$}] at (' + f'{(M.x + P.x)/2 + 0.25*(l_in+l_chip+l_out)}' + ',' + f'{(N.y + P.y)/2}' + ') {};\n')
    f.write('\\node [red, label=below:{$T_{chip}=' + f'{t_chip:.02f}' + 'K$}] at (' + f'{(H.x + L.x)/2}' + ',' + f'{(H.y + L.y)/2}' + ') {};\n')
    f.write('\\end{tikzpicture}\n')
    f.write('\\end{document}\n')
