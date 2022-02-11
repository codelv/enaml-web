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

static PyMethodDef speedups_methods[] = {
    {"gen_id",  gen_id, METH_O, "Generate a short ID."},
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
