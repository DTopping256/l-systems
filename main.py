#! /usr/bin/python3

import turtle
import tkinter as tk

# import time
import math

# A user editable dictionary of rules for an L-System.
rules = {"g": "+f+f+f+f+fg", "+": "-", "-": "+"}

# A user editable dictionary of the configuration options which are used by the commands to adjust the way an L-System is drawn.
config = {
    "axiom": "Pcf-f-f-f-f-fg",
    "startUnit": 150,
    "theta": 60,
    "iterations": 7,
    "speed": 10,
    "max_speed": 0.04,
    "colors": ["blue", "purple"],
    "dynamicScaling": True,
}


def getWidth(pattern):
    maxDist = 0
    minDist = 0
    currentXDist = 0
    xDistStack = []
    currentDirection = 0
    for char in pattern:
        if char == "f":
            currentXDist += math.cos(math.radians(currentDirection))
            if currentXDist > maxDist:
                maxDist = currentXDist
            if currentXDist < minDist:
                minDist = currentXDist
        elif char == "-":
            currentDirection = (currentDirection - config["theta"]) % 360
        elif char == "+":
            currentDirection = (currentDirection + config["theta"]) % 360
        elif char == "[":
            xDistStack.append(currentXDist)
        elif char == "]":
            currentXDist = xDistStack.pop()

    return round(maxDist - minDist)


def getScale(pattern):
    scale = config["startUnit"]
    if config["dynamicScaling"]:
        scale = config["startUnit"] * getWidth(config["axiom"]) / getWidth(pattern)

    print("New scale:", scale)
    return scale


def maintainGlobalVariables(pattern):
    global globalVars
    globalVars = {"currentColor": 0, "unit": getScale(pattern), "positionStack": []}


# Stores the global variables used and modified by the program.
globalVars = maintainGlobalVariables(config["axiom"])

# A user editable dictionary of string keys representing symbols in an L-System string to string values which represent commands.
symbols = {
    "f": "fd",
    "p": "pu",
    "P": "pd",
    "+": "rt",
    "-": "lt",
    "|": "ta",
    "c": "cc",
    "[": "sp",
    "]": "lp",
    ##	         Increment the line width by line width increment
    #!	         Decrement the line width by line width increment
    # @	         Draw a dot with line width radius
    # {	         Open a polygon
    # }	         Close a polygon and fill it with fill colour
    # >	         Multiply the line length by the line length scale factor
    # <	         Divide the line length by the line length scale factor
    # &	         Swap the meaning of + and -
    # (	         Decrement turning angle by turning angle increment
    # )	         Increment turning angle by turning angle increment
}


# A readonly dictionary of string keys representing a valid function to string values which can be used by exec.
def GetCommands(t):
    return {
        "fd": f"t.fd({globalVars['unit']})",
        "pu": "t.pu()",
        "pd": "t.pd()",
        "lt": f"t.lt({config['theta']})",
        "rt": f"t.rt({config['theta']})",
        "ta": "t.lt(180)",
        "cc": "changeColor(t)",
        "sp": "storePosition(t)",
        "lp": "loadPosition(t)",
    }


def storePosition(t):
    globalVars["positionStack"].append(t.pos())


def loadPosition(t):
    if len(globalVars["positionStack"]) > 0:
        t.setpos(globalVars["positionStack"].pop())


def changeColor(t):
    cols = config["colors"]
    nextCol = cols[globalVars["currentColor"]]
    t.pencolor(nextCol)
    globalVars["currentColor"] = (globalVars["currentColor"] + 1) % len(cols)


def draw(t, pattern):
    commands = GetCommands(t)
    for char in pattern:
        if char in symbols:
            commandKey = symbols[char]
            if commandKey in commands:
                # print(commands[commandKey])
                exec(commands[commandKey], globals(), {"t": t})


def setSpeed(t, pattern):
    newSpeed = config["speed"] / pattern.count("f")
    if newSpeed > config["max_speed"]:
        newSpeed = config["max_speed"]

    t.speed(newSpeed)


def applyRules(pattern):
    newPattern = ""
    for char in pattern:
        if char in rules:
            newPattern += rules[char]
        else:
            newPattern += char

    return newPattern


def simplify(pattern, i=0):
    output = ""
    outerloopEnd = len(pattern) - 1
    prefixStartIndex = 0
    multiplier = 0

    while prefixStartIndex < outerloopEnd:
        # print(prefixStartIndex)
        innerloopStart = prefixStartIndex + 1
        innerloopEnd = prefixStartIndex + math.floor(len(pattern) - prefixStartIndex)

        # Figure out how many consecutive suffix substrings are equal to the prefix string.
        multiplier = 0

        for prefixEndIndex in range(innerloopStart, innerloopEnd):

            class State:
                prefixLen = prefixEndIndex - prefixStartIndex
                suffixLen = len(pattern) - prefixEndIndex
                prefix = pattern[prefixStartIndex:prefixEndIndex]

                suffixSubStrStartIndex = 0
                suffixSubStrEndIndex = 0
                suffixSubStr = ""

            s = State()

            if s.prefixLen > s.suffixLen:
                continue

            def getSuffixSubStr():
                s.suffixSubStrStartIndex = prefixEndIndex + multiplier * s.prefixLen
                s.suffixSubStrEndIndex = s.suffixSubStrStartIndex + s.prefixLen
                s.suffixSubStr = pattern[
                    s.suffixSubStrStartIndex : s.suffixSubStrEndIndex
                ]

                # print(s.suffixSubStrStartIndex, s.suffixSubStrEndIndex)
                # print(f'Prefix: "{s.prefix}",\tSuffix (sub-string): "{s.suffixSubStr}"')

            getSuffixSubStr()
            while s.prefix == s.suffixSubStr:
                # print(f'[Match: {s.prefix}, {s.suffixSubStr}]')
                multiplier += 1
                getSuffixSubStr()

            # print(multiplier)
            if multiplier > 0:
                if len(s.prefix) > 1:
                    output += f"{multiplier + 1}({s.prefix})"
                else:
                    output += f"{multiplier + 1}{s.prefix}"
                prefixStartIndex = s.suffixSubStrStartIndex - 1
                break

        if multiplier is 0:
            output += pattern[prefixStartIndex]

        prefixStartIndex += 1

    # print(prefixStartIndex, outerloopEnd, multiplier)
    if prefixStartIndex == outerloopEnd:
        output += pattern[-1]

    # Attempt to simplify
    if len(output) <= len(pattern) and i < 100:
        return simplify(output, i + 1)
    elif len(pattern) < len(output):
        return pattern

    return output


def drawLoop(window, t, text, label):
    pattern = config["axiom"]
    print("Drawing L-System...")
    for i in range(config["iterations"]):
        text.delete("1.0", tk.END)
        text.insert(tk.END, f"Drawing iteration {i}...\n{simplify(pattern)}")
        t.reset()
        setSpeed(t, pattern)
        maintainGlobalVariables(pattern)
        draw(t, pattern)
        countdown = 3
        while countdown > 0:
            label.after(1000)
            label["text"] = countdown
            countdown -= 1
        pattern = applyRules(pattern)


def main():
    # Use the same tk window instance on the
    window = tk.Tk()
    window.title("DansPi Draw Screen")
    text = tk.Text(window, width=25, height=40)
    text.pack(side=tk.LEFT)
    label = tk.Label(window, text="")
    label.pack(side=tk.TOP)
    canvas = turtle.ScrolledCanvas(window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    window.attributes("-fullscreen", True)
    t = turtle.RawTurtle(canvas)

    # Settings to hide the turtle pointer and remove the drawing animation delay.
    # t.ht()
    # t.getscreen().tracer(0)

    drawLoop(window, t, text, label)


main()
