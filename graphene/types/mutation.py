from collections import OrderedDict

from ..utils.get_unbound_function import get_unbound_function
from ..utils.props import props
from .field import Field
from .utils import yank_fields_from_attrs
from .objecttype import ObjectType, ObjectTypeOptions

from .base import BaseOptions, BaseType


class MutationOptions(ObjectTypeOptions):
    arguments = None  # type: Dict[str, Argument]
    output = None  # type: Type[ObjectType]
    resolver = None  # type: Function


class Mutation(ObjectType):
    '''
    Mutation Type Definition
    '''
    @classmethod
    def __init_subclass_with_meta__(cls, resolver=None, output=None, arguments=None, **options):
        _meta = MutationOptions(cls)

        output = output or getattr(cls, 'Output', None)
        fields = {}
        if not output:
            # If output is defined, we don't need to get the fields
            fields = OrderedDict()
            for base in reversed(cls.__mro__):
                fields.update(
                    yank_fields_from_attrs(base.__dict__, _as=Field)
                )
            output = cls
        
        if not arguments:
            input_class = getattr(cls, 'Input', None)
            if input_class:
                arguments = props(input_class)
            else:
                arguments = {}

        resolver = resolver or get_unbound_function(getattr(cls, 'mutate', None))
        assert resolver, 'All mutations must define a mutate method in it'

        _meta.fields = fields
        _meta.output = output
        _meta.resolver = resolver
        _meta.arguments = arguments

        super(Mutation, cls).__init_subclass_with_meta__(_meta=_meta, **options)
    
    @classmethod
    def Field(cls, *args, **kwargs):
        return Field(
            cls._meta.output, args=cls._meta.arguments, resolver=cls._meta.resolver
        )
