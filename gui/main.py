import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import (
    glDeleteTextures, glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    glClearColor, glEnable, glBlendFunc, glViewport, glMatrixMode, glLoadIdentity,
    glOrtho, glClear, glBegin, glTexCoord2f, glVertex2f, glEnd, glColor4f,

    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
    GL_RGBA, GL_UNSIGNED_BYTE, GL_BLEND,GL_LINES, GL_QUADS, GL_LINE_LOOP, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION, GL_MODELVIEW, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINES, GL_QUADS, GL_LINE_STRIP, GL_LINES, GL_QUADS, GL_LINE_LOOP
)
from OpenGL.GLU import gluOrtho2D
from PIL import Image
from app import GameConfig, RobotConfig, PathPlanner, Utils


[{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"severity": 8,
	"message": "Statements must be separated by newlines or semicolons",
	"source": "Pylance",
	"startLineNumber": 20,
	"startColumn": 8,
	"endLineNumber": 20,
	"endColumn": 19
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"severity": 8,
	"message": "Expected expression",
	"source": "Pylance",
	"startLineNumber": 20,
	"startColumn": 31,
	"endLineNumber": 21,
	"endColumn": 1
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"severity": 8,
	"message": "Unexpected indentation",
	"source": "Pylance",
	"startLineNumber": 21,
	"startColumn": 1,
	"endLineNumber": 21,
	"endColumn": 5
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"severity": 8,
	"message": "Unindent not expected",
	"source": "Pylance",
	"startLineNumber": 130,
	"startColumn": 1,
	"endLineNumber": 130,
	"endColumn": 6
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportUndefinedVariable"
		}
	},
	"severity": 4,
	"message": "\"cclass\" is not defined",
	"source": "Pylance",
	"startLineNumber": 20,
	"startColumn": 1,
	"endLineNumber": 20,
	"endColumn": 7
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportUndefinedVariable"
		}
	},
	"severity": 4,
	"message": "\"OpenGLField\" is not defined",
	"source": "Pylance",
	"startLineNumber": 20,
	"startColumn": 8,
	"endLineNumber": 20,
	"endColumn": 19
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"code": {
		"value": "reportInvalidTypeForm",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportInvalidTypeForm"
		}
	},
	"severity": 4,
	"message": "Type annotation not supported for this statement",
	"source": "Pylance",
	"startLineNumber": 20,
	"startColumn": 31,
	"endLineNumber": 20,
	"endColumn": 31
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportUndefinedVariable"
		}
	},
	"severity": 4,
	"message": "\"OpenGLField\" is not defined",
	"source": "Pylance",
	"startLineNumber": 22,
	"startColumn": 15,
	"endLineNumber": 22,
	"endColumn": 26
},{
	"resource": "/huzaimm01/autonUI/gui/main.py",
	"owner": "python",
	"code": {
		"value": "reportUndefinedVariable",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportUndefinedVariable"
		}
	},
	"severity": 4,
	"message": "\"OpenGLField\" is not defined",
	"source": "Pylance",
	"startLineNumber": 139,
	"startColumn": 28,
	"endLineNumber": 139,
	"endColumn": 39
}]