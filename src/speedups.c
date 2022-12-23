/*
Copyright (c) 2022, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Feb 10, 2022

*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>

const char * alphabet = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

/**
 * Generate a short ID (8 characters)
 */
static PyObject * gen_id(PyObject *self, PyObject *obj)
{
    // Builtin ID
    PyObject *id = PyLong_FromVoidPtr(obj);
    if (id && PySys_Audit("builtins.id", "O", id) < 0) {
        Py_DECREF(id);
        return NULL;
    }
    // TODO: Should there be some randomness?
    uint64_t number = PyLong_AsUnsignedLong(id);
    uint8_t index = 0;
    char buf[8];
    while (index < 8)
    {
        // Mod must match sizeof alphabet
        lldiv_t r = lldiv(number, 59);
        number = r.quot;
        buf[index] = alphabet[r.rem];
        index += 1;
    }
    Py_DECREF(id);
    return _PyUnicode_FromASCII(buf, 8);
}

/**
 * Lookup the index of the child tag from the parent's children list ignoring
 * any pattern nodes. This provides about a 30% speedup.
 */
static PyObject * lookup_child_index(PyObject *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2) {
        PyErr_SetString( PyExc_ValueError, "must take exactly 2 arguments" );
        return 0;
    }

    PyObject* module = PyImport_ImportModule("web.components.html");
    if (!module) {
        PyErr_SetString( PyExc_ImportError, "Could not import web.components.html" );
        return 0;
    }

    PyObject* Tag = PyObject_GetAttrString(module, "Tag");
    Py_DECREF(module);
    if (!Tag) {
        PyErr_SetString( PyExc_ImportError, "Could not import web.components.html.Tag" );
        return 0;
    }

    PyObject* parent = args[0];
    PyObject* child = args[1];
    if (!PyObject_IsInstance(parent, Tag) || !PyObject_IsInstance(child, Tag)) {
        PyErr_SetString( PyExc_TypeError, "Both arguments must be Tags" );
        Py_DECREF(Tag);
        return 0;
    }

    PyObject* children = PyObject_GetAttrString(parent, "_children");
    if (!children || !PyList_Check(children)) {
        PyErr_SetString( PyExc_TypeError, "Tag's children must be a list" );
        Py_DECREF(children);
        Py_DECREF(Tag);
        return 0;
    }

    uint32_t index = 0;
    uint8_t found = 0;
    for (uint32_t i = 0; i < PyList_Size(children); i++) {
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
    Py_DECREF(Tag);

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
    return PyModule_Create( &speedups_module );
}
