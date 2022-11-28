import argparse
import subprocess
import random
import string


def main():
    # init startup, parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-testFile', type=str, help='Choose a c executable to test from /testfiles')
    parser.add_argument('-method', type=str, help='Choose a method to test (Iter, Random, Special)')
    parser.add_argument('-seed', type=str, help='Choose a seed input to test on the executable')

    args = parser.parse_args()

    # test the testFile arg
    try:
        test = open('../testfiles/' + args.testFile)
        test.close()
        test = ('../testfiles/' + args.testFile)
    except:
        print('Invalid test file!')

    # test the seed file arg
    try:
        seed = open('../seeds/' + args.seed)
        seed.close()
        seed = ('../seeds/' + args.seed)
    except:
        print('Invalid seed file!')

    # test and execute the method arg
    logFile = open('../logs/log.txt', 'w')
    if args.method == 'Iter':
        iterator(test, seed, logFile)
    elif args.method == 'Random':
        random(test, seed, logFile)
    elif args.method == 'Special':
        special(test, seed, logFile)
    else:
        print('Invalid method!')
    logFile.close()


# now the hard part, the fuzzer methods
def iterator(file, seed, logFile):
    # this one just continuously adds to the seed split by \ns, then adds to a blank seed using /n as a divider
    # does the same thing to args

    args, plain = seed_parse(seed)
    counter = 0
    # execute seed
    counter = process_run(file, args, plain, logFile, counter)
    # generate list of mutated plain text and args
    for x in range(0, 5):
        plain = plain + ' '
    length = len(plain)
    print(plain)
    mutated_plain = mutate_i(plain, length, [], 1, file, args, logFile, counter)
    for x in mutated_plain:
        mutated_plain = mutate_i(x, length, mutated_plain, 0, file, args, logFile, counter)


    return


def mutate_i(innie, i, listy, appender, file, args, logFile, counter):
    # generates a list of all mutated inputs
    # base case
    if i == -1:
        return listy
    for character in range(32, 126):

        text = innie[:i] + chr(character) + innie[i:]
        #print(text)
        if appender == 0:
            counter = process_run(file, args, text, logFile, counter)
        else:
            listy.append(text)
    listy = mutate_i(innie, i - 1, listy, appender, file, args, logFile, counter)

    return listy


def random(file, seed, logFile):
    # randomly adds chars to the seed input

    args, plain = seed_parse(seed)
    counter = 0
    for x in range(0, len(plain)):
        letters = string.ascii_uppercase + string.punctuation + string.digits + string.ascii_lowercase
        random_string = plain + ''.join(random.choice(letters) for i in range(len(plain) + 10))
        counter = process_run(file, args, random_string, logFile, counter)

    return


def special(file, seed, logFile):
    # randomly creates strings to pass as input

    args, plain = seed_parse(seed)
    counter = 0
    # mutator goes here
    counter = process_run(file, args, plain, logFile, counter)

    return


def process_run(file, args, plain, logFile, counter):
    # executes the test file with args and plain input
    run = subprocess.Popen([file, args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if plain != '':
        out, err = run.communicate(input=plain.encode('utf-8'))
    else:
        out, err = run.communicate()

    # log output
    logFile.write('Run ' + str(counter) + '\n')
    logFile.write('Out: ' + out.decode() + '\n')
    logFile.write('Err: ' + err.decode() + '\n')
    if plain != '':
        logFile.write('In: ' + plain + '\n')
    if args != '':
        logFile.write('Args: ' + args + '\n')
    counter += 1
    return counter


def seed_parse(seed):
    # parses the seed file, returns the cmd args and text prompt inputs
    file = open(seed)
    lines = file.readlines()

    args = ''
    plain = ''
    for line in lines:
        if 'arg' in line:
            args = args + line[5:]
        else:
            plain = plain + line + '\n'
    return args, plain


if __name__ == '__main__':
    main()
