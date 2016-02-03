## Parinfer.py - a Parinfer implementation in Python
## v0.7.0
## https://github.com/oakmac/parinfer.py
##
## More information about Parinfer can be found here:
## http://shaunlebron.github.io/parinfer/
##
## Copyright (c) 2015, Chris Oakman and other contributors
## Released under the ISC license
## https://github.com/oakmac/parinfer.py/blob/master/LICENSE.md

import re

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

INDENT_MODE = 'INDENT_MODE'
PAREN_MODE = 'PAREN_MODE'

BACKSLASH = '\\'
BLANK_SPACE = ' '
DOUBLE_SPACE = '  '
DOUBLE_QUOTE = '"'
NEWLINE = '\n'
SEMICOLON = ';'
TAB = '\t'

LINE_ENDING_REGEX = re.compile(r"\r?\n")

CLOSE_PARENS = frozenset(['}', ')', ']'])

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

def initialResult(text, options, mode):
    """Returns a dictionary of the initial state."""
    result = {
        'mode': mode,
        'origText': text,
        'origLines': text.split(NEWLINE),
        'lines': [],
        'lineNo': -1,
        'ch': '',
        'x': 0,
        'parenStack': [],
        'parenTrail': {
            'lineNo': None,
            'startX': None,
            'endX': None,
            'openers': [],
        },
        'cursorX': None,
        'cursorLine': None,
        'cursorDx': None,
        'isInCode': True,
        'isEscaping': False,
        'isInStr': False,
        'isInComment': False,
        'commentX': None,
        'quoteDanger': False,
        'trackingIndent': False,
        'skipChar': False,
        'success': False,
        'maxIndent': None,
        'indentDelta': 0,
        'error': {
            'name': None,
            'message': None,
            'lineNo': None,
            'x': None,
        },
        'errorPosCache': {},
    }

    if isinstance(options, dict):
        if 'cursorDx' in options:
            result['cursorDx'] = options['cursorDx']
        if 'cursorLine' in options:
            result['cursorLine'] = options['cursorLine']
        if 'cursorX' in options:
            result['cursorX'] = options['cursorX']

    return result

#-------------------------------------------------------------------------------
# Possible Errors
#-------------------------------------------------------------------------------

ERROR_QUOTE_DANGER = "quote-danger"
ERROR_EOL_BACKSLASH = "eol-backslash"
ERROR_UNCLOSED_QUOTE = "unclosed-quote"
ERROR_UNCLOSED_PAREN = "unclosed-paren"
ERROR_UNHANDLED = "unhandled"

errorMessages = {}
errorMessages[ERROR_QUOTE_DANGER] = "Quotes must balanced inside comment blocks."
errorMessages[ERROR_EOL_BACKSLASH] = "Line cannot end in a hanging backslash."
errorMessages[ERROR_UNCLOSED_QUOTE] = "String is missing a closing quote."
errorMessages[ERROR_UNCLOSED_PAREN] = "Unmatched open-paren."

def cacheErrorPos(result, name, lineNo, x):
    result['errorPosCache'][name] = {'lineNo': lineNo, 'x': x}

class ParinferError(Exception):
    pass

def error(result, name, lineNo, x):
    if lineNo is None:
        lineNo = result['errorPosCache'][name]['lineNo']
    if x is None:
        x = result['errorPosCache'][name]['x']

    return {
        'parinferError': True,
        'name': name,
        'message': errorMessages[name],
        'lineNo': lineNo,
        'x': x,
    }

#-------------------------------------------------------------------------------
# String Operations
#-------------------------------------------------------------------------------

def insertWithinString(orig, idx, insert):
    return orig[:idx] + insert + orig[idx:]

def replaceWithinString(orig, start, end, replace):
    return orig[:start] + replace + orig[end:]

def removeWithinString(orig, start, end):
    return orig[:start] + orig[end:]

def repeatString(text, n):
    result = ""
    for i in range(n):
        result = result + text
    return result

# NOTE: We assume that if the CR char "\r" is used anywhere, we should use CRLF
#       line-endings after every line.
def getLineEnding(text):
    i = text.find("\r")
    if i != -1:
        return "\r\n"
    return "\n"

#-------------------------------------------------------------------------------
# Line Operations
#-------------------------------------------------------------------------------

def insertWithinLine(result, lineNo, idx, insert):
    line = result['lines'][lineNo]
    result['lines'][lineNo] = insertWithinString(line, idx, insert)

def replaceWithinLine(result, lineNo, start, end, replace):
    line = result['lines'][lineNo]
    result['lines'][lineNo] = replaceWithinString(line, start, end, replace)

def removeWithinLine(result, lineNo, start, end):
    line = result['lines'][lineNo]
    result['lines'][lineNo] = removeWithinString(line, start, end)

def initLine(result, line):
    result['x'] = 0
    result['lineNo'] = result['lineNo'] + 1
    result['lines'].append(line)

    # reset line-specific state
    result['commentX'] = None
    result['indentDelta'] = 0

def commitChar(result, origCh):
    ch = result['ch']
    if origCh != ch:
        replaceWithinLine(result, result['lineNo'], result['x'], result['x'] + len(origCh), ch)
    result['x'] = result['x'] + len(ch)

#-------------------------------------------------------------------------------
# Misc Utils
#-------------------------------------------------------------------------------

def clamp(valN, minN, maxN):
    if minN is not None:
        valN = max(minN, valN)
    if maxN is not None:
        valN = min(maxN, valN)
    return valN

def peek(arr):
    arrLen = len(arr)
    if arrLen == 0:
        return None
    return arr[arrLen - 1]

#-------------------------------------------------------------------------------
# Character Functions
#-------------------------------------------------------------------------------

def isValidCloseParen(parenStack, ch):
    if len(parenStack) == 0:
        return False
    return peek(parenStack)['ch'] == PARENS[ch]

def onOpenParen(result):
    if result['isInCode']:
        result['parenStack'].append({
            'lineNo': result['lineNo'],
            'x': result['x'],
            'ch': result['ch'],
            'indentDelta': result['indentDelta'],
        })

def onMatchedCloseParen(result):
    opener = peek(result['parenStack'])
    result['parenTrail']['endX'] = result['x'] + 1
    result['parenTrail']['openers'].append(opener)
    result['maxIndent'] = opener['x']
    result['parenStack'].pop()

def onUnmatchedCloseParen(result):
    result['ch'] = ''

def onCloseParen(result):
    if result['isInCode']:
        if isValidCloseParen(result['parenStack'], result['ch']):
            onMatchedCloseParen(result)
        else:
            onUnmatchedCloseParen(result)

def onTab(result):
    if result['isInCode']:
        result['ch'] = DOUBLE_SPACE

def onSemicolon(result):
    if result['isInCode']:
        result['isInComment'] = True
        result['commentX'] = result['x']

def onNewLine(result):
    result['isInComment'] = False
    result['ch'] = ''

def onQuote(result):
    if result['isInStr']:
        result['isInStr'] = False
    elif result['isInComment']:
        result['quoteDanger'] = not result['quoteDanger']
        if result['quoteDanger']:
            cacheErrorPos(result, ERROR_QUOTE_DANGER, result['lineNo'], result['x'])
    else:
        result['isInStr'] = True
        cacheErrorPos(result, ERROR_UNCLOSED_QUOTE, result['lineNo'], result['x'])

def onBackslash(result):
    result['isEscaping'] = True

def afterBackslash(result):
    result['isEscaping'] = False

    if result['ch'] == NEWLINE:
        if result['isInCode']:
            err = error(result, ERROR_EOL_BACKSLASH, result['lineNo'], result['x'] - 1)
            raise ParinferError(err)
        onNewLine(result)

CHAR_DISPATCH = {
    '(': onOpenParen,
    '{': onOpenParen,
    '[': onOpenParen,

    ')': onCloseParen,
    '}': onCloseParen,
    ']': onCloseParen,

    DOUBLE_QUOTE: onQuote,
    SEMICOLON: onSemicolon,
    BACKSLASH: onBackslash,
    TAB: onTab,
    NEWLINE: onNewLine,
}

def onChar(result):
    ch = result['ch']

    if result['isEscaping']:
        afterBackslash(result)
    else:
        charFn = CHAR_DISPATCH.get(ch, None)
        if charFn is not None:
            charFn(result)

    result['isInCode'] = (not result['isInComment'] and not result['isInStr'])

#-------------------------------------------------------------------------------
# Cursor Functions
#-------------------------------------------------------------------------------

def isCursorOnLeft(result):
    return (result['lineNo'] == result['cursorLine'] and
            result['cursorX'] is not None and
            result['cursorX'] <= result['x'])

def isCursorOnRight(result, x):
    return (result['lineNo'] == result['cursorLine'] and
            result['cursorX'] is not None and
            x is not None and
            result['cursorX'] > x)

def isCursorInComment(result):
    return isCursorOnRight(result, result['commentX'])

def handleCursorDelta(result):
    hasCursorDelta = (result['cursorDx'] is not None and
                      result['cursorLine'] == result['lineNo'] and
                      result['cursorX'] == result['x'])

    if hasCursorDelta:
        result['indentDelta'] = result['indentDelta'] + result['cursorDx']

#-------------------------------------------------------------------------------
# Paren Trail Functions
#-------------------------------------------------------------------------------

def updateParenTrailBounds(result):
    line = result['lines'][result['lineNo']]
    prevCh = None
    if result['x'] > 0:
        prevCh = line[result['x'] - 1]
    ch = result['ch']

    shouldReset = (result['isInCode'] and
                   ch != "" and
                   ch not in CLOSE_PARENS and
                   (ch != BLANK_SPACE or prevCh == BACKSLASH) and
                   ch != DOUBLE_SPACE)

    if shouldReset:
        result['parenTrail']['lineNo'] = result['lineNo']
        result['parenTrail']['startX'] = result['x'] + 1
        result['parenTrail']['endX'] = result['x'] + 1
        result['parenTrail']['openers'] = []
        result['maxIndent'] = None

def clampParenTrailToCursor(result):
    startX = result['parenTrail']['startX']
    endX = result['parenTrail']['endX']

    isCursorClamping = (isCursorOnRight(result, startX) and
                        not isCursorInComment(result))

    if isCursorClamping:
        newStartX = max(startX, result['cursorX'])
        newEndX = max(endX, result['cursorX'])

        line = result['lines'][result['lineNo']]
        removeCount = 0
        for i in range(startX, newStartX):
            if line[i] in CLOSE_PARENS:
                removeCount = removeCount + 1

        for i in range(removeCount):
            result['parenTrail']['openers'].pop(0)
        result['parenTrail']['startX'] = newStartX
        result['parenTrail']['endX'] = newEndX

def removeParenTrail(result):
    startX = result['parenTrail']['startX']
    endX = result['parenTrail']['endX']

    if startX == endX:
        return

    openers = result['parenTrail']['openers']
    while len(openers) != 0:
        result['parenStack'].append(openers.pop())

    removeWithinLine(result, result['lineNo'], startX, endX)

def correctParenTrail(result, indentX):
    parens = ""

    while len(result['parenStack']) > 0:
        opener = peek(result['parenStack'])
        if opener['x'] >= indentX:
            result['parenStack'].pop()
            parens = parens + PARENS[opener['ch']]
        else:
            break

    insertWithinLine(result, result['parenTrail']['lineNo'], result['parenTrail']['startX'], parens)

def cleanParenTrail(result):
    startX = result['parenTrail']['startX']
    endX = result['parenTrail']['endX']

    if (startX == endX or result['lineNo'] != result['parenTrail']['lineNo']):
        return

    line = result['lines'][result['lineNo']]
    newTrail = ""
    spaceCount = 0
    for i in range(startX, endX):
        if line[i] in CLOSE_PARENS:
            newTrail = newTrail + line[i]
        else:
            spaceCount = spaceCount + 1

    if spaceCount > 0:
        replaceWithinLine(result, result['lineNo'], startX, endX, newTrail)
        result['parenTrail']['endX'] = result['parenTrail']['endX'] - spaceCount

def appendParenTrail(result):
    opener = result['parenStack'].pop()
    closeCh = PARENS[opener['ch']]

    result['maxIndent'] = opener['x']
    insertWithinLine(result, result['parenTrail']['lineNo'], result['parenTrail']['endX'], closeCh)
    result['parenTrail']['endX'] = result['parenTrail']['endX'] + 1

def finishNewParenTrail(result):
    if result['mode'] == INDENT_MODE:
        clampParenTrailToCursor(result)
        removeParenTrail(result)
    elif result['mode'] == PAREN_MODE:
        if result['lineNo'] != result['cursorLine']:
            cleanParenTrail(result)

#-------------------------------------------------------------------------------
# Indentation functions
#-------------------------------------------------------------------------------

def correctIndent(result):
    origIndent = result['x']
    newIndent = origIndent
    minIndent = 0
    maxIndent = result['maxIndent']

    opener = peek(result['parenStack'])
    if opener is not None:
        minIndent = opener['x'] + 1
        newIndent = newIndent + opener['indentDelta']

    newIndent = clamp(newIndent, minIndent, maxIndent)

    if newIndent != origIndent:
        indentStr = repeatString(BLANK_SPACE, newIndent)
        replaceWithinLine(result, result['lineNo'], 0, origIndent, indentStr)
        result['x'] = newIndent
        result['indentDelta'] = result['indentDelta'] + newIndent - origIndent

def onProperIndent(result):
    result['trackingIndent'] = False

    if result['quoteDanger']:
        err = error(result, ERROR_QUOTE_DANGER, None, None)
        raise ParinferError(err)

    if result['mode'] == INDENT_MODE:
        correctParenTrail(result, result['x'])
    elif result['mode'] == PAREN_MODE:
        correctIndent(result)

def onLeadingCloseParen(result):
    result['skipChar'] = True
    result['trackingIndent'] = True

    if result['mode'] == PAREN_MODE:
        if isValidCloseParen(result['parenStack'], result['ch']):
            if isCursorOnLeft(result):
                result['skipChar'] = False
                onProperIndent(result)
            else:
                appendParenTrail(result)

def onIndent(result):
    if result['ch'] in CLOSE_PARENS:
        onLeadingCloseParen(result)
    elif result['ch'] == SEMICOLON:
        # comments don't count as indentation points
        result['trackingIndent'] = False
    elif result['ch'] != NEWLINE:
        onProperIndent(result)

#-------------------------------------------------------------------------------
# High-level processing functions
#-------------------------------------------------------------------------------

def processChar(result, ch):
    origCh = ch

    result['ch'] = ch
    result['skipChar'] = False

    if result['mode'] == PAREN_MODE:
        handleCursorDelta(result)

    if result['trackingIndent'] and ch != BLANK_SPACE and ch != TAB:
        onIndent(result)

    if result['skipChar']:
        result['ch'] = ""
    else:
        onChar(result)
        updateParenTrailBounds(result)

    commitChar(result, origCh)

def processLine(result, line):
    initLine(result, line)

    if result['mode'] == INDENT_MODE:
        result['trackingIndent'] = (len(result['parenStack']) != 0 and
                                    not result['isInStr'])
    elif result['mode'] == PAREN_MODE:
        result['trackingIndent'] = not result['isInStr']

    chars = line + NEWLINE
    for c in chars:
        processChar(result, c)

    if result['lineNo'] == result['parenTrail']['lineNo']:
        finishNewParenTrail(result)

def finalizeResult(result):
    if result['quoteDanger']:
        err = error(result, ERROR_QUOTE_DANGER, None, None)
        raise ParinferError(err)

    if result['isInStr']:
        err = error(result, ERROR_UNCLOSED_QUOTE, None, None)
        raise ParinferError(err)

    if len(result['parenStack']) != 0:
        if result['mode'] == PAREN_MODE:
            opener = peek(result['parenStack'])
            err = error(result, ERROR_UNCLOSED_PAREN, opener['lineNo'], opener['x'])
            raise ParinferError(err)
        elif result['mode'] == INDENT_MODE:
            correctParenTrail(result, 0)

    result['success'] = True

def processError(result, e):
    result['success'] = False
    if e['parinferError']:
        del e['parinferError']
        result['error'] = e
    else:
        result['error']['name'] = ERROR_UNHANDLED
        result['error']['message'] = e['stack']

def processText(text, options, mode):
    result = initialResult(text, options, mode)

    try:
        for line in result['origLines']:
            processLine(result, line)
        finalizeResult(result)
    except ParinferError as e:
        errorDetails = e.args[0]
        processError(result, errorDetails)

    return result

#-------------------------------------------------------------------------------
# Public API Helpers
#-------------------------------------------------------------------------------

def getChangedLines(result):
    changedLines = []
    for i in range(len(result['lines'])):
        if result['lines'][i] != result['origLines'][i]:
            changedLines.append({
                'lineNo': i,
                'line': result['lines'][i],
            })
    return changedLines

def publicResult(result):
    if not result['success']:
        return {
            'text': result['origText'],
            'success': False,
            'error': result['error'],
        }

    lineEnding = getLineEnding(result['origText'])
    return {
        'text': lineEnding.join(result['lines']),
        'success': True,
        'changedLines': getChangedLines(result),
    }

#-------------------------------------------------------------------------------
# Public API
#-------------------------------------------------------------------------------

def indent_mode(text, options):
    result = processText(text, options, INDENT_MODE)
    return publicResult(result)

def paren_mode(text, options):
    result = processText(text, options, PAREN_MODE)
    return publicResult(result)
