import argparse
import subprocess
import random
import string

WORD = ''
counter = 0


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
        random_(test, seed, logFile)
    elif args.method == 'Special':
        special_(test, seed, logFile)
    else:
        print('Invalid method!')
    logFile.close()


# now the hard part, the fuzzer methods
def iterator(file, seed, logFile):
    # this one just continuously adds to the seed split by \ns, then adds to a blank seed using /n as a divider
    # does the same thing to args

    args, plain = seed_parse(seed)
    global WORD
    WORD = plain
    # execute seed
    process_run(file, args, plain, logFile)
    # generate list of mutated plain text and args

    print(plain)
    while True:
        mutate_i2(0, file, args, logFile)

    return


def mutate_i2(index, file, args, logFile):
    # this mutation function actually works
    global WORD
    text = WORD
    process_run(file, args, text, logFile)
    if ord(WORD[index]) == 127:
        WORD = WORD[:index] + chr(0) + WORD[index + 1:]
        mutate_i2(index + 1, file, args, logFile)
    else:
        WORD = WORD[:index] + chr(ord(WORD[index]) + 1) + WORD[index + 1:]


def mutate_i(innie, i, listy, appender, file, args, logFile):
    """THIS MUTATOR IS BROKEN, DO NOT USE"""
    # generates a list of all mutated inputs
    # base case
    if i == -1:
        return listy
    for character in range(0, 126):

        text = innie[:i] + chr(character) + innie[i:]
        # print(text)
        if appender == 0:
            process_run(file, args, text, logFile)
        else:
            listy.append(text)
    listy = mutate_i(innie, i - 1, listy, appender, file, args, logFile)

    return listy


def random_(file, seed, logFile):
    # randomly adds chars to the seed input
    special = '[\n \r\0]'
    args, plain = seed_parse(seed)
    process_run(file, args, plain, logFile)
    letters = string.ascii_uppercase + string.punctuation + string.digits + string.ascii_lowercase + special
    tracker = 0
    it = 0
    while True:
        choice = random.choice([True, False])
        random_string = ''
        if choice:
            random_string = plain[:-1]
        random_string = random_string + ''.join(random.choice(letters) for i in range(len(plain) + it))
        process_run(file, args, random_string, logFile)
        if tracker == 32:
            tracker = 0
            it += 1
        tracker +=1
    return


def special_(file, seed, logFile):
    # randomly creates strings to pass as input

    args, plain = seed_parse(seed)
    # mutator goes here
    process_run(file, args, plain, logFile)

    return


def process_run(file, args, plain, logFile):
    # executes the test file with args and plain input
    global counter
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
