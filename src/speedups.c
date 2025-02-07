/*
Copyright (c) 2022, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Feb 10, 2022

*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>

const char alphabet[] = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
// C adds a null at the end so it needs -1
const uint64_t alphabet_size = sizeof(alphabet) / sizeof(alphabet[0]) - 1;
const uint8_t id_size = 8;

static PyObject* Tag = 0;
static PyObject* children_str = 0;

/**
 * Generate a short ID (8 characters)
 */
static PyObject* gen_id(PyObject* mod, PyObject* obj)
{
    uint64_t number = (uint64_t) obj;
    char buf[id_size];
    for (uint8_t index = 0; index < id_size; index++)
    {
        lldiv_t r = lldiv(number, alphabet_size);
        number = r.quot;
        buf[index] = alphabet[r.rem];
    }
    return PyUnicode_FromStringAndSize(buf, id_size);
}

/**
 * Lookup the index of the child tag from the parent's children list ignoring
 * any pattern nodes. This provides about a 30% speedup.
 */
static PyObject* lookup_child_index(PyObject* mod, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2) {
        PyErr_SetString( PyExc_ValueError, "must take exactly 2 arguments" );
        return 0;
    }

    // Deferred import of web.components.html.Tag
    if ( !Tag ) {
        PyObject* module = PyImport_ImportModule("web.components.html");
        if (!module) {
            PyErr_SetString( PyExc_ImportError, "Could not import web.components.html" );
            return 0;
        }

        Tag = PyObject_GetAttrString(module, "Tag");
        Py_DECREF(module);
        if ( !Tag ) {
            PyErr_SetString( PyExc_ImportError, "Could not import web.components.html.Tag" );
            return 0;
        }
    }

    PyObject* parent = args[0];
    PyObject* child = args[1];
    if (!PyObject_IsInstance(parent, Tag) || !PyObject_IsInstance(child, Tag)) {
        PyErr_SetString( PyExc_TypeError, "Both arguments must be Tags" );
        return 0;
    }

    PyObject* children = PyObject_GetAttr(parent, children_str);
    if (!children || !PyList_Check(children)) {
        PyErr_SetString( PyExc_TypeError, "Tag's children must be a list" );
        Py_XDECREF(children);
        return 0;
    }

    uint32_t index = 0;
    uint8_t found = 0;
    for (uint32_t i = 0; i < PyList_GET_SIZE(children); i++) {
        PyObject* c = PyList_GET_ITEM(children, i);
        if (c == child)
        {
            found = 1;
            break;
        }

        if (PyObject_IsInstance(c, Tag))
            index += 1;
    }
    Py_DECREF(children);

    if (!found)  {
        PyErr_SetString( PyExc_KeyError, "Child not found" );
        return 0;
    }
    return PyLong_FromLongLong(index);
}

static PyMethodDef speedups_methods[] = {
    {"gen_id",  gen_id, METH_O, "Generate a short ID."},
    {"lookup_child_index", lookup_child_index, METH_FASTCALL, "Find child index"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyModuleDef speedups_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "speedups",
    .m_doc = "Speedups",
    .m_size = -1,
    speedups_methods
};

PyMODINIT_FUNC
PyInit_speedups(void)
{
    children_str = PyUnicode_InternFromString("_children");
    if ( !children_str )
        return 0;

    return PyModule_Create( &speedups_module );
}
