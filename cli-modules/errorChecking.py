import glob, sys

def EXIT(msg):
    raise RuntimeError(msg)


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


def globCheck(filepath):
    temp = glob.glob(filepath)

    if len(temp) > 1:
        EXIT(f"Multiple images found with the provided suffix at {filepath}, make that unique, and try again.")
    elif len(temp) == 0:
        EXIT(f"No image found with the provided suffix at {filepath}. Make the suffix general and try again.")
    else:
        return temp