import argparse
import subprocess


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
    # mutator goes here
    counter = process_run(file, args, plain, logFile, counter)

    return


def random(file, seed, logFile):
    # randomly adds chars to the seed input

    args, plain = seed_parse(seed)
    counter = 0
    # mutator goes here
    counter = process_run(file, args, plain, logFile, counter)

    return


def special(file, seed, logFile):
    # randomly adds special characters and normal chars to the seed input

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
