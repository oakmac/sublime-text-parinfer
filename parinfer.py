## Parinfer.py - a Parinfer implementation in Python
## v0.4.0
## https://github.com/oakmac/parinfer.py
##
## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/
##
## Copyright (c) 2015, Chris Oakman and other contributors
## Released under the ISC license
## https://github.com/oakmac/parinfer.py/blob/master/LICENSE.md

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

BACKSLASH = '\\'
COMMA = ','
DOUBLE_QUOTE = '"'
NEWLINE = '\n'
SEMICOLON = ';'
TAB = '\t'

PARENS = {
    '{': '}',
    '}': '{',
    '[': ']',
    ']': '[',
    '(': ')',
    ')': '(',
}

#-------------------------------------------------------------------------------
# Result Structure
#-------------------------------------------------------------------------------

def initialResult():
    """Returns a dictionary of the initial state."""
    return {
        'lines': [],
        'lineNo': -1,
        'ch': '',
        'x': 0,
        'stack': [],
        'backup': [],
        'insert': {'lineNo': None, 'x': None},
        'parenTrail': {'start': None, 'end': None},
        'cursorX': None,
        'cursorLine': None,
        'cursorDx': None,
        'quoteDanger': False,
        'trackIndent': False,
        'cursorInComment': False,
        'quit': False,
        'process': False,
        'success': False,
        'maxIndent': None,
        'indentDelta': 0,
    }

#-------------------------------------------------------------------------------
# String Operations
#-------------------------------------------------------------------------------

def insertString(orig, idx, insert):
    return orig[:idx] + insert + orig[idx:]

def replaceStringRange(orig, start, end, replace):
    return orig[:start] + replace + orig[end:]

def removeStringRange(orig, start, end):
    return orig[:start] + orig[end:]

#-------------------------------------------------------------------------------
# Reader Operations
#-------------------------------------------------------------------------------

def isOpenParen(c):
    return c == "{" or c == "(" or c == "["

def isCloseParen(c):
    return c == "}" or c == ")" or c == "]"

def isWhitespace(c):
    return c == " " or c == TAB or c== NEWLINE

#-------------------------------------------------------------------------------
# Stack States
#-------------------------------------------------------------------------------

# Returns the next-to-last element in the stack, or null if the stack is empty.
def peek(stack, i):
    idx = len(stack) - i;

    # return null if the index is out of range
    if idx < 0:
        return None

    return stack[idx]

def getPrevCh(stack, i):
    e = peek(stack, i)
    if e == None:
        return None
    return e['ch']

def isEscaping(stack):
    return getPrevCh(stack, 1) == BACKSLASH

def prevNonEscCh(stack):
    i = 1
    if isEscaping(stack):
        i = 2
    return getPrevCh(stack, i)

def isInStr(stack):
    return prevNonEscCh(stack) == DOUBLE_QUOTE

def isInComment(stack):
    return prevNonEscCh(stack) == SEMICOLON

def isInCode(stack):
    return (not isInStr(stack) and not isInComment(stack))

def isValidCloser(stack, ch):
    return getPrevCh(stack, 1) == PARENS[ch]

#-------------------------------------------------------------------------------
# Stack Operations
#-------------------------------------------------------------------------------

def pushOpen(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()
        return
    if isInCode(stack):
        stack.append({
            'ch': result['ch'],
            'indentDelta': result['indentDelta'],
            'x': result['x'],
        })

def pushClose(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()
        return

    backup = result['backup']
    ch = result['ch']
    if isInCode(stack):
        if isValidCloser(stack, ch):
            opener = stack.pop()
            result['maxIndent'] = opener['x']
            backup.append(opener)
        else:
            # erase non-matched paren
            result['ch'] = ""

def pushTab(result):
    if not isInStr(result['stack']):
        result['ch'] = "  "

def pushSemicolon(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()
        return
    if isInCode(stack):
        stack.append({
            'ch': result['ch'],
            'x': result['x'],
        })

def pushNewline(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()
    if isInComment(stack):
        stack.pop()
    result['ch'] = ""

def pushEscape(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()
    else:
        stack.append({
            'ch': result['ch'],
            'x': result['x'],
        })

def pushQuote(result):
    stack = result['stack']
    if isEscaping(stack) or isInStr(stack):
        stack.pop()
        return
    if isInComment(stack):
        result['quoteDanger'] = not result['quoteDanger']
        return
    # default case
    stack.append({
        'ch': result['ch'],
        'x': result['x'],
    })

def pushDefault(result):
    stack = result['stack']
    if isEscaping(stack):
        stack.pop()

def pushChar(result):
    ch = result['ch']
    if isOpenParen(ch):
        pushOpen(result)
        return
    if isCloseParen(ch):
        pushClose(result)
        return
    if ch == TAB:
        pushTab(result)
        return
    if ch == SEMICOLON:
        pushSemicolon(result)
        return
    if ch == NEWLINE:
        pushNewline(result)
        return
    if ch == BACKSLASH:
        pushEscape(result)
        return
    if ch == DOUBLE_QUOTE:
        pushQuote(result)
        return
    # default case
    pushDefault(result)

#-------------------------------------------------------------------------------
# Indent Mode Operations
#-------------------------------------------------------------------------------

def closeParens(result, indentX):
    if indentX == None:
        indentX = 0

    stack = result['stack']
    parens = ""

    while len(stack) > 0:
        opener = peek(stack, 1)
        if opener['x'] >= indentX:
            stack.pop()
            parens = parens + PARENS[opener['ch']]
        else:
            break

    insertLineNo = result['insert']['lineNo']
    newString = insertString(result['lines'][insertLineNo],
                             result['insert']['x'],
                             parens)
    result['lines'][insertLineNo] = newString

def updateParenTrail(result):
    ch = result['ch']
    stack = result['stack']
    closeParen = isCloseParen(ch)
    escaping = isEscaping(stack)
    inCode = isInCode(stack)

    shouldPass = (ch == SEMICOLON or
                  ch == COMMA or
                  isWhitespace(ch) or
                  closeParen)

    shouldReset = (inCode and
                   (escaping or not shouldPass))

    result['cursorInComment'] = (result['cursorInComment'] or
                                 (result['cursorLine'] == result['lineNo'] and
                                  result['x'] == result['cursorX'] and
                                  isInComment(stack)))

    shouldUpdate = (inCode and
                    not escaping and
                    closeParen and
                    isValidCloser(stack, ch))

    if shouldReset:
        result['backup'] = []
        result['parenTrail'] = {'start': None, 'end': None}
        result['maxIndent'] = None
    elif shouldUpdate:
        if result['parenTrail']['start'] == None:
            result['parenTrail']['start'] = result['x']
        result['parenTrail']['end'] = result['x'] + 1

def blockParenTrail(result):
    start = result['parenTrail']['start']
    end = result['parenTrail']['end']
    isCursorBlocking = (result['lineNo'] == result['cursorLine'] and
                        start != None and
                        result['cursorX'] > start and
                        not result['cursorInComment'])

    if start != None and isCursorBlocking:
        start = max(start, result['cursorX'])

    if end != None and isCursorBlocking:
        end = max(end, result['cursorX'])

    if start == end:
        start = None
        end = None

    result['parenTrail']['start'] = start
    result['parenTrail']['end'] = end

def removeParenTrail(result):
    start = result['parenTrail']['start']
    end = result['parenTrail']['end']

    if start == None or end == None:
        return

    stack = result['stack']
    backup = result['backup']

    line = result['lines'][result['lineNo']]
    removeCount = 0
    for i in range(start, end):
        if isCloseParen(line[i]):
            removeCount = removeCount + 1

    ignoreCount = len(backup) - removeCount
    while ignoreCount != len(backup):
        stack.append(backup.pop())

    result['lines'][result['lineNo']] = removeStringRange(line, start, end)

    if result['insert']['lineNo'] == result['lineNo']:
        result['insert']['x'] = min(result['insert']['x'], start)

def updateInsertionPt(result):
    line = result['lines'][result['lineNo']]
    prevChIdx = result['x'] - 1
    prevCh = None
    if prevChIdx >= 0:
        prevCh = line[prevChIdx]
    ch = result['ch']

    shouldInsert = (isInCode(result['stack']) and
                    ch != "" and
                    (not isWhitespace(ch) or prevCh == BACKSLASH) and
                    (not isCloseParen(ch) or result['lineNo'] == result['cursorLine']))

    if shouldInsert:
        result['insert'] = {
            'lineNo': result['lineNo'],
            'x': result['x'] + 1,
        }

def processIndentTrigger(result):
    closeParens(result, result['x'])
    result['trackIndent'] = False

def processIndent(result):
    stack = result['stack']
    ch = result['ch']
    checkIndent = (result['trackIndent'] and
                   isInCode(stack) and
                   not isWhitespace(ch) and
                   ch != SEMICOLON)
    skip = (checkIndent and isCloseParen(ch))
    atIndent = (checkIndent and not skip)
    quit = (atIndent and result['quoteDanger'])

    result['quit'] = quit
    result['process'] = (not skip and not quit)

    if atIndent and not quit:
        processIndentTrigger(result)

def updateLine(result, origCh):
    ch = result['ch']
    if origCh != ch:
        lineNo = result['lineNo']
        line = result['lines'][lineNo]
        result['lines'][lineNo] = replaceStringRange(line, result['x'], result['x'] + len(origCh), ch)

def processChar(result, ch):
    origCh = ch
    result['ch'] = ch
    processIndent(result)

    if result['quit']:
        return

    if result['process']:
        # NOTE: the order here is important!
        updateParenTrail(result)
        pushChar(result)
        updateInsertionPt(result)
    else:
        result['ch'] = ""

    updateLine(result, origCh)
    result['x'] = result['x'] + len(result['ch'])

def processLine(result, line):
    stack = result['stack']

    result['lineNo'] = result['lineNo'] + 1
    result['backup'] = []
    result['cursorInComment'] = False
    result['parenTrail'] = {'start': None, 'end': None}
    result['trackIndent'] = (len(stack) > 0 and not isInStr(stack))
    result['lines'].append(line)
    result['x'] = 0

    chars = line + NEWLINE
    for ch in chars:
        processChar(result, ch)
        if result['quit']:
            break

    if result['quit'] == False:
        blockParenTrail(result)
        removeParenTrail(result)

def finalizeResult(result):
    stack = result['stack']
    result['success'] = (not isInStr(stack) and
                         not result['quoteDanger'])
    if result['success'] and len(stack) > 0:
        closeParens(result, None)

def processText(text, options):
    result = initialResult()

    if isinstance(options, dict):
        if 'cursorLine' in options:
            result['cursorLine'] = options['cursorLine']
        if 'cursorX' in options:
            result['cursorX'] = options['cursorX']

    lines = text.split(NEWLINE)
    for line in lines:
        processLine(result, line)
        if result['quit']:
            break

    finalizeResult(result)
    return result

def formatText(text, options):
    result = processText(text, options)
    outText = text
    if result['success']:
        outText = NEWLINE.join(result['lines'])
    return {
        'text': outText,
        'success': result['success'],
    }

#-------------------------------------------------------------------------------
# Paren Mode Operations
# NOTE: Paren Mode re-uses some Indent Mode functions
#-------------------------------------------------------------------------------

def appendParenTrail(result):
    opener = result['stack'].pop()
    closeCh = PARENS[opener['ch']]
    result['maxIndent'] = opener['x']
    idx = result['insert']['lineNo']
    line = result['lines'][idx]
    result['lines'][idx] = insertString(line, result['insert']['x'], closeCh)
    result['insert']['x'] = result['insert']['x'] + 1

def minIndent(x, result):
    opener = peek(result['stack'], 1)
    if opener != None:
        startX = opener['x']
        return max(startX + 1, x)
    return x

def minDedent(x, result):
    if result['maxIndent'] != None:
        return min(result['maxIndent'], x)
    return x

def correctIndent(result):
    opener = peek(result['stack'], 1)
    delta = 0
    if opener != None and opener['indentDelta'] != None:
        delta = opener['indentDelta']

    newX1 = result['x'] + delta
    newX2 = minIndent(newX1, result)
    newX3 = minDedent(newX2, result)

    result['indentDelta'] = result['indentDelta'] + newX3 - result['x']

    if newX3 != result['x']:
        indentStr = ""
        for i in range(0, newX3):
            indentStr = indentStr + " "
        line = result['lines'][result['lineNo']]
        newLine = replaceStringRange(line, 0, result['x'], indentStr)
        result['lines'][result['lineNo']] = newLine
        result['x'] = newX3

    result['trackIndent'] = False
    result['maxIndent'] = None

def handleCursorDelta(result):
    hasCursorDelta = (result['cursorLine'] == result['lineNo'] and
                      result['cursorX'] == result['x'] and
                      result['cursorX'] != None)
    if hasCursorDelta and result['cursorDx'] != None:
        result['indentDelta'] = result['indentDelta'] + result['cursorDx']

def processIndent_paren(result):
    ch = result['ch']
    stack = result['stack']
    closeParen = isCloseParen(ch)

    checkIndent = (result['trackIndent'] and
                   isInCode(stack) and
                   not isWhitespace(ch) and
                   result['ch'] != SEMICOLON)

    atValidCloser = (checkIndent and
                     closeParen and
                     isValidCloser(stack, ch))

    isCursorHolding = (result['lineNo'] == result['cursorLine'] and
                       result['cursorX'] != None and
                       result['cursorX'] <= result['x'])

    shouldMoveCloser = (atValidCloser and
                        not isCursorHolding)

    skip = (checkIndent and
            closeParen and
            not isCursorHolding)

    atIndent = (checkIndent and not skip)
    quit = (atIndent and result['quoteDanger'])

    result['quit'] = quit
    result['process'] = (not skip)

    if quit:
        return

    if shouldMoveCloser:
        appendParenTrail(result)

    handleCursorDelta(result)

    if atIndent:
        correctIndent(result)

def processChar_paren(result, ch):
    origCh = ch
    result['ch'] = ch
    processIndent_paren(result)

    if result['quit']:
        return
    if result['process']:
        # NOTE: the order here is important!
        updateParenTrail(result)
        pushChar(result)
        updateInsertionPt(result)
    else:
        result['ch'] = ""

    updateLine(result, origCh)
    result['x'] = result['x'] + len(result['ch'])

def formatParenTrail(result):
    start = result['parenTrail']['start']
    end = result['parenTrail']['end']

    if start == None or end == None:
        return

    line = result['lines'][result['lineNo']]
    newTrail = ""
    spaceCount = 0
    for i in range(start, end):
        if isCloseParen(line[i]):
            newTrail = newTrail + line[i]
        else:
            spaceCount = spaceCount + 1

    if spaceCount > 0:
        result['lines'][result['lineNo']] = replaceStringRange(line, start, end, newTrail)
        end = end - spaceCount

    if result['insert']['lineNo'] == result['lineNo']:
        result['insert']['x'] = end

def processLine_paren(result, line):
    result['lineNo'] = result['lineNo'] + 1
    result['backup'] = []
    result['cursorInComment'] = False
    result['parenTrail'] = {'start': None, 'end': None}
    result['trackIndent'] = (not isInStr(result['stack']))
    result['lines'].append(line)
    result['x'] = 0
    result['indentDelta'] = 0

    chars = line + NEWLINE
    for ch in chars:
        processChar_paren(result, ch)
        if result['quit']:
            break

    if not result['quit']:
        formatParenTrail(result)

def finalizeResult_paren(result):
    result['success'] = (len(result['stack']) == 0 and
                         not result['quoteDanger'])

def processText_paren(text, options):
    result = initialResult()

    if isinstance(options, dict):
        if 'cursorDx' in options:
            result['cursorDx'] = options['cursorDx']
        if 'cursorLine' in options:
            result['cursorLine'] = options['cursorLine']
        if 'cursorX' in options:
            result['cursorX'] = options['cursorX']

    lines = text.split(NEWLINE)
    for line in lines:
        processLine_paren(result, line)
        if result['quit']:
            break

    finalizeResult_paren(result)
    return result

def formatText_paren(text, options):
    result = processText_paren(text, options)
    outText = text
    if result['success']:
        outText = NEWLINE.join(result['lines'])
    return {
        'text': outText,
        'success': result['success'],
    }

#-------------------------------------------------------------------------------
# Public API
#-------------------------------------------------------------------------------

def indent_mode(in_text, options):
    return formatText(in_text, options)

def paren_mode(in_text, options):
    return formatText_paren(in_text, options)
