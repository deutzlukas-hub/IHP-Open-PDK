# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                type_ = type_._type_
                if hasattr(type_, 'as_dict'):
                    value = [type_.as_dict(v) for v in value]
                else:
                    value = [i for i in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))





OSDI_VERSION_MAJOR_CURR = 0 # macro
OSDI_VERSION_MINOR_CURR = 4 # macro
PARA_TY_MASK = 3 # macro
PARA_TY_REAL = 0 # macro
PARA_TY_INT = 1 # macro
PARA_TY_STR = 2 # macro
PARA_KIND_MASK = (3<<30) # macro
PARA_KIND_MODEL = (0<<30) # macro
PARA_KIND_INST = (1<<30) # macro
PARA_KIND_OPVAR = (2<<30) # macro
ACCESS_FLAG_READ = 0 # macro
ACCESS_FLAG_SET = 1 # macro
ACCESS_FLAG_INSTANCE = 4 # macro
JACOBIAN_ENTRY_RESIST_CONST = 1 # macro
JACOBIAN_ENTRY_REACT_CONST = 2 # macro
JACOBIAN_ENTRY_RESIST = 4 # macro
JACOBIAN_ENTRY_REACT = 8 # macro
CALC_RESIST_RESIDUAL = 1 # macro
CALC_REACT_RESIDUAL = 2 # macro
CALC_RESIST_JACOBIAN = 4 # macro
CALC_REACT_JACOBIAN = 8 # macro
CALC_NOISE = 16 # macro
CALC_OP = 32 # macro
CALC_RESIST_LIM_RHS = 64 # macro
CALC_REACT_LIM_RHS = 128 # macro
ENABLE_LIM = 256 # macro
INIT_LIM = 512 # macro
ANALYSIS_NOISE = 1024 # macro
ANALYSIS_DC = 2048 # macro
ANALYSIS_AC = 4096 # macro
ANALYSIS_TRAN = 8192 # macro
ANALYSIS_IC = 16384 # macro
ANALYSIS_STATIC = 32768 # macro
ANALYSIS_NODESET = 65536 # macro
EVAL_RET_FLAG_LIM = 1 # macro
EVAL_RET_FLAG_FATAL = 2 # macro
EVAL_RET_FLAG_FINISH = 4 # macro
EVAL_RET_FLAG_STOP = 8 # macro
LOG_LVL_MASK = 7 # macro
LOG_LVL_DEBUG = 0 # macro
LOG_LVL_DISPLAY = 1 # macro
LOG_LVL_INFO = 2 # macro
LOG_LVL_WARN = 3 # macro
LOG_LVL_ERR = 4 # macro
LOG_LVL_FATAL = 5 # macro
LOG_FMT_ERR = 16 # macro
INIT_ERR_OUT_OF_BOUNDS = 1 # macro
ATTR_TYPE_STR = 0 # macro
ATTR_TYPE_INT = 1 # macro
ATTR_TYPE_REAL = 2 # macro
NATREF_NONE = 0 # macro
NATREF_NATURE = 1 # macro
NATREF_DISCIPLINE_FLOW = 2 # macro
NATREF_DISCIPLINE_POTENTIAL = 3 # macro
DOMAIN_NOT_GIVEN = 0 # macro
DOMAIN_DISCRETE = 1 # macro
DOMAIN_CONTINUOUS = 2 # macro
class struct_OsdiLimFunction(Structure):
    pass

struct_OsdiLimFunction._pack_ = 1 # source:False
struct_OsdiLimFunction._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('num_args', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('func_ptr', ctypes.POINTER(None)),
]

OsdiLimFunction = struct_OsdiLimFunction
class struct_OsdiSimParas(Structure):
    pass

struct_OsdiSimParas._pack_ = 1 # source:False
struct_OsdiSimParas._fields_ = [
    ('names', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
    ('vals', ctypes.POINTER(ctypes.c_double)),
    ('names_str', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
    ('vals_str', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
]

OsdiSimParas = struct_OsdiSimParas
class struct_OsdiSimInfo(Structure):
    pass

struct_OsdiSimInfo._pack_ = 1 # source:False
struct_OsdiSimInfo._fields_ = [
    ('paras', OsdiSimParas),
    ('abstime', ctypes.c_double),
    ('prev_solve', ctypes.POINTER(ctypes.c_double)),
    ('prev_state', ctypes.POINTER(ctypes.c_double)),
    ('next_state', ctypes.POINTER(ctypes.c_double)),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

OsdiSimInfo = struct_OsdiSimInfo
class union_OsdiInitErrorPayload(Union):
    pass

union_OsdiInitErrorPayload._pack_ = 1 # source:False
union_OsdiInitErrorPayload._fields_ = [
    ('parameter_id', ctypes.c_uint32),
]

OsdiInitErrorPayload = union_OsdiInitErrorPayload
class struct_OsdiInitError(Structure):
    pass

struct_OsdiInitError._pack_ = 1 # source:False
struct_OsdiInitError._fields_ = [
    ('code', ctypes.c_uint32),
    ('payload', OsdiInitErrorPayload),
]

OsdiInitError = struct_OsdiInitError
class struct_OsdiInitInfo(Structure):
    pass

struct_OsdiInitInfo._pack_ = 1 # source:False
struct_OsdiInitInfo._fields_ = [
    ('flags', ctypes.c_uint32),
    ('num_errors', ctypes.c_uint32),
    ('errors', ctypes.POINTER(struct_OsdiInitError)),
]

OsdiInitInfo = struct_OsdiInitInfo
class struct_OsdiNodePair(Structure):
    pass

struct_OsdiNodePair._pack_ = 1 # source:False
struct_OsdiNodePair._fields_ = [
    ('node_1', ctypes.c_uint32),
    ('node_2', ctypes.c_uint32),
]

OsdiNodePair = struct_OsdiNodePair
class struct_OsdiJacobianEntry(Structure):
    pass

struct_OsdiJacobianEntry._pack_ = 1 # source:False
struct_OsdiJacobianEntry._fields_ = [
    ('nodes', OsdiNodePair),
    ('react_ptr_off', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

OsdiJacobianEntry = struct_OsdiJacobianEntry
class struct_OsdiNode(Structure):
    pass

struct_OsdiNode._pack_ = 1 # source:False
struct_OsdiNode._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('units', ctypes.POINTER(ctypes.c_char)),
    ('residual_units', ctypes.POINTER(ctypes.c_char)),
    ('resist_residual_off', ctypes.c_uint32),
    ('react_residual_off', ctypes.c_uint32),
    ('resist_limit_rhs_off', ctypes.c_uint32),
    ('react_limit_rhs_off', ctypes.c_uint32),
    ('is_flow', ctypes.c_bool),
    ('PADDING_0', ctypes.c_ubyte * 7),
]

OsdiNode = struct_OsdiNode
class struct_OsdiParamOpvar(Structure):
    pass

struct_OsdiParamOpvar._pack_ = 1 # source:False
struct_OsdiParamOpvar._fields_ = [
    ('name', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
    ('num_alias', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('description', ctypes.POINTER(ctypes.c_char)),
    ('units', ctypes.POINTER(ctypes.c_char)),
    ('flags', ctypes.c_uint32),
    ('len', ctypes.c_uint32),
]

OsdiParamOpvar = struct_OsdiParamOpvar
class struct_OsdiNoiseSource(Structure):
    pass

struct_OsdiNoiseSource._pack_ = 1 # source:False
struct_OsdiNoiseSource._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('nodes', OsdiNodePair),
]

OsdiNoiseSource = struct_OsdiNoiseSource
class struct_OsdiNatureRef(Structure):
    pass

struct_OsdiNatureRef._pack_ = 1 # source:False
struct_OsdiNatureRef._fields_ = [
    ('ref_type', ctypes.c_uint32),
    ('index', ctypes.c_uint32),
]

OsdiNatureRef = struct_OsdiNatureRef
class struct_OsdiDescriptor(Structure):
    pass

struct_OsdiDescriptor._pack_ = 1 # source:False
struct_OsdiDescriptor._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('num_nodes', ctypes.c_uint32),
    ('num_terminals', ctypes.c_uint32),
    ('nodes', ctypes.POINTER(struct_OsdiNode)),
    ('num_jacobian_entries', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('jacobian_entries', ctypes.POINTER(struct_OsdiJacobianEntry)),
    ('num_collapsible', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('collapsible', ctypes.POINTER(struct_OsdiNodePair)),
    ('collapsed_offset', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('noise_sources', ctypes.POINTER(struct_OsdiNoiseSource)),
    ('num_noise_src', ctypes.c_uint32),
    ('num_params', ctypes.c_uint32),
    ('num_instance_params', ctypes.c_uint32),
    ('num_opvars', ctypes.c_uint32),
    ('param_opvar', ctypes.POINTER(struct_OsdiParamOpvar)),
    ('node_mapping_offset', ctypes.c_uint32),
    ('jacobian_ptr_resist_offset', ctypes.c_uint32),
    ('num_states', ctypes.c_uint32),
    ('state_idx_off', ctypes.c_uint32),
    ('bound_step_offset', ctypes.c_uint32),
    ('instance_size', ctypes.c_uint32),
    ('model_size', ctypes.c_uint32),
    ('PADDING_3', ctypes.c_ubyte * 4),
    ('access', ctypes.CFUNCTYPE(ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32, ctypes.c_uint32)),
    ('setup_model', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(struct_OsdiSimParas), ctypes.POINTER(struct_OsdiInitInfo))),
    ('setup_instance', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_double, ctypes.c_uint32, ctypes.POINTER(struct_OsdiSimParas), ctypes.POINTER(struct_OsdiInitInfo))),
    ('eval', ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(struct_OsdiSimInfo))),
    ('load_noise', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_double, ctypes.POINTER(ctypes.c_double))),
    ('load_residual_resist', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('load_residual_react', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('load_limit_rhs_resist', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('load_limit_rhs_react', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('load_spice_rhs_dc', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double))),
    ('load_spice_rhs_tran', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_double)),
    ('load_jacobian_resist', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None))),
    ('load_jacobian_react', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_double)),
    ('load_jacobian_tran', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_double)),
    ('given_flag_model', ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(None), ctypes.c_uint32)),
    ('given_flag_instance', ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(None), ctypes.c_uint32)),
    ('num_resistive_jacobian_entries', ctypes.c_uint32),
    ('num_reactive_jacobian_entries', ctypes.c_uint32),
    ('write_jacobian_array_resist', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('write_jacobian_array_react', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_double))),
    ('num_inputs', ctypes.c_uint32),
    ('PADDING_4', ctypes.c_ubyte * 4),
    ('inputs', ctypes.POINTER(struct_OsdiNodePair)),
    ('load_jacobian_with_offset_resist', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64)),
    ('load_jacobian_with_offset_react', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64)),
    ('unknown_nature', ctypes.POINTER(struct_OsdiNatureRef)),
    ('residual_nature', ctypes.POINTER(struct_OsdiNatureRef)),
]

OsdiDescriptor = struct_OsdiDescriptor
class struct_OsdiNature(Structure):
    pass

struct_OsdiNature._pack_ = 1 # source:False
struct_OsdiNature._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('parent_type', ctypes.c_uint32),
    ('parent', ctypes.c_uint32),
    ('ddt', ctypes.c_uint32),
    ('idt', ctypes.c_uint32),
    ('attr_start', ctypes.c_uint32),
    ('num_attr', ctypes.c_uint32),
]

OsdiNature = struct_OsdiNature
class struct_OsdiDiscipline(Structure):
    pass

struct_OsdiDiscipline._pack_ = 1 # source:False
struct_OsdiDiscipline._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('flow', ctypes.c_uint32),
    ('potential', ctypes.c_uint32),
    ('domain', ctypes.c_uint32),
    ('attr_start', ctypes.c_uint32),
    ('num_flow_attr', ctypes.c_uint32),
    ('num_potential_attr', ctypes.c_uint32),
    ('num_user_attr', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

OsdiDiscipline = struct_OsdiDiscipline
class union_OsdiAttributeValue(Union):
    pass

union_OsdiAttributeValue._pack_ = 1 # source:False
union_OsdiAttributeValue._fields_ = [
    ('string', ctypes.POINTER(ctypes.c_char)),
    ('integer', ctypes.c_int32),
    ('real', ctypes.c_double),
]

OsdiAttributeValue = union_OsdiAttributeValue
class struct_OsdiAttribute(Structure):
    pass

struct_OsdiAttribute._pack_ = 1 # source:False
struct_OsdiAttribute._fields_ = [
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('value_type', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('value', OsdiAttributeValue),
]

OsdiAttribute = struct_OsdiAttribute
__all__ = \
    ['ACCESS_FLAG_INSTANCE', 'ACCESS_FLAG_READ', 'ACCESS_FLAG_SET',
    'ANALYSIS_AC', 'ANALYSIS_DC', 'ANALYSIS_IC', 'ANALYSIS_NODESET',
    'ANALYSIS_NOISE', 'ANALYSIS_STATIC', 'ANALYSIS_TRAN',
    'ATTR_TYPE_INT', 'ATTR_TYPE_REAL', 'ATTR_TYPE_STR', 'CALC_NOISE',
    'CALC_OP', 'CALC_REACT_JACOBIAN', 'CALC_REACT_LIM_RHS',
    'CALC_REACT_RESIDUAL', 'CALC_RESIST_JACOBIAN',
    'CALC_RESIST_LIM_RHS', 'CALC_RESIST_RESIDUAL',
    'DOMAIN_CONTINUOUS', 'DOMAIN_DISCRETE', 'DOMAIN_NOT_GIVEN',
    'ENABLE_LIM', 'EVAL_RET_FLAG_FATAL', 'EVAL_RET_FLAG_FINISH',
    'EVAL_RET_FLAG_LIM', 'EVAL_RET_FLAG_STOP',
    'INIT_ERR_OUT_OF_BOUNDS', 'INIT_LIM', 'JACOBIAN_ENTRY_REACT',
    'JACOBIAN_ENTRY_REACT_CONST', 'JACOBIAN_ENTRY_RESIST',
    'JACOBIAN_ENTRY_RESIST_CONST', 'LOG_FMT_ERR', 'LOG_LVL_DEBUG',
    'LOG_LVL_DISPLAY', 'LOG_LVL_ERR', 'LOG_LVL_FATAL', 'LOG_LVL_INFO',
    'LOG_LVL_MASK', 'LOG_LVL_WARN', 'NATREF_DISCIPLINE_FLOW',
    'NATREF_DISCIPLINE_POTENTIAL', 'NATREF_NATURE', 'NATREF_NONE',
    'OSDI_VERSION_MAJOR_CURR', 'OSDI_VERSION_MINOR_CURR',
    'OsdiAttribute', 'OsdiAttributeValue', 'OsdiDescriptor',
    'OsdiDiscipline', 'OsdiInitError', 'OsdiInitErrorPayload',
    'OsdiInitInfo', 'OsdiJacobianEntry', 'OsdiLimFunction',
    'OsdiNature', 'OsdiNatureRef', 'OsdiNode', 'OsdiNodePair',
    'OsdiNoiseSource', 'OsdiParamOpvar', 'OsdiSimInfo',
    'OsdiSimParas', 'PARA_KIND_INST', 'PARA_KIND_MASK',
    'PARA_KIND_MODEL', 'PARA_KIND_OPVAR', 'PARA_TY_INT',
    'PARA_TY_MASK', 'PARA_TY_REAL', 'PARA_TY_STR',
    'struct_OsdiAttribute', 'struct_OsdiDescriptor',
    'struct_OsdiDiscipline', 'struct_OsdiInitError',
    'struct_OsdiInitInfo', 'struct_OsdiJacobianEntry',
    'struct_OsdiLimFunction', 'struct_OsdiNature',
    'struct_OsdiNatureRef', 'struct_OsdiNode', 'struct_OsdiNodePair',
    'struct_OsdiNoiseSource', 'struct_OsdiParamOpvar',
    'struct_OsdiSimInfo', 'struct_OsdiSimParas',
    'union_OsdiAttributeValue', 'union_OsdiInitErrorPayload']
