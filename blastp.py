from Bio.Blast.Applications import NcbiblastpCommandline
from zipfile import ZipFile
import os
import pandas as pd
import glob
from tkinter import messagebox
from rThread import retThread

''' Delete all files in a folder '''
def clean_up(path="./tmp"):

    all_files = glob.glob(os.path.join(path, "*"))
    for file in all_files:
        os.remove(file)

''' Pull peptide sequences from 'index_begin' to 'index_end' (inclusive) '''
def extract_peptides(focus_path, index_begin, index_end):
    
    r = open(focus_path)
    peptides = ""
    for line in r.readlines():
        peptides += line
    peptides = peptides.split('>')
    return peptides[index_begin:index_end+1]

''' Create .zip out of ./tmp '''
def create_zip(save_as): 

    shutil_used = False
    try:
        os.rename("tmp", save_as)
    except Exception:
        import shutil
        shutil.move("tmp", save_as)

    zipObj = ZipFile("zip/"+save_as+".zip", "w")
    zipObj.write(save_as + "/score.csv")
    zipObj.write(save_as + "/id.csv")
    zipObj.write(save_as + "/positive.csv")
    zipObj.write(save_as + "/gap.csv")
    zipObj.write(save_as + "/frequency.csv")
    zipObj.write(save_as + "/peptide.csv")
    zipObj.write(save_as + "/focus_peptides.faa")
    zipObj.write(save_as + "/data.xlsx")
    zipObj.write(save_as + "/all_blastp.txt")
    zipObj.write(save_as + "/all_blastp.xml")
    zipObj.close()
    if not shutil_used:
        os.rename(save_as, "tmp")
    else:
        shutil.move(save_as, "tmp")

''' Create .xlxs out of .csv files '''
def create_workbook(path="./tmp"):
    
    all_files = glob.glob(os.path.join(path, "*.csv"))
    writer = pd.ExcelWriter('tmp/data.xlsx', engine='xlsxwriter')
    for f in all_files:
        df = pd.read_csv(f)
        df.to_excel(writer, sheet_name=os.path.splitext(os.path.basename(f))[0], index=False)
    writer.save()

''' Run blastp query locally (Local Installation is REQUIRED) '''
def blastp(user_query, user_subject, user_evalue):
    
    ncbi_blastp = NcbiblastpCommandline(query=user_query,
                                        subject=user_subject,
                                        evalue=user_evalue)
    return ncbi_blastp() # Returns blastp query output in tuple of form (stdout, stderr)

''' Same as above, but output is XML format as AS requested '''
def blastp_xml(user_query, user_subject, user_evalue):
    
    ncbi_blastp = NcbiblastpCommandline(query=user_query,
                                        subject=user_subject,
                                        evalue=user_evalue,
                                        outfmt=5)
    return ncbi_blastp() # Returns blastp query output in tuple of form (stdout, stderr)

''' Get the Scores, Id, Positives, and Gap of the provided queries' details '''
def get_sipg(focus_path, _from, to, subject_path, subject_files, save_as):

    # multithreading thread to make blast faster

    s = []
    i = []
    p = []
    g = []

    partitions = []
    tmp_p = []
    output = []
    output_xml = []
    # Max number of threads
    thread_max = 5 # Default to 5 threads at most
    for a in range(0, subject_files.__len__()):
        if tmp_p.__len__() == thread_max:
            partitions.append(tmp_p)
            tmp_p = []
        tmp_p.append(a)
    if tmp_p.__len__() != 0:
        partitions.append(tmp_p)
    for a in range(0, partitions.__len__()):
        spool = []
        spool_xml = []
        for index in partitions[a]:
            t = retThread(target=blastp, args=["tmp/focus_peptides.faa", subject_path+"/"+subject_files[index], 0.001])
            t_xml = retThread(target=blastp_xml, args=["tmp/focus_peptides.faa", subject_path+"/"+subject_files[index], 0.001])
            t.start()
            t_xml.start()
            spool.append(t)
            spool_xml.append(t_xml)
        for b in range(0, spool.__len__()):
            output.append(spool[b].join())
            output_xml.append(spool_xml[b].join())
    # Runs through all threads at once, DO NOT IMPLEMENT AT ALL
    # Can be useful for powerful computers, but that's only if there is enough interest
    '''
    spool = []
    spool_xml = []
    output = []
    output_xml = []
    for a in range(0, subject_files.__len__()):
        t = retThread(target=blastp, args=["tmp/focus_peptides.faa", subject_path+"/"+subject_files[a], 0.001])
        t_xml = retThread(target=blastp_xml, args=["tmp/focus_peptides.faa", subject_path+"/"+subject_files[a], 0.001])
        t.start()
        t_xml.start()
        spool.append(t)
        spool_xml.append(t_xml)
    for a in range(0, subject_files.__len__()):
        output.append(spool[a].join())
        output_xml.append(spool_xml[a].join())
    '''
    for a in range(0, subject_files.__len__()):
        st = []
        it = []
        pt = []
        gt = []
        (stdout, stderr) = output[a]
        (stdout_xml, stderr_xml) = output_xml[a]
        if stderr != "":
            print(stderr)
            # return ("ERROR", stderr)
        elif stderr_xml != "":
            print(stderr_xml)
            # return ("ERROR", stderr_xml)
        stdout = stdout.split('\n')
        stdout_xml = stdout_xml.split('\n')
        aw = open("tmp/all_blastp.txt", "a")
        ax = open("tmp/all_blastp.xml", "a")
        if a != 0:
            aw.write("\n")
            ax.write("\n")
        ax.write("<!-- ")
        for _ in range(0, 100):
            aw.write("*")
        aw.write("\n")
        aw.write("query=" + focus_path + "(" + str(_from) + "," + str(to) + "), subject_path=" + subject_path + ", subject_files=" + subject_files[a] + ", save_as=" + save_as)
        aw.write("\n")
        ax.write("query=" + focus_path + "(" + str(_from) + "," + str(to) + "), subject_path=" + subject_path + ", subject_files=" + subject_files[a] + ", save_as=" + save_as)
        ax.write(" -->")
        for _ in range(0, 100):
            aw.write("*")
        aw.write("\n\n")
        ax.write("\n\n")
        mode = False
        for b in range(0, stdout.__len__()):
            aw.write(stdout[b])
            if b+1 != stdout.__len__():
                aw.write('\n')
            if stdout[b].__contains__("Query="):
                mode = True
                continue
            if mode and stdout[b].__contains__("***** No hits found *****"):
                st.append(-1)
                it.append(-1)
                pt.append(-1)
                gt.append(-1)
                mode = False
            elif mode and stdout[b].__contains__("Score ="):
                tmp = stdout[b].split(',')
                score = float(tmp[0].split(' ')[3])
                tmp = stdout[b+1].split(',')
                tmp2 = tmp[0].split(' ')[3].split('/')
                id = float(tmp2[0])/float(tmp2[1])
                tmp2 = tmp[1].split(' ')[3].split('/')
                positive = float(tmp2[0])/float(tmp2[1])
                tmp2 = tmp[2].split(' ')[3].split('/')
                gap = float(tmp2[0])/float(tmp2[1])
                st.append(score)
                it.append(id)
                pt.append(positive)
                gt.append(gap)
                mode = False
        s.append(st)
        i.append(it)
        p.append(pt)
        g.append(gt)
        for c in range(0, stdout_xml.__len__()):
            ax.write(stdout_xml[c])
            if c+1 != stdout_xml.__len__():
                ax.write("\n")
    aw.close()
    ax.close()
    return ("SUCCESS", (s, i, p, g))

''' Execute the function above, but does the data processing and packaging and neatly ties it all into one function '''
def massblastp(focus_path, _from, to, subject_path, subject_files, save_as, notify):

    clean_up()
    peptides_OI = extract_peptides(focus_path, _from, to)
    w = open("tmp/focus_peptides.faa", "w")
    for peptide in peptides_OI:
        w.write(">" + peptide)
    w.close()
    clear = open("tmp/all_blastp.txt", "w")
    clear.close()
   
    (status, returned) = get_sipg(focus_path, _from, to, subject_path, subject_files, save_as)
    if status == "ERROR":
        return (status, "Issue while doing individual blasts. Ensure subject files are proper protein fasta files.")
    else: 
        s, i, p, g = returned

    rMB = open("tmp/all_blastp.txt")
    allMB = []
    for a in range(0, subject_files.__len__()):
        allMB.append("")
    mode = 3
    index = -1
    for line in rMB.readlines():
        if line.__contains__("********************") and mode == 3:
            mode = 1
            index += 1
            continue
        elif mode == 1:
            mode = 2
            continue
        elif line.__contains__("********************") and mode == 2:
            mode = 3
        elif mode == 3:
            allMB[index] += line
    rMB.close()
    
    query = allMB[0].split('\n')
    peptideOI = []
    for a in range(0, query.__len__()):
        if query[a].__contains__('Query='):
            toAdd = query[a]
            if not query[a].__contains__(']'):
                toAdd += query[a + 1]
            toAdd += '\n'
            peptideOI.append(toAdd)
    allPeptides = []
    for a in range(0, peptideOI.__len__()):
        tmp2 = []
        for b in range(0, allMB.__len__()):
            lines = allMB[b].split('Query=')[a + 1].split('\n')
            tmp = []
            for c in range(1, lines.__len__()):
                if lines[c].__contains__('> '):
                    toAppend = lines[c]
                    if not toAppend.__contains__(']'):
                        toAppend += lines[c + 1]
                    tmp.append(toAppend.replace('\n', ' '))
            if tmp.__len__() == 0:
                tmp2.append(['***** No hits found *****'])
            else:
                tmp2.append(tmp)
        allPeptides.append(tmp2)
    
    wS = open("tmp/score.csv", "w")
    wI = open("tmp/id.csv", "w")
    wP = open("tmp/positive.csv", "w")
    wG = open("tmp/gap.csv", "w")
    wF = open("tmp/frequency.csv", "w")
    wA = open("tmp/peptide.csv", "w")
    # wB = open("tmp/link.csv", "w")

    def write(input):

        wS.write(input)
        wI.write(input)
        wP.write(input)
        wG.write(input)
        wF.write(input)
        wA.write(input)
        # wB.write(input)

    toWrite = '-,'
    for a in range(_from, to + 1):
        toWrite += str(a) + ','
    toWrite += "-\n"
    write(toWrite)
    for a in range(0, subject_files.__len__()):
        write(subject_files[a] + ',')
        for b in range(0, s[a].__len__()):
            wS.write(str(s[a][b]) + ',')
            wI.write(str(i[a][b]) + ',')
            wP.write(str(p[a][b]) + ',')
            wG.write(str(g[a][b]) + ',')
            if allPeptides[b][a] == ['***** No hits found *****']:
                wF.write('0,')
                wA.write('0,')
                # wB.write('0,')
            else:
                wF.write(str(allPeptides[b][a].__len__()) + ',')
                toWriteA = ''
                # toWriteB = ''
                for c in range(0, allPeptides[b][a].__len__()):
                    toWriteA += allPeptides[b][a][c]
                    # toWriteB += 'https://www.ncbi.nlm.nih.gov/protein/' + allPeptides[b][a][c].split(' ')[1]
                    if c != allPeptides[b][a].__len__() - 1:
                        toWriteA += ' | '
                        # toWriteB += ' | '
                if toWriteA.__contains__(','):
                    toWriteA = toWriteA.replace(',', '')
                # if toWriteB.__contains__(','):
                    # toWriteB = toWriteB.replace(',', '')
                wA.write(toWriteA + ',')
                # wB.write(toWriteB + ',')
        write("\n")
    wS.close()
    wI.close()
    wP.close()
    wG.close()
    wF.close()
    wA.close()
    # wB.close()

    create_workbook()
    create_zip(save_as)
    clean_up("./tmp2")
    clean_up()

    if notify:
        messagebox.showinfo("Query Completed", "Query under the name of " + save_as + " has been completed.")

    return 1

''' Record history of queries '''
def add_history(focus_path, _from, to, subject_path, subject_files, save_as, local):
    
    sub_files = str(subject_files).replace(', ', '|').replace("'", "")
    current = [focus_path, _from, to, subject_path, sub_files, save_as, local]
    history = []
    r = open("metadata/history.csv")
    for line in r.readlines():
        line = line.replace("\n", "").split(", ")
        history.append(line)
    r.close()
    added = False
    for a in range(0, history.__len__()):
        if history[a][-2] == save_as:
            history[a] = current
            added = True
    if not added:
        history.append(current)
    to_write = ""
    for a in range(0, history.__len__()):
        for b in range(0, history[a].__len__()):
            to_write += str(history[a][b]).replace("\r", "").replace("\n", "")
            if b+1 != history[a].__len__():
                to_write += ", "
        to_write += "\n"
    if to_write[-1] == "\n":
        to_write = to_write[:-1]
    w = open("metadata/history.csv", "w")
    w.write(to_write)
    w.close()

''' Read and store history in a formatted list '''
def get_history():

    r = open("metadata/history.csv")
    history = []
    for line in r.readlines():
        line = line.replace("\n", "").split(", ")
        data = {
            "focus_path" :  line[0],
            "from" : line[1],
            "to" : line[2], 
            "subject_folder" : line[3],
            "subject_files" : line[4].replace("[", "").replace("]", "").split("|"),
            "save_as" : line[5],
            "source" : line[6]
        }
        history.append(data)
    r.close()
    return history

''' Same as get_sipg(), but instead it is for the correlation HM '''
def corr_blastp(seqs, seq_names, viewing_path):

    for a in range(0, seqs.__len__()):
        w = open("tmp2/"+viewing_path+"-"+str(a)+".faa", "w")
        w.write(seq_names[a]+"\n")
        w.write(seqs[a])
        w.close()
    s = []
    i = []
    p = []
    g = []
    reports = []
    for a in range(0, seqs.__len__()):
        s.append([])
        i.append([])
        p.append([])
        g.append([])
        reports.append([])
        for b in range(0, seqs.__len__()):
            s[a].append(0)
            i[a].append(0)
            p[a].append(0)
            g[a].append(0)
            reports[a].append("")
    for a in range(0, seqs.__len__()):
        for b in range(0, seqs.__len__()):
            this_blast = blastp("tmp2/"+viewing_path+"-"+str(a)+".faa", "tmp2/"+viewing_path+"-"+str(b)+".faa", 0.001)[0]
            reports[a][b] = ""
            this_blast = this_blast.split("\n")
            mode = False
            for c in range(0, this_blast.__len__()):
                if not mode and this_blast[c].__contains__("Query= "):
                    reports[a][b] += str(this_blast[c]) + "\n"
                    mode = True
                    continue
                if mode:
                    reports[a][b] += str(this_blast[c])
                    if this_blast[c].__contains__("Effective search space used:"):
                        break
                    else:
                        reports[a][b] += "\n"
                    if this_blast[c].__contains__("Score") and this_blast[c].__contains__("Expect"):
                        this_ln = this_blast[c]
                        while this_ln.__contains__("  "):
                            this_ln = this_ln.replace("  ", " ")
                        this_ln = this_ln.split(" ")
                        s[a][b] = float(this_ln[3])
                        nxt_ln = this_blast[c+1]
                        while nxt_ln.__contains__("  "):
                            nxt_ln = nxt_ln.replace("  ", " ")
                        nxt_ln = nxt_ln.split(" ")
                        i[a][b] = float(nxt_ln[3].split("/")[0]) / float(nxt_ln[3].split("/")[1])
                        p[a][b] = float(nxt_ln[7].split("/")[0]) / float(nxt_ln[7].split("/")[1])
                        g[a][b] = float(nxt_ln[11].split("/")[0]) / float(nxt_ln[11].split("/")[1])
                    elif this_blast[c].__contains__("***** No hits found *****"):
                        s[a][b] = -1
                        i[a][b] = -1
                        p[a][b] = -1
                        g[a][b] = -1
    for a in range(0, seqs.__len__()):
        os.remove("tmp2/"+viewing_path+"-"+str(a)+".faa")
    return s, i, p, g, reports
    