## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: generator of latex files

import mmap
import re
import subprocess as sub
import os
from glob import glob

def insert_line_after(ifile, search, text) :
    insert_line_before(ifile, search, text, shift = 1)  

def insert_line_before(ifile, search, text, shift = 0) :
    f = open(ifile, "r")
    lines = f.readlines()
    f.close()

    ind = 0
    for ind,l in enumerate(lines) :
        if search in l :
            break

    lines.insert(ind+shift, text+"\n")

    f = open(ifile, "w")
    lines = "".join(lines)
    f.write(lines)
    f.close()


class latex_doc :

    def __init__(self, title = "", layout = "v") :
        
        if title != "" :
            title = title.replace(".tex","")+".tex"
        else :
            title = "latex_doc.tex"
        self.filetitle = title

        self.file = open(title,"w")
        self.file.write("\\documentclass{article}\n")
        if layout ==  "h" :
            self.file.write("\\usepackage[a4paper,margin=1in,landscape]{geometry}\n")
        self.file.write("\\usepackage{multirow}\n")
       
        self.file.write("\\usepackage{array}\n")
        self.file.write("\\newcolumntype{$}{>{\\global\\let\\currentrowstyle\\relax}}\n")
        self.file.write("\\newcolumntype{^}{>{\\currentrowstyle}}\n")
        self.file.write("\\newcommand{\\rowstyle}[1]{\\gdef\\currentrowstyle{#1}#1\\ignorespaces}\n")
        
        self.file.write("\\begin{document}\n\n")
        self.file.write("\n\n\\end{document}\n")
        self.file.close()
        self.file = open(title,"r+")

    def insert_line(self, text) :

        insert_line_before(self.filetitle, "end{document}", text) 
        self.file = open(self.filetitle,"r+")

    def insert_line_after(self, search, text) :

        insert_line_after(self.filetitle, search, text)
        self.file = open(self.filetitle,"r+")

    def set_title(self, title) :
       
        self.insert_line_after("begin{document}","\n\n\section{"+title+"}\n")

    def insert_section(self, title) :
       
        self.insert_line("\n\n\subsection{"+title+"}\n")

    def add_to_preamble(self, text) :

        if ".tex" in text[-4:] :
            text = open(text).read()
        insert_line_before(self.filetitle, "begin{document}","\n\n"+text+"\n\n")
        self.file = open(self.filetitle,"r+")

    def insert_latex(self, text) :

        if ".txt" in text[-4:] or ".tex" in text[-4:] :
            text = open(text).read()
        self.insert_line(text)

    def insert_figure(self, fig, width = None, ninrow=1, caption="") :

        if width is None : width = 0.9 / ninrow
        if isinstance(fig,list) :
            for fi,pic in enumerate(fig) :
                if fi%ninrow==0 : self.insert_line("\\begin{figure}[h!]")
                self.insert_line("\\includegraphics[width={w}\\textwidth]{{{f}}}".format(w=width,f=pic))
                if fi%ninrow==(ninrow-1) or (fi == len(fig)-1) : 
                    self.insert_line('\\caption{'+caption+'}')
                    self.insert_line("\\end{figure}\n")
        else :
            self.insert_line("\\begin{figure}")
            self.insert_line("\\includegraphics[width={w}\\textwidth]{{{f}}}".format(w=width,f=fig))
            self.insert_line('\\caption{'+caption+'}')
            self.insert_line("\\end{figure}\n")

    def insert_tabular(self, tab, caption = "", struct = None) :

        if ".txt" in tab[-4:] :
            tab = open(tab).read()

        self.insert_line('\\begin{table}[hb!]\n\\begin{center}')
        self.insert_line('\\caption{'+caption+'}')
        if struct : self.insert_line('\\begin{tabular}{'+struct.replace("{","").replace("}","")+'}\\hline')
        self.insert_line(tab)
        if struct : self.insert_line('\\hline\n\\end{tabular}')
        self.insert_line('\n\\end{center}\n\\end{table}\n')

    def insert_tabular_from_grid(self, grid, caption = None, has_title = True) :

        if ".txt" in grid[-4:] :
            grid = open(grid).read()

        lines = grid.split("\n")
        struct = ''
        for j,l in enumerate(lines[:-1]) :
            if has_title and j == 0 :
                lines[0] = "\\rowstyle{\\bfseries}\n"+l.replace(r'\\','') + r' \\ \hline' 
                continue
            l = l.replace("&","").replace("\\\\","") 
            elms = l.split()
            for i,e in enumerate(elms) :
                if (j == 1 and has_title) or (j == 0 and not has_title) : struct += "^c|"
                if r'\pm' in elms[i+1] or ('+' in elms[i+1] and '-' in elms[i+1]) :
                    elms[i] = "$%s \\pm %s$" % (e, elms[i+2])
                    del elms[i+1]
                    del elms[i+1]
            lines[j] = '  &  '.join(elms) + "  \\\\"
        
        self.insert_tabular('\n'.join(lines), struct = '|$' + struct[1:])


    def close_and_compile(self) :

        self.file.close()
        print "pdflatex " + self.filetitle
        sub.call("pdflatex " + self.filetitle,shell=True)
        for f in glob("*.log")+glob("*.aux")+glob("*.out") : os.remove(f)




