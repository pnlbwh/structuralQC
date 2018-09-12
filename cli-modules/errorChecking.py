def EXIT(msg):
    print(msg)
    exit(1)


def keyPrompt():

    while 1:
        sanity= input('[y/n] : ')
        if sanity=='n':
            EXIT('Program exiting ...')
        elif sanity=='y':
            print("Program will continue ...")
            break
        else:
            continue


def errorChecking(subjects, cases):

    # error checking
    if len(subjects)!=len(cases):
        EXIT("The number of given and predicted cases are not equal")

    if len(cases)!= len(set(cases)) or len(subjects)!= len(set(subjects)):
        EXIT("Possible case duplication in caselist or visual_qc file")

    # cases might be in different order than subjects
    for s in subjects:

        try:
            ind= cases.index(s)
        except ValueError:
            EXIT("Case missing, compare the caselist.txt and visual_qc.xlsx")